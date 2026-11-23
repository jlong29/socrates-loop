# MEMORY

**Task:** local commits and coding-agent capability review
**Last updated:** 2026-11-19 15:29 America/New_York

## Starting repository evidence
- Starting revision: `6637afc4df953e9f20c80b5ffe65350faf8ac530` (`Recursive-Use (#6)`). Initial `git status --short` was empty; neither active task record existed. Created `.agent/logs/` and copied the installed record templates before filling them.
- Only applicable AGENTS.md discovered is the repository root. Read README, canonical guidance, both installed record templates, Zero/Update prompts, relevant walkthrough sections, installer input/preflight code and regression-test names.
- Read one relevant archive: [20261104_2028_self_installation/CLOSEOUT.md](../20261104_2028_self_installation/CLOSEOUT.md). No deeper records or unrelated archive trees were read.
- Canonical and installed policy explicitly prohibit `git commit` in Phase 2 and require a human-made commit. This is intentional policy, not a newly reproduced implementation defect. User reports oversized accumulated changes; no impact count has been established.
- Complete policy equality from the unique `## Working agreement (four-phase execution)` heading through EOF: true. Installed TASK_BRIEF and MEMORY templates: byte-equal to canonical sources.
- Canonical guidance is 339 lines; task brief 69; memory 36. Recommendations target routine/duplicate instructions rather than impose a new arbitrary size threshold.
- Installer already copies canonical files as bytes; tests cover source preservation, self/external installation, conflicts, dry-run, provenance and CLI behavior. No installer-code change is needed for authorization text.
- README/Update prompt require separate source-development and self-update tasks. On 2026-11-09, corrected the initial inference that requesting both outcomes authorized a same-task exception: preserve source review/closeout followed by a separate fixed-source installation update. The user's requested local-commit policy change does not require changing that sequence.
- The original request explicitly separates rigorous evaluation from the present work; it does not defer discussion of the research recommendations. On 2026-11-09, corrected the brief's undefined "later decisions" timing to place recommendation selection in the current planning review, before source implementation and installation synchronization.
- The initial commit-policy draft mixed authorization boundaries with routine Git procedure and duplicated history in task records. The user's concision review prompted a shorter proposal: retain scope, coherent verified commits, unrelated-work preservation and separate review/publication/history-change authorization. Existing task templates need no changes solely to enable local commits.

## Starting source identity

These hashes identify the starting reference, not the later frozen implementation source:

| Input | SHA-256 |
|---|---|
| `templates/AGENTS_TEMPLATE.md` | `6aab48fbeed64551143e435716f717f6bca0f2016044915278e61a02c6ce012d` |
| `templates/TASK_BRIEF_TEMPLATE.md` | `732b0cceb7ec1e59cb0e5ff5e27e54d1b1c7a36e35c779591e2fb565667ec5c9` |
| `templates/MEMORY_TEMPLATE.md` | `1fa568779d7bce0780be78a0bfedac2ec16df6e7af85c8bbd1427c30ab2dc267` |
| `README.md` | `4b0f216532f56d2d64deaa1adc8922528fa60a99d6e576f8c666739c98aa00a3` |
| `Agent-Zero-prompt.md` | `8a0a0de1cf0a0911affb07da3bab9ec7b7574ccb15099726bd703903be5a6941` |
| `Update-prompt.md` | `d078f441c82b79ffc11671103a0b99d6ce85d3ed04a26e7f9b656394804d0145` |

## Research evidence — accessed 2026-11-06

Scope: primary documentation and research for OpenAI/Codex, Anthropic/Claude Code and Google/Gemini CLI/Antigravity, plus relevant empirical instruction-file research. This is not an exhaustive model leaderboard or a Socrates Loop evaluation. Source facts below are paraphrased; inference is identified separately.

