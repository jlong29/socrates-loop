# TASK BRIEF

## Task
- Authorize coherent local commits and simplify the distributed guidance and task records while retaining all four mandatory phases, approval gates and independent verification.
- The user's full request also includes updating this repository's installation. Complete that as the normal follow-on integration task after this source-development task is reviewed and closed out.

## Status
- **Phase:** Phase 4
- **State:** complete
- **Last updated:** 2026-11-19 15:29 America/New_York

## Context lineage
- **Epoch / initiative:** local commits and Socrates Loop simplification.
- **History scope:** archive names, then the one relevant completed closeout.
- **Closeouts reviewed:** [self-installation closeout](../20261104_2028_self_installation/CLOSEOUT.md).
- Applicable findings: canonical sources and installed guidance have distinct ownership; preserve repository-specific guidance and task history; compare the complete shared policy; validate command behavior, not merely text equality. Prior bootstrap observations were not a controlled evaluation.
- Preserve the existing sequence: finish and close out the source-template change, then update this repository's installation in a separate task using that fixed source. Requesting both outcomes does not require changing the update workflow.

## Why this update
- The user reports that prohibiting commits encourages changes to accumulate beyond a coherent commit boundary.
- Current agents increasingly provide context management and engineering routines themselves. Project constraints, useful decisions and independent outcome verification may retain value, but their incremental benefit needs separate measurement.

## Fixed invariants
- Preserve all four mandatory phases and their approval gates. The user approved the source result and requested closeout on 2026-11-19; the required installation update remains a separate task under those gates.
- Preserve existing project guidance, active records, archives and installer behavior. Do not recreate root bootstrap staging.
- Keep canonical templates generic. Synchronize installed copies in the required follow-on task after source development closes out.
- Local-commit permission does not authorize publishing, rewriting history, discarding unrelated work, or treating committed work as reviewed.
- Retain both active task files and the three-file closeout archive; scale their contents to the task and avoid duplicating Git diffs or commit history. Verification guidance does not prescribe or restrict who performs review.
- Hooks, permissions and CI configuration are explanatory guidance only in this task. Do not install enforcement integrations. Recommendation 7 is guidance, with no new automation or mandatory checklist. Rigorous comparative evaluation remains separate.

## Goal
- Let agents leave reviewable, verified local commits and apply the workflow improvements selected in this planning review, retaining project-specific constraints, useful decisions and independently checkable outcomes.

## Milestones
- [x] M1 — Read owners and relevant history; inspect starting state; research primary sources and prepare a concrete policy proposal.
- [x] M1a — Record the user's dispositions: approve 1, 3, 4 and revised 5; retain mandatory phases; apply the portable guidance portion of 6; explain hooks and 7 without adding enforcement or automation.
- [x] M2 — Update the distributed commit policy and selected workflow guidance in separate coherent changes, verify and commit them.
- [x] M2a — Restore separate milestone and success-criteria checklists while retaining the consolidated template; align the walkthrough and README, verify and commit this review revision.
- [x] M2b — Retain Plan and verification for the implementation approach and checks, with progress recorded in the milestone and success-criteria checklists; align the example and README, verify and commit.
- [x] M3 — Present source implementation and recommendations for Phase 3 review; close out only after approval, identifying the fixed source and required installation follow-on.

## Success criteria
- [x] Canonical guidance explicitly authorizes local commits in Phases 2–4 within approved scope without requiring approval for each commit.
- [x] Policy directs committing coherent, verified changes as they are completed; relevant implementation, tests and docs belong together, with no arbitrary file-count threshold.
- [x] Policy preserves unrelated work and excludes it from commits, distinguishes local commits from publication, history rewriting and review approval, and leaves routine Git mechanics to the agent.
- [x] Canonical Phase 2 no longer prohibits `git commit` or assumes a human must make every commit; handoff reports actual commits and remaining changes.
- [x] Local-commit authorization adds no mandatory commit ledger or task-template fields; Git history already records the commits.
- [x] README and walkthrough agree with the canonical policy.
- [x] After review approval, the source closeout identifies the installation changes still required to fulfill the user's full request.
- [x] Existing installer regression tests pass; no installer/CLI behavior change or new dependency is introduced.
- [x] All four phases, planning/review approval gates, file preservation, significant-bug traceability and archival verification remain intact.
- [x] Remove the planning command cap, routine manual-compaction instructions and generic debugging recipe; preserve compact handoff information and task-appropriate verification.
- [x] Task templates retain separate milestone and success-criteria checklists and Plan and verification for the approach and checks; omit duplicate progress lists and unused investigation sections. Records preserve rationale, evidence and open questions rather than restating Git diffs.
- [x] Phase 3 checks observable outcomes against acceptance criteria, including verification limitations, without prescribing the number or type of reviewers.
- [x] Research covers OpenAI/Codex, Anthropic/Claude Code, and Google/Gemini CLI/Antigravity; sources and feature-status caveats are preserved in [memory](MEMORY.md).
- [x] Recommendations distinguish documented capabilities, empirical evidence and project-specific hypotheses; rigorous evaluation remains a separate task.
- [x] Each recommendation has an explicit disposition and the selected changes are reflected in this implementation plan.

