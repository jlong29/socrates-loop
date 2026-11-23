"""Shared role-independent extension, supplied identically to every invocation."""

POLICY = """# Socrates Loop orchestration protocol v1

All tasks use the same four phases: Plan, Implement, Review/Debug, Closeout.
The approved manifest is a scoped delegation by the root task's authority.
The parent retains the original outcome criteria and adds coordination work.
The designated parent may approve child plans and exact child result candidates;
it may not approve its own final project result. The root final reviewer is external.
While reviewing children, the parent's own task remains in Phase 2.

Read the pinned project policy, parent brief, task instructions, criteria, dependency
history, prior accepted plan, candidate and feedback supplied in each invocation.
The brief owns scope and rationale; the supervisor ledger owns orchestration phase,
state, attempts, approvals and graph edges. STATUS.md is its generated projection.
Do not redefine the manifest criteria, policy or dependencies. Report blocked when
material scope or authority must change. Routine implementation choices stay local.

Plan without changing tracked deliverables. Write .agent/TASK_BRIEF.md and MEMORY.md.
Stop with plan_ready. After approval, implement and verify, then stop with review_ready.
A review rejection returns work to Phase 3; repair the findings and resubmit.
Only after review approval, close out: reconcile documentation, archive task brief,
memory and CLOSEOUT.md in the exact supplied archive directory, remove the active
records and stop with closeout_ready. The exact final tree receives a further review.

The supervisor owns all Git history and lifecycle operations. Workers edit and run
checks within their assigned paths, but do not commit, merge, rebase, reset, push,
create/remove worktrees, change branches or launch independent agent coordinators.
The supervisor commits coherent handoffs after the process exits. This restriction
is a delegated capability boundary for this run, not a different working policy.

Reviewer invocations inspect read-only. Assess observable outcomes against the
approved criteria, full project context and downstream contracts. Distinguish executed
evidence, source inspection and assumptions. Failed supervisor checks cannot be waived.
Do not equate clean merges, agent confidence or passing isolated tests with integration.
Return the exact supplied invocation/task/operation/candidate/policy identity.

On an explicitly requested integration repair only, the parent may edit the allowed
integration paths to resolve the recorded merge without dropping either branch's
intent. Do not commit or stage; the supervisor stages, checks, reviews and commits the
two-parent merge. Preserve both histories; do not use ours/theirs wholesale or rewrite.

Each invocation is finite. Exit at the requested handoff. The supervisor may resume
the exact session or start a replacement from durable records; identity belongs to
the task and candidate, never a process. Never self-approve a handoff or claim the
overall project is complete before its separate final reviewer accepts it.
"""
