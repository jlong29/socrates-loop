# AGENTS.md — <REPO_NAME>

You are an AI coding agent operating inside the `<REPO_NAME>` repository.

This file is **always-on guidance**. Focus on project-specific constraints, decisions and non-obvious commands. Link to maintained documentation and omit generic engineering advice or facts readily discoverable from the code. Task-specific scope and evidence belong in `.agent/`.

---

## How to instantiate this template in a new repo
The installer copies this distribution template to the target root as `AGENTS_TEMPLATE.md`. Create a separate repo-specific `AGENTS.md` from that staged copy as the first task in a repository. Preserve any existing repository guidance. Remove only the staged root copy at approved closeout; never customize or remove the canonical `templates/AGENTS_TEMPLATE.md` in the source checkout, including during self-installation.

When bootstrapping a new repo, the agent should:
1. Read the user’s project brief and the repo tree.
2. Replace the placeholders in the sections **before** `## Working agreement`.
3. Preserve all policy sections from `## Working agreement` onward unless the user explicitly changes them.
4. Generalize or prune inapplicable repo-specific sections.
5. Complete `## Documentation ownership` using existing files or sections. Remove unused optional roles; propose new documents only for distinct needs that existing owners cannot serve.

### Bootstrap acceptance checks

Keep these checks in the bootstrap task records; omit these instantiation instructions from the finalized `AGENTS.md`.

- **Command evidence:** For each recommended build/test command, establish prerequisites, working directory, environment, test discovery scope, and failure reporting. Inspect relevant wrappers or generators; this is a bounded review of recommended commands, not a general code audit. Distinguish source inspection from executed checks and state what remains unverified. If a wrapper can mask failure, document the limitation and a reliable alternative where available.
- **Documentation and findings:** Reconcile command instructions and known limitations with their existing documentation owner. Keep essential references in `AGENTS.md`. Apply the existing significant-bug traceability policy to observed defects even when repair is outside bootstrap scope; retain unresolved follow-ups without claiming untested behavior works. For a design-only repository, distinguish planned commands from existing functionality.
- **Provenance:** Before editing or deleting staging, record SHA-256 hashes of root `AGENTS_TEMPLATE.md` and both installed task templates in the task brief. Compare the installed-file hashes with any supplied by the installer and resolve mismatches before proceeding. Retain supplied source revision, input state, and source-prompt hash; record unavailable identity explicitly, never substitute the target repository's revision. Carry this provenance into the closeout.
- **Review:** Verify the complete shared policy against the staged template, check repository-specific claims and local references, and present command evidence, unverified assumptions, and unresolved defects separately. Confirm instructions agree with their documentation owners before requesting approval.

---

## Mission
<Describe the repo’s purpose in 2–5 lines. Focus on what the codebase does, for whom, and the dominant workflow or system boundary.>

## Source of truth
Inspect these files to understand implemented behavior:
- `<path/to/primary/entrypoint_or_cli>`
- `<path/to/core/runtime_or_train_logic>`
- `<path/to/secondary_runtime_or_eval_logic>`
- `<path/to/common/shared_logic>`
- `<path/to/config_or_schema_definition>`

Use approved requirements and contracts to establish intended behavior. When documentation, code or observed results disagree, investigate the discrepancy rather than assuming either the document or implementation is correct; ask the user if intended behavior remains ambiguous.

Additional repo-specific rules:
- <example: Keep optional subsystem infrastructure available; do not remove it unless explicitly requested.>
- <example: Prefer metadata-first inference over hard-coded defaults.>
- <example: Preserve backward compatibility for configs, artifacts, APIs, or on-disk layouts.>

---

## Repo map

Include navigation that saves meaningful rediscovery; omit obvious layout details.

### High-signal code
- `<src_or_pkg_dir>/` — <core library / application code>
  - `<important_file_or_subdir>` — <why it matters>
  - `<important_file_or_subdir>` — <why it matters>
  - `<important_file_or_subdir>` — <why it matters>
- `<secondary_code_dir>/` — <evaluation / reporting / tooling / services>
- `<tests_dir>/` — <test suite>
- `<configs_or_schema_dir>/` — <configuration / schemas / manifests>

### Large/noisy dirs (do not scan by default)
Avoid expensive traversal unless explicitly needed:
- `<artifacts_or_models_dir>/`
- `<data_dir_pattern>/`
- `<logs_or_runtime_dir>/`
- `<generated_or_cache_dir>/`

---

## Core workflow (essential agent commands)

`README.md` or a focused runbook owns setup and workflow procedures. Keep only commands essential to routine agent work here and under `Tests (default)`; link to the owner for full instructions. Any repeated command is a quick reference and must stay consistent with its owner.

