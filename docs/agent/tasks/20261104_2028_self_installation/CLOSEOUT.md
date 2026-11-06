# Closeout — Self-installation and bootstrap verification

- **Task:** `20261104_2028_self_installation`
- **State:** complete.
- **Last updated:** 2026-11-05T15:23-05:00
- **Approval:** the user approved the initial implementation plan, explicitly authorized the bootstrap-verification refinement, and then requested closeout of this task.
- **Supporting records:** [task brief](TASK_BRIEF.md) and [memory](MEMORY.md). Paths below are repository-relative; external review references identify another repository and are historical evidence.

## Outcome and decisions

Separated reusable distribution sources under [templates/](../../../../templates/AGENTS_TEMPLATE.md) from installed guidance and task templates. The same [installer](../../../../install.py) now supports this checkout and external targets without a self-installation special case. This repository has its own [AGENTS.md](../../../../AGENTS.md), installed task templates, and ignored active-task workspace. Approved closeout removed only root bootstrap staging; canonical sources remain intact and usable for subsequent installations.

External bootstrap comparisons informed a second small change: bounded evidence checks for recommended build/test commands, documentation reconciliation using existing owners, and source provenance carried with each printed Zero prompt. A faulty test-wrapper fixture and a correct control support repeatable evaluation. These checks belong to bootstrap instructions and task records; the shared working agreement is unchanged.

- Preserve external destination paths and CLI syntax; no new dependency, self-install mode or installation-state database.
- Keep development of source templates and subsequent integration updates as separate tasks with fixed source inputs. The update prompt distinguishes current and legacy source layouts.
- Record observed significant defects and unverified assumptions without expanding bootstrap into a general code audit. Documentation owners retain procedures; closeouts retain evidence and follow-ups.
- Prefer concrete command/failure evidence over textual policy equality alone. The first external review missed a wrapper hazard later exposed by branch comparison; that gap motivated the new checklist.

## Source identity and invariants

Initial source revision: `5aebda334b1e32a9fc6e94242c95e1a148e9d1f7`. Implementation was already recorded in `764a3d8210216faa4e834bb1bac5ad5805b91463` (source separation) and `da04d38a548be132e10ef252b9352c5f3e564106` (bootstrap checks/provenance) at closeout start. The latter is the final product reference; closeout changes only root staging and this archive.

Final canonical SHA-256 values, also identifying the removed staging input and retained installed task-template bytes:

| Canonical source | SHA-256 |
|---|---|
| `templates/AGENTS_TEMPLATE.md` | `6aab48fbeed64551143e435716f717f6bca0f2016044915278e61a02c6ce012d` |
| `templates/TASK_BRIEF_TEMPLATE.md` | `732b0cceb7ec1e59cb0e5ff5e27e54d1b1c7a36e35c779591e2fb565667ec5c9` |
| `templates/MEMORY_TEMPLATE.md` | `1fa568779d7bce0780be78a0bfedac2ec16df6e7af85c8bbd1427c30ab2dc267` |

Shared policy, from the actual working-agreement heading through EOF: 10903 bytes, SHA-256 `68055c1d137f6a17a91641d9908ffbe93fcf28712b051c639b0f8a1bcbabc5e9`. Installed guidance matches exactly. Earlier source snapshots and prompt/installer hashes are preserved in memory; source content was intentionally changed during the approved development task.

## Verification and command behavior

