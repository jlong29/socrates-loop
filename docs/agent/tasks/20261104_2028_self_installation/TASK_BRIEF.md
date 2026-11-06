# TASK BRIEF

Historical task record. Paths and commands are relative to the repository root unless stated otherwise; references to staging and `.agent/` describe their historical roles. See [CLOSEOUT.md](CLOSEOUT.md) and [MEMORY.md](MEMORY.md) for outcomes and evidence.

## Task
Separate reusable templates from installed integrations, bootstrap this repository, and strengthen bootstrap command verification and provenance based on external reviews.

## Status
- **Phase:** Phase 4
- **State:** complete
- **Last updated:** 2026-11-05T15:23-05:00

## Context lineage
- **Epoch / initiative:** self-installation
- **History scope:** no internal archive existed at planning; later external bootstrap/update closeouts informed review, as listed in CLOSEOUT.md.
- **Closeouts reviewed:** none during initial planning; external review lineage is preserved in CLOSEOUT.md.

## Why this update
Root AGENTS_TEMPLATE.md is both a canonical source input and disposable bootstrap staging. Self-bootstrap closeout removes an input required for future installations.

## Fixed invariants (do not change)
- Preserve the four-phase policy, approval gates, existing guidance, active task records and history.
- Preserve external destination paths, CLI syntax, preflight conflict/type/symlink checks and non-mutating previews.
- Source templates remain generic and reusable after self-bootstrap.
- No git history operations or closeout before the appropriate approval.

## Goal
This checkout can install into itself, complete bootstrap and still install into external repositories.

## Milestones
- [x] Review repository and establish baseline.
- [x] Separate source assets, update installer and add lifecycle regression coverage.
- [x] Reconcile instructions and instantiate this repository's integration.
- [x] User approved review; staging cleanup, archival and final verification completed.

## Success criteria
- [x] Canonical templates live in templates/ and are never customized or removed by bootstrap.
- [x] External targets retain root AGENTS_TEMPLATE.md staging and docs/agent/ task templates.
- [x] Self-installation uses the same mapping without a special mode.
- [x] After simulated self-bootstrap cleanup, the checkout still installs into a fresh external target; source bytes remain intact.
- [x] Root AGENTS.md accurately describes this project and preserves shared policy.
- [x] Update guidance supports fixed source identity when source and target are the same checkout.
- [x] Existing preservation, conflicts, symlinks, repeat-install and dry-run checks pass.

