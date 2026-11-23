"""Validate the approved task graph before creating any worktrees."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any


class ManifestError(ValueError):
    pass


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def strict_json(text: str) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ManifestError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    def invalid(value: str) -> None:
        raise ManifestError(f"Invalid JSON number: {value}")

    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)
    except (ValueError, TypeError) as exc:
        raise ManifestError(str(exc)) from exc


def identifier(value: Any, name: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]{0,63}", value):
        raise ManifestError(f"{name} must be a 1–64 character identifier")
    return value


def relative_path(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value or "\0" in value:
        raise ManifestError(f"Invalid {name}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(p in (".", "..", ".git") for p in value.split("/")):
        raise ManifestError(f"{name} must be a relative path without traversal or .git")
    if str(path) != value.rstrip("/") or str(path) == ".":
        raise ManifestError(f"Invalid {name}: {value}")
    return value


def strings(value: Any, name: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
        raise ManifestError(f"{name} must be a list of nonempty strings")
    if nonempty and not value:
        raise ManifestError(f"{name} must not be empty")
    if len(set(value)) != len(value):
        raise ManifestError(f"{name} contains duplicates")
    return value


def commands(value: Any, name: str) -> list[list[str]]:
    if not isinstance(value, list):
        raise ManifestError(f"{name} must be a list of argv lists (no shell strings)")
    for command in value:
        if not isinstance(command, list) or not command or any(
            not isinstance(part, str) or "\0" in part for part in command
        ) or not command[0].strip():
            raise ManifestError(f"Invalid argv in {name}")
    return value


def validate(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManifestError("Manifest must be an object")
    required = {"schema_version", "run_id", "goal", "parent_brief", "milestones", "criteria",
                "parent_criteria", "tasks", "integration_verify", "authorization"}
    optional = {"max_workers", "max_attempts", "timeout_seconds", "repair_mode", "cleanup",
                "policy_files", "merge_verify", "integration_paths"}
    if required - value.keys() or value.keys() - required - optional:
        raise ManifestError(f"Manifest fields: missing={sorted(required - value.keys())}, "
                            f"unknown={sorted(value.keys() - required - optional)}")
    result = json.loads(canonical(value))
    if type(result["schema_version"]) is not int or result["schema_version"] != 1:
        raise ManifestError("Only schema_version 1 is supported")
    identifier(result["run_id"], "run_id")
    if not isinstance(result["goal"], str) or not result["goal"].strip():
        raise ManifestError("goal must be nonempty")
    relative_path(result["parent_brief"], "parent_brief")
    strings(result["milestones"], "milestones", nonempty=True)
    criteria = result["criteria"]
    if not isinstance(criteria, list) or not criteria:
        raise ManifestError("criteria must be a nonempty list")
    ids = set()
    for criterion in criteria:
        if not isinstance(criterion, dict) or set(criterion) != {"id", "text"}:
            raise ManifestError("Each criterion needs exactly id and text")
        cid = identifier(criterion["id"], "criterion id")
        if cid in ids or not isinstance(criterion["text"], str) or not criterion["text"].strip():
            raise ManifestError("Criterion IDs must be unique and text nonempty")
        ids.add(cid)
    parent_ids = strings(result["parent_criteria"], "parent_criteria")
    if set(parent_ids) - ids:
        raise ManifestError("Unknown parent criterion")
    auth = result["authorization"]
    auth_fields = {"parent_plan_approved", "delegate_plan_review", "delegate_result_review",
                   "local_merge", "final_reviewer"}
    if not isinstance(auth, dict) or set(auth) != auth_fields:
        raise ManifestError("authorization must explicitly name each delegated authority")
    if any(auth[field] is not True for field in auth_fields - {"final_reviewer"}):
        raise ManifestError("This runtime requires approved parent plan, delegated reviews and local merges")
    if not isinstance(auth["final_reviewer"], str) or not auth["final_reviewer"].strip() or auth["final_reviewer"].strip().lower() in {"parent", "self"}:
        raise ManifestError("final_reviewer must be a separate reviewer, not the parent itself")
    tasks = result["tasks"]
    if not isinstance(tasks, list) or not tasks:
        raise ManifestError("tasks must be a nonempty list")
    task_ids = set()
    covered = set(parent_ids)
    task_fields = {"id", "title", "instructions", "milestones", "criteria", "depends_on",
                   "reviewer", "allowed_paths", "verify"}
    for task in tasks:
        if not isinstance(task, dict) or set(task) != task_fields:
            raise ManifestError("Every task must have exactly " + ", ".join(sorted(task_fields)))
        tid = identifier(task["id"], "task id")
        if tid == "parent":
            raise ManifestError("parent is reserved for the root task")
        if tid in task_ids:
            raise ManifestError(f"Duplicate task id: {tid}")
        task_ids.add(tid)
        for key in ("title", "instructions"):
            if not isinstance(task[key], str) or not task[key].strip():
                raise ManifestError(f"{tid}.{key} must be nonempty")
        strings(task["milestones"], f"{tid}.milestones", nonempty=True)
        task_criteria = strings(task["criteria"], f"{tid}.criteria", nonempty=True)
        if set(task_criteria) - ids:
            raise ManifestError(f"Unknown criteria in {tid}")
        covered.update(task_criteria)
        strings(task["depends_on"], f"{tid}.depends_on")
        if task["reviewer"] != "parent":
            raise ManifestError("v1 supports one parent reviewer; review edges are not dependency edges")
        for path in strings(task["allowed_paths"], f"{tid}.allowed_paths", nonempty=True):
            relative_path(path, "allowed path")
            if path.rstrip("/") == ".agent" or path.startswith(".agent/"):
                raise ManifestError(".agent is runtime/task evidence, not a tracked deliverable path")
        commands(task["verify"], f"{tid}.verify")
    if covered != ids:
        raise ManifestError(f"Unassigned original criteria: {sorted(ids - covered)}")
    graph = {task["id"]: task["depends_on"] for task in tasks}
    visited, active = set(), set()

    def visit(tid: str) -> None:
        if tid in active:
            raise ManifestError(f"Dependency cycle at {tid}")
        if tid in visited:
            return
        active.add(tid)
        for dep in graph[tid]:
            if dep not in task_ids:
                raise ManifestError(f"Unknown prerequisite {dep}")
            visit(dep)
        active.remove(tid)
        visited.add(tid)

    for tid in graph:
        visit(tid)
    defaults = {"max_workers": 2, "max_attempts": 3, "timeout_seconds": 1800,
                "repair_mode": "resume", "cleanup": True, "policy_files": ["AGENTS.md"],
                "merge_verify": [], "integration_paths": []}
    for key, default in defaults.items():
        result.setdefault(key, default)
    for key in ("max_workers", "max_attempts", "timeout_seconds"):
        if type(result[key]) is not int or result[key] < 1:
            raise ManifestError(f"{key} must be a positive integer")
    if result["repair_mode"] not in ("resume", "fresh") or type(result["cleanup"]) is not bool:
        raise ManifestError("Invalid repair_mode or cleanup")
    for key in ("policy_files", "integration_paths"):
        for path in strings(result[key], key, nonempty=key == "policy_files"):
            relative_path(path, key)
            if path.endswith("/") and key == "policy_files":
                raise ManifestError("policy_files must name files")
    commands(result["integration_verify"], "integration_verify")
    commands(result["merge_verify"], "merge_verify")
    return result


def load(path: Path) -> dict[str, Any]:
    return validate(strict_json(path.read_text(encoding="utf-8")))