- Workflow instructions: `<owning path#section>`

```bash
<essential agent command, if needed; otherwise remove this block>
```

---

## Metadata contracts (important)
Document the contracts the agent must preserve. Examples:
- Inputs / outputs written to disk:
  - `<path_or_pattern>` writes `<artifact>`
  - `<path_or_pattern>` reads `<artifact>`
- Metadata or schema behavior:
  - <example: omitted CLI args are inferred from metadata>
  - <example: explicit CLI args override inferred defaults>
- Runtime invariants:
  - <example: preserve backward compatibility of config keys>
  - <example: never change reward semantics without explicit approval>

If this repo does not use metadata-driven behavior, replace this section with the relevant invariants/contracts.

---

## Tests (default)
List reliable project checks and any non-obvious prerequisites:
```bash
<insert canonical fast test command>
```

If the repo has special runtime issues, document the workaround here:
```bash
<insert env workaround if needed>
```

Optional additional checks:
```bash
<insert lint / typecheck / integration command if appropriate>
```

---

## Coding/style conventions
- <language/runtime version(s), if important>
- <naming/style conventions that should be preserved>
- <linter / formatter / style-config rule if one exists>

---

## Documentation ownership

Give each maintained topic one authoritative owner. Map the roles below to existing files or sections and remove unused optional rows; a small repository may use README sections for several roles.

| Document or section | Owns | Does not own |
|---|---|---|
| `AGENTS.md` | Agent working agreement, essential invariants and documentation routing | Task status, detailed manuals and historical results |
| `README.md` | Setup, common usage and navigation | Investigation chronology |
| `.agent/TASK_BRIEF.md` | Active task scope, acceptance criteria and execution state | Project-wide reference documentation |
| `.agent/MEMORY.md` | Task investigation and verification evidence | A duplicate task plan |
| `docs/agent/tasks/<task_slug>/CLOSEOUT.md` | Historical task outcomes, decisions, verification and follow-ups | Current operating instructions |
| Other archived task records | Supporting plans, investigation and evidence for deeper dives | Current guidance or active task state |
| `<orchestration manifest and runbook, if used>` | Approved task assignments, dependency and review relationships, execution transitions and integration procedure | Replacement project requirements or independent working policy |
| `<current-state path#section, if needed>` | Project-wide active work, accepted deliverables, unresolved issues and next boundary | Detailed task plans and completed-work chronology |
| `<architecture path#section, if needed>` | Implementation responsibilities and entrypoints | Operating procedures and task history |
| `<runbook path#section, if needed>` | Current procedures and operating contracts | Experiment chronology |
| `<metrics path#section, if needed>` | Definitions, comparability and interpretation | Individual run results |
| `<design path#section, if needed>` | Approved design, constraints and acceptance gates | Live task progress |
| `<results path#section, if needed>` | Historical findings and supporting evidence | Current operating instructions |

Project state summarizes and links to active tasks rather than copying their plans.

---

## Significant behavior

For traceability, treat a bug as significant when it can affect:

- <user-visible behavior, persisted data, public APIs, safety or security, model outputs, evaluation results, or other repository-specific outcomes>

---

## Working agreement (four-phase execution)

### Local commits (Phases 2–4)

Local commits within the approved task scope need no further approval. Commit coherent, verified changes as you complete them, keeping related code, tests and documentation together. Preserve unrelated work and exclude it from commits. Commits do not replace review; pushing, merging, rewriting history or discarding work requires explicit authorization.

### Review authority and optional delegation

The user is the reviewer unless the user explicitly delegates review authority for a named scope. Record the assigned reviewer, approved scope and boundaries in the task brief and, when used, the orchestration manifest. Delegation preserves all four phases and their gates; it does not authorize changing parent requirements, accepting one's own work, or publishing changes. The same working agreement applies to parent agents, child agents and reviewer turns. Their assignments and permitted actions differ; their policy does not.

Before proposing delegation, assess whether work has separable outcomes, clear success-criterion ownership, sufficiently stable interfaces, useful parallelism, and an identified integration owner. Account for shared files, review effort and integration cost. Keep the task with one agent when these conditions do not justify delegation.

For approved delegation:

