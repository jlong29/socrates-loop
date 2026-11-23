#!/usr/bin/env python3
"""Deterministic CLI transport fixture; never calls a model or writes Git history.

Task instructions are JSON fixture settings. Runtime observation/rendezvous files
live beside invocation logs, outside the checkouts. This exercises subprocess and
controller behavior, not the security enforcement of the real Codex sandbox.
"""
from __future__ import annotations

import json
from pathlib import Path
import sys
import time
import uuid


def emit(kind: str, **fields: object) -> None:
    print(json.dumps({"type": kind, **fields}), flush=True)


def write_files(root: Path, outputs: dict[str, str]) -> None:
    for name, content in outputs.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def wait_for(paths: list[Path]) -> None:
    deadline = time.monotonic() + 15
    while not all(path.exists() for path in paths):
        if time.monotonic() >= deadline:
            raise RuntimeError("Fixture rendezvous timed out: " + repr(paths))
        time.sleep(0.02)


def main() -> None:
    args = sys.argv[1:]
    value = lambda flag: args[args.index(flag) + 1]
    root = Path(value("-C")).resolve()
    destination = Path(value("-o"))
    sandbox = value("--sandbox")
    request = json.loads(sys.stdin.read())
    assert Path.cwd().resolve() == root == Path(request["cwd"]).resolve()
    assert args[:3] == ["-a", "never", "exec"] and args[-1] == "-"
    assert "--json" in args and Path(value("--output-schema")).is_file()
    resumed = "resume" in args
    thread_id = value("resume") if resumed else "fixture-" + uuid.uuid4().hex
    operation = request["operation"]
    is_parent = request["role"] != "task_worker"
    assert sandbox == ("read-only" if is_parent and operation != "integration_repair" else "workspace-write")
    assert request["role"] == ("integration_author" if operation == "integration_repair" else "parent_reviewer" if is_parent else "task_worker")
    (destination.parent / "fixture-observation.json").write_text(json.dumps({
        "argv": args, "cwd": str(root), "sandbox": sandbox,
        "thread_id": thread_id, "resumed": resumed,
    }), encoding="utf-8")
    emit("thread.started", thread_id=thread_id)
    emit("turn.started")

    config = json.loads(request["task"]["instructions"]) if request["task"] else {}
    marker_dir = destination.parents[2] / "fixture-rendezvous"
    marker_dir.mkdir(exist_ok=True)
    notes = "Fixture examined the assigned scope and criterion evidence."
    kind, status = "approved", "passed"
    if operation == "plan":
        marker = marker_dir / (request["task_id"] + "-plan")
        marker.touch()
        wait_for([marker_dir / (tid + "-plan") for tid in config.get("plan_barrier", [])])
        for name in ("TASK_BRIEF.md", "MEMORY.md"):
            with (root / ".agent" / name).open("a", encoding="utf-8") as stream:
                stream.write("\nPlanned criteria: " + ", ".join(request["criterion_ids"]) + "\n")
        kind = "plan_ready"
    elif operation in {"implement", "repair"}:
        if operation == "implement" and config.get("wait_for_plan"):
            wait_for([marker_dir / (config["wait_for_plan"] + "-plan")])
        outputs = config.get("draft_outputs", config["outputs"]) if operation == "implement" else config["outputs"]
        write_files(root, outputs)
        with (root / ".agent" / "MEMORY.md").open("a", encoding="utf-8") as stream:
            stream.write("\n" + operation + ": wrote and inspected assigned deliverables.\n")
        kind = "review_ready"
    elif operation == "closeout":
        archive = root / request["archive_path"]
        archive.mkdir(parents=True, exist_ok=True)
        for name in ("TASK_BRIEF.md", "MEMORY.md"):
            (root / ".agent" / name).replace(archive / name)
        (archive / "CLOSEOUT.md").write_text(
            "# Closeout\n\nAccepted criteria: " + ", ".join(request["criterion_ids"]) +
            "\n\nEvidence: assigned output inspected and supervisor verification recorded.\n",
            encoding="utf-8")
        kind = "closeout_ready"
    elif operation == "review_result":
        source = Path(request["task_workspace"])
        if any((source / name).read_text() != text for name, text in config["outputs"].items()):
            kind, status = "changes_requested", "failed"
            notes = "The draft output does not satisfy the delegated criterion; apply the final specified content."
    elif operation in {"review_plan", "review_closeout", "review_integration"}:
        assert request["candidate"] and request["candidate_id"]
        if operation == "review_integration":
            assert all(text in (root / name).read_text() for name, text in config["outputs"].items())
    elif operation == "integration_repair":
        settings = [json.loads(task["instructions"]) for task in request["manifest"]["tasks"]]
        if request["merge_pending"]:
            for name in request["conflicts"]:
                parts = [entry["outputs"][name] for entry in settings if name in entry["outputs"]]
                write_files(root, {name: "".join(dict.fromkeys(parts))})
        else:
            for entry in settings:
                write_files(root, entry.get("integration_outputs", {}))
        kind = "review_ready"
    elif operation == "prepare_handoff":
        kind = "review_ready"
        notes = "Combined results are ready for the separate human final reviewer; the root remains unapproved."
    else:
        raise ValueError("Unknown fixture operation: " + operation)

    assert kind in request["expected_kinds"]
    result = {key: request[key] for key in (
        "task_id", "operation", "invocation_id", "candidate_id", "policy_hash")}
    result.update(kind=kind, notes=notes, criteria=[
        {"id": cid, "status": status, "evidence": notes} for cid in request["criterion_ids"]])
    destination.write_text(json.dumps(result), encoding="utf-8")
    emit("turn.completed", usage={"input_tokens": 0, "output_tokens": 0})


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"fixture failure: {error!r}", file=sys.stderr, flush=True)
        sys.exit(2)