### OpenAI / Codex
- [Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra), dated 2026-09-11, explicitly recommends revisiting accumulated instructions, loading only relevant guidance, reducing procedural prescriptions and reconsidering approval boundaries. It cautions that different models may need different guidance. This directly supports auditing the current fixed ceremony rather than assuming it remains valuable.
- [Unrolling the Codex agent loop](https://openai.com/index/unrolling-the-codex-agent-loop/), dated 2026-01-23, documents automatic compaction at a configured threshold. This is an agent-harness capability; do not attribute it to Markdown templates or a model alone.
- [Code generation](https://developers.openai.com/api/docs/guides/code-generation) identifies current general-purpose models such as GPT-6.1 Sol for coding in Codex. The practical comparison must specify model plus harness, tools, settings and permissions.
- [Maintaining software with the GPT-6 family](https://developers.openai.com/blog/maintaining-software-with-the-gpt-6-family) was located and opened as additional current material; no uninspected article-body claims are used.

### Anthropic / Claude Code
- [Current best practices](https://code.claude.com/docs/en/best-practices) describes built-in compaction and delegation, recommends short project instructions for otherwise unavailable knowledge and concrete checks, and distinguishes advisory prose from enforced controls. Its current obsolete-advice section explicitly retires aggressive manual context management and delegation solely to save context. Defaults depend on client/configuration; these docs are vendor guidance, not independent reliability measurements.
- [Haiku 5.5 release](https://www.anthropic.com/claude-haiku-5-5), dated 2026-10-07, places Haiku alongside Opus 5.5 and Sonnet 5.5 and describes summaries/compaction and delegated coding uses. No vendor benchmark ranking or cost comparison is used to justify a Socrates Loop change.
- [Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents), dated 2025-11-26, reports value from incremental work, local commits and progress artifacts in Opus 4.5-era experiments. It also describes incomplete end-to-end verification despite simpler checks. Retained as historical counterevidence to deleting all durable state, not evidence about today's model failure rates.

### Google / Gemini CLI and Antigravity
- [Gemini 4 Argon for developers](https://blog.google/innovation-and-ai/technology/developers-tools/build-with-gemini-4-argon/), dated 2026-10-13, describes long-horizon engineering/code migrations and availability in Antigravity. This is a model/product announcement, not proof of project-specific correctness.
- [Gemini CLI settings](https://geminicli.com/docs/cli/settings/) documents threshold-triggered context compression (`model.compressionThreshold`, shown as 0.5). Native support weakens the case for a universal mandatory manual-compaction step.
- [Checkpointing](https://geminicli.com/docs/cli/checkpointing/) documents snapshots in a separate shadow Git repository and states the feature is disabled by default. It is not equivalent to coherent commits in the user's project history.
- [Auto Memory](https://geminicli.com/docs/cli/auto-memory/) is explicitly experimental and proposes memory/skill changes for user review. It does not justify assuming all clients automatically maintain authoritative, shared project decisions.

### Empirical instruction-file evidence
- [Evaluating AGENTS.md: Are Repository-Level Context Files Helpful for Coding Agents?](https://arxiv.org/abs/2602.11988v3), submitted 2026-02-12, revised 2026-09-29. The current abstract reports no general task-success improvement and over 20% average inference-cost growth across its tested context-file settings; it finds utility for nonstandard practices and questions generic repository overviews.
- This is an author-reported study of particular tasks/models/files, not a result for Socrates Loop, its human review workflow, or every current agent. Do not transfer its numeric cost result to this repository. It motivates the separately requested controlled comparison.

## Synthesis and caveats
- Inference: move Socrates Loop's emphasis toward project intent, constraints, durable decisions and independently checkable outcomes; reduce generic step-by-step engineering instructions.
- Inference: native compaction/session restoration reduces the need for manual context ceremony, while portable team-readable decision records can serve a different purpose.
- Inference: commit permission should explicitly encourage coherent boundaries; automatic checkpoints and a permission statement alone do not produce good project history.
- Verification should use acceptance criteria and observable outcomes, preserving reproducible evidence and limitations. The user requested removal of agent-related review prescriptions; the distributed policy will not constrain future reviewer arrangements.
- The user retained mandatory phases and approved removing the command cap and compaction ceremony, simplifying generic routines and reducing duplicate record content. Required record files and archival checks remain; only their contents become more concise.
- Keep distinctive local contracts: file preservation, non-mutating dry runs, source/staging separation, reliable failure-reporting commands and fixed source inputs during synchronization. These cannot safely be replaced with generic model capability claims.
- Future evaluation needs a well-defined baseline with the same native harness/tools and no Socrates additions, not a raw model stripped of its normal capabilities. Detailed protocol and trials are deferred by the user.

## Failed experiments / research tooling
- Two official documentation `.md` URLs returned unsupported `text/markdown` errors in the web tool. Opened the HTML equivalents successfully; no content was inferred from the failed fetches.

## Hooks and enforcement guidance — accessed 2026-11-09
- [Git hooks](https://git-scm.com/docs/githooks) run scripts at Git events. A failing pre-commit hook aborts a commit, but can be bypassed; a local hook is useful feedback rather than a remote merge guarantee. A possible repo-specific hook would run the existing installer suite; none is being installed.
- [Codex hooks](https://learn.chatgpt.com/docs/hooks) and [Claude Code hooks](https://code.claude.com/docs/en/hooks) provide agent lifecycle events such as PreToolUse and Stop. They have client-specific configuration and trust requirements; a command hook can invoke a deterministic project check. Do not assume identical schemas or blanket security enforcement.
- [Codex approvals/security](https://learn.chatgpt.com/docs/agent-approvals-security) distinguishes technical sandbox permissions from when approval is requested. Runtime/OS/admin configuration governs filesystem and network access; repository prose cannot grant it.
- [GitHub required status checks](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/available-rules-for-rulesets) can gate merges using results from GitHub Actions or external CI. CI execution and repository merge rules are separate controls. No remote settings were inspected or changed.
- Repository inspection found no tracked .github, .githooks, .claude or .codex configuration. This does not establish which user-local hooks or remote repository rules are configured.

## Verification evidence
- Planning: clean initial Git status; unique policy markers; complete policy equality; installed task-template equality; starting source hashes; selected historical closeout reconciled with current owners.
- No implementation test has been run in Phase 1. Planned installer suite: `python3 -B -m unittest discover -s tests -v`. It verifies distribution/installer behavior, not instruction following or incremental workflow value.
- Final Phase 1 checks passed: Git status clean; tracked and staged diffs empty; six source hashes unchanged; both active records ignored by Git; 13 relative link targets resolve. Brief: 128 lines; memory: 69 lines.

## Implementation verification
- Source commits: `20d8031` (local-commit authorization) and `2a0bd91` (approved guidance/record simplification and outcome verification). Detailed changes remain in Git.
- `python3 -B -m unittest discover -s tests -v`: all 20 tests passed after each coherent source change. Coverage remains installer/fixture behavior; no agent-compliance or incremental-value claim is made.
- Independent walkthrough execution in a temporary directory: original code fails the regression on `KNOW`; the documented fix passes all five checks and four CLI cases (uppercase, omitted query, explicit empty query, unmatched query), with expected outputs derived from the stated requirements.
- Source review confirmed all four phase headings and approval gates, local-commit boundaries, significant-bug traceability and archival verification remain. Command cap, manual-compaction instructions, stale debugging-loop references and reviewer restrictions are absent from the updated canonical policy.
- All 17 relative documentation links/anchors resolve. A trailing blank line introduced during template editing was removed; final task-range `git diff --check` passes.
- Installed AGENTS/task templates, installer, tests and historical archives remain byte-identical to the starting revision. Root bootstrap staging remains absent. Tracked worktree and index are clean.
- Initial implementation line counts, before the checklist review revision: guidance 339 → 308, task brief 69 → 39, memory 36 → 32. These describe size, not measured workflow value.

## Review revision verification — 2026-11-13
- Commit: `2671b81` (`docs: restore milestone and success criteria checklists`). Inspected the canonical template and walkthrough: distinct deliverable and acceptance checklists are present; milestones own execution order and needed implementation detail, with no separate implementation-plan/change-set list. The README description agrees. This inspection does not measure improved handoff performance.
- `python3 -B -m unittest discover -s tests -v`: all 20 tests passed. Working and staged `git diff --check` passed. Only the task template, walkthrough and README were staged; the tracked worktree and index are clean after the commit.
- `git diff --exit-code 6637afc -- AGENTS.md docs/agent/TASK_BRIEF_TEMPLATE.md docs/agent/MEMORY_TEMPLATE.md install.py tests docs/agent/tasks`: passed, confirming installed guidance, installer/tests and archives remain unchanged. No executable walkthrough code or links changed, so the prior walkthrough execution and link evidence remain applicable.

## Plan-section review verification — 2026-11-13
- Commit: `52d4ba9` (`docs: retain plan and verification alongside milestones`). Inspected the template and example: Plan and verification holds the approach/dependencies and checks, referring to milestone IDs; progress stays in the two checklists. This supersedes the earlier placement of implementation detail inside milestones. README describes the restored plan.
- `python3 -B -m unittest discover -s tests -v`: all 20 tests passed. Working and staged `git diff --check` passed. Reviewed the staged diff: only the task template, walkthrough and README changed; executable examples and links remain unchanged. Tracked worktree and index are clean after the commit. No handoff-performance claim is established by these checks.

## Approved source identity for the required installation update
- Revision: `52d4ba976064120497251ac9c80246af8418dabe`. The user approved closeout on 2026-11-19. All six hashes below were rechecked at closeout and remain unchanged; recheck them when starting the integration task. The archive-only closeout commit does not change these source inputs.

| Input | SHA-256 |
|---|---|
| `templates/AGENTS_TEMPLATE.md` | `da7203eb5dc8d8ab1a309f0ace8d86ed08ef2fafdf91d1df064c0508e3a9afdb` |
| `templates/TASK_BRIEF_TEMPLATE.md` | `5f95a3a285126a6441e628e944277d49b3bf75ac2221e7eef5d3a253e7316324` |
| `templates/MEMORY_TEMPLATE.md` | `8d0a5f144594e48c35a653ef1a889ea76a8457c852ae9bfd6a0b56d5e4de92f9` |
| `README.md` | `96c652854534e7adfe99d5eb485570d1fc9ae16c0fe5d9f04285033c85754d1f` |
| `Agent-Zero-prompt.md` | `2541648f4a0ec54362c4efbca9ffaddbd85c3ee2a2c4f21b1d0adba683d54d4c` |
| `Update-prompt.md` | `d31d710c18369be8c8b634f24c704ac56aacbaf032d6ce47c4f2d66769decb02` |

## Persistent Git approvals
- Local client: Codex CLI 0.166.0. This checkout is trusted; its project-local Codex configuration/rules are absent.
- Inspected personal `~/.codex/rules/default.rules`: user-authorized allow rules for `git add` and `git commit` are saved there. `codex execpolicy check --rules ~/.codex/rules/default.rules -- git add README.md` and the corresponding `git commit -m example` check both return `allow`. These checks do not execute the Git commands.
- These are approvals granted by the user during this session, not built-in Codex defaults. Existing unrelated rules were left intact. The second actual source commit completed without a new approval prompt.
- [Codex rules documentation](https://learn.chatgpt.com/docs/agent-configuration/rules) states that saved approvals persist in the user layer and are loaded by subsequent sessions. Prefix rules approve command execution; they do not replace the task scope and review requirements in AGENTS.md.
- A candidate limited to explicit `git -C <this checkout> add/commit` commands passed 10 policy-matching cases when combined with the other existing rules. User selected **Keep the existing global approvals**, so the candidate was discarded and persistent configuration was not edited.

## Closeout verification — 2026-11-19
- Confirmed HEAD is the approved source revision and computed SHA-256 with Python `hashlib` for all six recorded inputs; all match the approved-source table. The complete implementation diff contains only the seven expected source/documentation files.
- `git diff --check 6637afc HEAD` passed. `git diff --exit-code 6637afc HEAD -- AGENTS.md docs/agent/TASK_BRIEF_TEMPLATE.md docs/agent/MEMORY_TEMPLATE.md install.py tests docs/agent/tasks` passed before the new archive was created.
- Reconciled the canonical policy/task templates, README, walkthrough, Zero and Update prompts against the final decisions and acceptance criteria; no further source edit is needed. Installed guidance and templates require the separate follow-on update.
- Reused the 2026-11-13 result of all 20 installer/fixture tests passing: their inputs are unchanged, and closeout changes only task records. Research remains dated historical evidence; no new capability claim or workflow-value measurement was made at closeout.
- Read the records for sensitive content and unnecessary machine-specific paths; only public research/documentation URLs and portable paths remain. Python archival checks verified all three archive files, absence of both active records, 24 resolving local links/anchors and unchanged source hashes before the archived brief was marked complete. No evidence depends solely on ignored logs.
