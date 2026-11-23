"""Execute approved verification argv, retaining output and killing child groups."""
from __future__ import annotations

import asyncio
import hashlib
import json
import os
from pathlib import Path

from .process import _finish_cleanup


async def verify(commands: list[list[str]], *, cwd: Path, directory: Path,
                 timeout: int) -> list[dict]:
    directory.mkdir(parents=True, exist_ok=False)
    results = []
    for number, argv in enumerate(commands):
        output = directory / f"{number:02d}.log"
        error = ""
        with output.open("xb") as log:
            try:
                process = await asyncio.create_subprocess_exec(
                    *argv, cwd=cwd, stdin=asyncio.subprocess.DEVNULL,
                    stdout=log, stderr=asyncio.subprocess.STDOUT,
                    start_new_session=True)
            except OSError as exc:
                results.append({"argv": argv, "returncode": None, "passed": False,
                                "error": str(exc), "log": str(output)})
                continue
            wait = asyncio.create_task(process.wait())
            try:
                await asyncio.wait_for(asyncio.shield(wait), timeout)
            except asyncio.TimeoutError:
                error = "verification timed out"
            finally:
                await _finish_cleanup(process, [wait])
                log.flush()
                os.fsync(log.fileno())
        results.append({"argv": argv, "returncode": process.returncode,
                        "passed": not error and process.returncode == 0,
                        "error": error, "log": str(output)})
    for result in results:
        result["log_sha256"] = hashlib.sha256(Path(result["log"]).read_bytes()).hexdigest()
    (directory / "results.json").write_text(json.dumps(results, indent=2) + "\n")
    return results
