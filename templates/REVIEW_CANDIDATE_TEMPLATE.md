# REVIEW CANDIDATE

Use this optional record for an explicit review handoff. The supervisor's machine record owns candidate identity and execution state; this document explains scope and evidence without creating a second approval ledger. The existing installer does not copy this template into targets automatically.

## Identity and authority
- **Task / parent:** <stable task IDs>
- **Candidate / attempt:** <supervisor candidate ID and invocation or attempt ID>
- **Kind:** <plan | implementation | closeout | integration>
- **Assigned reviewer:** <reviewer and source of delegated authority>
- **Policy:** <authoritative files and pinned digest or revision>
- **Approved brief / requirements:** <exact revision or digest and durable reference>
- **Input baseline:** <commit/tree and accepted prerequisite candidates>
- **Candidate version:** <exact commit/tree and snapshot manifest; include relevant untracked task records separately>

## Scope and parent intent
- <delegated outcomes and applicable parent constraints>
- <interfaces supplied to consumers and assumptions required from prerequisites>
- <explicit exclusions and parent-owned integration checks>

## Acceptance evidence

Expected results come from approved requirements, independently of the implementation. Distinguish executed verification, source inspection and unverified assumptions.

| Parent criterion | Child obligation | Expected result | Check and observed result | Evidence / limitation |
|---|---|---|---|---|
| <S1> | <scoped requirement> | <observable behavior> | <command, environment, result> | <durable path or unresolved gap> |

## Changes and uncertainty
- **Outcome:** <what this version establishes>
- **Decisions:** <material choices and rationale; link to the brief/memory>
- **Findings / blockers:** <reproduction and impact, or none>
- **Requested scope changes:** <proposal requiring separate authority, or none>
- **Downstream implications:** <compatibility checks and affected tasks>

## Handoff
- **Working tree status:** <clean candidate / deliberately captured task records; explain exclusions>
- **Next action:** <review this exact candidate; repair findings; validate closeout; or integrate>
- **Relevant records:** <task brief, memory, prior reviews, closeout, verification evidence>

The reviewer records its decision through the supervisor against this candidate. Approval of another version does not transfer automatically. Phase 4 changes and integration repairs must be checked before an accepted candidate is published to dependent work.