- `python3 -B -m unittest discover -s tests -v`: **20 tests passed after root staging was removed**. Coverage includes self-bootstrap followed by external installation, preservation/conflicts/symlinks, non-mutating dry runs, repeat setup, source provenance and missing Git, plus faulty/control wrapper behavior.
- A temporary external installation from the live checkout succeeded after cleanup: all three files matched canonical bytes, workspace/ignore setup was correct, and both printed prompts retained source revision and hashes. No staging was recreated in the source checkout.
- `python3 -B install.py . --dry-run`: would recreate root staging, with installed task templates and `.gitignore` unchanged; it wrote nothing. Use the update workflow for an existing integration rather than rerunning initial setup.
- Before staging removal, verified its full canonical equality; installed policy and both task templates remain exact matches. All **20 retained tracked files** matched the closeout-start fingerprints.
- `git diff --check` passed. Final archival, relative-reference and sanitization checks are recorded below after completion.
- CLI flags are unchanged. Initial setup now reads `templates/` and prints source provenance inside each prompt. Self-install uses `python3 install.py .`; [README](../../../../README.md#setup) owns procedures and [bootstrap evaluation](../../../../README.md#bootstrap-evaluation) owns the fixture/trial instructions.

## BUG-001 — Self-bootstrap removed a distribution input

- **Root cause / impact:** root `AGENTS_TEMPLATE.md` was both the canonical installer input and the disposable bootstrap file. Following the original closeout instructions in the source checkout removed a file needed by later installs.
- **Fix:** move canonical inputs to `templates/`, read them there in `install.py`, and explicitly limit Zero cleanup to root staging. Delivered in `764a3d8`.
- **Regression evidence:** the self-bootstrap lifecycle test verifies installation, simulated staging cleanup, subsequent external installation and source preservation. Actual source staging removal followed by a successful external install was also verified at this closeout.
- **Affected bounds:** earliest/latest directly inspected affected source was `5aebda334b1e32a9fc6e94242c95e1a148e9d1f7`. Earlier introduction and actual affected installations are unknown; no production impact count is inferred from the fix.
- **Follow-up:** historical impact analysis remains unresolved and was outside scope; investigate if affected-installation evidence becomes available. No known current lifecycle defect remains.

## External review findings and limitations

The earlier updated integration preserved a useful test-wrapper failure warning; the fresh bootstrap had cleaner documentation ownership but missed that warning. Their initial context differed, so the comparison did not isolate model randomness. The revised fresh bootstrap subsequently documented wrapper and Eigen-provisioning defects, supplied direct verification commands, retained four-test success and controlled failure evidence, and closed out correctly with both follow-ups. Its archive was independently checked for cleanup, 13 fingerprints, 36 links, policy equality and retained evidence.

These are observations from user-run external sessions, not a controlled repeated evaluation. No measured reliability improvement is claimed. The external agent reported that no printed provenance block was supplied; it retained measured hashes and explicit unavailable upstream fields. This review confirmed content equality, not independently observed install-time source identity. Always include the printed provenance when transferring a prompt.

External defects belong to their own task namespace: AFineCppRepo bootstrap `20261105_1150_bootstrap_agents/BUG-001` concerns wrapper failure propagation, and `BUG-002` concerns Eigen provisioning. Their implementation repairs and historical impact remain successor work in that repository; this task changed no external target files.

## Documentation reconciliation

| Owner / artifact | Final disposition |
|---|---|
| [README.md](../../../../README.md) | Updated source layout, self-install/update behavior, provenance handoff and evaluation procedure. Reviewed at closeout; no further change needed. |
| [Canonical guidance template](../../../../templates/AGENTS_TEMPLATE.md) | Added source/staging distinction and bootstrap acceptance checks above the policy boundary; shared policy unchanged. |
| [Zero prompt](../../../../Agent-Zero-prompt.md) | Both variants require the acceptance checks and staged-copy cleanup; retained unchanged at closeout. |
| [Update prompt](../../../../Update-prompt.md) | Supports current/legacy source layouts and fixed-source self-updates; no additional closeout change needed. |
| [Installed AGENTS.md](../../../../AGENTS.md) | Repository-specific guidance and ownership created; commands/contracts still agree with their owners and canonical policy. |
| Canonical and installed task templates | Structures unchanged; installed copies retained byte-for-byte. |
| [Walkthrough](../../../example-walkthrough.md) | No change needed; references current README setup and the unchanged four-phase workflow. |
| Root staging and active task records | Removed only staging; sanitized and moved both records into this archive. Ignored logs remain supplementary. |

## Follow-ups and context lineage

- **Epoch / initiative:** self-installation and bootstrap quality.
- **Recommended successor:** repeat the documented faulty/control bootstrap trials with fixed source and model/settings, ensuring complete provenance handoff. This is evaluation work, not a blocker to the implemented workflow.
- **Other unresolved work:** historical impact of local BUG-001; external wrapper/provisioning repairs remain with their repository. No packaging system, automatic policy merger or installation database was introduced.
- **Prior closeouts reviewed:** none in this repository at initial planning. Later external reviews consulted the following exact paths; essential findings are summarized above and in memory, without depending on access to that checkout:
  - AFineCppRepo at `a500dd2`: `docs/agent/tasks/20261005_1508_instantiate_agents/CLOSEOUT.md` and `docs/agent/tasks/20261104_1930_update_socrates_loop/CLOSEOUT.md`.
  - AFineCppRepo at `2e28261`: `docs/agent/tasks/20261104_2059_agents_bootstrap/CLOSEOUT.md`.
  - AFineCppRepo working tree based on `b74fcbc`, with the new archive still uncommitted at review: `docs/agent/tasks/20261105_1150_bootstrap_agents/CLOSEOUT.md`.

## Final archival verification

Verified on 2026-11-05T15:23-05:00 before marking the archived brief complete: exactly three archive records exist; both active records and root staging are absent; all 20 retained tracked files and canonical/installed policy/template comparisons are unchanged; all 17 archive links/anchors resolve; sanitization and whitespace checks pass. Memory remains under 200 lines. Git scope is only the authorized root-staging deletion and this archive, with an unchanged index. Essential evidence is preserved here and in memory; ignored logs are supplementary.

No Git history operation was performed by this agent. Suggested closeout commit: `docs: close out self-installation and bootstrap verification`.
