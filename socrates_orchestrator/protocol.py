"""The model proposes typed handoffs; the controller owns all transitions."""
from __future__ import annotations

from typing import Any


KINDS = ["plan_ready", "review_ready", "closeout_ready", "approved",
         "changes_requested", "blocked"]
SCHEMA = {
    "type": "object", "additionalProperties": False,
    "properties": {
        "kind": {"type": "string", "enum": KINDS},
        "task_id": {"type": "string"},
        "operation": {"type": "string"},
        "invocation_id": {"type": "string"},
        "candidate_id": {"type": "string"},
        "policy_hash": {"type": "string"},
        "notes": {"type": "string"},
        "criteria": {
            "type": "array", "items": {
                "type": "object", "additionalProperties": False,
                "properties": {
                    "id": {"type": "string"},
                    "status": {"type": "string", "enum": ["passed", "failed", "not_checked"]},
                    "evidence": {"type": "string"},
                }, "required": ["id", "status", "evidence"],
            },
        },
    },
    "required": ["kind", "task_id", "operation", "invocation_id", "candidate_id",
                 "policy_hash", "notes", "criteria"],
}


def validate_result(result: Any, request: dict, expected: set[str]) -> dict:
    if not isinstance(result, dict) or set(result) != set(SCHEMA["required"]):
        raise ValueError("Handoff fields do not match the protocol")
    for key in SCHEMA["required"]:
        if key != "criteria" and not isinstance(result[key], str):
            raise ValueError(f"Handoff {key} must be a string")
    for key in ("task_id", "operation", "invocation_id", "candidate_id", "policy_hash"):
        if result[key] != request[key]:
            raise ValueError(f"Stale or mismatched handoff {key}")
    if result["kind"] not in expected:
        raise ValueError("Unexpected handoff kind")
    evidence = result["criteria"]
    if not isinstance(evidence, list):
        raise ValueError("criteria must be a list")
    ids = []
    for item in evidence:
        if not isinstance(item, dict) or set(item) != {"id", "status", "evidence"}:
            raise ValueError("Invalid criterion evidence")
        if any(not isinstance(value, str) for value in item.values()):
            raise ValueError("Criterion evidence values must be strings")
        if item["status"] not in {"passed", "failed", "not_checked"} or not item["evidence"].strip():
            raise ValueError("Criterion evidence needs a valid status and explanation")
        ids.append(item["id"])
    if len(set(ids)) != len(ids) or set(ids) != set(request["criterion_ids"]):
        raise ValueError("Handoff must account for exactly the assigned criteria")
    if result["kind"] == "approved" and any(item["status"] != "passed" for item in evidence):
        raise ValueError("Approval cannot contain unmet or unexamined criteria")
    return result
