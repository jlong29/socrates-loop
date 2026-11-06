# MEMORY

Historical investigation record. Paths and commands are repository-relative unless stated otherwise. Earlier observations describe the repository at their recorded stage; removed staging and ignored logs are historical references. See [CLOSEOUT.md](CLOSEOUT.md) and [TASK_BRIEF.md](TASK_BRIEF.md).

**Task:** self-installation source separation
**Last updated:** 2026-11-05T15:23-05:00

## Repro commands
- python3 -B install.py . --dry-run

## Initial hypotheses + evidence (before refactor)
- install.py reads root source templates. Self-install treats root AGENTS_TEMPLATE.md as unchanged.
- Both Zero prompts explicitly remove that root template at closeout. They do not literally prescribe a rename; source loss is nevertheless the same concern.
- No AGENTS.md, .gitignore, docs/agent/ templates, archive or active task records existed before planning.
- Reviewed installer, tests, all Markdown workflow/template documents and walkthrough. Image asset and license are outside behavioral scope.

## Initial gotchas (subsequently reconciled)
- Update-prompt.md assumes root source paths and an unchanged source checkout during integration updates; self-update sequencing needs clarification.
- Existing tests exercise external installations but not self-bootstrap cleanup followed by external installation.
- Initialized active records from root templates because installed paths are absent.

## Bug impact traceability
### BUG-001 — Self-bootstrap removes a distribution input
- Impact: following the initial Zero instructions to closeout in the source checkout removes AGENTS_TEMPLATE.md, required by subsequent installer invocations. Established by inspection; destructive cleanup was not run.
- Root cause: source and disposable staging share a path when source equals target.
- Fix location: templates/ layout, install.py source mapping, both Zero prompts and canonical template instantiation instructions; delivered in commit 764a3d8210216faa4e834bb1bac5ad5805b91463.
- Regression evidence: test_self_bootstrap_preserves_source_for_external_installation passes: self-install, repeat install, simulated cleanup, external install, source byte/mtime preservation and user-content preservation.
- Affected versions/artifacts: earliest and latest directly inspected commit: 5aebda334b1e32a9fc6e94242c95e1a148e9d1f7. Earlier history and actual affected installations unknown.
- Follow-up: historical impact not quantified; earliest introduction and actual affected installations remain unknown. No historical audit was in scope.

## Verification run
- python3 -B -m unittest discover -s tests -v: 13 tests passed.
- python3 -B install.py . --dry-run: succeeds; would add installed task templates and ignore rule, leaves source AGENTS_TEMPLATE.md unchanged.
- Initial git status: clean. git check-ignore found no ignore rule for active records.
- Only Phase 1 task records written; no product changes.

## Phase 2 verification — 2026-11-04T20:35-05:00
- python3 -B -m unittest discover -s tests -v: all 16 tests passed after code changes and again after final product/doc changes.
- python3 -B install.py .: installed staging, task templates and ignore rule, preserving active task records.
- python3 -B install.py . --dry-run: all four installation files unchanged after self-installation.
- Direct comparisons: AGENTS.md and staged template policy equal canonical policy and original HEAD policy exactly; installed task templates equal canonical files and original HEAD inputs.
- Local Markdown links/anchors in README and prompts resolve. AGENTS.md mappings manually reviewed against actual files and test commands; no invented runtime/configuration sections.
- git diff --check: passed. git check-ignore confirms both active task records are ignored.
- Diff reviewed: source mapping changed by one expression, generic inputs moved, three lifecycle regression tests added, owning lifecycle docs updated, integration outputs created. Root staging remains pending review approval.

## Documentation reconciliation (implementation handoff)
- README: source paths, self-installation, repeat setup behavior and self-update sequencing updated.
- Zero prompts and canonical template preamble: explicit staged-copy ownership and cleanup.
- Update prompt: new/legacy source layouts and fixed self-update source inputs.
- AGENTS.md: actual repository guidance, owners, contracts and unchanged shared policy.
- Walkthrough: no change needed; uses README links and normal phase flow, both still valid.
- Final reconciliation and archival remain Phase 4 work after user approval.

## Source identity at review
Base revision: 5aebda334b1e32a9fc6e94242c95e1a148e9d1f7, plus approved uncommitted source-layout and documentation edits. SHA-256:

