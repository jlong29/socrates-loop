"""Linux process adapter for one bounded Codex invocation.

The caller owns task locks, policy prompts, domain/schema validation, candidate
identity, approval authority, and recovery. This adapter validates the transport
and a result object's `kind`; it does not validate arbitrary JSON Schema.
Requires Python 3.11+ and a Codex CLI supporting the flags below.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable, Collection
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import signal
from typing import Any


@dataclass(frozen=True)
class CodexRun:
    thread_id: str
    result: dict[str, Any]
    invocation_dir: Path


class CodexRunError(RuntimeError):
    def __init__(self, message: str, invocation_dir: Path):
        super().__init__(f"{message}; inspect {invocation_dir}")
        self.invocation_dir = invocation_dir


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")


def _decode_json(text: str | bytes) -> Any:
    return json.loads(text, object_pairs_hook=_unique_object,
                      parse_constant=_invalid_constant)


def _write_new(path: Path, text: str) -> None:
    with path.open("x", encoding="utf-8") as output:
        output.write(text)
        output.flush()
        os.fsync(output.fileno())


async def _feed(proc: asyncio.subprocess.Process, prompt: str) -> None:
    assert proc.stdin is not None
    try:
        proc.stdin.write(prompt.encode("utf-8"))
        await proc.stdin.drain()
    except (BrokenPipeError, ConnectionResetError):
        pass  # The process status and result checks report the failure.
    finally:
        proc.stdin.close()
        try:
            await proc.stdin.wait_closed()
        except (BrokenPipeError, ConnectionResetError):
            pass


async def _stop_group(proc: asyncio.subprocess.Process,
                      tasks: list[asyncio.Task[Any]]) -> None:
    """Stop descendants even when the group leader has already exited."""
    drained = asyncio.gather(*tasks, return_exceptions=True)
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        await asyncio.wait_for(asyncio.shield(drained), 1.0)
    except asyncio.TimeoutError:
        pass
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    await drained
    await proc.wait()


async def _finish_cleanup(proc: asyncio.subprocess.Process,
                          tasks: list[asyncio.Task[Any]]) -> None:
    cleanup = asyncio.create_task(_stop_group(proc, tasks))
    while not cleanup.done():
        try:
            await asyncio.shield(cleanup)
        except asyncio.CancelledError:
            continue  # Finish reaping even if cancellation is requested twice.
    cleanup.result()


async def run_codex(
    *, worktree: Path, invocation_dir: Path, prompt: str,
    schema: dict[str, Any], expected_kinds: Collection[str],
    session_id: str | None = None, timeout_s: float = 1800,
    executable: str = "codex", sandbox: str = "workspace-write",
    on_start: Callable[[int, int], None] | None = None,
    on_thread: Callable[[str], None] | None = None,
) -> CodexRun:
    """Run one turn; resume only the supplied exact recorded thread ID.

    invocation_dir must be new. Logs and inputs survive a failed invocation.
    Callers must not concurrently run two turns on one thread/worktree.
    Cancellation is re-raised after cleanup; timeouts raise CodexRunError.
    Remaining same-group background processes are stopped on success too.
    Process groups cannot contain descendants that deliberately call setsid().
    Trusted synchronous callbacks can journal process and thread ownership.
    """
    if os.name != "posix":
        raise ValueError("This adapter requires POSIX process groups")
    if sandbox not in {"read-only", "workspace-write"}:
        raise ValueError("sandbox must be read-only or workspace-write")
    if not math.isfinite(timeout_s) or timeout_s <= 0 or not expected_kinds:
        raise ValueError("Supply a positive finite timeout and expected kinds")
    worktree = Path(worktree).resolve(strict=True)
    if not worktree.is_dir():
        raise ValueError("worktree must be a directory")
    invocation_dir = Path(invocation_dir).absolute()
    invocation_dir.parent.mkdir(parents=True, exist_ok=True)
    invocation_dir.mkdir(mode=0o700)  # Exclusive leaf: never reuse stale results.
    _write_new(invocation_dir / "prompt.txt", prompt)
    _write_new(invocation_dir / "schema.json",
               json.dumps(schema, indent=2, allow_nan=False))
    result_path = invocation_dir / "result.json"
    args = [executable, "-a", "never", "exec", "-C", str(worktree),
            "--sandbox", sandbox]
    if session_id is not None:
        args += ["resume", session_id]
    args += ["--json", "--output-schema", str(invocation_dir / "schema.json"),
             "-o", str(result_path), "-"]
    _write_new(invocation_dir / "invocation.json", json.dumps({
        "argv": args, "cwd": str(worktree), "session_id": session_id,
        "expected_kinds": sorted(expected_kinds), "timeout_s": timeout_s,
    }, indent=2))
    thread_id: str | None = None
    completed = False
    errors: list[str] = []

    def consume(line: bytes) -> None:
        nonlocal thread_id, completed
        try:
            event = _decode_json(line)
            if not isinstance(event, dict):
                raise ValueError("event is not an object")
            kind = event.get("type")
            if kind == "thread.started":
                current = event.get("thread_id")
                if not isinstance(current, str) or not current:
                    raise ValueError("missing thread_id")
                if (thread_id and current != thread_id) or (
                        session_id and current != session_id):
                    raise ValueError("thread identity changed")
                if thread_id is None:
                    _write_new(invocation_dir / "session.json",
                               json.dumps({"thread_id": current}))
                    if on_thread is not None:
                        try:
                            on_thread(current)
                        except Exception as exc:
                            errors.append(f"Thread journaling failed: {type(exc).__name__}")
                thread_id = current
            elif kind == "turn.completed":
                completed = True
            elif kind in {"turn.failed", "error"}:
                raise ValueError(f"Codex emitted {kind}")
        except (OSError, ValueError, UnicodeError) as exc:
            if len(errors) < 8:
                errors.append(str(exc))

    async def capture(stream: asyncio.StreamReader) -> None:
        with (invocation_dir / "events.jsonl").open("xb") as log:
            pending = b""
            while chunk := await stream.read(65536):
                log.write(chunk)
                log.flush()
                os.fsync(log.fileno())
                pending += chunk
                while b"\n" in pending:
                    line, pending = pending.split(b"\n", 1)
                    if line.strip():
                        consume(line)
            if pending.strip():
                consume(pending)

    with (invocation_dir / "stderr.log").open("xb") as stderr:
        try:
            proc = await asyncio.create_subprocess_exec(
                *args, cwd=worktree, stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE, stderr=stderr,
                start_new_session=True,
            )
        except OSError as exc:
            raise CodexRunError(f"Cannot launch Codex: {exc}", invocation_dir) from exc
        assert proc.stdout is not None
        tasks = [asyncio.create_task(capture(proc.stdout)),
                 asyncio.create_task(_feed(proc, prompt)),
                 asyncio.create_task(proc.wait())]
        completion = asyncio.gather(*tasks)
        try:
            _write_new(invocation_dir / "process.json",
                       json.dumps({"pid": proc.pid, "pgid": proc.pid}))
            if on_start is not None:
                on_start(proc.pid, proc.pid)
            await asyncio.wait_for(asyncio.shield(completion), timeout_s)
            await _stop_group(proc, tasks)
        except BaseException as exc:
            await _finish_cleanup(proc, tasks)
            if not completion.cancelled():
                completion.exception()  # Retrieve an I/O failure, if any.
            if isinstance(exc, asyncio.CancelledError):
                raise
            raise CodexRunError(f"Invocation failed: {type(exc).__name__}",
                                invocation_dir) from exc
        finally:
            stderr.flush()
            os.fsync(stderr.fileno())
    if proc.returncode != 0 or errors or not completed or not thread_id:
        detail = "; ".join(errors) or "missing completed turn/thread identity"
        raise CodexRunError(f"Exit {proc.returncode}: {detail}", invocation_dir)
    try:
        result = _decode_json(result_path.read_text(encoding="utf-8"))
        if (not isinstance(result, dict) or not isinstance(result.get("kind"), str)
                or result["kind"] not in expected_kinds):
            raise ValueError("unexpected result kind or non-object result")
    except (OSError, ValueError, UnicodeError) as exc:
        raise CodexRunError(f"Invalid final result: {exc}", invocation_dir) from exc
    return CodexRun(thread_id, result, invocation_dir)