- Preserve the parent's original goal, milestones, constraints and success criteria. Add coordination milestones as needed; do not replace product outcomes with checkboxes that only say to launch or review agents. Map each child to stable parent milestone and criterion IDs, and retain cross-cutting acceptance and integration checks with the parent.
- Give each active task its own workspace and task records. A parent reviewing a child remains in its own Phase 2 while the child is in Phase 1 or Phase 3. Preserve the parent's `.agent/TASK_BRIEF.md` and `.agent/MEMORY.md`; do not load a child's records as if they replaced the parent task.
- Distinguish dependency edges from reviewer assignments. A reviewer relationship does not mean the parent task must finish before the child can run. A dependent task may use only the accepted input version named in its brief; changed inputs require revalidation.
- Use one approved policy version throughout a run. Record its identity and relevant input versions. If policy, scope, criteria or contracts change, stop affected work and resolve the change explicitly instead of allowing agents to proceed under different assumptions.
- At a gate, submit a review candidate identifying the task, approved brief and criteria, baseline, exact code/documentation version, verification evidence and unresolved findings. Stop making changes to that candidate. The assigned reviewer evaluates it against both delegated criteria and applicable parent constraints; the author cannot approve its own candidate.
- An approval applies to the reviewed version. Requested repairs remain in Phase 3, produce a new candidate, and require a new review. A resumed or replacement agent reconstructs the same task from durable records and the review findings; a new session does not create new authority.
- After Phase 4, verify archival and reconcile any changes made after review. Substantive code, contract or maintained-document changes need revalidation before integration. Child completion does not establish that the combined parent result works.
- An explicitly authorized integration controller may combine accepted changes into the named parent branch and remove clean, archived, integrated child worktrees according to the approved runbook. Local-commit permission alone does not authorize merges, cleanup that discards work, pushes, or changes to other branches.
- An approved runbook may reserve local Git operations to the supervisor for every agent role. In that mode agents yield coherent, verified changes and the supervisor creates their local commits. This assigns an existing capability; it does not remove the default workflow's local-commit permission or create a separate policy for the parent.

The parent remains responsible for checking the assembled result against its original success criteria. Its own Phase 3 requires the user or another explicitly assigned reviewer; approving child candidates does not approve the parent result.

### Investigation and plan changes (all phases)

When material uncertainty about behavior, cause or approach affects the work, state a testable hypothesis. Identify observations that could support, distinguish or contradict the explanation, and choose checks or experiments accordingly. Compare results with predictions and revise the hypothesis, conclusion or plan. Preserve meaningful evidence under the `.agent/` policy below. Routine changes with clear acceptance checks need no invented hypothesis or fixed experiment sequence.

Use available project context and proportionate checks within the current phase's permissions and approved scope to resolve uncertainty before asking the user or reviewer. Act on supported conclusions and report them as findings with evidence. Raise remaining questions when evidence is insufficient or unavailable, or the answer requires the author's judgment; explain what was checked, what remains unresolved and the decision needed. Bring blocking decisions to the user when encountered rather than waiting for the review handoff.

If findings require a material change to approved scope, constraints or success criteria, record the proposed change in the brief and obtain user approval before proceeding with work that depends on it. Updating the brief alone does not authorize the change. Routine implementation choices within approved bounds need no additional approval.

### Documentation maintenance - all phases

Use the documentation ownership table to identify affected documents and read their relevant sections before editing.

- **Maintain scope:** Update the owning document; other documents may summarize and link. Leave unaffected documents alone.
- **Replace before adding:** Replace superseded guidance and consolidate duplication. Incorporate reusable lessons into existing sections wherever possible.
- **Separate guidance from history:** Maintained docs describe current behavior, procedures and state. Closeouts preserve task outcomes, decisions and verification; deeper task records preserve supporting detail. Preserve unique historical evidence before removing it from maintained docs.
- **Keep documents consistent:** Update affected guidance when behavior changes; synchronize status at implementation start, handoff and closeout. Verify affected instructions and links agree.
- **Reconcile before completion:** At closeout, review affected owners and record updates, justified no-change conclusions and unresolved follow-ups. Repeat a bounded review at major milestones or when drift becomes apparent.

### Bug impact traceability (all phases)

For every bug affecting behavior defined as significant above:

- Assign a stable task-local bug ID in `.agent/MEMORY.md` and the closeout.
- Record the root cause, fix location, regression evidence, and earliest and latest known affected version, commit, dataset, or generated artifact.
- Quantify the impact when evidence is available; never infer impact solely from the fix.
- Record unresolved impact analysis as an explicit follow-up.

### Phase 1 — Plan + Task Definition (read-only)
Goal: build repo-aware understanding and produce one planning deliverable.