```text
0bda33e1f681fe1550f3f302b94c2e641f87a1e9184c83c1aee6fbbce1b5e6d7  templates/AGENTS_TEMPLATE.md
732b0cceb7ec1e59cb0e5ff5e27e54d1b1c7a36e35c779591e2fb565667ec5c9  templates/TASK_BRIEF_TEMPLATE.md
1fa568779d7bce0780be78a0bfedac2ec16df6e7af85c8bbd1427c30ab2dc267  templates/MEMORY_TEMPLATE.md
de241d459f46029695bb11e0a4a98aba18655f92f37d93f9fc712ef3df10b6a9  README.md
691d4025b065223d6c4fe83d7ab5fda7737e0dc315d315752f8eea6607c716dd  Agent-Zero-prompt.md
d078f441c82b79ffc11671103a0b99d6ce85d3ed04a26e7f9b656394804d0145  Update-prompt.md
```

## External bootstrap review — 2026-11-04T21:09-05:00
- User requested inspection of AFineCppRepo bootstrap as Phase 3 validation. Read-only inspection of that target; no target files changed.
- Compared against current source revision 764a3d8210216faa4e834bb1bac5ad5805b91463: staged guidance and both installed task templates match canonical bytes; generated AGENTS.md policy suffix matches exactly.
- Repository-specific guidance and README clarifications agree with CMake, build/dependency scripts, module READMEs and fixture-handling source. Local links/anchors resolve; no pre-policy placeholders remain.
- Target task brief is Phase 3 / awaiting review and records Phase 2 approval. Staging and active records remain appropriately; closeout has not occurred. Approval history was assessed from task records, not an independent conversation transcript.
- Recomputed saved baseline hashes: only approved README differs among 35 files, with remaining 34 unchanged. Both active records and logs are ignored. Tracked and untracked guidance whitespace checks passed.
- No installation/setup defects found through Phase 2. Runtime compilation was outside this documentation review; Phase 4 cleanup/archival remains pending target review approval.

## External closeout review — 2026-11-04T21:12-05:00
- Read AFineCppRepo bootstrap CLOSEOUT.md and archived brief/memory after user-authorized closeout. No target files modified.
- Independently verified all three archive files, absence of both active records and root staging, complete status, unchanged shared policy and recorded hash, canonical task-template equality, 33 protected baseline files, 33 local links/anchors, whitespace and empty Git index diff. Bounded archive scan found no private URLs, machine-specific home paths or obvious credential markers.
- Closeout records outcomes, decisions, contracts, command disposition, owner reconciliation, verification limitations and context lineage; evidence survives independently of ignored logs. No blocking defects found.
- Optional improvement: record upstream Socrates Loop revision and full installed-template hashes in future bootstrap closeouts; current bootstrap policy does not require source revision provenance. Target bootstrap is complete; source refactor task remains in Phase 3 pending its own review/closeout approval.

## External branch comparison — 2026-11-04T21:20-05:00
- Requested agentIntUd vs agentIntRepo; no agentIntRepo local or remote-tracking ref exists. Asked whether agentIntRedo was intended; compared agentIntUd (a500dd2) with agentIntRedo (2e28261), the reviewed fresh bootstrap. No target checkout changes or file edits.
- Both branches: policy suffix and installed templates equal current canonical bytes; staging/active records absent from tracked trees; completed archive briefs; local links resolve (28 Ud / 33 Redo). Application/build/CI trees identical.
- Ud strengths: explicit generated CTest wrapper failure-status warning, direct per-module default tests, test coverage limitations and module-option distinctions, stable BUG-001 successor work, source revision plus input hashes in update archive.
- Redo strengths: reconciled README requirements/CPack caveats, fewer maintained documentation owners, smaller always-on prefix (122 vs 149 lines), clean complete bootstrap archive.
- Decisive gap: Redo default test command uses the generated wrapper and says inspect both summaries but omits the explicit false-success mechanism and bug follow-up. Bash simulation of the shared generator structure with mocked ctest returning 7 exits 0; no actual CTest or C++ build run. Ud documents the mechanism accurately.
- Judgement: Ud has the stronger final integration for reliable agent verification/continuity; Redo has cleaner documentation structure. This is not a controlled bootstrap comparison: Ud is bootstrap plus update; Redo follows the user-directed removal commit d0fdd92. Do not attribute removed earlier archives to unauthorized deletion by the Redo bootstrap agent.
- Prior positive Redo review covered installation/closeout correctness but missed this diagnostic-coverage gap. Future improvement could combine Redo owner/README structure with Ud warning/direct tests and provenance without recreating all old documents.

