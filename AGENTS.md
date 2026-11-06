# AGENTS.md — socrates-loop

You are an AI coding agent operating inside the `socrates-loop` repository.

This file is always-on guidance. Keep task scope and progress in `.agent/TASK_BRIEF.md`, and investigation evidence in `.agent/MEMORY.md`.

## Mission
Socrates Loop supplies Markdown templates and a Python installer for a four-phase, human-guided agent workflow. It installs repository guidance and task-record templates into target projects, including this repository itself.

## Source of truth
- `install.py` owns installation behavior, destination checks and CLI options.
- `templates/AGENTS_TEMPLATE.md` owns the distributed working agreement and guidance template.
- `templates/TASK_BRIEF_TEMPLATE.md` and `templates/MEMORY_TEMPLATE.md` own distributed task-record structures.
- `Agent-Zero-prompt.md` and `Update-prompt.md` own bootstrap and integration-update instructions.
- `tests/test_install.py` exercises installer behavior in isolated temporary checkouts and targets.

## Repo map
- `templates/` — generic source assets shipped to every target repository.
- `install.py` — standard-library Python CLI; no package dependencies.
- `tests/` — installer regression tests.
- `docs/agent/` — this repository's installed task templates and, after closeout, task archives.
- `docs/example-walkthrough.md` — illustrative complete workflow.
- `.agent/` — ignored active task records and diagnostic artifacts.

Do not scan `.agent/logs/`, `docs/assets/` or task archives by default. Select relevant historical closeouts under the docs policy below.

## Core workflow (essential agent commands)
`README.md` owns setup, self-installation, usage, updates and development checks. `Agent-Zero-prompt.md` owns bootstrap phases; `Update-prompt.md` owns integration-update checks. Use those procedures for installation work.

## Installation contracts
- Canonical files under `templates/` remain generic. Installation reads them and never customizes or removes them.
- Root `AGENTS_TEMPLATE.md` is temporary bootstrap staging, removed only at approved bootstrap closeout. Root `AGENTS.md` is this repository's installed guidance.
- Installed task templates live under `docs/agent/`; active task records live under ignored `.agent/`.
- Preserve existing guidance, task records, logs and archives. Conflicting templates and invalid destination types or symlinks must fail preflight before installation writes.
- `--dry-run` makes no filesystem changes. Relative targets resolve from the caller's working directory.
- Keep external target paths and CLI compatibility. Self-installation uses the same mapping as external installation.
- Source-template development and later integration updates are separate tasks. Use fixed source inputs throughout an integration update, as described in `Update-prompt.md`.

## Tests (default)
From the checkout root, as documented in `README.md#development-checks`:

```bash
python3 -B -m unittest discover -s tests -v
```

Tests use temporary directories. The Git ignore-behavior test skips if Git is unavailable.

## Coding/style conventions
- Use Python 3 and the standard library; follow the existing local style.
- Keep changes localized and avoid broad formatting-only edits.
- Keep shared policy and installed templates consistent with their canonical sources; document any approved deviation.

## Documentation ownership

| Document or section | Owns | Does not own |
|---|---|---|
| `AGENTS.md` | This repository's working agreement, essential invariants and routing | Task status, detailed procedures and historical results |
| `README.md` | Setup, usage, repository navigation and development checks | Investigation chronology |
| `templates/AGENTS_TEMPLATE.md` | Distributed guidance template and shared workflow policy | This repository's specific guidance |
| `templates/TASK_BRIEF_TEMPLATE.md`, `templates/MEMORY_TEMPLATE.md` | Distributed task-record structures | Active task content |
| `Agent-Zero-prompt.md` | Bootstrap instructions | Ongoing integration updates |
| `Update-prompt.md` | Integration-update scope and acceptance checks | General setup or task history |
| `docs/example-walkthrough.md` | Illustrative task lifecycle | Normative installation or policy rules |
| `.agent/TASK_BRIEF.md` | Active scope, acceptance criteria and execution state | Project-wide reference documentation |
| `.agent/MEMORY.md` | Investigation and verification evidence | Duplicate task plans |
| `docs/agent/tasks/<task_slug>/CLOSEOUT.md` | Historical outcomes, decisions, verification and follow-ups | Current operating instructions |
| Other archived task records | Supporting plans and evidence | Active task state |

The files under `docs/agent/` are installed copies of the canonical task templates, not independent documentation owners.

## Significant behavior
Treat bugs affecting installed file contents, preservation of user files or task history, installation safety, CLI behavior, or bootstrap/update policy as significant.

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
- Construct the task brief from relevant maintained guidance and, when available, prior closeouts according to `Prior task context (selective)` under `## Docs policy`.
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

### Purpose
1. **Task-related documents** most notably TASK_BRIEF.md
2. **User-provided artifacts for debugging** (logs, traces, perf output) that the agent should inspect.
3. **Agent working memory externalization** when the chat context window is under pressure.

> Record new gotchas in `.agent/MEMORY.md` and apply `Documentation maintenance - all phases` as guidance changes.

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

Use `Documentation ownership` to select relevant maintained guidance. Treat superseded specs and plans as historical evidence, not current instructions.

In Phases 2–3, use the active task brief alongside maintained guidance; revisit history when a new question requires it. If a topic has no owner, propose an existing section or a focused new document in the task plan.

### Prior task context (selective)

Skip archive review until a task has been completed and closed out. Thereafter, use relevant closeouts during Phase 1 to construct `.agent/TASK_BRIEF.md`, checking their findings against maintained guidance and the current repository.

1. Use the scope specified by the user or `.agent/TASK_BRIEF.md`: explicit closeout paths, the last N relevant closeouts, or all closeouts associated with a named epoch or initiative.
2. If no scope is provided, inspect archive names first and read no more than the three most recent closeouts that are clearly relevant.
3. Read `CLOSEOUT.md` files first, newest to oldest. Read deeper archived task records only when a closeout leaves a question material to the plan unanswered.
4. Record reviewed paths and synthesize applicable decisions, constraints, gotchas and unresolved follow-ups in the task brief, with evidence links. Keep supporting investigation in memory. If none are relevant, record none.
5. Do not scan or load the entire task archive by default.

For a large multi-task epoch, process closeouts in bounded batches and maintain a compact synthesis in `.agent/MEMORY.md`.