Rules:
- Follow `Starting or resuming work` below before planning.
- Construct the task brief from relevant maintained guidance and, when available, prior closeouts according to `Prior task context (selective)` under `## Docs policy`.
- Do not edit code or tracked files in this phase.
- Restate goal + success criteria.
- Identify the minimal relevant files and affected documentation owners, and why.
- Propose a plan and verification commands, including how to investigate material uncertainties.
- Stop for approval of the brief by the user or explicitly assigned reviewer before Phase 2.

**Phase 1 deliverable:**
- Write the plan to `.agent/TASK_BRIEF.md`, using the template sections that serve the task. Define observable acceptance criteria and checks that can expose incorrect or incomplete results.

Task records under `.agent/` may be written during planning.

### Phase 2 — Implement + Learn (write + verify + local commits)
Goal: Execute the plan developed in Phase 1 and memorialized in `.agent/TASK_BRIEF.md`

After approval, set the brief to **Phase 2 / in progress**. Implement the approved plan in coherent changes, verifying and committing each under `Local commits (Phases 2–4)` above. Use investigation findings to refine the approach within approved bounds; avoid unrelated refactoring or formatting.

When ready for review by the user or explicitly assigned reviewer, set the brief to **Phase 3 / awaiting review**. At handoff, report the outcome, verification results and gaps, local commits, and remaining changes or blockers. Include `git status`. In an orchestrated task, identify the exact review candidate and yield control to the supervisor; do not begin closeout until that candidate is approved.

### Phase 3 — Review + Debug
Goal: Review the Phase 2 output with the user or explicitly assigned reviewer and remain in this phase until it is approved.

- Verify outcomes against the agreed acceptance criteria. Derive expected results from the requirements, independently of the implementation; confirm that checks exercise the intended behavior and expose failures.
- Distinguish executed checks from source inspection and assumptions. Report unverified behavior and limitations; a success message alone is insufficient evidence.
- Reproduce and investigate reported failures under `Investigation and plan changes`, correct them within scope, and add targeted regression coverage when feasible. Re-run affected checks.

### Phase 4 — Task completion / closeout procedure
Goal: Summarize completed work and clean up.

After the user or explicitly assigned reviewer approves the Phase 3 result, the agent should:
1. Update `.agent/TASK_BRIEF.md`: set **Phase** to `Phase 4`, **State** to `in progress`, and **Last updated** to the current date and time.
2. Review this `AGENTS.md` and the task's acceptance criteria and verification evidence.
3. Apply `Documentation maintenance - all phases` to affected owners; no new permanent guidance is required when none is warranted.
4. Produce a **closeout summary** from `.agent/MEMORY.md` and `.agent/TASK_BRIEF.md`, concise but sufficient for future Phase 1 planning:
   - Outcome and completed scope
   - Decisions made (and why)
   - New invariants/gotchas discovered
   - New/changed commands (CLI flags, scripts)
   - TODOs / follow-ups
   - Verification evidence (commands run)
   - Documentation reconciliation: affected owners, updates or justified no-change conclusions, and unresolved follow-ups
   - Context lineage:
      - Epoch / initiative: `<name or none>`
      - Prior closeouts reviewed: `<exact paths or none>`
      - Recommended successor tasks: `<task slugs or short descriptions, or none>`
5. Complete `Cleanup at task closeout` below.

#### Cleanup at task closeout
At completion:
1. Before archiving, remove credentials, secrets, private URLs, sensitive user data, and unnecessary machine-specific paths.
2. Create `docs/agent/tasks/<task_slug>/`, using a slug such as `YYYYMMDD_HHMM_<short_topic>`.
3. Move `.agent/TASK_BRIEF.md` and `.agent/MEMORY.md` there and write `CLOSEOUT.md` alongside them.
4. Retain evidence needed to understand the closeout as concise summaries or sanitized excerpts in the archive, or link to a durable location accessible to future readers. Do not rely on untracked `.agent/logs/` as the only source.
5. Repair relative links after moving files and verify references from their archived locations. Verify all three archive files exist and the two active task files no longer exist.
6. Only after reconciliation and archival verification succeed, set **State** to `complete` and update **Last updated** in the archived task brief. If closeout fails, leave the task incomplete and report the remaining work and record locations.

---

## .agent/ folder policy

`.agent/` is **untracked**.

Updating this repository's Socrates Loop integration is a normal task under this working agreement. Start only when no other task is active, and use the selected Socrates Loop checkout's `Update-prompt.md` for update-specific scope and verification. The update task's own records remain active through implementation and review.

Keep task records proportionate to the work. Git history owns code changes; records preserve scope, rationale, evidence and unresolved questions. Do not restate commit diffs or maintain a duplicate commit ledger. Omit unused sections and link to existing evidence instead of repeating it. Keep both active record files and the required closeout archive even for small tasks.

