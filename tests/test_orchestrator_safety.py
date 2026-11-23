"""Controller boundary checks in temporary repositories; no agent invocation."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from socrates_orchestrator.controller import Controller, ControllerError, initialize


@unittest.skipUnless(sys.platform.startswith("linux") and shutil.which("git"),
                     "Requires Linux and Git")
class OrchestratorSafetyTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="socrates-safety-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / "project"
        self.repo.mkdir()
        self.git("init", "-q")
        self.git("config", "user.name", "Socrates test")
        self.git("config", "user.email", "socrates-test@example.invalid")
        self.git("switch", "-c", "feature/safety")
        (self.repo / "AGENTS.md").write_text("# Shared fixture policy\n")
        (self.repo / ".gitignore").write_text("/.agent/\n")
        (self.repo / "outside.py").write_text("VALUE = 1\n")
        (self.repo / "src").mkdir()
        (self.repo / "src/owned.py").write_text("VALUE = 2\n")
        self.git("add", ".")
        self.git("commit", "-qm", "fixture baseline")
        (self.repo / ".agent").mkdir()
        (self.repo / ".agent/TASK_BRIEF.md").write_text(
            "# Approved parent\nPreserve both original criteria.\n")
        manifest = {
            "schema_version": 1, "run_id": "safety", "goal": "Verify boundaries",
            "parent_brief": ".agent/TASK_BRIEF.md", "milestones": ["M1", "M2"],
            "criteria": [{"id": "C1", "text": "First outcome"},
                         {"id": "C2", "text": "Second outcome"}],
            "parent_criteria": [], "integration_verify": [],
            "tasks": [
                {"id": name, "title": name, "instructions": "Change the owned module",
                 "milestones": [milestone], "criteria": [criterion], "depends_on": [],
                 "reviewer": "parent", "allowed_paths": ["src/"], "verify": []}
                for name, milestone, criterion in (("one", "M1", "C1"), ("two", "M2", "C2"))
            ],
            "authorization": {"parent_plan_approved": True, "delegate_plan_review": True,
                              "delegate_result_review": True, "local_merge": True,
                              "final_reviewer": "human"},
        }
        manifest_path = self.root / "manifest.json"
        manifest_path.write_text(json.dumps(manifest))
        self.run_dir = self.root / "run"
        initialize(repo=self.repo, manifest_path=manifest_path, run_dir=self.run_dir,
                   approved=True)
        self.controller = Controller(self.run_dir)
        self.addCleanup(self.controller.close)

    def git(self, *arguments):
        return subprocess.run(["git", "-C", str(self.repo), *arguments], check=True,
                              capture_output=True, text=True).stdout.strip()

    async def test_staged_rename_cannot_hide_out_of_scope_deletion(self):
        baseline = self.git("rev-parse", "HEAD")
        self.git("mv", "outside.py", "src/moved.py")
        with self.assertRaisesRegex(ControllerError, "outside.py"):
            self.controller.check_scope(self.repo, baseline, ["src/"])

    async def test_new_nested_policy_is_not_an_ordinary_allowed_edit(self):
        (self.repo / "src/AGENTS.md").write_text("Different policy\n")
        with self.assertRaisesRegex(ControllerError, "file set changed"):
            self.controller.check_policy(self.repo)

    async def test_added_candidate_file_invalidates_frozen_subject(self):
        self.controller.ensure_worktree("one")
        candidate_id = await self.controller.freeze("one", "plan")
        self.controller.candidate(candidate_id)
        record = self.controller.record("candidate", candidate_id)
        (Path(record.data["directory"]) / "unreviewed.txt").write_text("New evidence\n")
        with self.assertRaisesRegex(ControllerError, "changed after freezing"):
            self.controller.candidate(candidate_id)

    async def test_scoped_recovery_handles_orphan_without_clearing_other_parent_turn(self):
        self.controller.ledger.put(
            "invocation", "orphan-one", state="running", expected_revision=None,
            data={"task_id": "one", "operation": "plan", "parent": False})
        self.controller.ledger.put(
            "invocation", "parent-two", state="failed", expected_revision=None,
            data={"task_id": "two", "operation": "review_plan", "parent": True})
        self.controller.update("run", "safety", active_invocation="parent-two")
        self.controller.update("task", "two", active_invocation="parent-two")

        self.controller.recover(task_id="one", acknowledged_stopped=True)

        self.assertEqual(self.controller.record("invocation", "orphan-one").state,
                         "interrupted")
        self.assertEqual(self.controller.record("run", "safety").data["active_invocation"],
                         "parent-two")
        self.assertEqual(self.controller.record("task", "two").data["active_invocation"],
                         "parent-two")
        self.assertEqual(self.controller.record("invocation", "parent-two").state,
                         "failed")

    async def test_different_run_ledgers_cannot_share_a_git_writer(self):
        manifest_path = self.root / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["run_id"] = "second"
        manifest_path.write_text(json.dumps(manifest))
        second_run = self.root / "second-run"
        initialize(repo=self.repo, manifest_path=manifest_path, run_dir=second_run, approved=True)
        with self.assertRaisesRegex(ControllerError, "Another supervisor"):
            Controller(second_run)
        # The failed constructor releases its own ledger lock. Once the first
        # owner releases Git, an explicitly separate run can acquire ownership.
        self.controller.close()
        with Controller(second_run) as second:
            self.assertEqual(second.repo.path, self.repo)


if __name__ == "__main__":
    unittest.main()
