"""Run with python3 -m socrates_orchestrator; never publishes or merges to main."""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
import sys

from .controller import Controller, initialize, status


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Local Socrates Loop task-graph supervisor (Linux, Python 3.11+)")
    commands = result.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="Record an operator-approved graph; never overwrite existing evidence")
    init.add_argument("--repo", type=Path, required=True)
    init.add_argument("--manifest", type=Path, required=True)
    init.add_argument("--run-dir", type=Path, required=True)
    init.add_argument("--approve", action="store_true", help="Acknowledge approval of this exact plan and its delegated review/merge authority")
    run = commands.add_parser("run", help="Dispatch finite Codex turns and integrate accepted children")
    run.add_argument("--run-dir", type=Path, required=True)
    run.add_argument("--codex", default="codex", help="Codex executable path (or deterministic test fixture)")
    run.add_argument("--repair-conflicts", action="store_true", help="Allow bounded parent repairs of pending merges")
    run.add_argument("--repair-integration", action="store_true", help="Allow bounded parent fixes after combined verification fails")
    state = commands.add_parser("status", help="Read status while a controller runs")
    state.add_argument("--run-dir", type=Path, required=True)
    state.add_argument("--json", action="store_true")
    recovery = commands.add_parser("recover", help="Explicitly reconcile interrupted attempts; does not kill stale PIDs")
    recovery.add_argument("--run-dir", type=Path, required=True)
    recovery.add_argument("--task", help="Task ID, parent, or omit for all unfinished tasks")
    recovery.add_argument("--acknowledge-stopped", action="store_true", help="Confirm old workers/descendants have stopped after inspecting retained records")
    recovery.add_argument("--fresh-session", action="store_true")
    cleanup = commands.add_parser("cleanup", help="Remove only registered, clean, archived, integrated worktrees")
    cleanup.add_argument("--run-dir", type=Path, required=True)
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if sys.version_info < (3, 11) or not sys.platform.startswith("linux"):
        print("The optional orchestrator requires Linux and Python 3.11+", file=sys.stderr)
        return 2
    try:
        if args.command == "init":
            outcome = initialize(repo=args.repo, manifest_path=args.manifest,
                                 run_dir=args.run_dir, approved=args.approve)
        elif args.command == "status":
            outcome = status(args.run_dir.resolve())
            if not args.json:
                for record in outcome["run"] + outcome["tasks"]:
                    print(f"{record['kind']} {record['id']}: {record['phase']}; {record['state']}")
                return 0
        else:
            with Controller(args.run_dir, executable=getattr(args, "codex", "codex")) as controller:
                if args.command == "run":
                    outcome = asyncio.run(controller.run(repair_conflicts=args.repair_conflicts,
                                                         repair_integration=args.repair_integration))
                elif args.command == "recover":
                    outcome = controller.recover(task_id=args.task,
                                                 acknowledged_stopped=args.acknowledge_stopped,
                                                 fresh_session=args.fresh_session)
                else:
                    outcome = {"cleanup": controller.cleanup()}
        print(json.dumps(outcome, indent=2))
        return 1 if isinstance(outcome, dict) and outcome.get("state") == "blocked" else 0
    except (Exception, KeyboardInterrupt) as exc:
        print(f"socrates: {exc or 'interrupted; inspect status and recover explicitly'}", file=sys.stderr)
        return 130 if isinstance(exc, KeyboardInterrupt) else 2


if __name__ == "__main__":
    raise SystemExit(main())