## Bootstrap review improvements — 2026-11-05T11:41-05:00
- Implemented the user-authorized refinement on base revision 764a3d8210216faa4e834bb1bac5ad5805b91463. Existing active task records preserved; shared working agreement untouched.
- Canonical bootstrap instructions now require bounded command evidence (prerequisites, directory/environment, discovery and failure reporting), existing-owner reconciliation, existing bug traceability for observed out-of-scope defects, input provenance and explicit review limitations. These instructions are omitted from finalized AGENTS.md.
- Both Zero prompts invoke those checks. Installer embeds identical provenance in each copyable prompt: source revision or unavailable, relevant input modification state, raw installed-file hashes and raw source-prompt hash. Source identity is sampled before self-installation writes, requires the checkout root rather than an enclosing repository, and is optional when Git is absent. No additional target files or installation database.
- Added tiny default/control bootstrap fixtures: required EXAMPLE_VALUE=42 is absent from the initial README; default shell wrapper masks failure, control uses exec. README owns trial setup and review criteria; agents get only the fixture, without evaluator hints.
- python3 -B -m unittest discover -s tests -v: all 20 tests passed. New coverage checks per-prompt provenance, missing Git, correct source attribution, clean/modified/untracked/enclosing-root cases, and default/control/direct command outcomes under failure and success. Existing preservation, conflicts, symlinks, previews, repeat and self-bootstrap tests pass.
- python3 -B install.py . --dry-run: all installation files unchanged.
- Temporary installation output inspected: source revision 764a3d8 with modified/untracked source inputs, correct raw template/prompt SHA-256 values in each prompt. Preview log retained only as supplementary evidence; conclusions and hashes are here.
- Direct byte comparisons: canonical and staged guidance equal; shared policy equal to HEAD and installed AGENTS.md; both task-record templates unchanged and equal to installed copies.
- Local Markdown links/anchors and whitespace checks passed, including new fixture files. git diff --check passed. No target-repository writes, commits or source-code repair in AFineCppRepo.
- Documentation reconciliation: canonical/staged bootstrap instructions, both Zero prompts and README updated. Installed AGENTS.md, task templates, Update-prompt.md and walkthrough require no changes: shared policy/record formats/update workflow remain unchanged, and walkthrough routes through README setup.
- No repeated LLM evaluations were run, so no measured reliability improvement is claimed. Fixture behavior is deterministic and verified; semantic bootstrap quality still requires the documented fresh-session trials.
- Phase 3 review and authorized closeout of this source task remain pending.

### Refined source identity (SHA-256)
- install.py: `b18c40a54ed7a68f18a9da602aaf69c8978c60e6966426d8a56f3659552ced97`
- templates/AGENTS_TEMPLATE.md: `6aab48fbeed64551143e435716f717f6bca0f2016044915278e61a02c6ce012d`
- Agent-Zero-prompt.md: `8a0a0de1cf0a0911affb07da3bab9ec7b7574ccb15099726bd703903be5a6941`
- README.md: `4b0f216532f56d2d64deaa1adc8922528fa60a99d6e576f8c666739c98aa00a3`

## External bootstrap after acceptance-check changes — 2026-11-05T14:18-05:00
- Reviewed AFineCppRepo agentIntRedo2 at target baseline b74fcbcd52520a0e4192f4476e3f82b5212adff7, currently Phase 3 / awaiting review. Target inspection was read-only; no C++ build/test reruns performed.
- Source reference for this comparison: current Socrates Loop HEAD da04d38a548be132e10ef252b9352c5f3e564106, clean tracked state. All three installed inputs match canonical bytes and their measured hashes in the target task brief; shared AGENTS policy equals canonical policy exactly. These checks establish content equality, not independently observed install-time source identity.
- New bootstrap instructions are reflected in the target brief, excluded from finalized guidance. README/AGENTS use direct build and test commands with proper failure propagation and zero-test protection; prerequisites, fixture environment, discovery scope and older-CTest fallback are explicit. Both command blocks agree, Bash syntax and 17 local links/anchors pass, and recorded source fingerprints match.
- Target records BUG-001 wrapper false-success behavior and BUG-002 missing Eigen provisioning with known affected source, evidence, limits and successor repairs. Synthetic wrapper probe log confirms four wrappers returned 0 after stub commands returned 23. Retained CTest LastTest logs show all four tests passed. Target memory reports direct configure/build/app and deliberate missing-fixture/empty-discovery checks, explicitly separating executed/source-only/unverified areas.
- No runtime/build/CI source changes; installer ignore-rule addition remains accounted for. Active records/staging correctly remain for review. No extra diagnostics/results manuals; README owns the procedures.
- Provenance handoff limitation: target records no supplied installer provenance; upstream revision/input state/prompt hash remain explicitly unavailable. This follows the static-prompt fallback; current content was independently confirmed here. Whether the full printed block was supplied is not established by repository records.
- Assessment: correct installation and stronger setup through Phase 2, addressing both prior-branch weaknesses in this observed run. No bootstrap-blocking defect found. Closeout and carrying bug/provenance evidence into its archive still require target review approval. No general reliability claim inferred from this one run.