### Starting or resuming work

- Before starting or resuming work, read `.agent/TASK_BRIEF.md` and `.agent/MEMORY.md` if they exist. Reconcile their scope, phase, decisions and evidence with the latest user request and current repository state.
- For the same task, resume its recorded phase and next action, incorporating later user decisions. Reconstruct missing records from their templates and available evidence once the task and phase are clear; preserve any existing record.
- If records belong to another task or the task/phase remains unclear after checking available context, preserve them and resolve this with the user before starting new work. Do not overwrite existing records to initialize a new task.
- For a new task with neither record present, run `mkdir -p .agent/logs`, copy `docs/agent/TASK_BRIEF_TEMPLATE.md` to `.agent/TASK_BRIEF.md` and `docs/agent/MEMORY_TEMPLATE.md` to `.agent/MEMORY.md`, and begin Phase 1.

During work, consult relevant memory entries before repeating investigations or revising conclusions. Follow evidence references as needed; inspect relevant or user-identified logs/artifacts selectively rather than scanning the entire `.agent/` folder.

### Flat structure (preferred)
- `.agent/TASK_BRIEF.md` — compact task description, success criteria, and progress notes
- `.agent/MEMORY.md` — compact running notes related to the work process rather than the task definition itself
- `.agent/logs/` — log files and small extracted snippets

### `.agent/TASK_BRIEF.md`

`docs/agent/TASK_BRIEF_TEMPLATE.md` defines the document structure.

The task brief is the authoritative record of the task’s scope and execution state. Update it when goals, scope, constraints, plans, success criteria, decisions, milestone progress or next actions change materially, and at each phase/state transition. Update **Last updated** with those changes.

For an explicitly orchestrated run, the approved brief remains authoritative for scope and intended outcomes; the supervisor ledger owns observed execution phase/state and accepted review transitions. Use its status projection for current progress when the approved parent brief is frozen, and reconcile task records with it at handoff. An agent's edit to a status field cannot approve its candidate, release a dependency or authorize integration.

### `.agent/MEMORY.md`

`docs/agent/MEMORY_TEMPLATE.md` defines the document structure.

Record meaningful investigation and verification results when obtained: the hypothesis or question where relevant, reproducible checks and conditions, expected and observed results, conclusions and limitations. Preserve material negative results, rejected hypotheses and unresolved uncertainty; revise conclusions when evidence changes. Keep observations distinct from inference. Omit unused investigation sections.

Do not duplicate the task plan or current task status in memory. Findings are candidates for documentation reconciliation, not automatic additions to permanent guidance.

### Log naming convention
Store logs as:

- `.agent/logs/YYYYMMDD_HHMM_<topic>.log`

The agent may create filtered snippets alongside logs, e.g.:

- `.agent/logs/YYYYMMDD_HHMM_<topic>__excerpt.log`
- `.agent/logs/YYYYMMDD_HHMM_<topic>__grep_<pattern>.log`

Keep snippets **small** (e.g., ≤ 500 lines). Do not copy huge logs.

### Handoffs
Before requesting approval or handing off work, bring both records up to date using their roles above. Make the next action and unresolved questions clear enough for another session to resume. Conversation compaction is managed by the agent client; no manual compaction step is required by this workflow.

---

## Docs policy
Read documentation relevant to the task rather than scanning the entire docs tree.

Use `Documentation ownership` to select relevant maintained guidance. Treat superseded specs and plans as historical evidence, not current instructions.

Use the active task records alongside maintained guidance during execution; revisit history when a new question requires it. If a topic has no owner, propose an existing section or a focused new document in the task plan.

### Prior task context (selective)

Skip archive review until a task has been completed and closed out. Thereafter, use relevant closeouts during Phase 1 to construct `.agent/TASK_BRIEF.md`, checking their findings against maintained guidance and the current repository.

1. Use the scope specified by the user or `.agent/TASK_BRIEF.md`: explicit closeout paths, the last N relevant closeouts, or all closeouts associated with a named epoch or initiative.
2. If no scope is provided, inspect archive names first and read no more than the three most recent closeouts that are clearly relevant.
3. Read `CLOSEOUT.md` files first, newest to oldest. Read deeper archived task records only when a closeout leaves a question material to the plan unanswered.
4. Record reviewed paths and synthesize applicable decisions, constraints, gotchas and unresolved follow-ups in the task brief, with evidence links. Keep supporting investigation in memory. If none are relevant, record none.
5. Do not scan or load the entire task archive by default.

For a large multi-task epoch, process closeouts in bounded batches and maintain a compact synthesis in `.agent/MEMORY.md`.
