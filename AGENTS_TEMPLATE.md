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
5. Identify the repo’s durable docs that play the roles described in `## Docs policy`.

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

## Significant behavior

For traceability, treat a bug as significant when it can affect:

- <user-visible behavior, persisted data, public APIs, safety or security, model outputs, evaluation results, or other repository-specific outcomes>

---

## Working agreement (four-phase execution)

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
- Load prior task context according to `Prior task context (selective)` under `## Docs policy`.
- Do not edit code or tracked files in this phase.
- Use ≤10 shell commands and keep output concise (avoid long listings).
- Restate goal + success criteria.
- Identify the minimal relevant files and why.
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

When the task is complete (as defined in `.agent/TASK_BRIEF.md`), the agent should:
1. Update `.agent/TASK_BRIEF.md`: set **Phase** to `Phase 4`, **State** to `complete`, and **Last updated** to the current date and time.
2. Review this `AGENTS.md`.
3. Produce a **closeout summary** (short, high-signal), using `.agent/MEMORY.md` and `.agent/TASK_BRIEF.md` as the sources of truth:
   - Decisions made (and why)
   - New invariants/gotchas discovered
   - New/changed commands (CLI flags, scripts)
   - TODOs / follow-ups
   - Verification evidence (commands run)
   - Context lineage:
      - Epoch / initiative: `<name or none>`
      - Prior closeouts reviewed: `<exact paths or none>`
      - Recommended successor tasks: `<task slugs or short descriptions, or none>`
4. Update repo docs **only when the information is stable and reusable**:
   - Update `AGENTS.md` for durable workflow/invariants only.
   - Update the applicable durable documentation identified during template instantiation.
5. Follow the procedure defined in `Cleanup at task closeout` (defined below)

#### Cleanup at task closeout
At completion:
1. Before archiving, remove credentials, secrets, private URLs, sensitive user data, and unnecessary machine-specific paths.
2. Summarize “gotchas / decisions / commands / TODOs” and promote them to durable docs (see `Task completion / closeout procedure`).
3. Create a folder `docs/agent/tasks/<task_slug>` under `docs/agent/tasks`.
   - e.g. <task_slug> = YYYYMMDD_HHMM_<short_topic>
4. Move `.agent/TASK_BRIEF.md` to `docs/agent/tasks/<task_slug>/`.
5. Move `.agent/MEMORY.md` to `docs/agent/tasks/<task_slug>/`.
6. Write the closeout into `docs/agent/tasks/<task_slug>/CLOSEOUT.md`.
7. Verify that `.agent/TASK_BRIEF.md` and `.agent/MEMORY.md` no longer exist, and the archive contains `TASK_BRIEF.md`, `MEMORY.md`, and `CLOSEOUT.md`.

---

## .agent/ folder policy

`.agent/` is **untracked**.

### Purpose
1. **Task-related documents** most notably TASK_BRIEF.md
2. **User-provided artifacts for debugging** (logs, traces, perf output) that the agent should inspect.
3. **Agent working memory externalization** when the chat context window is under pressure.

> Policy: when the agent learns a new *gotcha* during Phase 2, it should record it in `.agent/MEMORY.md` and only promote it to durable docs during closeout.

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

Do not duplicate the task plan or current task status in memory. Promote durable findings to repository documentation during closeout.

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

Open docs only when needed, in this priority order:
1. The repo’s current workflow / operational workflow doc
2. The repo’s module / architecture map doc
3. The repo’s metrics / diagnostics doc
4. The repo’s experiment log / change log / results log

Treat these as historical unless explicitly requested:
- old specs
- old work plans
- archived project-state headers
- other superseded planning docs

If the repo does not yet have durable docs in these roles, ask the user which files are intended to fill them.

### Prior task context (selective)

When the current task continues earlier work:

1. Use the scope specified by the user or `.agent/TASK_BRIEF.md`: explicit closeout paths, the last N relevant closeouts, or all closeouts associated with a named epoch or initiative.
2. If no scope is provided, inspect archive names first and read no more than the three most recent closeouts that are clearly relevant.
3. Read `CLOSEOUT.md` files first, newest to oldest. Do not read archived `TASK_BRIEF.md` or `MEMORY.md` files unless a closeout identifies unresolved detail needed for the current task.
4. Record the closeouts reviewed and carry only relevant decisions, invariants, gotchas, and follow-ups into the current task brief or memory.
5. Do not scan or load the entire task archive by default.

For a large multi-task epoch, process closeouts in bounded batches and maintain a compact synthesis in `.agent/MEMORY.md`.
