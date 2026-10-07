# AGENTS.md — <REPO_NAME>

You are an AI coding agent operating inside the `<REPO_NAME>` repository.

This file is **always-on guidance**. Keep it short, stable, and high-signal. If something is task-specific, it belongs in `.agent/TASK_BRIEF.md`, `.agent/MEMORY.md`, or other `.agent/` artifacts, not here.

---

## How to instantiate this template in a new repo
This template is meant to be converted into a repo-specific `AGENTS.md` as one of the first tasks in a repository.

When bootstrapping a new repo, the agent should:
1. Read the user’s project brief and the repo tree.
2. Replace the placeholders in the sections **before** `## Working agreement`.
3. Preserve all policy sections from `## Working agreement` onward unless the user explicitly changes them.
4. Generalize or prune sections that do not apply.
5. Complete `## Documentation ownership` using existing files or sections. Remove unused optional roles; propose new documents only for distinct needs. Preserve the maintenance policy under `## Working agreement`.

---

## Mission
<Describe the repo’s purpose in 2–5 lines. Focus on what the codebase does, for whom, and the dominant workflow or system boundary.>

Examples:
- Train and evaluate <MODEL_TYPE> for <TASK>, using a <DATA_WORKFLOW> workflow.
- Build and operate <SYSTEM_NAME>, including <CORE_SUBSYSTEMS>.
- Provide tools and services for <PRIMARY_USE_CASE>.

## Source of truth
When docs and code disagree, trust these files:
- `<path/to/primary/entrypoint_or_cli>`
- `<path/to/core/runtime_or_train_logic>`
- `<path/to/secondary_runtime_or_eval_logic>`
- `<path/to/common/shared_logic>`
- `<path/to/config_or_schema_definition>`

Additional repo-specific rules:
- <example: Keep optional subsystem infrastructure available; do not remove it unless explicitly requested.>
- <example: Prefer metadata-first inference over hard-coded defaults.>
- <example: Preserve backward compatibility for configs, artifacts, APIs, or on-disk layouts.>

---

## Repo map

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

Use targeted commands instead (e.g., `ls <dir>`, `find <dir> -maxdepth 2 ...`, `rg ...`) and keep outputs small.

---

## Core workflow (minimal commands)

### Build / prepare / ingest
```bash
<insert canonical setup, build, or data-preparation command>
```

### Main run / train / serve path
```bash
<insert canonical primary workflow command>
```

### Secondary workflow(s)
```bash
<insert canonical fine-tune / batch / deploy / report command>
```

### Evaluate / validate
```bash
<insert canonical evaluation, smoke-test, or validation command>
```

Notes:
- <call out required invariants, e.g. data layout assumptions, required companions, default modes, etc.>
- <call out important defaults or caveats.>

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
Run the fastest meaningful checks first:
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
- Prefer minimal, localized diffs; avoid broad formatting-only changes unless requested.
- <linter / formatter / style-config rule if one exists>
- If no single formatter/linter is enforced, follow existing local style in touched files.

---

## Documentation ownership

Each maintained topic has one authoritative documentation location. Other documents may summarize and link to it. Use existing files or sections; separate files are not required for every role.

| Document or section | Owns | Does not own |
|---|---|---|
| `AGENTS.md` | Agent working agreement, essential invariants and documentation routing | Task status, detailed manuals and historical results |
| `README.md` | Setup, common usage and navigation | Investigation chronology |
| `.agent/TASK_BRIEF.md` | Active task scope, acceptance criteria and execution state | Project-wide reference documentation |
| `.agent/MEMORY.md` | Task investigation and verification evidence | A duplicate task plan |
| `docs/agent/tasks/<task_slug>/CLOSEOUT.md` | Historical task outcomes, decisions, verification and follow-ups | Current operating instructions |
| Other archived task records | Supporting plans, investigation and evidence for deeper dives | Current guidance or active task state |
| `<current-state path#section, if needed>` | Project-wide active work, accepted deliverables, unresolved issues and next boundary | Detailed task plans and completed-work chronology |
| `<architecture path#section, if needed>` | Implementation responsibilities and entrypoints | Operating procedures and task history |
| `<runbook path#section, if needed>` | Current procedures and operating contracts | Experiment chronology |
| `<metrics path#section, if needed>` | Definitions, comparability and interpretation | Individual run results |
| `<design path#section, if needed>` | Approved design, constraints and acceptance gates | Live task progress |
| `<results path#section, if needed>` | Historical findings and supporting evidence | Current operating instructions |

