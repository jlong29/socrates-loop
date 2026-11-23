"""Real local Git tests: exact snapshots, merge gates, and safe cleanup."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

from socrates_orchestrator.git import GitError, GitRepo
from socrates_orchestrator import git as git_module


@unittest.skipUnless(shutil.which("git"), "Git is required")
class GitLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repository = self.root / "repository"
        self.repository.mkdir()
        self.managed = self.root / "workers"
        self.command(self.repository, "init", "-b", "main")
        self.command(self.repository, "config", "user.name", "Orchestrator Tests")
        self.command(self.repository, "config", "user.email", "tests@example.invalid")
        self.command(self.repository, "config", "commit.gpgsign", "false")
        (self.repository / ".gitignore").write_text(".agent/\n.cache/\n")
        (self.repository / "left.txt").write_text("left baseline\n")
        (self.repository / "right.txt").write_text("right baseline\n")
        self.command(self.repository, "add", ".")
        self.command(self.repository, "commit", "-m", "Initial baseline")
        self.command(self.repository, "switch", "-c", "project-a")
        self.repo = GitRepo(self.repository)
        self.baseline = self.repo.head()

    @staticmethod
    def command(path, *args):
        result = subprocess.run(["git", "-C", str(path), *args], check=True,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.stdout.decode("utf-8", "surrogateescape").strip()

    def worker(self, name):
        return self.repo.create_worktree(self.managed / name, f"socrates/{name}",
                                        self.baseline, self.managed)

    def candidate(self, name, filename="left.txt", content="changed\n"):
        worker = self.worker(name)
        (worker.path / filename).write_text(content)
        return worker, worker.commit_snapshot(f"Task {name}", self.baseline)

    def integrate(self, commit):
        before = self.repo.head()
        pending = self.repo.begin_merge(commit, before, self.baseline)
        self.assertEqual(pending.state, "pending")
        return self.repo.finish_merge("Integrate accepted task", before, commit, pending.tree)

    def cleanup_worker(self, worker, **kwargs):
        return self.repo.cleanup_worktree(worker.path, worker.branch(), self.managed,
                                         self.repo.head(), **kwargs)

    def test_common_exact_baseline_and_independent_worktrees(self):
        first, second = self.worker("one"), self.worker("two")
        self.assertEqual(first.head(), self.baseline)
        self.assertEqual(second.head(), self.baseline)
        self.assertEqual(first.common_dir, self.repo.common_dir)
        (first.path / "left.txt").write_text("private change\n")
        self.assertEqual((second.path / "left.txt").read_text(), "left baseline\n")
        self.assertEqual(first.branch(), "socrates/one")
        with self.assertRaises(GitError):
            self.repo.create_worktree(self.managed / "three", "socrates/three", "HEAD", self.managed)
        with self.assertRaises(GitError):
            self.worker("one")

    def test_registered_worktree_verification_rejects_unregistered_or_wrong_base(self):
        worker, snapshot = self.candidate("registered")
        self.assertEqual(self.repo.verify_managed_worktree(
            worker.path, worker.branch(), self.baseline, self.managed).head(), snapshot.commit)
        with self.assertRaises(GitError):
            self.repo.verify_managed_worktree(worker.path, worker.branch(), snapshot.commit, self.managed)
        unmanaged = self.managed / "unregistered"
        self.command(self.repository, "worktree", "add", "-b", "unregistered", str(unmanaged), self.baseline)
        with self.assertRaises(GitError):
            self.repo.verify_managed_worktree(unmanaged, "unregistered", self.baseline, self.managed)

    def test_reconcile_creation_after_git_add_before_active_marker(self):
        original_write = git_module._write_json

        def crash_before_activation(path, value, **kwargs):
            if value["state"] == "active":
                raise OSError("simulated crash after successful git worktree add")
            return original_write(path, value, **kwargs)

        with mock.patch.object(git_module, "_write_json", side_effect=crash_before_activation):
            with self.assertRaises(OSError):
                self.worker("creation-crash")
        path = self.managed / "creation-crash"
        self.assertTrue(path.is_dir())
        with self.assertRaises(GitError):
            self.repo.verify_managed_worktree(path, "socrates/creation-crash", self.baseline, self.managed)
        recovered = self.repo.verify_managed_worktree(
            path, "socrates/creation-crash", self.baseline, self.managed, reconcile_creating=True)
        self.assertEqual(recovered.head(), self.baseline)
        self.assertTrue(recovered.clean())
        self.assertEqual(json.loads(self.repo._management_path(path).read_text())["state"], "active")

    def test_creation_reconciliation_refuses_advanced_or_dirty_worktree(self):
        worker = self.worker("creation-mismatch")
        marker = self.repo._management_path(worker.path)
        record = json.loads(marker.read_text())
        record["state"] = "creating"
        marker.write_text(json.dumps(record))
        (worker.path / "left.txt").write_text("unrecognized partial activity\n")
        with self.assertRaises(GitError):
            self.repo.verify_managed_worktree(worker.path, worker.branch(), self.baseline,
                                             self.managed, reconcile_creating=True)
        worker.commit_snapshot("Unregistered further work", self.baseline)
        with self.assertRaises(GitError):
            self.repo.verify_managed_worktree(worker.path, worker.branch(), self.baseline,
                                             self.managed, reconcile_creating=True)

    def test_creation_retries_exact_recorded_intent_before_git_add(self):
        original_run = self.repo._run

        def crash_before_add(*args, **kwargs):
            if args[:2] == ("worktree", "add"):
                raise GitError("simulated crash before git add")
            return original_run(*args, **kwargs)

        with mock.patch.object(self.repo, "_run", side_effect=crash_before_add):
            with self.assertRaises(GitError):
                self.worker("unstarted")
        self.assertFalse((self.managed / "unstarted").exists())
        worker = self.worker("unstarted")
        self.assertEqual(worker.head(), self.baseline)
        self.assertEqual(json.loads(self.repo._management_path(worker.path).read_text())["state"], "active")
        with self.assertRaises(GitError):
            self.worker("unstarted")

    def test_snapshot_captures_new_binary_modified_and_deleted_files(self):
        worker = self.worker("snapshot")
        (worker.path / "left.txt").write_text("new left\n")
        (worker.path / "right.txt").unlink()
        (worker.path / "new file\nname.bin").write_bytes(b"\x00\xffbinary\n")
        (worker.path / ".agent").mkdir()
        (worker.path / ".agent/MEMORY.md").write_text("private working notes")
        snapshot = worker.commit_snapshot("Complete candidate", self.baseline)
        self.assertTrue(snapshot.created)
        self.assertEqual(snapshot.parent, self.baseline)
        self.assertEqual(snapshot.tree, worker.tree(snapshot.commit))
        self.assertEqual(set(snapshot.changed_paths), {"left.txt", "right.txt", "new file\nname.bin"})
        self.assertTrue(worker.clean())
        self.assertNotIn(".agent", self.command(worker.path, "ls-tree", "-r", "--name-only", "HEAD"))
        again = worker.commit_snapshot("No new change", snapshot.commit)
        self.assertFalse(again.created)
        self.assertEqual(again.commit, snapshot.commit)
        metadata = worker.diff_metadata(self.baseline, snapshot.commit)
        self.assertEqual(metadata["changed_paths"], snapshot.changed_paths)

    def test_dirty_and_nonignored_untracked_files_are_not_clean(self):
        self.repo.require_clean()
        unknown = self.repository / "untracked.txt"
        unknown.write_text("not snapshotted")
        self.assertFalse(self.repo.clean())
        with self.assertRaises(GitError):
            self.repo.require_clean()
        unknown.unlink()
        (self.repository / "left.txt").write_text("dirty\n")
        with self.assertRaises(GitError):
            self.repo.require_clean()

    def test_snapshot_rejects_stale_head_before_staging(self):
        worker, snapshot = self.candidate("stale")
        (worker.path / "right.txt").write_text("second change\n")
        with self.assertRaises(GitError):
            worker.commit_snapshot("Invalid stale snapshot", self.baseline)
        self.assertEqual(worker.head(), snapshot.commit)
        self.assertEqual(self.command(worker.path, "diff", "--cached", "--name-only"), "")

    def test_active_agent_records_must_be_ignored_and_untracked(self):
        worker = self.worker("agent-records")
        (worker.path / ".agent").mkdir()
        record = worker.path / ".agent/TASK_BRIEF.md"
        record.write_text("scope")
        self.command(worker.path, "add", "-f", ".agent/TASK_BRIEF.md")
        with self.assertRaises(GitError):
            worker.commit_snapshot("Do not publish active records", self.baseline)

    def test_even_fast_forward_candidate_stops_before_real_merge_commit(self):
        _, candidate = self.candidate("fast-forward")
        pending = self.repo.begin_merge(candidate.commit, self.baseline, self.baseline)
        self.assertEqual(pending.state, "pending")
        self.assertEqual(self.repo.head(), self.baseline)
        self.assertEqual(self.repo.merge_head(), candidate.commit)
        merged = self.repo.finish_merge("Accepted merge", self.baseline, candidate.commit, pending.tree)
        parents = self.command(self.repository, "rev-list", "--parents", "-n", "1", merged.commit).split()[1:]
        self.assertEqual(parents, [self.baseline, candidate.commit])
        self.assertTrue(self.repo.is_ancestor(candidate.commit, merged.commit))
        self.assertIsNone(self.repo.merge_head())
        repeated = self.repo.begin_merge(candidate.commit, merged.commit, self.baseline)
        self.assertEqual(repeated.state, "already_integrated")
        self.assertEqual(self.repo.head(), merged.commit)

    def test_parallel_children_integrate_sequentially_and_keep_history(self):
        _, first = self.candidate("first", "left.txt", "child one\n")
        _, second = self.candidate("second", "right.txt", "child two\n")
        self.integrate(first.commit)
        final = self.integrate(second.commit)
        self.assertEqual((self.repository / "left.txt").read_text(), "child one\n")
        self.assertEqual((self.repository / "right.txt").read_text(), "child two\n")
        self.assertTrue(self.repo.is_ancestor(first.commit, final.commit))
        self.assertTrue(self.repo.is_ancestor(second.commit, final.commit))

    def test_conflict_is_preserved_until_explicit_resolution_and_review(self):
        _, first = self.candidate("conflict-one", "left.txt", "one\n")
        _, second = self.candidate("conflict-two", "left.txt", "two\n")
        initial = self.integrate(first.commit).commit
        conflict = self.repo.begin_merge(second.commit, initial, self.baseline)
        self.assertEqual(conflict.state, "conflicted")
        self.assertEqual(conflict.conflicts, ("left.txt",))
        self.assertEqual(self.repo.head(), initial)
        self.assertEqual(self.repo.merge_head(), second.commit)
        self.assertIn("<<<<<<<", (self.repository / "left.txt").read_text())
        with self.assertRaises(GitError):
            self.repo.index_tree()
        with self.assertRaises(GitError):
            self.repo.finish_merge("Forbidden unresolved commit", initial, second.commit, first.tree)
        (self.repository / "left.txt").write_text("reviewed combined behavior\n")
        self.command(self.repository, "add", "left.txt")
        verified_tree = self.repo.index_tree()
        merged = self.repo.finish_merge("Verified resolution", initial, second.commit, verified_tree)
        self.assertEqual(merged.tree, verified_tree)
        self.assertTrue(self.repo.clean())

    def test_merge_gates_reject_stale_head_dirty_files_and_wrong_lineage(self):
        _, first = self.candidate("gate-one")
        _, second = self.candidate("gate-two", "right.txt", "second\n")
        merged = self.integrate(first.commit)
        with self.assertRaises(GitError):
            self.repo.begin_merge(second.commit, self.baseline, self.baseline)
        unknown = self.repository / "untracked"
        unknown.write_text("preserve")
        with self.assertRaises(GitError):
            self.repo.begin_merge(second.commit, merged.commit, self.baseline)
        unknown.unlink()
        unrelated = self.command(self.repository, "commit-tree", self.repo.tree(), "-m", "Unrelated root")
        with self.assertRaises(GitError):
            self.repo.begin_merge(unrelated, merged.commit, self.baseline)
        self.assertIsNone(self.repo.merge_head())

    def test_finish_rejects_wrong_candidate_changed_index_and_unstaged_files(self):
        _, candidate = self.candidate("finish-gate")
        pending = self.repo.begin_merge(candidate.commit, self.baseline, self.baseline)
        with self.assertRaises(GitError):
            self.repo.finish_merge("Wrong candidate", self.baseline, self.baseline, pending.tree)
        (self.repository / "right.txt").write_text("unreviewed unstaged change\n")
        with self.assertRaises(GitError):
            self.repo.finish_merge("Unstaged change", self.baseline, candidate.commit, pending.tree)
        self.command(self.repository, "add", "right.txt")
        with self.assertRaises(GitError):
            self.repo.finish_merge("Index changed", self.baseline, candidate.commit, pending.tree)
        self.assertEqual(self.repo.head(), self.baseline)
        self.assertEqual(self.repo.merge_head(), candidate.commit)

    def test_archive_refs_are_immutable_and_idempotent(self):
        _, candidate = self.candidate("archive")
        ref = self.repo.archive_ref("run-1", "task-1", candidate.commit)
        self.assertEqual(self.repo.archive_ref("run-1", "task-1", candidate.commit), ref)
        self.assertEqual(self.repo.resolve_commit(ref), candidate.commit)
        with self.assertRaises(GitError):
            self.repo.archive_ref("run-1", "task-1", self.baseline)
        with self.assertRaises(GitError):
            self.repo.archive_ref("../outside", "task-1", candidate.commit)

    def test_cleanup_requires_archive_and_reachability_and_keeps_branch(self):
        worker, candidate = self.candidate("cleanup")
        with self.assertRaises(GitError):
            self.cleanup_worker(worker)
        self.integrate(candidate.commit)
        with self.assertRaises(GitError):
            self.cleanup_worker(worker)
        self.repo.archive_ref("run", "cleanup", candidate.commit)
        self.cleanup_worker(worker)
        self.assertFalse(worker.path.exists())
        self.assertEqual(self.repo.resolve_commit("socrates/cleanup"), candidate.commit)
        record = json.loads(self.repo._management_path(worker.path).read_text())
        self.assertEqual(record["state"], "removed")
        self.repo.cleanup_worktree(worker.path, "socrates/cleanup", self.managed, self.repo.head())
        self.assertEqual(self.repo.resolve_commit("socrates/cleanup"), candidate.commit)

    def test_cleanup_retries_after_recording_intent_before_git_removal(self):
        worker, candidate = self.candidate("remove-before")
        self.integrate(candidate.commit)
        self.repo.archive_ref("run", "remove-before", candidate.commit)
        original_run = self.repo._run

        def crash_before_remove(*args, **kwargs):
            if args[:2] == ("worktree", "remove"):
                raise GitError("simulated crash before removal")
            return original_run(*args, **kwargs)

        with mock.patch.object(self.repo, "_run", side_effect=crash_before_remove):
            with self.assertRaises(GitError):
                self.cleanup_worker(worker)
        self.assertTrue(worker.path.exists())
        self.assertEqual(json.loads(self.repo._management_path(worker.path).read_text())["state"], "removing")
        self.cleanup_worker(worker)
        self.assertFalse(worker.path.exists())

    def test_cleanup_retries_after_git_removal_before_final_marker(self):
        worker, candidate = self.candidate("remove-after")
        self.integrate(candidate.commit)
        self.repo.archive_ref("run", "remove-after", candidate.commit)
        original_write = git_module._write_json

        def crash_before_removed_marker(path, value, **kwargs):
            if value["state"] == "removed":
                raise OSError("simulated crash after successful removal")
            return original_write(path, value, **kwargs)

        with mock.patch.object(git_module, "_write_json", side_effect=crash_before_removed_marker):
            with self.assertRaises(OSError):
                self.cleanup_worker(worker)
        self.assertFalse(worker.path.exists())
        self.assertEqual(json.loads(self.repo._management_path(worker.path).read_text())["state"], "removing")
        self.repo.cleanup_worktree(worker.path, "socrates/remove-after", self.managed, self.repo.head())
        self.assertEqual(json.loads(self.repo._management_path(worker.path).read_text())["state"], "removed")

    def test_cleanup_retry_refuses_a_reused_path_or_changed_branch(self):
        worker, candidate = self.candidate("reuse")
        self.integrate(candidate.commit)
        self.repo.archive_ref("run", "reuse", candidate.commit)
        self.cleanup_worker(worker)
        worker.path.mkdir()
        retained = worker.path / "user-data"
        retained.write_text("new unrelated data")
        with self.assertRaises(GitError):
            self.repo.cleanup_worktree(worker.path, "socrates/reuse", self.managed, self.repo.head())
        self.assertEqual(retained.read_text(), "new unrelated data")
        retained.unlink()
        worker.path.rmdir()
        changed = self.command(self.repository, "commit-tree", candidate.tree,
                               "-p", candidate.commit, "-m", "Subsequent task branch work")
        self.command(self.repository, "update-ref", "refs/heads/socrates/reuse", changed, candidate.commit)
        with self.assertRaises(GitError):
            self.repo.cleanup_worktree(worker.path, "socrates/reuse", self.managed, self.repo.head())

    def test_cleanup_refuses_dirty_untracked_and_unknown_ignored_data(self):
        worker, candidate = self.candidate("preserve")
        self.integrate(candidate.commit)
        self.repo.archive_ref("run", "preserve", candidate.commit)
        unknown = worker.path / "untracked"
        unknown.write_text("keep")
        with self.assertRaises(GitError):
            self.cleanup_worker(worker)
        unknown.unlink()
        ignored = worker.path / ".cache"
        ignored.mkdir()
        (ignored / "data").write_text("keep ignored data too")
        with self.assertRaises(GitError):
            self.cleanup_worker(worker, agent_state_archived=True)
        self.assertTrue((ignored / "data").exists())

    def test_cleanup_agent_state_needs_explicit_archived_confirmation(self):
        worker, candidate = self.candidate("agent-cleanup")
        self.integrate(candidate.commit)
        self.repo.archive_ref("run", "agent-cleanup", candidate.commit)
        (worker.path / ".agent").mkdir()
        (worker.path / ".agent/log.txt").write_text("already copied to durable archive")
        with self.assertRaises(GitError):
            self.cleanup_worker(worker)
        self.cleanup_worker(worker, agent_state_archived=True)
        self.assertFalse(worker.path.exists())

    def test_cleanup_refuses_changed_branch_identity(self):
        worker, candidate = self.candidate("identity")
        self.integrate(candidate.commit)
        self.repo.archive_ref("run", "identity", candidate.commit)
        self.command(worker.path, "switch", "-c", "unexpected-branch")
        with self.assertRaises(GitError):
            self.repo.cleanup_worktree(worker.path, "socrates/identity", self.managed, self.repo.head())
        self.assertTrue(worker.path.exists())

    def test_managed_paths_reject_escape_symlinks_and_unregistered_worktrees(self):
        with self.assertRaises(GitError):
            self.repo.create_worktree(self.root / "outside", "outside", self.baseline, self.managed)
        self.managed.mkdir()
        link = self.managed / "linked"
        link.symlink_to(self.repository, target_is_directory=True)
        with self.assertRaises(GitError):
            self.repo.create_worktree(link / "child", "linked", self.baseline, self.managed)
        with self.assertRaises(GitError):
            self.repo.cleanup_worktree(self.managed / "unknown", "unknown", self.managed, self.baseline)

    def test_environment_cannot_redirect_repository_or_index(self):
        with mock.patch.dict(os.environ, {"GIT_DIR": str(self.root / "wrong-git"),
                                         "GIT_INDEX_FILE": str(self.root / "wrong-index")}):
            self.assertEqual(GitRepo(self.repository).head(), self.baseline)


if __name__ == "__main__":
    unittest.main()
