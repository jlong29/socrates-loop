"""Bounded local Git operations for an explicitly authorized supervisor.

The controller owns authorization, run/task locks, and verification decisions.
This module checks repository identity, exact revisions, and operation state;
it never fetches, pushes, rebases, squashes, force-removes, or force-deletes.
Ignored files are not part of Git snapshots. Cleanup treats ignored files more
strictly than Git does so that user data cannot disappear with a worktree.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
from typing import Any


class GitError(RuntimeError):
    """A Git operation or its deterministic preconditions failed."""


@dataclass(frozen=True)
class Snapshot:
    commit: str
    tree: str
    parent: str  # HEAD before this operation; equal to commit for a no-op.
    changed_paths: tuple[str, ...]
    created: bool = True


@dataclass(frozen=True)
class MergeResult:
    state: str  # pending, conflicted, or already_integrated
    head: str
    candidate: str
    conflicts: tuple[str, ...] = ()
    tree: str | None = None


def _no_symlinks(path: Path) -> None:
    for entry in (path, *path.parents):
        if entry.is_symlink():
            raise GitError(f"Managed paths cannot contain symlinks: {entry}")


def _write_json(path: Path, value: dict[str, Any], *, exclusive: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    target = path if exclusive else path.with_suffix(".tmp")
    with target.open("x" if exclusive else "w", encoding="utf-8") as output:
        json.dump(value, output, indent=2)
        output.write("\n")
        output.flush()
        os.fsync(output.fileno())
    if not exclusive:
        target.replace(path)


class GitRepo:
    def __init__(self, repo: Path):
        try:
            self.path = Path(repo).resolve(strict=True)
        except OSError as error:
            raise GitError(f"Repository path is unavailable: {repo}") from error
        if not self.path.is_dir():
            raise GitError(f"Not a repository directory: {self.path}")
        self.path = Path(self._text("rev-parse", "--show-toplevel")).resolve()
        common = Path(self._text("rev-parse", "--git-common-dir"))
        self.common_dir = (self.path / common).resolve() if not common.is_absolute() else common.resolve()

    def _run(self, *args: str, allowed: tuple[int, ...] = (0,)) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        for key in ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                    "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_PREFIX"):
            env.pop(key, None)
        env["GIT_TERMINAL_PROMPT"] = "0"
        try:
            result = subprocess.run(
                ["git", "-c", "color.ui=false", "-C", str(self.path), *args],
                stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=env, timeout=60, check=False)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise GitError(f"Cannot run git {args[0]}: {error}") from error
        if result.returncode not in allowed:
            message = result.stderr.decode("utf-8", "replace").strip()
            raise GitError(f"git {' '.join(args[:3])} failed ({result.returncode}): {message}")
        return result

    def _text(self, *args: str) -> str:
        return self._run(*args).stdout.decode("utf-8", "surrogateescape").removesuffix("\n")

    def _git_path(self, name: str) -> Path:
        path = Path(self._text("rev-parse", "--git-path", name))
        return path if path.is_absolute() else self.path / path

    def resolve_commit(self, ref: str) -> str:
        if not isinstance(ref, str) or not ref or ref.startswith("-"):
            raise GitError("Expected a commit reference")
        return self._text("rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}")

    def _exact_commit(self, value: str) -> str:
        if not isinstance(value, str) or not re.fullmatch(r"[0-9a-fA-F]{40}|[0-9a-fA-F]{64}", value):
            raise GitError("Mutation requires a full, exact commit SHA")
        resolved = self.resolve_commit(value)
        if resolved != value.lower():
            raise GitError("Commit identity mismatch")
        return resolved

    def head(self) -> str:
        return self.resolve_commit("HEAD")

    def branch(self) -> str:
        result = self._run("symbolic-ref", "--quiet", "--short", "HEAD", allowed=(0, 1))
        if result.returncode:
            raise GitError("Operation requires an attached branch")
        return result.stdout.decode("utf-8", "surrogateescape").strip()

    def tree(self, ref: str = "HEAD") -> str:
        commit = self.resolve_commit(ref)
        return self._text("rev-parse", f"{commit}^{{tree}}")

    def index_tree(self) -> str:
        if self.conflicts():
            raise GitError("Index has unresolved merge conflicts")
        return self._text("write-tree")

    def clean(self) -> bool:
        return not self._run("status", "--porcelain=v1", "-z", "--untracked-files=all").stdout

    def require_clean(self) -> None:
        if not self.clean():
            raise GitError(f"Repository has tracked changes or nonignored untracked files: {self.path}")

    def require_head(self, expected: str) -> None:
        if self.head() != self._exact_commit(expected):
            raise GitError("HEAD changed since the operation was authorized")

    def is_ancestor(self, base: str, tip: str) -> bool:
        base, tip = self.resolve_commit(base), self.resolve_commit(tip)
        return self._run("merge-base", "--is-ancestor", base, tip, allowed=(0, 1)).returncode == 0

    def require_descendant(self, base: str, tip: str) -> None:
        if not self.is_ancestor(base, tip):
            raise GitError("Accepted output is not descended from its recorded baseline")

    def changed_paths(self, base: str, tip: str) -> tuple[str, ...]:
        base, tip = self.resolve_commit(base), self.resolve_commit(tip)
        output = self._run("diff", "--name-only", "--no-renames", "-z", base, tip, "--").stdout
        return tuple(os.fsdecode(item) for item in output.split(b"\0") if item)

    def diff_metadata(self, base: str, tip: str) -> dict[str, Any]:
        base, tip = self.resolve_commit(base), self.resolve_commit(tip)
        return {"base": base, "tip": tip, "base_tree": self.tree(base),
                "tip_tree": self.tree(tip), "changed_paths": self.changed_paths(base, tip),
                "stat": self._text("diff", "--stat", "--no-ext-diff", "--no-textconv", base, tip, "--")}

    def _require_no_operation(self) -> None:
        for name in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply", "sequencer"):
            if self._git_path(name).exists():
                raise GitError(f"An existing Git operation must be resolved first: {name}")

    def _require_agent_ignored(self) -> None:
        if self._run("ls-files", "--", ".agent").stdout:
            raise GitError("Active .agent records must not be tracked")
        if self._run("ls-files", "--others", "--exclude-standard", "--", ".agent").stdout:
            raise GitError("Active .agent records must be ignored before snapshotting")

    def _require_index_matches_worktree(self) -> None:
        if self._run("diff", "--quiet", "--no-ext-diff", "--no-textconv",
                     "--ignore-submodules=none", "--", allowed=(0, 1)).returncode:
            raise GitError("Working files differ from the reviewed index tree")
        if self._run("ls-files", "--others", "--exclude-standard", "-z").stdout:
            raise GitError("Nonignored untracked files are outside the reviewed index tree")

    def commit_snapshot(self, message: str, expected_head: str) -> Snapshot:
        expected_head = self._exact_commit(expected_head)
        self.branch()
        self.require_head(expected_head)
        self._require_no_operation()
        self._require_agent_ignored()
        # The precondition above requires .agent to be ignored and untracked;
        # normal add respects that ignore rule while including intended new files.
        self._run("add", "--all", "--", ".")
        self._require_agent_ignored()
        self.require_head(expected_head)
        staged_tree = self.index_tree()
        self._require_index_matches_worktree()
        if staged_tree == self.tree(expected_head):
            self.require_clean()
            return Snapshot(expected_head, staged_tree, expected_head, (), False)
        self._run("commit", "-m", message)
        commit = self.head()
        parents = self._text("rev-list", "--parents", "-n", "1", commit).split()[1:]
        if parents != [expected_head] or self.tree(commit) != staged_tree:
            raise GitError("Commit hooks or concurrent writers changed the snapshot")
        self.require_clean()
        return Snapshot(commit, staged_tree, expected_head, self.changed_paths(expected_head, commit))

    def conflicts(self) -> tuple[str, ...]:
        records = self._run("ls-files", "--unmerged", "-z").stdout.split(b"\0")
        return tuple(sorted({os.fsdecode(item.split(b"\t", 1)[1]) for item in records if item}))

    def merge_head(self) -> str | None:
        path = self._git_path("MERGE_HEAD")
        if not path.exists():
            return None
        lines = path.read_text(encoding="ascii").splitlines()
        if len(lines) != 1:
            raise GitError("Only a single approved candidate may be merged at a time")
        return self._exact_commit(lines[0])

    def begin_merge(self, approved_sha: str, expected_head: str, baseline: str) -> MergeResult:
        approved_sha, baseline = self._exact_commit(approved_sha), self._exact_commit(baseline)
        expected_head = self._exact_commit(expected_head)
        self.branch()
        self.require_head(expected_head)
        self._require_no_operation()
        self.require_clean()
        self.require_descendant(baseline, approved_sha)
        self.require_descendant(baseline, expected_head)
        if self.is_ancestor(approved_sha, expected_head):
            return MergeResult("already_integrated", expected_head, approved_sha, tree=self.tree())
        result = self._run("merge", "--no-ff", "--no-commit", "--no-edit", approved_sha, allowed=(0, 1))
        self.require_head(expected_head)
        if self.merge_head() != approved_sha:
            raise GitError("Git did not preserve the expected pending merge")
        conflicts = self.conflicts()
        if conflicts:
            return MergeResult("conflicted", expected_head, approved_sha, conflicts)
        if result.returncode:
            raise GitError(result.stderr.decode("utf-8", "replace").strip())
        self._require_index_matches_worktree()
        return MergeResult("pending", expected_head, approved_sha, tree=self.index_tree())

    def finish_merge(self, message: str, expected_head: str, approved_sha: str, expected_tree: str) -> Snapshot:
        approved_sha = self._exact_commit(approved_sha)
        expected_head = self._exact_commit(expected_head)
        self.branch()
        self.require_head(expected_head)
        if self.merge_head() != approved_sha:
            raise GitError("Pending merge is not the approved candidate")
        if self.index_tree() != expected_tree:
            raise GitError("Index changed since integration verification")
        self._require_index_matches_worktree()
        self._run("commit", "-m", message)
        commit = self.head()
        parents = self._text("rev-list", "--parents", "-n", "1", commit).split()[1:]
        if parents != [expected_head, approved_sha] or self.tree(commit) != expected_tree:
            raise GitError("Merge commit differs from the verified candidate")
        self.require_clean()
        return Snapshot(commit, expected_tree, expected_head, self.changed_paths(expected_head, commit))

    def _management_path(self, path: Path) -> Path:
        key = hashlib.sha256(os.fsencode(str(path))).hexdigest()
        return self.common_dir / "socrates-orchestrator/worktrees" / f"{key}.json"

    def _worktree_entries(self, path: Path) -> list[dict[str, str]]:
        entries = []
        for block in self._run("worktree", "list", "--porcelain", "-z").stdout.split(b"\0\0"):
            fields = {}
            for field in block.split(b"\0"):
                if field:
                    key, _, value = field.partition(b" ")
                    fields[os.fsdecode(key)] = os.fsdecode(value)
            if fields.get("worktree") == str(path):
                entries.append(fields)
        return entries

    @staticmethod
    def _managed_path(path: Path, managed_root: Path) -> tuple[Path, Path]:
        path, root = Path(path).absolute(), Path(managed_root).absolute()
        if ".." in path.parts or ".." in root.parts or path == root or not path.is_relative_to(root):
            raise GitError("Worktree must be strictly inside its declared managed root")
        _no_symlinks(path)
        _no_symlinks(root)
        return path, root

    def create_worktree(self, path: Path, branch: str, base: str, managed_root: Path) -> GitRepo:
        path, root = self._managed_path(path, managed_root)
        base = self._exact_commit(base)
        self._run("check-ref-format", "--branch", branch)
        self._run("check-ref-format", f"refs/heads/{branch}")
        if path.exists() or path.is_symlink():
            raise GitError("Managed worktree path already exists")
        if self._run("show-ref", "--verify", "--quiet", f"refs/heads/{branch}", allowed=(0, 1)).returncode == 0:
            raise GitError("Managed task branch already exists")
        if self._worktree_entries(path):
            raise GitError("Git already registers the managed worktree path")
        marker = self._management_path(path)
        record = {"path": str(path), "branch": branch, "baseline": base,
                  "managed_root": str(root), "common_dir": str(self.common_dir), "state": "creating"}
        if marker.exists():
            try:
                previous = json.loads(marker.read_text(encoding="utf-8"))
            except (OSError, ValueError) as error:
                raise GitError("Invalid existing worktree creation record") from error
            if previous != record:
                raise GitError("Existing worktree identity is not this unfinished creation")
            # Exact prior intent, no path/ref/registration: retry the unstarted add.
        else:
            try:
                _write_json(marker, record, exclusive=True)
            except FileExistsError as error:
                raise GitError("Managed worktree identity already exists") from error
        path.parent.mkdir(parents=True, exist_ok=True)
        self._run("worktree", "add", "-b", branch, str(path), base)
        return self.verify_managed_worktree(path, branch, base, root, reconcile_creating=True)

    def verify_managed_worktree(self, path: Path, branch: str, base: str,
                                managed_root: Path, *, reconcile_creating: bool = False) -> GitRepo:
        """Verify registered ownership; optionally finish a successful create.

        Recovery only changes a ``creating`` marker when Git already has the
        exact requested clean worktree at its original baseline. It never creates,
        resets, checks out, or otherwise edits the worktree during reconciliation.
        """
        path, root = self._managed_path(path, managed_root)
        base = self._exact_commit(base)
        marker = self._management_path(path)
        try:
            record = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise GitError("No valid management record for this exact worktree") from error
        required = {"path": str(path), "branch": branch, "baseline": base,
                    "managed_root": str(root), "common_dir": str(self.common_dir)}
        if not isinstance(record, dict) or any(record.get(key) != value for key, value in required.items()):
            raise GitError("Worktree does not match its management record")
        state = record.get("state")
        if state != "active" and not (state == "creating" and reconcile_creating):
            raise GitError("Worktree registration is incomplete or no longer active")
        target = GitRepo(path)
        if target.path != path or target.common_dir != self.common_dir or target.branch() != branch:
            raise GitError("Worktree identity differs from the registered request")
        registered = self._worktree_entries(path)
        if (len(registered) != 1 or registered[0].get("branch") != f"refs/heads/{branch}"
                or registered[0].get("HEAD") != target.head()):
            raise GitError("Git worktree metadata does not match the registered identity")
        target.require_descendant(base, target.head())
        if state == "creating":
            target.require_head(base)
            target._require_no_operation()
            target.require_clean()
            record["state"] = "active"
            _write_json(marker, record)
        return target

    def archive_ref(self, run_id: str, task_id: str, commit: str) -> str:
        for name in (run_id, task_id):
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", name):
                raise GitError("Archive identifiers must be simple names")
        ref = f"refs/socrates/archives/{run_id}/{task_id}"
        self._run("check-ref-format", ref)
        commit = self._exact_commit(commit)
        existing = self._run("show-ref", "--verify", "--quiet", ref, allowed=(0, 1))
        if existing.returncode == 0:
            if self.resolve_commit(ref) != commit:
                raise GitError("Archive references are immutable")
            return ref
        self._run("update-ref", ref, commit, "0" * len(commit))
        return ref

    def cleanup_worktree(self, path: Path, branch: str, managed_root: Path,
                         integrated_into: str, *, agent_state_archived: bool = False,
                         delete_branch: bool = False) -> None:
        path, root = self._managed_path(path, managed_root)
        marker = self._management_path(path)
        try:
            record = json.loads(marker.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise GitError("No valid management record for this exact worktree") from error
        required = {"path": str(path), "branch": branch, "managed_root": str(root),
                    "common_dir": str(self.common_dir)}
        if not isinstance(record, dict) or any(record.get(key) != value for key, value in required.items()):
            raise GitError("Worktree does not match its management record")
        state = record.get("state")
        if state not in {"active", "removing", "removed"}:
            raise GitError("Worktree registration is not eligible for cleanup")
        if state != "active" and record.get("delete_branch", False) != delete_branch:
            raise GitError("Cleanup retry differs from its recorded deletion intent")
        branch_exists = self._run("show-ref", "--verify", "--quiet", f"refs/heads/{branch}", allowed=(0, 1)).returncode == 0
        if not branch_exists and not (state == "removed" and delete_branch):
            raise GitError("Managed task branch disappeared")
        tip = self.resolve_commit(f"refs/heads/{branch}") if branch_exists else self._exact_commit(record["removal_tip"])
        if state != "active" and tip != record.get("removal_tip"):
            raise GitError("Task branch changed after cleanup was authorized")
        self.require_descendant(self._exact_commit(record.get("baseline", "")), tip)
        integrated_into = self._exact_commit(integrated_into)
        self.require_descendant(tip, integrated_into)
        if state == "active":
            archived = self._text("for-each-ref", "--format=%(objectname) %(refname)", "refs/socrates/archives/")
            archive_refs = [line.split(" ", 1)[1] for line in archived.splitlines() if line.startswith(tip + " ")]
        else:
            self.require_descendant(self._exact_commit(record.get("integrated_into", "")), integrated_into)
            archive_refs = record.get("archived_refs", [])
            if not isinstance(archive_refs, list) or any(
                    not isinstance(ref, str) or not ref.startswith("refs/socrates/archives/")
                    or self.resolve_commit(ref) != tip for ref in archive_refs):
                raise GitError("Recorded archive references changed")
        if not archive_refs:
            raise GitError("An immutable archive reference must retain the exact task tip before cleanup")
        if path.exists():
            if state == "removed":
                raise GitError("A removed worktree path has been reused; refusing deletion")
            target = GitRepo(path)
            registered = self._worktree_entries(path)
            if (target.path != path or target.common_dir != self.common_dir or target.branch() != branch
                    or len(registered) != 1 or registered[0].get("branch") != f"refs/heads/{branch}"
                    or registered[0].get("HEAD") != tip):
                raise GitError("Refusing cleanup of a different worktree or branch")
            target._require_no_operation()
            target.require_clean()
            ignored = target._run("ls-files", "--others", "--ignored", "--exclude-standard", "-z").stdout
            for raw in ignored.split(b"\0"):
                if not raw:
                    continue
                name = os.fsdecode(raw)
                if not (agent_state_archived and (name == ".agent" or name.startswith(".agent/"))):
                    raise GitError(f"Ignored data must be preserved before cleanup: {name}")
            record.update(state="removing", removal_tip=tip, archived_refs=archive_refs,
                          integrated_into=integrated_into, delete_branch=delete_branch,
                          agent_state_archived=agent_state_archived)
            _write_json(marker, record)
            self._run("worktree", "remove", str(path))
        elif state == "active":
            raise GitError("Worktree disappeared before a removal intent was recorded")
        if path.exists() or self._worktree_entries(path):
            raise GitError("Worktree removal is incomplete; preserve registration for inspection")
        record.update(state="removed", integrated_into=integrated_into)
        _write_json(marker, record)
        if delete_branch and branch_exists:
            self._run("branch", "-d", "--", branch)