Replace optional rows with applicable owners or remove them. A small repository may use README sections for several maintained roles. Keep project state distinct from task state: summarize and link to active tasks rather than copying their plans.

---

## Significant behavior

For traceability, treat a bug as significant when it can affect:

- <user-visible behavior, persisted data, public APIs, safety or security, model outputs, evaluation results, or other repository-specific outcomes>

---

## Working agreement (four-phase execution)

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
- At the start of a new task, initialize the workspace:
  1. Run `mkdir -p .agent/logs`.
  2. If `.agent/TASK_BRIEF.md` or `.agent/MEMORY.md` already exists, treat it as possible unfinished work and do not overwrite it without user confirmation.
  3. Otherwise, copy:
     - `docs/agent/TASK_BRIEF_TEMPLATE.md` to `.agent/TASK_BRIEF.md`
     - `docs/agent/MEMORY_TEMPLATE.md` to `.agent/MEMORY.md`
- Construct the task brief from relevant maintained guidance and prior closeouts according to `Prior task context (selective)` under `## Docs policy`.
- Do not edit code or tracked files in this phase.
- Use ≤10 shell commands and keep output concise (avoid long listings).
- Restate goal + success criteria.
- Identify the minimal relevant files and affected documentation owners, and why.
- Propose a plan + verification commands.
- Stop and ask before proceeding.

**Phase 1 deliverable:**
- Write the plan to `.agent/TASK_BRIEF.md` following the template and augmenting it where warranted.

`.agent/` is **untracked**. The brief may be updated in Phase 2.

At the end of Phase 1:
- Ensure `.agent/TASK_BRIEF.md` is up to date.
- If the client supports `/compact`, prompt the user to run it.

### Phase 2 — Implement + Learn (write + verify, no git history operations)
Goal: Execute the plan developed in Phase 1 and memorialized in `.agent/TASK_BRIEF.md`

Rules:
- You may edit files, but do NOT run:
  `git commit`, `git push`, `git merge`/`rebase`, `git reset --hard`, `git clean -fd`
- Keep diffs minimal; no broad “format-only” changes unless requested.
- After each coherent edit set:
  1. state intent + files touched
  2. apply changes
  3. run verification and report results
  4. show diff summary and key hunks
- Finish with `git status` and suggested commit message(s) (human will commit).

### Phase 3 — Review + Debug
Goal: Review the Phase 2 output with the user and remain in this phase until it is approved.

When debugging a failure or unexpected behavior found during review, follow this strict loop:
1. Reproduce the failure with the exact command provided.
2. Minimize the repro (smallest failing command/test).
3. Propose 1–2 hypotheses and what evidence would confirm each.
4. Add a targeted regression test when feasible.
5. Make a **surgical** fix (minimal files), re-run the failing test(s), then broaden coverage.
6. Update `.agent/TASK_BRIEF.md` with what changed and why; add a timestamp to all edits to preserve the chronology of decisions.

### Phase 4 — Task completion / closeout procedure
Goal: Summarize completed work and clean up.

After the user approves the Phase 3 result, the agent should:
1. Update `.agent/TASK_BRIEF.md`: set **Phase** to `Phase 4`, **State** to `in progress`, and **Last updated** to the current date and time.
2. Review this `AGENTS.md` and the task's acceptance criteria and verification evidence.
3. Apply `Documentation maintenance - all phases` to affected owners. Reconcile current guidance and state, preserve unique historical evidence, and verify affected instructions and links. Do not require new permanent guidance when none is warranted.
4. Produce a **closeout summary** (short, high-signal), using `.agent/MEMORY.md` and `.agent/TASK_BRIEF.md` as the sources of truth. Make it useful to a future Phase 1 agent constructing a task brief:
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
5. Follow `Cleanup at task closeout` below. Mark the task complete only after reconciliation and archival verification succeed; record any deferred work explicitly.

#### Cleanup at task closeout
At completion:
1. Before archiving, remove credentials, secrets, private URLs, sensitive user data, and unnecessary machine-specific paths.
2. Confirm the documentation reconciliation and closeout summary above are ready.
3. Create a folder `docs/agent/tasks/<task_slug>` under `docs/agent/tasks`.
   - e.g. <task_slug> = YYYYMMDD_HHMM_<short_topic>
