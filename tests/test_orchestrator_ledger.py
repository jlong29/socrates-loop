"""Ledger isolation, transaction, and interrupted-controller regressions."""

from pathlib import Path
import select
import subprocess
import sys
import tempfile
import unittest

from socrates_orchestrator.ledger import Ledger, LedgerBusy, RevisionConflict


REPO = Path(__file__).resolve().parents[1]


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux writer lock")
class LedgerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "state.sqlite3"

    def test_revision_compare_and_event_are_one_transaction(self):
        with Ledger(self.path) as ledger:
            original = ledger.put("task", "T1", state="planned", phase="Phase 1",
                                  data={"criterion_ids": ["S1"]}, event="task.planned")
            self.assertEqual(original.revision, 1)
            changed = ledger.put("task", "T1", state="running", phase="Phase 2",
                                 data=original.data, expected_revision=1,
                                 event="task.started")
            self.assertEqual(changed.revision, 2)
            for stale in (None, 1):
                with self.subTest(stale=stale), self.assertRaises(RevisionConflict):
                    ledger.put("task", "T1", state="complete", data={},
                               expected_revision=stale)
            self.assertEqual(ledger.get("task", "T1"), changed)
            events = ledger.events()
            self.assertEqual([item["event"] for item in events],
                             ["task.planned", "task.started"])
            self.assertEqual(events[-1]["payload"]["before"]["state"], "planned")
            self.assertEqual(events[-1]["payload"]["after"]["revision"], 2)
            self.assertEqual(len(ledger.events(after_sequence=events[0]["sequence"])), 1)

    def test_failed_event_serialization_rolls_back_record_write(self):
        with Ledger(self.path) as ledger:
            original = ledger.put("task", "T1", state="running", data={})
            with self.assertRaises(TypeError):
                ledger.put("task", "T1", state="complete", data={"changed": True},
                           expected_revision=1, event_data={"invalid": object()})
            self.assertEqual(ledger.get("task", "T1"), original)
            self.assertEqual(len(ledger.events()), 1)
            with self.assertRaises(ValueError):
                ledger.put("task", "T2", state="planned", data={"invalid": float("nan")})
            self.assertIsNone(ledger.get("task", "T2"))

    def test_writer_exclusion_and_concurrent_readonly_status(self):
        with Ledger(self.path) as writer:
            writer.put("run", "P", state="running", data={})
            with self.assertRaises(LedgerBusy):
                Ledger(self.path)
            script = (
                "import sys; from socrates_orchestrator.ledger import Ledger, LedgerBusy\n"
                "try:\n Ledger(sys.argv[1])\n"
                "except LedgerBusy:\n sys.exit(23)\n"
                "sys.exit(1)\n")
            blocked = subprocess.run([sys.executable, "-c", script, str(self.path)],
                                     cwd=REPO, capture_output=True, text=True, timeout=5)
            self.assertEqual(blocked.returncode, 23, blocked.stderr)
            with Ledger(self.path, readonly=True) as reader:
                self.assertEqual(reader.get("run", "P").state, "running")
                writer.put("task", "T1", state="planned", data={})
                self.assertEqual([item.id for item in reader.list("task")], ["T1"])
                with self.assertRaises(PermissionError):
                    reader.put("task", "T2", state="planned", data={})
        with Ledger(self.path) as next_writer:
            self.assertEqual(next_writer.get("run", "P").state, "running")

    def test_crash_releases_lock_and_recovery_is_explicit_and_idempotent(self):
        script = (
            "import sys,time; from pathlib import Path; "
            "from socrates_orchestrator.ledger import Ledger\n"
            "ledger=Ledger(Path(sys.argv[1]))\n"
            "ledger.put('invocation','I1',state='running',phase='Phase 2',"
            "data={'thread_id':'thread-A'})\n"
            "ledger.put('task','T1',state='complete',data={})\n"
            "print('ready',flush=True)\n"
            "time.sleep(60)\n")
        child = subprocess.Popen([sys.executable, "-c", script, str(self.path)],
                                 cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                 text=True)
        try:
            ready, _, _ = select.select([child.stdout], [], [], 5)
            self.assertTrue(ready, "child did not initialize ledger")
            self.assertEqual(child.stdout.readline().strip(), "ready")
            child.kill()
            child.communicate(timeout=5)
        finally:
            if child.poll() is None:
                child.kill()
                child.communicate(timeout=5)
        with Ledger(self.path) as ledger:
            self.assertEqual(ledger.get("invocation", "I1").state, "running")
            recovered = ledger.recover_interrupted(reason="operator reconciled old worktree")
            self.assertEqual([(r.id, r.state, r.revision) for r in recovered],
                             [("I1", "interrupted", 2)])
            self.assertEqual(recovered[0].data["thread_id"], "thread-A")
            self.assertEqual(ledger.get("task", "T1").state, "complete")
            count = len(ledger.events())
            self.assertEqual(ledger.recover_interrupted(), [])
            self.assertEqual(len(ledger.events()), count)

    def test_audit_events_and_filtered_records_survive_reopen(self):
        with Ledger(self.path) as ledger:
            ledger.put("task", "T1", state="running", data={})
            ledger.put("task", "T2", state="planned", data={})
            sequence = ledger.append_event("operator.note", data={"reason": "inspection"})
        with Ledger(self.path, readonly=True) as ledger:
            self.assertEqual([item.id for item in ledger.list("task", state="planned")], ["T2"])
            self.assertEqual(ledger.events(after_sequence=sequence - 1)[0]["payload"],
                             {"reason": "inspection"})


if __name__ == "__main__":
    unittest.main()
