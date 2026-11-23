"""Transport tests use a fake executable; they never invoke a model or edit Git."""

import asyncio
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

from socrates_orchestrator.process import CodexRunError, run_codex


FAKE = r'''
import json, os, pathlib, signal, subprocess, sys, time
args = sys.argv[1:]
out = pathlib.Path(args[args.index("-o") + 1])
mode = sys.stdin.read()
(out.parent / "observed.json").write_text(json.dumps({
    "argv": args, "cwd": os.getcwd(), "prompt": mode, "pid": os.getpid()}))
thread = args[args.index("resume") + 1] if "resume" in args else "thread-A"
if mode == "wrong-thread":
    thread = "thread-B"
print(json.dumps({"type": "thread.started", "thread_id": thread}), flush=True)
if mode == "background":
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(60)"],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    (out.parent / "descendant.pid").write_text(str(child.pid))
if mode in {"timeout", "cancel"}:
    child = subprocess.Popen([sys.executable, "-c",
        "import signal,time; signal.signal(signal.SIGTERM,signal.SIG_IGN); time.sleep(60)"])
    (out.parent / "descendant.pid").write_text(str(child.pid))
    time.sleep(0.1)
    if mode == "timeout":
        sys.exit(0)  # Leader exits; descendant keeps stdout pipe open.
    time.sleep(60)
if mode == "bad-event":
    print("not JSON", flush=True)
if mode == "error-event":
    print(json.dumps({"type": "error", "message": "fake failure"}), flush=True)
if mode != "no-completion":
    print(json.dumps({"type": "turn.completed"}), flush=True)
if mode == "malformed":
    out.write_text("{invalid")
elif mode == "duplicate":
    out.write_text('{"kind":"review_requested","kind":"review_decided"}')
elif mode != "missing":
    out.write_text(json.dumps({"kind": "unexpected" if mode == "bad-kind"
                               else "review_requested", "task_id": "T1"}))
print("fake diagnostic", file=sys.stderr, flush=True)
if mode == "nonzero":
    sys.exit(7)
'''


@unittest.skipUnless(sys.platform.startswith("linux"), "Linux process-group tests")
class CodexProcessTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.worktree = self.root / "worktree with spaces"
        self.worktree.mkdir()
        self.executable = self.root / "fake codex"
        self.executable.write_text(f"#!{sys.executable}\n" + FAKE)
        self.executable.chmod(0o700)

    def run_args(self, mode, **overrides):
        return dict(worktree=self.worktree, invocation_dir=self.root / mode,
                    prompt=mode, schema={"type": "object"},
                    expected_kinds={"review_requested"}, timeout_s=5,
                    executable=str(self.executable), **overrides)

    async def wait_for_file(self, path):
        async def wait():
            while not path.exists():
                await asyncio.sleep(0.01)
        await asyncio.wait_for(wait(), 3)

    def assert_not_running(self, pid):
        status = Path(f"/proc/{pid}/stat")
        if status.exists():
            # An orphan may briefly await reaping by PID 1; it cannot run.
            state = status.read_text().rsplit(")", 1)[1].split()[0]
            self.assertEqual(state, "Z", f"process {pid} is still {state}")

    async def wait_stopped(self, pid):
        for _ in range(100):
            try:
                self.assert_not_running(pid)
                return
            except AssertionError:
                await asyncio.sleep(0.01)
        self.assert_not_running(pid)

    async def test_new_and_resume_have_exact_identity_and_argument_boundaries(self):
        starts, threads = [], []
        first = await run_codex(**self.run_args(
            "new", on_start=lambda pid, pgid: starts.append((pid, pgid)),
            on_thread=threads.append))
        self.assertEqual(first.thread_id, "thread-A")
        self.assertEqual(threads, ["thread-A"])
        self.assertEqual(len(starts), 1)
        self.assertEqual(starts[0][0], starts[0][1])
        identity = json.loads((first.invocation_dir / "process.json").read_text())
        self.assertEqual(identity, {"pid": starts[0][0], "pgid": starts[0][1]})
        second = await run_codex(**self.run_args("resume", session_id=first.thread_id,
                                                 sandbox="read-only"))
        self.assertEqual(second.thread_id, first.thread_id)
        observed = json.loads((second.invocation_dir / "observed.json").read_text())
        args = observed["argv"]
        self.assertEqual(args[:4], ["-a", "never", "exec", "-C"])
        self.assertEqual(args[args.index("resume") + 1], "thread-A")
        self.assertEqual(args[args.index("--sandbox") + 1], "read-only")
        self.assertNotIn("--last", args)
        self.assertEqual(observed["cwd"], str(self.worktree))
        self.assertEqual(observed["prompt"], "resume")
        self.assertIn("thread.started", (second.invocation_dir / "events.jsonl").read_text())
        self.assertIn("fake diagnostic", (second.invocation_dir / "stderr.log").read_text())
        self.assertEqual(json.loads((second.invocation_dir / "session.json").read_text()),
                         {"thread_id": "thread-A"})

    async def test_invalid_protocol_and_outcomes_are_not_success(self):
        for mode in ("missing", "malformed", "duplicate", "bad-kind", "bad-event",
                     "error-event", "no-completion", "nonzero", "wrong-thread"):
            with self.subTest(mode=mode), self.assertRaises(CodexRunError):
                await run_codex(**self.run_args(mode, session_id="thread-A"))

    async def test_existing_attempt_is_never_reused(self):
        await run_codex(**self.run_args("new"))
        with self.assertRaises(FileExistsError):
            await run_codex(**self.run_args("new"))

    async def test_journal_failure_cannot_be_accepted(self):
        def failed_callback(*args):
            raise RuntimeError("fake journal failure")

        for callback in ("on_start", "on_thread"):
            with self.subTest(callback=callback), self.assertRaises(CodexRunError):
                await run_codex(**self.run_args(callback, **{callback: failed_callback}))

    async def test_timeout_kills_group_even_after_leader_exits(self):
        kwargs = self.run_args("timeout")
        kwargs["timeout_s"] = 0.5
        with self.assertRaises(CodexRunError):
            await run_codex(**kwargs)
        pid = int((self.root / "timeout" / "descendant.pid").read_text())
        self.assert_not_running(pid)

    async def test_success_also_stops_background_writers(self):
        result = await run_codex(**self.run_args("background"))
        pid = int((result.invocation_dir / "descendant.pid").read_text())
        await self.wait_stopped(pid)

    async def test_cancellation_drains_and_kills_process_group(self):
        task = asyncio.create_task(run_codex(**self.run_args("cancel")))
        pid_file = self.root / "cancel" / "descendant.pid"
        await self.wait_for_file(pid_file)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        observed = json.loads((pid_file.parent / "observed.json").read_text())
        self.assert_not_running(observed["pid"])
        self.assert_not_running(int(pid_file.read_text()))
        self.assertIn("thread.started", (pid_file.parent / "events.jsonl").read_text())


if __name__ == "__main__":
    unittest.main()