## Relevant files (why)
- install.py: source/destination mapping.
- templates/AGENTS_TEMPLATE.md, templates/TASK_BRIEF_TEMPLATE.md, templates/MEMORY_TEMPLATE.md: canonical sources, moved from the root during implementation.
- tests/test_install.py: fixtures and lifecycle regressions.
- Agent-Zero-prompt.md: copy/customize/cleanup contract.
- Update-prompt.md: source paths, provenance and self-update sequencing.
- README.md: authoritative setup, repository map and development instructions.
- AGENTS.md, docs/agent/*_TEMPLATE.md, .gitignore: proposed integration outputs.

## Documentation impact
- README.md repository contents/setup/getting started/update sections: distinguish source and installed assets; document python3 install.py . and self-updates.
- Agent-Zero-prompt.md: create guidance from the staged copy; remove only staging at closeout, preserving source templates and existing guidance.
- templates/AGENTS_TEMPLATE.md: clarify instantiation above the shared policy boundary. Root AGENTS.md owns this checkout's concrete guidance.
- Update-prompt.md: use new source paths and explicitly handle legacy root-layout sources; never guess between ambiguous layouts. Freeze source inputs during updates, including when source equals target.
- docs/example-walkthrough.md: reviewed; no direct source-template paths, so no change expected unless the workflow changes.

## Implementation plan
1. Move the three canonical templates into templates/; update installer input mappings while retaining target paths.
2. Adapt fixtures; add self-install, self-install dry-run/conflict and self-bootstrap-cleanup-to-external-install tests. Verify source preservation.
3. Reconcile README, Zero and update prompts. Document source-template development and subsequent integration updates as separate tasks using fixed source identity.
4. Run the installer against this checkout, preserving these active records as continuation of this task. Instantiate root AGENTS.md using actual files, owners and commands.
5. Compare policy and installed templates against canonical sources, run tests, inspect diff and stop for review. Retain staging until approved closeout.
6. After approval, remove only staged root AGENTS_TEMPLATE.md, verify the checkout remains usable as a source, and archive task records normally.

## Small change sets (execution order)
1. Template layout, installer mapping and regression tests.
2. Lifecycle documentation and this repository's integration.
3. Approved closeout cleanup and archival.

## Verification
- Fast/full: python3 -B -m unittest discover -s tests -v
- Preview: python3 -B install.py . --dry-run
- Targeted: isolated source checkout installs into itself, simulated bootstrap creates AGENTS.md and removes staging, then installs into an external target; compare canonical bytes and preserved user content.
- Compare AGENTS.md policy from the unique working-agreement heading to templates/AGENTS_TEMPLATE.md; compare installed task templates with canonical files.
- git diff --check; git diff --stat; git status --short; review affected links and instructions.

## Risks / gotchas
- Source moves affect update consumers: describe both new and legacy source layouts explicitly.
- Canonical and installed copies intentionally coexist; synchronize through normal integration updates.
- Initial setup currently recreates staging after bootstrap; retain and explain this behavior instead of implicitly making installation an updater.
- At initial planning, no .gitignore existed; self-installation subsequently added the ignore rule for active records.
- At initial planning, installed docs/agent/ templates were absent; this task was initialized from equivalent root sources before self-installation created the installed copies.
- Automated lifecycle tests simulate agent actions; manually review repository-specific guidance.

## Decisions
- Separate source and destination paths instead of adding repository-name detection or conditional source-deletion exceptions.
- Keep external target layout compatible.
- Finish source development before starting a separate integration-update task; preserve fixed template inputs throughout that update.

## Next steps
1. No work remains in this completed task.
2. Optional successor evaluation and unresolved historical-impact work are recorded in CLOSEOUT.md.

## Deferred work note
No packaging system, automatic policy merge, installation database or broad installer redesign.

## Execution notes
- 2026-11-04T20:33-05:00 — User approved Phase 2; implementing the recorded plan.

- 2026-11-04T20:35-05:00 — Implementation and verification complete; entered Phase 3. All 16 regression tests pass, self-install dry run is unchanged, policy equals the original shared policy, installed templates equal canonical inputs, local documentation links resolve, and git diff --check passes. Root staging intentionally remains until approved closeout.

## Initial implementation handoff (historical)
- Source identity: base commit 5aebda334b1e32a9fc6e94242c95e1a148e9d1f7 plus this uncommitted refactor. Exact source hashes are recorded in task memory.
- No approved-plan deviations. No source policy changes below the working-agreement boundary.
- Pending work is review and approved closeout; no commits made.

- 2026-11-04T21:09-05:00 — Reviewed user-provided external bootstrap in AFineCppRepo against source revision 764a3d8. Exact installed template/policy matches and repository adaptation checks passed; no setup defects found. External task awaits Phase 3 approval and closeout. This task remains in Phase 3.

## Approved review follow-up — 2026-11-05T11:33-05:00
The user requested the smallest changes fully integrating the recommendations from external bootstrap comparisons. Continue this task without replacing its existing records.

### Scope and execution
1. Add bounded command-verification and evidence acceptance checks to the canonical template's bootstrap instructions. Reuse existing documentation ownership and significant-bug policies; preserve the shared policy suffix.
2. Make both Zero prompts require the bootstrap checks and retain source provenance in the brief/closeout. Print template hashes, source prompt hash, source revision when available and relevant source-input state with each copyable prompt. No installation database or new target artifacts.
3. Add a small evaluation fixture with a failure-masking wrapper, incomplete README prerequisites and a correct-wrapper control; document fresh-session evaluation and add deterministic fixture-behavior tests. Do not claim that fixture tests measure LLM reliability.
4. Synchronize this checkout's still-active root bootstrap staging, update affected README instructions, run installer/fixture regression tests and policy/link/whitespace checks. Return to Phase 3 review, leaving closeout pending.

### Acceptance criteria
- [x] Each printed prompt carries accurate hashes of the bytes supplied to the target and the source prompt, with source-only Git identity or an explicit unavailable value.
- [x] Missing Git/source metadata does not prevent installation; dry runs and existing preservation/preflight behavior remain intact.
- [x] Bootstrap instructions require evidence for recommended command prerequisites, scope and failure reporting, distinguish inspection from execution, and route known defects to existing owners and task records.
- [x] Both evaluation cases expose the expected exit behavior under deliberate failure and pass with the documented prerequisite; repeated agent evaluation is documented separately from unit tests.
- [x] Shared policy and installed task-record templates are unchanged; canonical/staged guidance agree.

### Verification
- python3 -B -m unittest discover -s tests -v
- python3 -B install.py . --dry-run
- Direct policy/template comparisons, local documentation link review, git diff --check and final scope review.

### Decisions
- The user explicitly authorized this refinement; no additional implementation approval is needed.
- Keep provenance in printed prompts and existing task archives, not in persistent installer metadata.
- Source revision describes the installer checkout, never the target/caller or an unrelated enclosing checkout. Input state is collected before self-installation writes.

- 2026-11-05T11:41-05:00 — Review follow-up implemented and verified. All 20 tests pass, self-install preview is unchanged, source provenance output was inspected from a temporary installation, policy/task templates match the prior revision, and link/whitespace checks pass. Ready for Phase 3 review; no closeout or Git history operations performed. Repeated LLM bootstrap evaluations remain unrun; the fixture and scoring procedure are ready.

- 2026-11-05T14:18-05:00 — Read-only review of fresh external bootstrap on agentIntRedo2 confirmed current input/policy equality and adoption of command evidence/bug follow-ups with existing documentation owners. Target remains Phase 3; source provenance was unavailable to that agent and is a handoff limitation, not a content mismatch. This source task also remains in Phase 3.

- 2026-11-05T14:47-05:00 — Read-only audit confirmed the revised external bootstrap completed Phase 4 correctly, retaining both defect follow-ups and explicit provenance limits. Archive cleanup, policy/templates, 13 fingerprints, 36 links and scope checks passed. No source-task phase transition or target changes.

## Closeout authorization — 2026-11-05T15:18-05:00
- The user requested closeout of this Socrates Loop task, approving the Phase 3 result and authorizing staging cleanup and archival. Entered Phase 4 / in progress.
- Archive destination: docs/agent/tasks/20261104_2028_self_installation/.
- Product changes are already present in commits 764a3d8 and da04d38, created outside this agent's work. The checkout is clean at closeout start. This phase will remove only root staging and add the sanitized archive; no Git history operations.

- 2026-11-05T15:22-05:00 — Removed only root bootstrap staging after verifying equality to its canonical source. All 20 regression tests passed; an actual temporary external install succeeded afterward with exact template hashes and source identity. Self-install preview would recreate staging, as documented, without writing it. All 20 retained tracked files match the closeout baseline. Archived state remains in progress until final checks pass.

- 2026-11-05T15:23-05:00 — Final archival checks passed while this brief was still in progress: exactly three archive records, no active records or root staging, unchanged 20 retained tracked files, exact policy/template comparisons, 17 working archive links/anchors, sanitization/whitespace checks, and expected Git scope with unchanged index. Marked archived Phase 4 complete after verification.
