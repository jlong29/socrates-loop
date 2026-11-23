"""Real Git and subprocess integration tests, with deterministic model responses."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from socrates_orchestrator.controller import Controller, ControllerError, initialize


FIXTURE = Path(__file__).parent / "fixtures" / "orchestrator" / "fake_codex.py"


@unittest.skipUnless(sys.platform == "linux" and shutil.which("git"), "Linux and Git are required")
class ControllerLifecycleTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name)

    async def asyncSetUp(self):
        # These integration tests intentionally include synchronous local Git work.
        asyncio.get_running_loop().slow_callback_duration = 1.0

    @staticmethod
    def git(repo, *args):
        result = subprocess.run(["git", "-C", str(repo), *args], check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        return result.stdout.decode().strip()

    @staticmethod
    def task(tid, outputs, *, depends=(), **settings):
        return {
            "id": tid, "title": f"Deliver {tid}",
            "instructions": json.dumps({"outputs": outputs, **settings}),
            "milestones": ["M" + tid[1:]], "criteria": ["S" + tid[1:]],
            "depends_on": list(depends), "reviewer": "parent",
            "allowed_paths": list(outputs),
            "verify": [[sys.executable, "-c", "from pathlib import Path; " +
                        "; ".join(f"assert Path({name!r}).is_file()" for name in outputs)]],
        }

    def project(self, tasks, *, name="project", baseline=None, **options):
        root = self.directory / name
        root.mkdir()
        repo, run = root / "checkout", root / "run"
        repo.mkdir()
        self.git(repo, "init", "-b", "project-a")
        self.git(repo, "config", "user.name", "Orchestrator Fixture")
        self.git(repo, "config", "user.email", "fixture@example.invalid")
        self.git(repo, "config", "commit.gpgsign", "false")
        self.git(repo, "config", "core.hooksPath", "/dev/null")
        (repo / ".gitignore").write_text("/.agent/\n")
        (repo / "AGENTS.md").write_text("# Shared policy\nFollow the approved four-phase task and its criterion evidence.\n")
        for path, content in (baseline or {"README.md": "Fixture project\n"}).items():
            (repo / path).write_text(content)
        self.git(repo, "add", ".")
        self.git(repo, "commit", "-m", "Fixture baseline")
        h0 = self.git(repo, "rev-parse", "HEAD")
        (repo / ".agent").mkdir()
        (repo / ".agent" / "PARENT_BRIEF.md").write_text(
            "# Approved parent plan\nIntegrate all delegated outputs and retain independent final review.\n")
        manifest = {
            "schema_version": 1, "run_id": name, "goal": "Deliver all original project outcomes",
            "parent_brief": ".agent/PARENT_BRIEF.md",
            "milestones": [task["milestones"][0] for task in tasks],
            "criteria": [{"id": task["criteria"][0], "text": task["title"]} for task in tasks] +
                        [{"id": "S_parent", "text": "Combined outputs satisfy the original project"}],
            "parent_criteria": ["S_parent"], "tasks": tasks,
            "integration_verify": [], "timeout_seconds": 30,
            "authorization": {"parent_plan_approved": True, "delegate_plan_review": True,
                              "delegate_result_review": True, "local_merge": True,
                              "final_reviewer": "human"},
            **options,
        }
        manifest_path = root / "approved-manifest.json"
        manifest_path.write_text(json.dumps(manifest))
        initialize(repo=repo, manifest_path=manifest_path, run_dir=run, approved=True)
        return repo, run, h0

    def assert_parent_serialized(self, controller):
        active = None
        for event in controller.ledger.events():
            if event["event"] not in {"invocation.started", "invocation.completed", "invocation.failed"}:
                continue
            record = event["payload"]["after"]
            if not record["data"]["parent"]:
                continue
            if event["event"] == "invocation.started":
                self.assertIsNone(active, "Two parent turns overlapped")
                active = record["id"]
            else:
                self.assertEqual(active, record["id"])
                active = None
        self.assertIsNone(active)

    def observations(self, controller):
        rows = []
        for record in controller.ledger.list("invocation"):
            folder = Path(record.data["path"])
            rows.append((record, json.loads((folder / "prompt.txt").read_text()),
                         json.loads((folder / "fixture-observation.json").read_text())))
        return rows

    def combined_repair_project(self):
        tasks = [self.task("T1", {"alpha.txt": "alpha\n"},
                           integration_outputs={"integration.txt": "joined\n"})]
        command = [sys.executable, "-c", "from pathlib import Path; assert Path('integration.txt').read_text() == 'joined\\n'"]
        return self.project(tasks, integration_paths=["integration.txt"], integration_verify=[command])

    async def test_parallel_roots_repair_dependency_integration_and_external_review(self):
        for mode in ("resume", "fresh"):
            with self.subTest(repair_mode=mode):
                tasks = [
                    self.task("T1", {"alpha.txt": "alpha accepted\n"},
                              draft_outputs={"alpha.txt": "alpha draft\n"}, plan_barrier=["T1", "T2"]),
                    self.task("T2", {"beta.txt": "beta accepted\n"},
                              plan_barrier=["T1", "T2"], wait_for_plan="T3"),
                    self.task("T3", {"gamma.txt": "gamma accepted\n"}, depends=["T1"]),
                ]
                check = "from pathlib import Path; " + "; ".join(
                    f"assert Path({path!r}).read_text() == {content!r}"
                    for task in tasks for path, content in json.loads(task["instructions"])["outputs"].items())
                repo, run, h0 = self.project(tasks, name=mode, repair_mode=mode,
                                             integration_verify=[[sys.executable, "-c", check]])
                with Controller(run, executable=str(FIXTURE.resolve())) as controller:
                    outcome = await controller.run()
                    states = {t.id: t for t in controller.ledger.list("task")}
                    self.assertEqual(outcome["state"], "awaiting_review", {t.id: t.data for t in states.values()})
                    parent = controller.record("run", mode)
                    self.assertEqual((parent.phase, parent.state), ("Phase 3", "awaiting_review"))
                    self.assertEqual(states["T1"].data["base"], h0)
                    self.assertEqual(states["T2"].data["base"], h0)
                    self.assertNotEqual(states["T3"].data["base"], h0)
                    self.git(repo, "merge-base", "--is-ancestor", states["T1"].data["integration_commit"], states["T3"].data["base"])
                    self.assert_parent_serialized(controller)
                    rows = self.observations(controller)
                    requests = [request for _, request, _ in rows]
                    self.assertEqual(len({json.dumps(r["protocol"], sort_keys=True) for r in requests}), 1)
                    self.assertEqual(len({r["policy_hash"] for r in requests}), 1)
                    self.assertEqual(len({json.dumps(r["project_policy"], sort_keys=True) for r in requests}), 1)
                    parent_rows = [row for row in rows if row[0].data["parent"]]
                    self.assertEqual(len({row[2]["thread_id"] for row in parent_rows}), 1)
                    for _, request, observation in parent_rows:
                        self.assertEqual(Path(observation["cwd"]), repo)
                        self.assertEqual(observation["sandbox"], "read-only")
                        self.assertEqual(request["role"], "parent_reviewer")
                    worker = {r.data["operation"]: (r, request, obs) for r, request, obs in rows
                              if r.data["task_id"] == "T1" and not r.data["parent"]}
                    self.assertEqual(worker["repair"][2]["thread_id"] == worker["implement"][2]["thread_id"], mode == "resume")
                    self.assertEqual(worker["repair"][2]["resumed"], mode == "resume")
                    self.assertTrue(worker["repair"][1]["feedback"])
                    self.assertEqual(worker["repair"][0].phase, "Phase 3")
                    decisions = [r.data["result"]["kind"] for r, _, _ in rows if r.data["task_id"] == "T1" and r.data["operation"] == "review_result"]
                    self.assertCountEqual(decisions, ["changes_requested", "approved"])
                    dependent = next(r for r in requests if r["task_id"] == "T3" and r["operation"] == "plan")
                    self.assertEqual(dependent["dependency_history"][0]["task_id"], "T1")
                    self.assertEqual(dependent["dependency_history"][0]["commit"], states["T1"].data["accepted_commit"])
                    events = controller.ledger.events()
                    def sequence(tid, operation, event_name):
                        return next(e["sequence"] for e in events if e["event"] == event_name
                                    and e["payload"]["after"]["data"]["task_id"] == tid
                                    and e["payload"]["after"]["data"]["operation"] == operation)
                    # Both root plans started before either could finish, and a dependent
                    # dispatched before the unrelated root's implementation finished.
                    self.assertLess(max(sequence(t, "plan", "invocation.started") for t in ("T1", "T2")),
                                    min(sequence(t, "plan", "invocation.completed") for t in ("T1", "T2")))
                    self.assertLess(sequence("T3", "plan", "invocation.started"), sequence("T2", "implement", "invocation.completed"))
                    for tid, task in states.items():
                        self.assertEqual((task.state, task.data["cleanup"]), ("integrated", "removed"))
                        self.assertFalse(Path(task.data["path"]).exists())
                        parents = self.git(repo, "show", "-s", "--format=%P", task.data["integration_commit"]).split()
                        self.assertEqual(len(parents), 2)
                        self.assertEqual(parents[1], task.data["accepted_commit"])
                        self.git(repo, "merge-base", "--is-ancestor", task.data["accepted_commit"], "HEAD")
                        for name in ("TASK_BRIEF.md", "MEMORY.md", "CLOSEOUT.md"):
                            self.assertTrue((repo / controller.archive_path(tid) / name).is_file())
                        refs = self.git(repo, "for-each-ref", "--format=%(objectname)", f"refs/socrates/archives/{mode}/")
                        self.assertIn(task.data["accepted_commit"], refs.splitlines())
                    packet = json.loads((run / "review-packet.json").read_text())
                    self.assertEqual(packet["run"]["state"], "awaiting_review")
                    self.assertTrue(all(t["data"]["cleanup"] == "removed" for t in packet["tasks"]))
                    self.assertEqual({item["id"] for item in packet["handoff"]["criteria"]}, {"S1", "S2", "S3", "S_parent"})
                    self.assertTrue(all(check["passed"] for check in packet["checks"]))
                    invocation_count = len(rows)
                    self.assertEqual((await controller.run())["state"], "awaiting_review")
                    self.assertEqual(len(controller.ledger.list("invocation")), invocation_count)
                self.assertEqual(self.git(repo, "branch", "--show-current"), "project-a")
                self.assertEqual(self.git(repo, "status", "--porcelain"), "")

    async def test_parent_cannot_approve_failed_supervisor_check(self):
        task = self.task("T1", {"alpha.txt": "accepted by fake reviewer\n"})
        task["verify"] = [[sys.executable, "-c", "raise SystemExit(9)"]]
        repo, run, h0 = self.project([task])
        with Controller(run, executable=str(FIXTURE.resolve())) as controller:
            self.assertEqual((await controller.run())["state"], "blocked")
            child = controller.record("task", "T1")
            self.assertIn("approve failed supervisor verification", child.data["error"])
            self.assertEqual(child.state, "blocked")
            self.assertTrue(Path(child.data["path"]).exists())
            self.assertEqual(self.git(repo, "rev-parse", "HEAD"), h0)
            self.assertFalse(any(r.data["operation"] == "prepare_handoff" for r in controller.ledger.list("invocation")))
            candidate = controller.candidate(child.data["candidate_id"])
            self.assertFalse(candidate["checks"][0]["passed"])

    async def test_conflict_stays_pending_then_explicit_repair_preserves_both_commits(self):
        tasks = [self.task("T1", {"shared.txt": "alpha\n"}, plan_barrier=["T1", "T2"]),
                 self.task("T2", {"shared.txt": "beta\n"}, plan_barrier=["T1", "T2"])]
        combined = "from pathlib import Path; text = Path('shared.txt').read_text(); assert 'alpha\\n' in text and 'beta\\n' in text"
        repo, run, _ = self.project(tasks, baseline={"shared.txt": "baseline\n"},
                                     integration_verify=[[sys.executable, "-c", combined]])
        with Controller(run, executable=str(FIXTURE.resolve())) as controller:
            self.assertEqual((await controller.run())["state"], "blocked")
            self.assertIsNotNone(controller.repo.merge_head())
            self.assertTrue(controller.repo.conflicts())
            self.assertEqual(len(controller.ledger.list("task", state="integrated")), 1)
        with Controller(run, executable=str(FIXTURE.resolve())) as controller:
            result = await controller.run(repair_conflicts=True)
            self.assertEqual(result["state"], "awaiting_review", {t.id: t.data for t in controller.ledger.list("task")})
            rows = self.observations(controller)
            author = [row for row in rows if row[0].data["operation"] == "integration_repair"]
            self.assertEqual(len(author), 1)
            self.assertTrue(author[0][1]["merge_pending"])
            self.assertEqual(author[0][2]["sandbox"], "workspace-write")
            self.assertEqual(author[0][1]["role"], "integration_author")
            reviewer_threads = {obs["thread_id"] for record, _, obs in rows if record.data["parent"] and record.data["operation"] != "integration_repair"}
            self.assertNotIn(author[0][2]["thread_id"], reviewer_threads)
            self.assert_parent_serialized(controller)
            for task in controller.ledger.list("task"):
                self.git(repo, "merge-base", "--is-ancestor", task.data["accepted_commit"], "HEAD")
                self.assertEqual(task.data["cleanup"], "removed")
        self.assertEqual((repo / "shared.txt").read_text(), "alpha\nbeta\n")
        self.assertEqual(self.git(repo, "status", "--porcelain"), "")

    async def test_combined_verification_requires_explicit_repair_and_final_review(self):
        repo, run, _ = self.combined_repair_project()
        with Controller(run, executable=str(FIXTURE.resolve())) as controller:
            self.assertEqual((await controller.run())["state"], "blocked")
            self.assertFalse(controller.record("run", "project").data["integration_checks"][0]["passed"])
            self.assertEqual(controller.record("task", "T1").data["cleanup"], "eligible")
            self.assertFalse(any(r.data["operation"] == "prepare_handoff" for r in controller.ledger.list("invocation")))
        with Controller(run, executable=str(FIXTURE.resolve())) as controller:
            self.assertEqual((await controller.run(repair_integration=True))["state"], "awaiting_review")
            parent = controller.record("run", "project")
            self.assertEqual((parent.phase, parent.data["integration_repair_attempts"]), ("Phase 3", 1))
            author = next(row for row in self.observations(controller) if row[0].data["operation"] == "integration_repair")
            self.assertEqual(author[1]["task_id"], "parent")
            self.assertFalse(author[1]["merge_pending"])
            self.assertEqual(author[2]["sandbox"], "workspace-write")
            self.assertEqual(self.git(repo, "rev-parse", "HEAD"), parent.data["integration_repair_commit"])
            self.assert_parent_serialized(controller)
        self.assertEqual((repo / "integration.txt").read_text(), "joined\n")
        self.assertEqual(self.git(repo, "status", "--porcelain"), "")

    async def test_cli_requires_authorization_and_completes_an_offline_run(self):
        tasks = [self.task("T1", {"alpha.txt": "alpha\n"}), self.task("T2", {"beta.txt": "beta\n"})]
        repo, original_run, _ = self.project(tasks, name="cli")
        run = original_run.parent / "cli-run"
        manifest = original_run.parent / "approved-manifest.json"

        async def cli(*arguments, expected=0):
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-B", "-m", "socrates_orchestrator", *map(str, arguments),
                cwd=Path(__file__).resolve().parents[1], stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)
            try:
                out, err = await asyncio.wait_for(process.communicate(), 40)
            finally:
                if process.returncode is None:
                    process.kill()
                    await process.wait()
            self.assertEqual(process.returncode, expected, out.decode() + err.decode())
            return json.loads(out) if expected == 0 else err.decode()

        init = ["init", "--repo", repo, "--manifest", manifest, "--run-dir", run]
        self.assertIn("--approve", await cli(*init, expected=2))
        self.assertFalse(run.exists())
        await cli(*init, "--approve")
        outcome = await cli("run", "--run-dir", run, "--codex", FIXTURE.resolve())
        self.assertEqual(outcome["state"], "awaiting_review")
        state = await cli("status", "--run-dir", run, "--json")
        self.assertEqual(state["run"][0]["phase"], "Phase 3")
        self.assertTrue(all(task["state"] == "integrated" for task in state["tasks"]))
        self.assertEqual(await cli("cleanup", "--run-dir", run), {"cleanup": []})

    async def test_parent_repair_crash_before_commit_requires_explicit_reconciliation(self):
        repo, run, _ = self.combined_repair_project()
        with Controller(run, executable=str(FIXTURE.resolve())) as controller:
            self.assertEqual((await controller.run())["state"], "blocked")
            base = controller.repo.head()
            with mock.patch.object(controller.repo, "commit_snapshot", side_effect=RuntimeError("injected before commit")):
                with self.assertRaisesRegex(RuntimeError, "injected before commit"):
                    await controller.run(repair_integration=True)
            parent = controller.record("run", "project")
            pending = parent.data["parent_repair_pending"]
            self.assertEqual((pending["base"], pending["tree"]), (base, controller.repo.index_tree()))
            self.assertFalse(parent.data["parent_repair_reconciled"])
            old_session = parent.data["repair_session_id"]
            self.assertEqual(controller.repo.head(), base)
            self.assertTrue(self.git(repo, "status", "--porcelain"))
        with Controller(run, executable=str(FIXTURE.resolve())) as controller:
            with self.assertRaisesRegex(ControllerError, "requires explicit recovery"):
                await controller.run(repair_integration=True)
            with self.assertRaisesRegex(ControllerError, "acknowledge-stopped"):
                controller.recover(task_id="parent", acknowledged_stopped=False)
            controller.recover(task_id="parent", acknowledged_stopped=True, fresh_session=True)
            self.assertTrue(controller.record("run", "project").data["parent_repair_reconciled"])
            count = len(controller.ledger.list("invocation"))
            self.assertEqual((await controller.run())["state"], "blocked")
            self.assertEqual(len(controller.ledger.list("invocation")), count)
            self.assertEqual(controller.repo.head(), base)
            self.assertEqual((await controller.run(repair_integration=True))["state"], "awaiting_review")
            parent = controller.record("run", "project")
            self.assertIsNone(parent.data["parent_repair_pending"])
            self.assertEqual(parent.data["integration_repair_attempts"], 2)
            self.assertNotEqual(parent.data["repair_session_id"], old_session)
            self.assertEqual(controller.repo.tree(), pending["tree"])
            events = [event["event"] for event in controller.ledger.events()]
            self.assertIn("recovery.parent_repair_worktree_reconciled", events)
            self.assertNotIn("recovery.parent_repair_commit_adopted", events)
            self.assertEqual(controller.record("task", "T1").data["cleanup"], "removed")
        self.assertEqual(self.git(repo, "status", "--porcelain"), "")

    async def test_parent_repair_commit_crash_adopts_only_the_exact_recorded_tree(self):
        repo, run, _ = self.combined_repair_project()
        with Controller(run, executable=str(FIXTURE.resolve())) as controller:
            self.assertEqual((await controller.run())["state"], "blocked")
            base = controller.repo.head()
            update = controller.update

            def interrupt_head_record(kind, identifier, **fields):
                if fields.get("event") == "run.integration_repair_committed":
                    raise RuntimeError("injected after commit before ledger head")
                return update(kind, identifier, **fields)

            with mock.patch.object(controller, "update", side_effect=interrupt_head_record):
                with self.assertRaisesRegex(RuntimeError, "injected after commit"):
                    await controller.run(repair_integration=True)
            committed = controller.repo.head()
            parent = controller.record("run", "project")
            self.assertNotEqual(committed, base)
            self.assertEqual(parent.data["head"], base)
            self.assertEqual(parent.data["parent_repair_pending"]["tree"], controller.repo.tree())
        with Controller(run, executable=str(FIXTURE.resolve())) as controller:
            with self.assertRaisesRegex(ControllerError, "requires explicit recovery"):
                await controller.run()
            # An unrelated amended tree with the same single parent must not be
            # mistaken for the crash-window commit. Restore the recorded commit
            # afterward without discarding its history or the journal.
            (repo / "integration.txt").write_text("unrecorded content\n")
            self.git(repo, "add", "integration.txt")
            self.git(repo, "commit", "--amend", "--no-edit")
            self.assertEqual(self.git(repo, "show", "-s", "--format=%P", "HEAD"), base)
            with self.assertRaisesRegex(ControllerError, "outside the recorded repair"):
                controller.recover(task_id="parent", acknowledged_stopped=True)
            self.assertEqual(controller.record("run", "project").data["head"], base)
            self.git(repo, "update-ref", "HEAD", committed)
            (repo / "integration.txt").write_text("joined\n")
            self.git(repo, "add", "integration.txt")
            controller.recover(task_id="parent", acknowledged_stopped=True)
            parent = controller.record("run", "project")
            self.assertEqual(parent.data["head"], committed)
            self.assertEqual(parent.data["integration_repair_commit"], committed)
            self.assertIsNone(parent.data["parent_repair_pending"])
            self.assertEqual((await controller.run())["state"], "awaiting_review")
            self.assertEqual(controller.repo.head(), committed)
            repairs = [record for record in controller.ledger.list("invocation")
                       if record.data["operation"] == "integration_repair"]
            self.assertEqual(len(repairs), 1, "An adopted commit must not replay the model repair")
            self.assertEqual(controller.record("run", "project").phase, "Phase 3")
            self.assertIn("recovery.parent_repair_commit_adopted", [event["event"] for event in controller.ledger.events()])
            refs = self.git(repo, "for-each-ref", "--format=%(objectname)", "refs/socrates/archives/project/")
            self.assertIn(committed, refs.splitlines())
        self.assertEqual(self.git(repo, "status", "--porcelain"), "")


if __name__ == "__main__":
    unittest.main()
