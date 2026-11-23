"""A local, single-parent task-graph controller with durable approval boundaries.

The model reasons about plans and outcomes. This module owns process dispatch,
candidate identity, state transitions and Git authority. No model result can
approve the root task or publish a branch.
"""
from __future__ import annotations

import asyncio
from dataclasses import asdict
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any
import uuid

from .git import GitRepo
from .ledger import Ledger, Record, fcntl
from .manifest import canonical, digest, load, strict_json, validate
from .policy import POLICY
from .process import run_codex
from .protocol import SCHEMA, validate_result
from .verification import verify


class ControllerError(RuntimeError):
    pass


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp-" + uuid.uuid4().hex)
    with temporary.open("x", encoding="utf-8") as output:
        output.write(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
        output.flush()
        os.fsync(output.fileno())
    temporary.replace(path)


def sha_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ControllerError(f"Expected regular file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def within(root: Path, path: Path) -> None:
    """Protect evidence reads/writes from symlinked ancestor directories."""
    if not path.is_relative_to(root) or not path.resolve().is_relative_to(root.resolve()):
        raise ControllerError(f"Path escapes its workspace: {path}")
    for component in (path, *path.parents):
        if component == root.parent:
            break
        if component.is_symlink():
            raise ControllerError(f"Workspace evidence path contains a symlink: {component}")


def git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    environment = os.environ.copy()
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                 "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_PREFIX"):
        environment.pop(name, None)
    environment["GIT_TERMINAL_PROMPT"] = "0"
    return subprocess.run(["git", "-C", str(repo), *args], check=check, env=environment,
                          stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60)


def instruction_paths(repo: Path) -> list[str]:
    tracked = git(repo, "ls-files", "-z").stdout.split(b"\0")
    other = git(repo, "ls-files", "--others", "-z").stdout.split(b"\0")
    return sorted({os.fsdecode(name) for name in tracked + other if name and (
        Path(os.fsdecode(name)).name in {"AGENTS.md", "AGENTS.override.md"}
        or os.fsdecode(name).startswith(".codex/"))})


def matched(path: str, allowed: list[str]) -> bool:
    return any(path == prefix or (prefix.endswith("/") and path.startswith(prefix))
               for prefix in allowed)


def initialize(*, repo: Path, manifest_path: Path, run_dir: Path, approved: bool) -> dict:
    if not approved:
        raise ControllerError("init requires --approve: the operator must approve this exact plan and its delegations")
    manifest = load(manifest_path)
    repo = repo.resolve(strict=True)
    parent = GitRepo(repo)
    repo = parent.path
    parent.require_clean()
    if parent.branch() in {"main", "master"}:
        raise ControllerError("Use a dedicated parent task branch, not main/master")
    run_dir = run_dir.absolute()
    if run_dir.resolve().is_relative_to(repo) or repo.is_relative_to(run_dir.resolve()):
        raise ControllerError("run-dir must be outside the parent checkout and cannot contain it")
    if run_dir.exists() or run_dir.is_symlink():
        raise ControllerError("run-dir must be new; existing task evidence is never overwritten")
    brief = repo / manifest["parent_brief"]
    within(repo, brief)
    if not brief.resolve(strict=True).is_relative_to(repo):
        raise ControllerError("Parent brief must remain in the checkout")
    brief_hash = sha_file(brief)
    if git(repo, "check-ignore", "-q", ".agent/TASK_BRIEF.md", check=False).returncode:
        raise ControllerError("The project must ignore /.agent/ before orchestration")
    paths = sorted(set(manifest["policy_files"]) | set(instruction_paths(repo)))
    pinned = {}
    for name in paths:
        file = repo / name
        within(repo, file)
        if not file.resolve(strict=True).is_relative_to(repo):
            raise ControllerError(f"Policy path escapes checkout: {name}")
        if git(repo, "ls-files", "--error-unmatch", "--", name, check=False).returncode:
            raise ControllerError(f"Policy must be tracked and committed: {name}")
        pinned[name] = {"sha256": sha_file(file), "text": file.read_text(encoding="utf-8")}
    policy = {"protocol": POLICY, "files": pinned, "instruction_paths": instruction_paths(repo)}
    h0 = parent.head()
    run_dir.mkdir(parents=True, mode=0o700)
    write_json(run_dir / "manifest.json", manifest)
    write_json(run_dir / "policy.json", policy)
    (run_dir / "parent-brief.md").write_bytes(brief.read_bytes())
    with Ledger(run_dir / "ledger.sqlite3") as ledger:
        ledger.put("run", manifest["run_id"], data={
            "repo": str(repo), "branch": parent.branch(), "h0": h0, "head": h0,
            "manifest_hash": digest(manifest), "policy_hash": digest(policy),
            "parent_brief_hash": brief_hash, "session_id": None,
            "repair_session_id": None,
            "active_invocation": None, "authorization": manifest["authorization"],
        }, phase="Phase 2", state="ready", expected_revision=None,
            event="run.authorized", event_data={"operator_approved": True})
        for task in manifest["tasks"]:
            ledger.put("task", task["id"], data={
                "base": h0 if not task["depends_on"] else None,
                "path": str(run_dir / "worktrees" / task["id"]),
                "branch": f"socrates/{manifest['run_id']}/{task['id']}",
                "session_id": None, "active_invocation": None,
                "attempts": {}, "candidate_id": None, "plan_id": None,
                "feedback": "", "cleanup": "not_eligible",
            }, phase="Phase 1", state="pending", expected_revision=None,
                event="task.delegated", event_data={"criteria": task["criteria"],
                                                    "depends_on": task["depends_on"],
                                                    "reviewer": task["reviewer"]})
    return {"run_dir": str(run_dir), "run_id": manifest["run_id"], "base": h0}


class Controller:
    def __init__(self, run_dir: Path, *, executable: str = "codex"):
        self.directory = run_dir.resolve(strict=True)
        self.manifest = validate(strict_json((self.directory / "manifest.json").read_text()))
        self.run_id = self.manifest["run_id"]
        self.tasks = {task["id"]: task for task in self.manifest["tasks"]}
        self.policy = strict_json((self.directory / "policy.json").read_text())
        self.ledger = Ledger(self.directory / "ledger.sqlite3")
        self._repo_lock_fd: int | None = None
        self.executable = executable
        self.parent_lock = asyncio.Lock()
        self.semaphore = asyncio.Semaphore(self.manifest["max_workers"])
        try:
            run = self.record("run", self.run_id)
            if run.data["manifest_hash"] != digest(self.manifest) or run.data["policy_hash"] != digest(self.policy):
                raise ControllerError("Approved manifest or policy changed; start a newly approved run")
            if run.data["parent_brief_hash"] != sha_file(self.directory / "parent-brief.md"):
                raise ControllerError("Approved parent brief snapshot changed")
            if self.policy["protocol"] != POLICY:
                raise ControllerError("Runtime policy version changed; use the original runtime or approve a new run")
            self.repo = GitRepo(Path(run.data["repo"]))
            # Different run directories still share Git metadata and possibly the
            # parent checkout. A per-run SQLite lock alone cannot serialize them.
            lock = self.repo.common_dir / "socrates-orchestrator" / "controller.lock"
            lock.parent.mkdir(parents=True, exist_ok=True)
            self._repo_lock_fd = os.open(lock, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
            try:
                fcntl.flock(self._repo_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise ControllerError("Another supervisor owns this Git repository") from exc
        except BaseException:
            self.close()
            raise

    def __enter__(self) -> Controller:
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def close(self) -> None:
        if self._repo_lock_fd is not None:
            os.close(self._repo_lock_fd)
            self._repo_lock_fd = None
        self.ledger.close()

    def record(self, kind: str, identifier: str) -> Record:
        result = self.ledger.get(kind, identifier)
        if result is None:
            raise ControllerError(f"Missing {kind}: {identifier}")
        return result

    def update(self, kind: str, identifier: str, *, state: str | None = None,
               phase: str | None = None, event: str = "state.changed", **data: Any) -> Record:
        record = self.record(kind, identifier)
        return self.ledger.put(kind, identifier, data={**record.data, **data},
                               phase=phase or record.phase, state=state or record.state,
                               expected_revision=record.revision, event=event)

    def transition(self, tid: str, state: str, phase: int, **data: Any) -> Record:
        record = self.update("task", tid, state=state, phase=f"Phase {phase}",
                             event="task.transition", active_invocation=None, **data)
        self.project_status()
        return record

    def project_status(self) -> None:
        run = self.record("run", self.run_id)
        lines = [f"# Orchestration {self.run_id}", "", f"Parent: {run.phase}; {run.state}",
                 f"Approved scope: parent-brief.md; manifest {run.data['manifest_hash']}", "",
                 "This is a generated projection. The SQLite ledger owns execution state.", "",
                 "| Task | Phase | State | Worktree cleanup |", "|---|---|---|---|"]
        for task in self.ledger.list("task"):
            lines.append(f"| {task.id} | {task.phase} | {task.state} | {task.data['cleanup']} |")
        (self.directory / "STATUS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    def check_parent(self, *, clean: bool = True) -> None:
        run = self.record("run", self.run_id)
        self.check_parent_identity()
        self.repo.require_head(run.data["head"])
        if clean:
            self.repo.require_clean()

    def check_parent_identity(self) -> None:
        run = self.record("run", self.run_id)
        if self.repo.branch() != run.data["branch"]:
            raise ControllerError("Parent task branch changed")
        self.check_policy(self.repo.path)
        original = self.repo.path / self.manifest["parent_brief"]
        within(self.repo.path, original)
        if sha_file(original) != run.data["parent_brief_hash"]:
            raise ControllerError("Active parent brief changed after approval; reconcile scope explicitly")

    def check_task_identity(self, tid: str, repo: GitRepo) -> None:
        task = self.record("task", tid)
        if repo.common_dir != self.repo.common_dir or repo.branch() != task.data["branch"]:
            raise ControllerError(f"Task worktree branch or repository changed: {tid}")
        repo.require_descendant(task.data["base"], repo.head())

    def check_policy(self, root: Path) -> None:
        if instruction_paths(root) != self.policy["instruction_paths"]:
            raise ControllerError("Instruction/config file set changed")
        for name, policy in self.policy["files"].items():
            within(root, root / name)
            if sha_file(root / name) != policy["sha256"]:
                raise ControllerError(f"Pinned policy changed: {name}")

    def archive_path(self, tid: str) -> str:
        return f"docs/agent/tasks/{self.run_id}/{tid}"

    def allowed_paths(self, tid: str, *, archives: bool = False) -> list[str]:
        paths = list(self.tasks[tid]["allowed_paths"])
        if archives:
            paths.append(self.archive_path(tid) + "/")
        return paths

    def check_scope(self, root: Path, base: str, paths: list[str]) -> None:
        changed = git(root, "diff", "--no-renames", "--no-ext-diff", "--no-textconv",
                      "--ignore-submodules=none", "--name-only", "-z", base).stdout.split(b"\0")
        new = git(root, "ls-files", "--others", "--exclude-standard", "-z").stdout.split(b"\0")
        rejected = sorted({os.fsdecode(p) for p in changed + new if p and not matched(os.fsdecode(p), paths)})
        if rejected:
            raise ControllerError(f"Changes exceed approved paths: {rejected}")
        self.check_policy(root)

    def ensure_worktree(self, tid: str) -> GitRepo:
        record = self.record("task", tid)
        path = Path(record.data["path"])
        if record.data["base"] is None:
            for dependency in self.tasks[tid]["depends_on"]:
                if self.record("task", dependency).state != "integrated":
                    raise ControllerError(f"Prerequisite not integrated: {dependency}")
            self.check_parent()
            record = self.update("task", tid, base=self.repo.head(), event="task.base_pinned")
        if not path.exists():
            self.repo.create_worktree(path, record.data["branch"], record.data["base"],
                                      managed_root=self.directory / "worktrees")
        task_repo = self.repo.verify_managed_worktree(path, record.data["branch"], record.data["base"],
                                                     managed_root=self.directory / "worktrees")
        self.check_task_identity(tid, task_repo)
        self.check_policy(path)
        if record.state == "pending":
            agent = path / ".agent"
            within(path, agent)
            agent.mkdir(exist_ok=True)
            task = self.tasks[tid]
            seed_brief = (
                f"# {tid}: {task['title']}\n\n## Delegated scope\n{task['instructions']}\n\n"
                + "## Original success criteria\n"
                + "\n".join(f"- {c['id']}: {c['text']}" for c in self.manifest["criteria"] if c["id"] in task["criteria"])
                + f"\n\n## Execution state\nSee {self.directory / 'STATUS.md'}.\n"
                + "\n## Plan\nComplete the plan before requesting approval.\n")
            seeds = {"TASK_BRIEF.md": seed_brief, "MEMORY.md": f"# Investigation evidence for {tid}\n"}
            for name, content in seeds.items():
                file = agent / name
                if file.exists():
                    sha_file(file)
                    if file.read_text() != content:
                        raise ControllerError("Unexpected active records in new task worktree; inspect before recovery")
                else:
                    file.write_text(content, encoding="utf-8")
            self.transition(tid, "planning", 1)
        return task_repo

    def candidate(self, candidate_id: str) -> dict:
        record = self.record("candidate", candidate_id)
        directory = Path(record.data["directory"])
        within(self.directory, directory)
        expected = record.data["files"]
        entries = list(directory.rglob("*"))
        if any(p.is_symlink() for p in entries):
            raise ControllerError("Candidate contains a symlink")
        files = {str(p.relative_to(directory)): sha_file(p) for p in entries if p.is_file()}
        if files != expected:
            raise ControllerError("Candidate artifacts changed after freezing")
        content = strict_json((directory / "candidate.json").read_text())
        if digest(content) != candidate_id:
            raise ControllerError("Candidate identity does not match its content")
        for check in content["checks"]:
            if sha_file(Path(check["log"])) != check["log_sha256"]:
                raise ControllerError("Candidate verification log changed")
        return content

    async def freeze(self, tid: str, stage: str) -> str:
        record = self.record("task", tid)
        repo = GitRepo(Path(record.data["path"]))
        self.check_task_identity(tid, repo)
        self.check_scope(repo.path, record.data["base"], self.allowed_paths(tid, archives=stage == "closeout" or record.data.get("reopened", False)))
        if stage == "plan":
            repo.require_head(record.data["base"])
            repo.require_clean()
        else:
            repo.commit_snapshot(f"socrates: {self.run_id}/{tid} {stage} candidate", expected_head=repo.head())
        repo.require_clean()
        head = repo.head()
        checks = []
        if stage != "plan":
            checks = await verify(self.tasks[tid]["verify"], cwd=repo.path,
                                  directory=self.directory / "checks" / uuid.uuid4().hex,
                                  timeout=self.manifest["timeout_seconds"])
            repo.require_head(head)
            repo.require_clean()
            self.check_policy(repo.path)
        archive = repo.path / self.archive_path(tid)
        source = archive if stage == "closeout" else repo.path / ".agent"
        within(repo.path, source)
        names = ["TASK_BRIEF.md", "MEMORY.md"] + (["CLOSEOUT.md"] if stage == "closeout" else [])
        records = {}
        for name in names:
            file = source / name
            sha_file(file)
            text = file.read_text(encoding="utf-8")
            if not text.strip():
                raise ControllerError(f"Empty task record: {file}")
            records[name] = text
        if stage == "closeout" and any((repo.path / ".agent" / name).exists() for name in names[:2]):
            raise ControllerError("Closeout left active task records instead of archiving them")
        content = {"run_id": self.run_id, "task_id": tid, "stage": stage,
                   "base": record.data["base"], "commit": head, "tree": repo.tree(head),
                   "policy_hash": self.record("run", self.run_id).data["policy_hash"],
                   "manifest_hash": digest(self.manifest), "criteria": self.tasks[tid]["criteria"],
                   "plan_id": record.data["plan_id"], "records": records, "checks": checks,
                   "attempts": record.data["attempts"]}
        cid = digest(content)
        directory = self.directory / "candidates" / tid / cid
        directory.mkdir(parents=True, exist_ok=False)
        write_json(directory / "candidate.json", content)
        for name, text in records.items():
            (directory / name).write_text(text, encoding="utf-8")
        hashes = {p.name: sha_file(p) for p in directory.iterdir()}
        self.ledger.put("candidate", cid, data={"directory": str(directory), "files": hashes,
                                               "task_id": tid, "commit": head, "stage": stage},
                        phase=record.phase, state="frozen", expected_revision=None, event="candidate.frozen")
        self.repo.archive_ref(self.run_id, f"{tid}-{stage}-{cid[:12]}", head)
        return cid

    def check_candidate_source(self, cid: str) -> dict:
        content = self.candidate(cid)
        task = self.record("task", content["task_id"])
        repo = GitRepo(Path(task.data["path"]))
        self.check_task_identity(task.id, repo)
        repo.require_head(content["commit"])
        repo.require_clean()
        self.check_policy(repo.path)
        source = repo.path / (self.archive_path(task.id) if content["stage"] == "closeout" else ".agent")
        within(repo.path, source)
        for name, expected in content["records"].items():
            file = source / name
            sha_file(file)
            if file.read_text(encoding="utf-8") != expected:
                raise ControllerError("Live task records changed after candidate freeze")
        return content

    async def invoke(self, tid: str, operation: str, expected: set[str], *,
                     parent: bool = False, candidate_id: str = "", extra: dict | None = None) -> dict:
        run = self.record("run", self.run_id)
        task = self.record("task", tid) if tid != "parent" else None
        if parent and run.data["active_invocation"]:
            raise ControllerError("A previous parent invocation requires explicit recovery")
        target = self.repo.path if parent else Path(task.data["path"])
        self.check_policy(target)
        iid = uuid.uuid4().hex
        criteria = self.tasks[tid]["criteria"] if task else [c["id"] for c in self.manifest["criteria"]]
        request = {
            "protocol": POLICY, "project_policy": self.policy["files"],
            "parent_brief": (self.directory / "parent-brief.md").read_text(),
            "manifest": self.manifest, "task": self.tasks.get(tid),
            "task_id": tid, "operation": operation, "invocation_id": iid,
            "role": "integration_author" if parent and operation == "integration_repair" else "parent_reviewer" if parent else "task_worker",
            "candidate_id": candidate_id, "policy_hash": run.data["policy_hash"],
            "criterion_ids": criteria, "parent_task_phase": "Phase 2",
            "task_workspace": str(Path(task.data["path"])) if task else str(self.repo.path),
            "cwd": str(target), "archive_path": self.archive_path(tid),
            "candidate": self.candidate(candidate_id) if candidate_id else None,
            "approved_plan": self.candidate(task.data["plan_id"]) if task and task.data["plan_id"] else None,
            "feedback": task.data["feedback"] if task else "",
            "dependency_history": [self.candidate(self.record("task", dep).data["accepted_id"])
                                   for dep in self.tasks[tid]["depends_on"]] if task else [],
            "expected_kinds": sorted(expected),
            "instruction": "Execute only the named operation and stop at its handoff. Return the schema object. "
                           "Plans and scope are explicit approvals, not tool permission requests. "
                           "For review_plan, criterion status passed means the plan credibly covers the requirement and its verification, "
                           "not that unimplemented behavior has already passed tests. For result/closeout/integration reviews, "
                           "passed means acceptance of the available outcome evidence; identify source inspection and unexecuted assumptions. "
                           "Prepare_handoff reports readiness for the external final reviewer; it never approves the root.",
            **(extra or {}),
        }
        owner_kind, owner_id = ("run", self.run_id) if parent else ("task", tid)
        owner = self.record(owner_kind, owner_id)
        session_key = "repair_session_id" if parent and operation == "integration_repair" else "session_id"
        session = owner.data.get(session_key)
        invocation_dir = self.directory / "invocations" / iid
        self.ledger.put("invocation", iid, data={"task_id": tid, "operation": operation,
                                               "parent": parent, "path": str(invocation_dir),
                                               "session_id": session, "session_key": session_key,
                                               "candidate_id": candidate_id},
                        phase=owner.phase, state="running", expected_revision=None, event="invocation.started")
        self.update(owner_kind, owner_id, active_invocation=iid, event="invocation.assigned")
        if parent and task:
            self.update("task", tid, active_invocation=iid)

        def started(pid: int, pgid: int) -> None:
            self.update("invocation", iid, pid=pid, pgid=pgid, event="invocation.process_started")

        def thread(thread_id: str) -> None:
            self.update("invocation", iid, session_id=thread_id, event="invocation.thread_recorded")
            self.update(owner_kind, owner_id, **{session_key: thread_id})

        try:
            outcome = await run_codex(
                worktree=target, invocation_dir=invocation_dir, prompt=json.dumps(request),
                schema=SCHEMA, expected_kinds=expected, session_id=session,
                timeout_s=self.manifest["timeout_seconds"], executable=self.executable,
                sandbox="read-only" if parent and operation != "integration_repair" else "workspace-write",
                on_start=started, on_thread=thread)
            result = validate_result(outcome.result, request, expected)
            self.check_policy(target)
            self.update("invocation", iid, state="complete", result=result, event="invocation.completed")
            if parent:
                self.update("run", self.run_id, active_invocation=None)
            return result
        except BaseException as exc:
            self.update("invocation", iid, state="failed", error=str(exc), event="invocation.failed")
            raise

    async def review(self, tid: str, cid: str, operation: str) -> dict:
        async with self.parent_lock:
            self.check_parent()
            candidate = self.check_candidate_source(cid)
            decision = await self.invoke(tid, operation, {"approved", "changes_requested", "blocked"},
                                         parent=True, candidate_id=cid)
            self.check_parent()
            self.check_candidate_source(cid)
            if decision["kind"] == "approved" and any(not result["passed"] for result in candidate["checks"]):
                raise ControllerError("Parent attempted to approve failed supervisor verification")
            self.update("candidate", cid, state=decision["kind"], review=decision, event="candidate.reviewed")
            return decision

    def attempts(self, tid: str, operation: str) -> None:
        record = self.record("task", tid)
        attempts = dict(record.data["attempts"])
        attempts[operation] = attempts.get(operation, 0) + 1
        if attempts[operation] > self.manifest["max_attempts"]:
            raise ControllerError(f"{tid}: bounded {operation} attempt budget exhausted")
        self.update("task", tid, attempts=attempts, event="task.attempt")

    def reopen(self, tid: str) -> None:
        root = Path(self.record("task", tid).data["path"])
        archive = root / self.archive_path(tid)
        within(root, archive)
        within(root, root / ".agent")
        for name in ("TASK_BRIEF.md", "MEMORY.md"):
            destination = root / ".agent" / name
            if destination.exists():
                raise ControllerError("Cannot overwrite active task records on repair")
            destination.write_bytes((archive / name).read_bytes())

    async def child(self, tid: str) -> None:
        async with self.semaphore:
            try:
                async with self.parent_lock:
                    repo = self.ensure_worktree(tid)
                while True:
                    task = self.record("task", tid)
                    state = task.state
                    if state in {"planning", "implementing", "repairing", "closing_out"}:
                        operation = {"planning": "plan", "implementing": "implement", "repairing": "repair",
                                     "closing_out": "closeout"}[state]
                        expected = {"planning": "plan_ready", "implementing": "review_ready", "repairing": "review_ready",
                                    "closing_out": "closeout_ready"}[state]
                        self.attempts(tid, operation)
                        if operation == "repair" and self.manifest["repair_mode"] == "fresh":
                            self.update("task", tid, session_id=None, event="task.fresh_session")
                        before = repo.head()
                        result = await self.invoke(tid, operation, {expected, "blocked"},
                                                   candidate_id=task.data["candidate_id"] or "")
                        if result["kind"] == "blocked":
                            raise ControllerError(result["notes"])
                        repo.require_head(before)  # The supervisor, not a worker, owns Git writes.
                        self.check_task_identity(tid, repo)
                        stage = "plan" if state == "planning" else "closeout" if state == "closing_out" else "result"
                        cid = await self.freeze(tid, stage)
                        self.transition(tid, {"plan": "plan_review", "result": "result_review", "closeout": "closeout_review"}[stage],
                                        {"plan": 1, "result": 3, "closeout": 4}[stage], candidate_id=cid)
                    elif state in {"plan_review", "result_review", "closeout_review"}:
                        cid = task.data["candidate_id"]
                        decision = await self.review(tid, cid, {"plan_review": "review_plan", "result_review": "review_result",
                                                               "closeout_review": "review_closeout"}[state])
                        if decision["kind"] == "blocked":
                            raise ControllerError(decision["notes"])
                        if decision["kind"] == "approved":
                            if state == "plan_review":
                                self.transition(tid, "implementing", 2, plan_id=cid, feedback="")
                            elif state == "result_review":
                                self.transition(tid, "closing_out", 4, implementation_id=cid, feedback="")
                            else:
                                self.transition(tid, "ready_for_integration", 4, accepted_id=cid,
                                                accepted_commit=self.candidate(cid)["commit"], feedback="")
                        else:
                            if state == "closeout_review":
                                self.reopen(tid)
                            next_state = "planning" if state == "plan_review" else "repairing"
                            self.transition(tid, next_state, 1 if state == "plan_review" else 3,
                                            feedback=decision["notes"], reopened=state == "closeout_review" or task.data.get("reopened", False))
                    else:
                        return
            except asyncio.CancelledError:
                current = self.record("task", tid)
                self.update("task", tid, state="interrupted", resume_state=current.state,
                            error="controller cancelled", event="task.interrupted")
                raise
            except Exception as exc:
                current = self.record("task", tid)
                self.update("task", tid, state="blocked", resume_state=current.state, error=str(exc), event="task.blocked")
                self.project_status()

    def integration_paths(self) -> list[str]:
        return self.manifest["integration_paths"] + [path for tid in self.tasks for path in self.allowed_paths(tid, archives=True)]

    async def integrate(self, tid: str, *, repair_conflicts: bool) -> None:
        async with self.parent_lock:
            task = self.record("task", tid)
            accepted = self.check_candidate_source(task.data["accepted_id"])
            self.check_parent(clean=task.state == "ready_for_integration")
            if task.state == "ready_for_integration":
                self.update("task", tid, state="integrating", integration_parent=self.repo.head(), event="integration.started")
                merge = self.repo.begin_merge(accepted["commit"], expected_head=self.repo.head(), baseline=accepted["base"])
                if merge.state == "already_integrated":
                    raise ControllerError("Candidate unexpectedly already integrated; reconcile explicitly")
                self.update("task", tid, state="integration_conflict" if merge.state == "conflicted" else "integration_review",
                            conflicts=list(merge.conflicts), event="integration.prepared")
                task = self.record("task", tid)
            if self.repo.merge_head() != accepted["commit"]:
                raise ControllerError("Pending merge identity changed")
            if self.repo.conflicts() or task.state == "integration_conflict":
                if not repair_conflicts:
                    self.update("task", tid, state="integration_conflict", event="integration.needs_repair")
                    return
                self.attempts(tid, "integration_repair")
                before = self.repo.head()
                repair = await self.invoke(tid, "integration_repair", {"review_ready", "blocked"}, parent=True,
                                           candidate_id=task.data["accepted_id"], extra={
                                               "conflicts": list(self.repo.conflicts()),
                                               "integration_parent": task.data["integration_parent"],
                                               "integration_paths": self.integration_paths(),
                                               "integration_checks": task.data.get("integration_checks", []),
                                               "integration_review": task.data.get("integration_review"),
                                               "merge_pending": True,
                                               "accepted_history": [self.candidate(t.data["accepted_id"]) for t in self.ledger.list("task") if t.data.get("accepted_id")],
                                           })
                if repair["kind"] == "blocked":
                    raise ControllerError(repair["notes"])
                self.repo.require_head(before)
                self.check_scope(self.repo.path, task.data["integration_parent"], self.integration_paths())
                git(self.repo.path, "add", "--all", "--", ".")
                self.update("task", tid, state="integration_review", event="integration.repaired", active_invocation=None)
            self.check_scope(self.repo.path, task.data["integration_parent"], self.integration_paths())
            tree = self.repo.index_tree()
            if git(self.repo.path, "diff", "--quiet", check=False).returncode:
                raise ControllerError("Pending merge has unstaged changes")
            checks = await verify(self.manifest["merge_verify"], cwd=self.repo.path,
                                  directory=self.directory / "checks" / uuid.uuid4().hex,
                                  timeout=self.manifest["timeout_seconds"])
            if self.repo.index_tree() != tree or git(self.repo.path, "diff", "--quiet", check=False).returncode:
                raise ControllerError("Verification changed the pending merge tree")
            merge_identity = digest({"parent": task.data["integration_parent"], "candidate": accepted["commit"], "tree": tree})
            decision = await self.invoke(tid, "review_integration", {"approved", "changes_requested", "blocked"},
                                         parent=True, candidate_id=task.data["accepted_id"], extra={
                                             "integration_tree": tree, "integration_id": merge_identity,
                                             "integration_parent": task.data["integration_parent"], "integration_checks": checks,
                                             "instruction": "Review this exact tentative combined index tree read-only. "
                                                            "Inspect git diff --cached and both contracts; approving this merge does not approve the root project.",
                                         })
            self.check_parent(clean=False)
            self.check_candidate_source(task.data["accepted_id"])
            if decision["kind"] != "approved" or any(not c["passed"] for c in checks):
                self.update("task", tid, state="integration_conflict", feedback=decision["notes"],
                            integration_checks=checks, integration_review=decision, active_invocation=None,
                            event="integration.changes_requested")
                return
            self.update("task", tid, integration_tree=tree, integration_id=merge_identity,
                        integration_checks=checks, integration_review=decision, event="integration.approved")
            snapshot = self.repo.finish_merge(f"socrates: integrate {self.run_id}/{tid}",
                                              expected_head=task.data["integration_parent"],
                                              approved_sha=accepted["commit"], expected_tree=tree)
            self.update("run", self.run_id, head=snapshot.commit, event="run.head_advanced")
            self.transition(tid, "integrated", 4, integration_commit=snapshot.commit, cleanup="eligible")
            self.repo.archive_ref(self.run_id, f"{tid}-integrated", snapshot.commit)

    def cleanup(self) -> list[dict]:
        outcomes = []
        self.check_parent(clean=self.repo.merge_head() is None)
        for task in self.ledger.list("task"):
            if task.state != "integrated" or task.data["cleanup"] == "removed":
                continue
            path = Path(task.data["path"])
            evidence = self.directory / "retained" / task.id
            try:
                self.candidate(task.data["accepted_id"])
                # Retain all local agent evidence before deleting an eligible worktree.
                if (path / ".agent").exists():
                    within(path, path / ".agent")
                    if any(p.is_symlink() for p in (path / ".agent").rglob("*")):
                        raise ControllerError("Agent evidence contains symlinks; retain worktree for inspection")
                    shutil.copytree(path / ".agent", evidence / ".agent", dirs_exist_ok=True)
                self.repo.cleanup_worktree(path, task.data["branch"], managed_root=self.directory / "worktrees",
                                            integrated_into=self.repo.head(), agent_state_archived=True)
                self.update("task", task.id, cleanup="removed", cleanup_error=None, event="worktree.removed")
                outcomes.append({"task": task.id, "removed": True})
            except Exception as exc:
                self.update("task", task.id, cleanup="retained", cleanup_error=str(exc), event="worktree.retained")
                outcomes.append({"task": task.id, "removed": False, "reason": str(exc)})
        self.project_status()
        return outcomes

    async def final_handoff(self, *, repair_integration: bool = False) -> None:
        current = self.record("run", self.run_id)
        if current.data.get("parent_repair_pending"):
            if not repair_integration:
                self.update("run", self.run_id, state="blocked", error="Continue the reconciled parent repair with --repair-integration",
                            event="run.repair_pending")
                return
            await self.repair_combined(current.data["parent_repair_pending"]["checks"])
            return
        self.check_parent()
        head = self.repo.head()
        checks = await verify(self.manifest["integration_verify"], cwd=self.repo.path,
                              directory=self.directory / "checks" / uuid.uuid4().hex,
                              timeout=self.manifest["timeout_seconds"])
        self.check_parent()
        self.repo.require_head(head)
        if any(not item["passed"] for item in checks):
            self.update("run", self.run_id, state="blocked", integration_checks=checks,
                        error="Combined verification failed; retain evidence and revise the integration within approved scope",
                        event="run.verification_failed")
            self.write_packet(checks, None)
            if repair_integration:
                await self.repair_combined(checks)
            return
        async with self.parent_lock:
            handoff = await self.invoke("parent", "prepare_handoff", {"review_ready", "blocked"}, parent=True,
                                        extra={"integration_checks": checks, "final_commit": head,
                                               "accepted_tasks": [asdict(t) for t in self.ledger.list("task")]})
        self.check_parent()
        state = "awaiting_review" if handoff["kind"] == "review_ready" else "blocked"
        self.update("run", self.run_id, phase="Phase 3" if state == "awaiting_review" else "Phase 2",
                    state=state, final_commit=head, integration_checks=checks, handoff=handoff,
                    event="run.external_review_required")
        self.write_packet(checks, handoff)

    async def repair_combined(self, checks: list[dict]) -> None:
        """Parent Phase 2 repair; its resulting commit still awaits external review."""
        run = self.record("run", self.run_id)
        attempt = run.data.get("integration_repair_attempts", 0) + 1
        if attempt > self.manifest["max_attempts"]:
            self.update("run", self.run_id, state="blocked", error="Combined repair budget exhausted",
                        event="run.repair_budget_exhausted")
            return
        self.update("run", self.run_id, integration_repair_attempts=attempt,
                    event="run.integration_repair_started")
        async with self.parent_lock:
            self.check_parent(clean=not run.data.get("parent_repair_pending"))
            before = self.repo.head()
            self.check_scope(self.repo.path, before, self.integration_paths())
            self.update("run", self.run_id,
                        parent_repair_pending={"base": before, "checks": checks, "attempt": attempt},
                        parent_repair_reconciled=False, event="run.repair_intent")
            result = await self.invoke("parent", "integration_repair", {"review_ready", "blocked"}, parent=True,
                                       extra={"merge_pending": False, "integration_checks": checks,
                                              "integration_parent": before,
                                              "integration_paths": self.integration_paths(),
                                              "accepted_history": [self.candidate(t.data["accepted_id"]) for t in self.ledger.list("task")],
                                              "instruction": "Repair failed combined behavior within the authorized integration paths. "
                                                             "Preserve every accepted child commit and both contracts. Do not commit or stage. "
                                                             "This is parent Phase 2 implementation, still subject to external final review."})
            if result["kind"] == "blocked":
                self.update("run", self.run_id, state="blocked", error=result["notes"], event="run.repair_blocked")
                return
            self.check_parent_identity()
            self.repo.require_head(before)
            self.check_scope(self.repo.path, before, self.integration_paths())
            git(self.repo.path, "add", "--all", "--", ".")
            tree = self.repo.index_tree()
            self.update("run", self.run_id,
                        parent_repair_pending={"base": before, "tree": tree, "checks": checks, "attempt": attempt},
                        event="run.repair_tree_recorded")
            snapshot = self.repo.commit_snapshot(f"socrates: repair combined integration {self.run_id}", expected_head=before)
            self.update("run", self.run_id, head=snapshot.commit, state="running",
                        integration_repair_commit=snapshot.commit, parent_repair_pending=None,
                        parent_repair_reconciled=False, event="run.integration_repair_committed")
            self.repo.archive_ref(self.run_id, f"parent-repair-{attempt}", snapshot.commit)
        await self.final_handoff(repair_integration=True)

    def write_packet(self, checks: list[dict], handoff: dict | None) -> None:
        run = self.record("run", self.run_id)
        packet = {"run": asdict(run), "manifest": self.manifest,
                  "tasks": [asdict(t) for t in self.ledger.list("task")],
                  "candidates": [asdict(c) for c in self.ledger.list("candidate")],
                  "checks": checks, "handoff": handoff,
                  "events": self.ledger.events()}
        write_json(self.directory / "review-packet.json", packet)
        lines = [f"# Project review: {self.run_id}", "", f"{self.manifest['goal']}", "",
                 f"State: **{run.state}**. Final reviewer: **{self.manifest['authorization']['final_reviewer']}**.",
                 f"Initial commit: `{run.data['h0']}`. Combined head: `{self.repo.head()}`.", "",
                 "The parent has not approved its own project. Review the full combined diff and outcomes.", "",
                 "## Original outcome coverage", "", "| Criterion | Required outcome | Owners |", "|---|---|---|"]
        for criterion in self.manifest["criteria"]:
            owners = [tid for tid, task in self.tasks.items() if criterion["id"] in task["criteria"]]
            if criterion["id"] in self.manifest["parent_criteria"]:
                owners.append("parent integration")
            lines.append(f"| {criterion['id']} | {criterion['text'].replace('|', '/')} | {', '.join(owners)} |")
        lines += ["", "## Accepted child commits and integration", "", "| Task | Accepted candidate | Merge commit |", "|---|---|---|"]
        for task in self.ledger.list("task"):
            lines.append(f"| {task.id} | `{task.data.get('accepted_commit', 'pending')}` | `{task.data.get('integration_commit', 'pending')}` |")
        lines += ["", "## Combined verification", ""]
        for check in checks:
            lines.append(f"- {'PASS' if check['passed'] else 'FAIL'} `{json.dumps(check['argv'])}`; log: `{check['log']}`")
        if not checks:
            lines.append("No combined verification commands were configured; this is an explicit evidence gap.")
        lines += ["", "## Parent handoff", "", handoff["notes"] if handoff else "Blocked before parent handoff.", "",
                  "Machine-readable approvals, exact identities, criteria evidence, and transition history: review-packet.json.",
                  "Invocation logs and candidate snapshots are retained in this run directory. Sanitize any evidence selected for publication."]
        (self.directory / "REVIEW.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    async def run(self, *, repair_conflicts: bool = False, repair_integration: bool = False) -> dict:
        if self.record("run", self.run_id).state == "awaiting_review":
            self.check_parent()
            return {"state": "awaiting_review", "review": str(self.directory / "REVIEW.md")}
        if self.record("run", self.run_id).data["active_invocation"] or any(
            task.data["active_invocation"] for task in self.ledger.list("task")
        ) or self.ledger.list("invocation", state="running"):
            raise ControllerError("Interrupted/incomplete handoff found; inspect artifacts and use explicit recover before replay")
        current = self.record("run", self.run_id)
        if current.data.get("parent_repair_pending") and not current.data.get("parent_repair_reconciled"):
            raise ControllerError("An incomplete parent repair requires explicit recovery before replay")
        self.update("run", self.run_id, state="running", event="run.started")
        self.project_status()
        running: dict[str, asyncio.Task] = {}
        try:
            while True:
                for tid, job in list(running.items()):
                    if job.done():
                        await job
                        del running[tid]
                records = self.ledger.list("task")
                merge_tasks = [t for t in records if t.id not in running and t.state in {
                    "ready_for_integration", "integration_conflict", "integration_review", "integrating"}]
                for task in merge_tasks:
                    try:
                        await self.integrate(task.id, repair_conflicts=repair_conflicts)
                    except Exception as exc:
                        current = self.record("task", task.id)
                        self.update("task", task.id, state="blocked", resume_state=current.state,
                                    error=str(exc), event="integration.blocked")
                    current = self.record("task", task.id)
                    if current.state != "integrated":
                        self.update("run", self.run_id, state="blocked", event="run.integration_blocked")
                        self.project_status()
                        return {"state": "blocked", "task": task.id, "status": str(self.directory / "STATUS.md")}
                records = self.ledger.list("task")
                if all(t.state == "integrated" for t in records):
                    await self.final_handoff(repair_integration=repair_integration)
                    if self.manifest["cleanup"] and self.record("run", self.run_id).state == "awaiting_review":
                        self.cleanup()
                        current = self.record("run", self.run_id)
                        self.write_packet(current.data["integration_checks"], current.data["handoff"])
                    self.project_status()
                    return {"state": self.record("run", self.run_id).state, "review": str(self.directory / "REVIEW.md")}
                # Dispatch dependants as soon as their prerequisites have integrated;
                # unrelated long-running workers need not finish the whole frontier.
                self.check_parent()
                ready = [t for t in records if t.id not in running and t.state not in {"integrated", "blocked", "interrupted"}
                         and all(self.record("task", dep).state == "integrated" for dep in self.tasks[t.id]["depends_on"])]
                for task in ready:
                    running[task.id] = asyncio.create_task(self.child(task.id))
                if not running:
                    self.update("run", self.run_id, state="blocked", event="run.dependencies_blocked")
                    self.project_status()
                    return {"state": "blocked", "status": str(self.directory / "STATUS.md")}
                await asyncio.wait(running.values(), return_when=asyncio.FIRST_COMPLETED)
        finally:
            for job in running.values():
                if not job.done():
                    job.cancel()
            if running:
                await asyncio.gather(*running.values(), return_exceptions=True)

    def recover(self, *, task_id: str | None, acknowledged_stopped: bool,
                fresh_session: bool = False) -> dict:
        if not acknowledged_stopped:
            raise ControllerError("Recovery requires --acknowledge-stopped after verifying all prior worker processes are stopped")
        if task_id is not None and task_id != "parent" and task_id not in self.tasks:
            raise ControllerError(f"Unknown task: {task_id}")
        run = self.record("run", self.run_id)
        if run.state == "awaiting_review":
            raise ControllerError("Final external review is pending; no runtime recovery is needed")
        pending = run.data.get("parent_repair_pending")
        if task_id in (None, "parent") and pending:
            self.check_parent_identity()
            if self.repo.head() != pending["base"]:
                parents = git(self.repo.path, "show", "-s", "--format=%P", "HEAD").stdout.decode().strip().split()
                if parents != [pending["base"]] or self.repo.tree() != pending.get("tree"):
                    raise ControllerError("Parent moved outside the recorded repair; manual reconciliation required")
                self.repo.require_clean()
                self.update("run", self.run_id, head=self.repo.head(), integration_repair_commit=self.repo.head(),
                            parent_repair_pending=None, parent_repair_reconciled=False,
                            event="recovery.parent_repair_commit_adopted")
                self.repo.archive_ref(self.run_id, f"parent-repair-{pending['attempt']}", self.repo.head())
            else:
                self.check_scope(self.repo.path, pending["base"], self.integration_paths())
                self.update("run", self.run_id, parent_repair_reconciled=True,
                            event="recovery.parent_repair_worktree_reconciled")
        targets = self.ledger.list("task") if task_id is None else ([] if task_id == "parent" else [self.record("task", task_id)])
        # Creation can finish in Git before its management marker is activated.
        # Only an exact, still-clean original-base worktree can be reconciled.
        for task in targets:
            path = Path(task.data["path"])
            if task.state != "integrated" and path.exists() and task.data["base"]:
                self.repo.verify_managed_worktree(path, task.data["branch"], task.data["base"],
                                                  managed_root=self.directory / "worktrees", reconcile_creating=True)
        recovered = []
        for task in targets:
            if task.state == "integrated":
                continue
            state = task.data.get("resume_state") or task.state
            if state in {"integrating", "integration_review", "integration_conflict"}:
                accepted = task.data["accepted_commit"]
                previous = task.data["integration_parent"]
                if self.repo.head() != previous:
                    self.check_parent_identity()
                    parents = git(self.repo.path, "show", "-s", "--format=%P", "HEAD").stdout.decode().strip().split()
                    if parents != [previous, accepted] or self.repo.tree() != task.data.get("integration_tree") or task.data.get("integration_review", {}).get("kind") != "approved":
                        raise ControllerError("Parent moved outside the exact approved pending merge; manual reconciliation required")
                    self.repo.require_clean()
                    self.update("run", self.run_id, head=self.repo.head(), event="recovery.merge_commit_adopted")
                    self.transition(task.id, "integrated", 4, integration_commit=self.repo.head(), cleanup="eligible")
                    self.repo.archive_ref(self.run_id, f"{task.id}-integrated", self.repo.head())
                    recovered.append(task.id)
                    continue
                state = ("integration_conflict" if self.repo.conflicts() else "integration_review") if self.repo.merge_head() else "ready_for_integration"
            iid = task.data["active_invocation"]
            if iid:
                self.update("invocation", iid, state="interrupted", event="recovery.invocation_reconciled")
            data = {"active_invocation": None, "error": None, "resume_state": None}
            if fresh_session:
                data["session_id"] = None
            self.update("task", task.id, state=state, event="recovery.task_reconciled", **data)
            recovered.append(task.id)
        run = self.record("run", self.run_id)
        invocation_ids = {record.data["active_invocation"] for record in targets if record.data["active_invocation"]}
        if task_id in (None, "parent") and run.data["active_invocation"]:
            invocation_ids.add(run.data["active_invocation"])
        # Also cover a crash between writing an invocation and assigning its owner.
        for invocation in self.ledger.list("invocation", state="running"):
            if task_id is None or invocation.data["task_id"] == task_id or (task_id == "parent" and invocation.data["parent"]):
                invocation_ids.add(invocation.id)
        for iid in invocation_ids:
            self.update("invocation", iid, state="interrupted", event="recovery.invocation_reconciled")
        for task in self.ledger.list("task"):
            if task.data["active_invocation"] in invocation_ids:
                self.update("task", task.id, active_invocation=None, event="recovery.owner_reconciled")
        clear_parent = run.data["active_invocation"] in invocation_ids or task_id is None
        self.update("run", self.run_id, state="ready", active_invocation=None if clear_parent else run.data["active_invocation"],
                    **({"session_id": None, "repair_session_id": None} if fresh_session else {}), event="recovery.acknowledged")
        self.project_status()
        return {"recovered": recovered, "next": "run; no previous approval was inferred or fabricated"}


def status(run_dir: Path) -> dict:
    with Ledger(run_dir / "ledger.sqlite3", readonly=True) as ledger:
        return {"run": [asdict(record) for record in ledger.list("run")],
                "tasks": [asdict(record) for record in ledger.list("task")]}