## External revised-bootstrap closeout review — 2026-11-05T14:47-05:00
- Read AFineCppRepo archive docs/agent/tasks/20261105_1150_bootstrap_agents/ after its agent completed Phase 4. No target writes or runtime test reruns.
- Independent checks passed: exactly three archive records, both active records/root staging absent, brief Phase 4/complete with checked acceptance criteria, unchanged shared policy and policy hash, canonical installed task-template equality, all 13 retained deliverable/template/source/guidance fingerprints, 36 local links/anchors including 19 archived, command agreement, whitespace and bounded sanitization scan.
- git diff --check passed; Git index unchanged; tracked modifications remain only README and the installer-origin .gitignore addition. No runtime/build/CI changes.
- Closeout preserves both BUG-001 and BUG-002 with causes, deferred fix sites, measured probe scope, known affected source, unknown historical impact and successor tasks. It separates synthetic failure probes, actual four-test success and unverified clean-machine/standalone/older-tool environments. Essential evidence is archived, not dependent on ignored logs.
- Missing upstream source revision/input state/prompt hash remains explicitly unavailable, consistent with the input handoff limitation observed before closeout. Installed hashes and policy still match current Socrates Loop source; no provenance claim was invented.
- Assessment: complete, high-quality closeout with no blocking defects. The 110-line summary is detailed but supports future planning without loading the 200-line brief or 108-line memory. Target bootstrap is complete; this source task remains Phase 3 pending its own approval.

## Approved source-task closeout — 2026-11-05T15:22-05:00
- User explicitly requested closeout; active brief entered Phase 4/in progress before cleanup. Implementation is recorded in commits 764a3d8 and da04d38; both were already present at closeout start. No Git history operation performed by this agent.
- Before removal, root AGENTS_TEMPLATE.md equaled templates/AGENTS_TEMPLATE.md exactly; installed policy equaled its canonical suffix and both installed task templates equaled source bytes. Removed only root staging.
- python3 -B -m unittest discover -s tests -v: all 20 tests passed after actual staging removal.
- A one-off temporary external install using the live checkout passed: all three outputs equal canonical bytes, ignore/log setup correct, both printed prompts carry the expected hashes and source revision da04d38a548be132e10ef252b9352c5f3e564106 with clean source inputs. The source checkout did not recreate staging.
- python3 -B install.py . --dry-run: would create root AGENTS_TEMPLATE.md; both installed task templates and .gitignore unchanged. No files written. This is the documented initial-setup behavior after closeout, not an integration update.
- SHA-256 comparison against the clean closeout-start baseline confirmed all 20 other tracked files unchanged. git diff --check passed. Supplemental baseline is ignored; these conclusions and final source identity are retained in the archive.
- Reviewed all affected owners: README, Zero/update prompts and canonical template instructions agree with final behavior. Installed AGENTS.md and docs/agent task templates agree with canonical policy/structures. Walkthrough still routes through current README instructions. No additional maintained-document edits required at closeout.
- Canonical templates remain reusable; active records are being moved to the archive with repaired navigation and historical path interpretation. The final archive check and completion marker follow separately.

- 2026-11-05T15:23-05:00 — Final archive verification passed: exactly three archive records; both active records/root staging absent; all 20 retained tracked files unchanged; policy and installed templates equal canonical sources; 17 local archive links/anchors resolve; no sensitive URL/home-path/credential markers found; whitespace passes; memory remains under 200 lines. Git scope is only the authorized staging deletion and this archive; index unchanged. Archived brief marked complete only afterward.