## Relevant files (why)
- [Canonical guidance](../../../../templates/AGENTS_TEMPLATE.md) — owns the distributed authorization and Phase 2 behavior.
- [Installed guidance](../../../../AGENTS.md) — governs this task; the follow-on integration task will adopt the new policy while retaining repository-specific content.
- [Canonical task brief](../../../../templates/TASK_BRIEF_TEMPLATE.md) and [memory template](../../../../templates/MEMORY_TEMPLATE.md) — consolidate duplicate fields and make investigation detail optional while preserving useful evidence and status. Their installed copies change in the follow-on task.
- [README](../../../../README.md#how-it-works) — user-facing explanation of implementation and review.
- [Walkthrough](../../../example-walkthrough.md#2-implement-and-verify) — show one verified implementation/test/documentation change committed before review.
- [Update prompt](../../../../Update-prompt.md) and [Zero prompt](../../../../Agent-Zero-prompt.md) — retain separate bootstrap/update procedures and align references to revised Phase 3 verification.
- [Installer](../../../../install.py) and [tests](../../../../tests/test_install.py) — existing source-copy and preservation contracts; no implementation changes expected.

## Documentation impact
- First change: canonical guidance, README and walkthrough authorize and illustrate local commits. Second change: those files, both task templates and the two prompts implement the approved simplifications. The existing installed agreement governs this task's approval gates.
- Keep research evidence in task memory and the eventual closeout, with recommendations in the review response. No new permanent research document is needed.
- Installer, installed integration and historical archives remain unchanged during source development. Bootstrap checks, source provenance and the separate fixed-source update workflow remain intact.

## Implementation plan
1. After approval, add a compact local-commit policy applicable to Phases 2–4; update Phase 2's title, prohibited-command wording, change-set sequence and handoff requirements.
2. Update the README summary and walkthrough to reflect local commits. Use the existing task-record structures and Git history without adding mandatory commit fields.
3. Verify the source edit, inspect the staged change, and make the scoped local source-policy commit. The user's explicit requested authorization governs this change even while the old installed copy is awaiting synchronization.
4. Simplify source guidance: emphasize project-specific knowledge; remove the command cap, compaction ceremony and generic debugging recipe; state independent verification requirements without reviewer restrictions. Consolidate task-template fields and prohibit duplicating Git diffs. Align README, walkthrough and prompt references, retaining all phases and approval gates. Verify and commit this coherent workflow change separately.
5. Present source commits, verification and answers about hooks/reassessment for Phase 3 review. Archive only after approval, retaining the final source identity and required installation follow-on.
6. After source closeout, start the separate integration-update task under `Update-prompt.md`. Record the final source revision and hashes, keep those inputs fixed, and synchronize installed policy and task templates. The full user request remains pending until that update is complete.

## Local-commit policy

Place this under the shared working agreement, explicitly applying to Phases 2–4:

> Local commits within the approved task scope need no further approval. Commit coherent, verified changes as you complete them, keeping related code, tests and documentation together. Preserve unrelated work and exclude it from commits. Commits do not replace review; pushing, merging, rewriting history or discarding work requires explicit authorization.

Replace the Phase 2 no-history title and human-only commit handoff. Retain the mandatory phases and their approval gates as directed by the user.

## Small change sets (execution order)
1. Distributed local-commit policy and examples: `templates/AGENTS_TEMPLATE.md`, `README.md`, `docs/example-walkthrough.md`. Intended commit: `docs: authorize scoped local commits in the workflow`.
2. Approved workflow simplifications: all three canonical templates, README, walkthrough, Zero prompt and Update prompt. Intended commit: `docs: streamline guidance and strengthen outcome verification`.
3. Approved review revision: restore milestone and success-criteria checklists in the canonical task brief; align README and walkthrough without restoring overlapping execution lists. Intended commit: `docs: restore milestone and success criteria checklists`.
4. After review approval: sanitized source-task archive. Intended commit: `docs: close out local-commit policy and agent review`.

## Required follow-on installation task
- After this source-development task closes out, update `AGENTS.md` and affected installed task templates from the fixed source under the existing update procedure, including the selected workflow improvements as well as local-commit authorization.
- Verify complete shared-policy equality, both installed task-template comparisons, preservation of repository-specific content and unchanged source hashes. Commit the installation update separately.
- This is part of fulfilling the original request, not an optional improvement or a change to the previous task's decisions.

## Verification
- Each source change: inspect policy references and scoped diff; run `git diff --check` and `python3 -B -m unittest discover -s tests -v`. The second change alters all canonical templates and prompt references, warranting a new suite run.
- Final source review: verify local links, four phase headings and approval gates, retained installation/archival contracts, removal of command/compaction ceremony and stale debugging-loop references, and absence of reviewer restrictions. Confirm installer, installed copies and archives still match the starting revision.
- Follow-on installation task: compare the full region from the unique working-agreement heading through EOF; byte-compare both installed task templates; recheck fixed source SHA-256 hashes and the preserved repository-specific prefix.
- Before each commit: inspect `git status --short`, `git diff --cached --check` and `git diff --cached`; confirm only the intended change is staged. Inspect the resulting commit and remaining work afterward.
- Installer tests already check canonical-byte propagation and preservation in isolated targets. Do not add tests that only assert documentation wording; these tests do not prove agent compliance or workflow value.
- Repeat tests only if later changes or failures warrant it. Final handoff: compare complete task diff against starting revision and run `git status --short`.

## Risks / gotchas
- Permission alone does not specify when to commit. Retain the coherent, verified change boundary; routine Git mechanics do not need a distributed checklist.
- Commit authorization in prose does not override tool/sandbox permissions. If Git metadata writes are blocked, use the normal tool approval mechanism and report the exact limitation.
- Source development and installation remain separate tasks. Temporary differences between canonical and installed guidance are expected until the required integration update is complete.
- Current vendor documentation changes rapidly. Capability claims are not evidence that this workflow helps or hurts on this project's tasks.
- Automated compaction/checkpoints/private memory do not by themselves preserve team-visible decisions or produce reviewable project commits.

## Recommendation decisions

1. **Approved:** retain project-specific constraints, non-obvious command requirements, acceptance criteria and decision rationale; trim generic engineering instruction.
2. **Rejected:** retain the mandatory four-phase workflow and its approval gates.
3. **Approved:** remove the ten-command cap and mandatory `/compact` prompt; retain useful handoff information without manual context rituals.
4. **Approved, clarified 2026-11-13:** keep records proportionate and avoid duplicating Git diffs. Preserve separate milestone and success-criteria checklists and Plan and verification for the approach and checks; consolidate overlapping progress lists and omit unused investigation sections. Preserve required record files and closeout.
5. **Approved with revision:** strengthen verification of outcomes against acceptance criteria. Remove statements about other agents; do not restrict future review arrangements.
6. **Generally agreed; guidance requested:** keep detailed bootstrap/update procedures in their existing prompts and remove the generic debugging recipe from always-on policy. Explain optional Git/agent hooks, environment permissions and CI separately; no integration installation is authorized or needed for this change.
7. **Guidance only:** reassess instructions when models/tools change or recurring problems appear. No additional scheduled task, automation or mandatory review process is proposed. Formal evaluation remains a separate task.

## Decisions
- 2026-11-06 16:42 — Treat this as a commit-policy implementation plus a research/recommendation task; do not infer permission for a broad workflow rewrite or evaluation.
- 2026-11-06 16:42 — Use the existing planning gate for this task. Local commits become available during approved implementation; a commit does not close the review gate.
- 2026-11-06 16:42 — Initially proposed source development and installation in one task. Superseded by the 2026-11-09 clarification below.
- 2026-11-06 16:42 — No demonstrated implementation bug is being repaired; this changes an intentional authorization policy. The user's oversized-change observation is reported, not independently quantified.
- 2026-11-09 17:28 — Corrected the interpretation of the user's request after they questioned the exception wording. The requested policy change is local-commit authorization, applied to both templates and installation. Follow the existing separate-task sequence; the user did not request an exception to it.
- 2026-11-09 17:35 — Corrected the undefined timing implied by "Recommendations for later decisions." Review the recommendations in the current planning discussion and include selected improvements before source closeout and installation synchronization. This is a timing clarification, not approval of every recommendation; rigorous evaluation remains a separate task.
- 2026-11-09 20:25 — Shortened the proposed commit policy to authorization, coherent verified changes, preservation of unrelated work and separate approval boundaries. Removed routine Git instructions and mandatory commit-ID bookkeeping; local-commit authorization alone no longer requires task-template changes. The revised policy remains a proposal for review.
- 2026-11-09 20:34 — User approved recommendations 1, 3 and 4, retained mandatory phases, approved stronger verification with agent-related wording removed, and requested explanation rather than installation of hooks. Proceed with the authorized source changes; keep existing approval gates, record-file lifecycle and separate self-update task. Treat recommendation 7 as guidance without new machinery.
- 2026-11-09 20:56 America/New_York — Both source changes are committed and verified; source development is awaiting Phase 3 review. Installed guidance and task templates remain unchanged until approved source closeout and the separate integration task.
- 2026-11-09 20:56 America/New_York — User chose to retain the global Codex `git add` and `git commit` approvals they granted during this session. Verified persistence in personal rules; no repo-specific rule or broader permission change was installed. Runtime permissions and workflow authorization remain distinct.
- 2026-11-11 12:15 America/New_York — Phase 3 review reopened the task-brief structure: the user values separate milestone and success-criteria checklists for deliverables, correctness and resuming incomplete work in new sessions. Discuss the rationale and tradeoffs before deciding; no template revision or reversion has been requested. The current source retains acceptance checkboxes but replaces the explicit milestone checklist with a numbered plan.
- 2026-11-13 13:32 America/New_York — User authorized restoring Milestones and Success criteria checklists while retaining the changes that eliminate redundant planning records. Milestones will own execution order and any necessary implementation detail; verification describes checks separately. Apply this bounded review revision to canonical sources and their example; installed copies remain the required follow-on task after source closeout.
- 2026-11-13 13:34 America/New_York — Checklist revision implemented, verified and committed. Source changes remain in Phase 3 awaiting review; updated verification and source identity are in memory.
- 2026-11-13 13:44 America/New_York — User authorized retaining Plan and verification. This supersedes placing implementation detail in Milestones: keep the approach, dependencies and checks in the plan, refer to milestone IDs where useful, and record progress in the two checklists. Update the canonical template, illustrative brief and README description; no change to the separate installation-update sequence.
- 2026-11-13 13:45 America/New_York — Plan-section revision implemented, verified and committed; source changes return to Phase 3 awaiting review. Verification and source identity are updated in memory.
- 2026-11-19 15:25 America/New_York — User requested closeout, approving the reviewed source result and authorizing Phase 4. Reconcile affected owners, preserve verification and source identity, sanitize and archive the task records, verify archival, then commit the closeout. The installation update remains the required separate follow-on task.
- 2026-11-19 15:29 America/New_York — Documentation reconciliation and archival verification passed: all three archive files exist, both active records are absent, all 24 local links/anchors resolve and all six source hashes match. Mark this source-development task complete; carry the installation update and separate evaluation forward explicitly.

## Next steps
1. Complete the required separate installation-update task from the approved fixed source so subsequent sessions here inherit the new workflow authorization.
2. In the separately requested evaluation task, measure Socrates Loop's value against the bare agent/model under comparable conditions.

## Deferred work note
- Rigorous comparison of Socrates Loop with the bare agent/model, including repeated trials and outcome/cost measurement, is a separate task requested by the user.
- Hook installation, runtime permission changes and CI enforcement are outside this documentation change; revisit if a concrete recurring failure warrants one. No archive-structure change or automatic instruction-review schedule is planned.