4. Move `.agent/TASK_BRIEF.md` to `docs/agent/tasks/<task_slug>/`.
5. Move `.agent/MEMORY.md` to `docs/agent/tasks/<task_slug>/`.
6. Write the closeout into `docs/agent/tasks/<task_slug>/CLOSEOUT.md`.
7. Verify that `.agent/TASK_BRIEF.md` and `.agent/MEMORY.md` no longer exist, and the archive contains `TASK_BRIEF.md`, `MEMORY.md`, and `CLOSEOUT.md`.
8. In the archived `TASK_BRIEF.md`, set **State** to `complete` and update **Last updated**. If closeout fails, leave the task incomplete and report the remaining work and record locations.

---

## .agent/ folder policy

`.agent/` is **untracked**.

### Purpose
1. **Task-related documents** most notably TASK_BRIEF.md
2. **User-provided artifacts for debugging** (logs, traces, perf output) that the agent should inspect.
3. **Agent working memory externalization** when the chat context window is under pressure.

> Record new gotchas in `.agent/MEMORY.md`. Reconcile reusable findings with their maintained owners under `Documentation maintenance - all phases`; do not wait for closeout to correct guidance made misleading by implementation changes.

### Flat structure (preferred)
- `.agent/TASK_BRIEF.md` — compact task description, success criteria, and progress notes
- `.agent/MEMORY.md` — compact running notes related to the work process rather than the task definition itself
- `.agent/logs/` — log files and small extracted snippets

### `.agent/TASK_BRIEF.md`

`docs/agent/TASK_BRIEF_TEMPLATE.md` defines the document structure.

The task brief is the authoritative record of the task’s scope and execution state. Keep its goal, success criteria, status, decisions, and next steps current. Update it whenever the plan, scope, acceptance criteria, or execution state changes materially.

### `.agent/MEMORY.md`

`docs/agent/MEMORY_TEMPLATE.md` defines the document structure.

Memory is a compact investigation notebook for evidence that supports the task brief: reproduction commands, hypotheses, failed experiments, debugging evidence, gotchas, bug-impact records, and verification results. Keep it to **≤200 lines** when possible and use concise bullets.

Do not duplicate the task plan or current task status in memory. Findings are candidates for documentation reconciliation, not automatic additions to permanent guidance.

### Log naming convention
Store logs as:

- `.agent/logs/YYYYMMDD_HHMM_<topic>.log`

The agent may create filtered snippets alongside logs, e.g.:

- `.agent/logs/YYYYMMDD_HHMM_<topic>__excerpt.log`
- `.agent/logs/YYYYMMDD_HHMM_<topic>__grep_<pattern>.log`

Keep snippets **small** (e.g., ≤ 500 lines). Do not copy huge logs.

### When to externalize to `.agent/`
Externalize (write/update `.agent/MEMORY.md`) when any of these is true:
- The plan has evolved materially beyond Phase 1.
- Debugging involves multiple hypotheses or long traces.
- The session is getting long (check `/status` or a token status line).
- The agent is about to run `/compact`.

After externalizing:
- Update `.agent/MEMORY.md`

---

## Docs policy (protect the context window)
Do NOT read the entire docs tree by default.

Use `Documentation ownership` to select relevant maintained guidance. `AGENTS.md` supplies the working agreement; maintained docs explain the current repository; closeouts provide historical task context; deeper archived records support specific investigations. Superseded specs and plans are historical evidence, not current instructions.

In Phases 2–3, use the active task brief alongside maintained guidance. Revisit history when a new question requires it. If an applicable topic has no owner, identify an existing section or propose a focused owner in the task plan; do not create a full documentation suite by default.

### Prior task context (selective)

During Phase 1, use relevant closeouts to construct the task-specific `.agent/TASK_BRIEF.md`. Reconcile their findings with maintained documentation and the current repository. Historical decisions must still apply before being carried forward.

1. Use the scope specified by the user or `.agent/TASK_BRIEF.md`: explicit closeout paths, the last N relevant closeouts, or all closeouts associated with a named epoch or initiative.
2. If no scope is provided, inspect archive names first and read no more than the three most recent closeouts that are clearly relevant.
3. Read `CLOSEOUT.md` files first, newest to oldest. Read deeper archived task records only when a closeout leaves a question material to the plan unanswered.
4. Record the closeouts reviewed in the task brief and synthesize applicable decisions, constraints, gotchas and unresolved follow-ups there, with evidence links. Keep supporting investigation in memory; do not copy whole histories. If no closeouts are relevant, record none.
5. Do not scan or load the entire task archive by default.

For a large multi-task epoch, process closeouts in bounded batches and maintain a compact synthesis in `.agent/MEMORY.md`.
