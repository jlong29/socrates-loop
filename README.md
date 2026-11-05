![Unable to load image asset](docs/assets/social-preview.png)

# Socrates Loop

Socrates Loop is a small set of Markdown templates for bootstrapping repository-specific instructions and a four-phase AI-assisted development workflow. It separates durable repository guidance from task plans, working memory, and diagnostic artifacts.

## How it works

Socrates Loop turns a long-running agent task into a sequence of inspectable, verifiable stages:

**Specification → Plan → Implement → Review → Learn → Next task**

1. **Plan:** The agent studies the repository, relevant maintained docs and any completed task closeouts without editing tracked files, then writes a task brief with constraints, milestones, success criteria, risks, and verification commands. Work pauses for approval.
2. **Implement:** The agent executes the approved plan in small change sets, verifies each set, and records investigation evidence outside the permanent repository guidance.
3. **Review and debug:** The user reviews the result. The agent handles failures with a reproduce, hypothesize, test, and surgical-fix loop.
4. **Close out:** The agent reconciles affected documentation, replacing superseded guidance and preserving unique historical evidence. It archives sanitized task records and a closeout that supports future Phase 1 planning, then marks the task complete.

## Why it works

- **Documentation has bounded owners.** Each topic has an owner; superseded guidance is replaced rather than accumulated.
- **Intent is inspectable before implementation.** Milestones, success criteria, invariants, and verification commands make drift visible while it is still inexpensive to correct.
- **Working evidence has a defined home.** Reproduction commands, hypotheses, failed experiments, and bug-impact records live in memory rather than being lost in chat history.
- **Human approval remains part of the loop.** The workflow creates explicit checkpoints before implementation and before closeout.
- **Useful history informs the next plan.** Relevant closeouts supply decisions, outcomes and follow-ups; deeper archives resolve questions left unanswered.

This is a human-guided engineering workflow, not an autonomous orchestration system. Its purpose is to help an agent work for longer without losing the goal, repeating mistakes, or silently changing important assumptions.

## Documentation roles

The ownership table in `AGENTS.md` maps roles to repository-specific files or sections. The maintenance rules live under its working agreement and apply throughout the task.

| Layer | Purpose |
|---|---|
| `AGENTS.md` | Working rules, essential constraints and documentation routing |
| Maintained documentation, including `README.md` | Current behavior, procedures, architecture and project state, as applicable |
| `.agent/TASK_BRIEF.md` and `.agent/MEMORY.md` | Active task scope/state and supporting investigation |
| Archived `CLOSEOUT.md` | Historical task context used primarily to construct a new task brief in Phase 1 |
| Deeper archived task records | Supporting detail when a closeout leaves a material question unanswered |

Small repositories can use README sections for several maintained roles. Separate project-state, architecture, operations, metrics or design documents are optional. Closeout reviews affected owners; it does not require every task to add permanent guidance.

## Repository contents

| File | Purpose |
| --- | --- |
| [`install.py`](install.py) | Installs the templates in a target project and displays the zero prompts. |
| [`templates/AGENTS_TEMPLATE.md`](templates/AGENTS_TEMPLATE.md) | Customizable repository guidance and the four-phase working agreement. |
| [`Agent-Zero-prompt.md`](Agent-Zero-prompt.md) | Bootstrap prompts for existing repositories and new repositories that begin with a design specification. |
| [`Update-prompt.md`](Update-prompt.md) | Instructions and acceptance checks for updating an installed integration as a normal task. |
| [`templates/TASK_BRIEF_TEMPLATE.md`](templates/TASK_BRIEF_TEMPLATE.md) | Task scope, status, milestones, success criteria, implementation plan, and decisions. |
| [`templates/MEMORY_TEMPLATE.md`](templates/MEMORY_TEMPLATE.md) | Compact investigation evidence, gotchas, bug-impact records, and verification results. |
| [`docs/assets/social-preview.png`](docs/assets/social-preview.png) | Source image for the repository’s GitHub social preview. |
| [`LICENSE`](LICENSE) | MIT license terms. |

## Setup

Requires Python 3 and an existing target repository:

```bash
git clone https://github.com/jlong29/socrates-loop.git
python3 socrates-loop/install.py /path/to/your/repo
```

Use an absolute path or one relative to your current directory; quote paths containing spaces. Add `--dry-run` to preview changes. On Windows, use `py` if that is your Python launcher.

The installer reads canonical sources from its checkout's `templates/` directory. It copies `AGENTS_TEMPLATE.md` to the target root as temporary bootstrap input and the task brief and memory templates to `docs/agent/`, creates `.agent/logs/`, updates `.gitignore`, and prints both zero prompts. Existing guidance and task records are preserved; conflicting templates stop installation.

### Installing into this repository

Use the same installer from the Socrates Loop checkout:

```bash
python3 install.py . --dry-run
python3 install.py .
```

Follow the Existing Repo Zero prompt below. Canonical files under `templates/` remain generic distribution inputs. Root `AGENTS.md` and the templates under `docs/agent/` are this repository's installed integration. Bootstrap creates repository-specific guidance from the staged root `AGENTS_TEMPLATE.md`; approved closeout removes only that staging file. The checkout remains usable for installing into other repositories afterward.

If the checkout already has `AGENTS.md` and installed task templates, use the update workflow for changes to its integration. Re-running initial setup can recreate root staging after bootstrap; it preserves existing guidance and rejects conflicting templates, so it is not an integration updater.

---

## Getting Started

Open the target repository in your coding agent and paste the appropriate printed zero prompt, including its source provenance: **Existing Repo** or **New Repo with design specification**. For the latter, replace `MY_DESIGN.md` with your design document's path. Both prompts are also in [`Agent-Zero-prompt.md`](Agent-Zero-prompt.md).

Each printed prompt includes the source revision when Git metadata is available, the modification state of the installer/prompt/canonical templates, and SHA-256 hashes of the installed files and source prompt. Hashes identify the supplied bytes even for modified or unpacked sources. The agent verifies installed-file hashes and retains provenance in the task brief and closeout; no separate installation metadata file is created. When using a static prompt, the agent records installed-template hashes and marks unavailable source identity explicitly.

Bootstrap includes a bounded review of recommended build/test commands, including failure reporting. The agent reconciles findings with existing documentation owners and distinguishes executed checks, source inspection, and unverified assumptions before asking for review.

See the [Ask Socrates walkthrough](docs/example-walkthrough.md) for a complete task, including resuming work in a new session.

## Updating an installation

Updating Socrates Loop is a Socrates Loop task in the target repository. Its existing four-phase working agreement supplies planning, approval, implementation, review, and closeout. Start when no other task is active; the update itself has normal task records.

Refresh or select a local Socrates Loop checkout, then open your coding agent in the target repository. For example:

```bash
cd /path/to/socrates-loop
git pull --ff-only
cd /path/to/your/repo
```

Give the agent this request, replacing the source path:

> Update this repository's Socrates Loop integration using `/path/to/socrates-loop` as the source. Read that checkout's `Update-prompt.md` and follow this repository's existing four-phase working agreement. Begin with a Phase 1 task brief and stop for approval. Preserve repository-specific guidance and history; explicitly propose any structural changes or replacement of customized policy.

[The update prompt](Update-prompt.md) supplies update-specific scope and acceptance checks. The agent compares the installed policy and templates directly with the selected source, adapts repository-specific sections such as documentation ownership, and iterates on verification before presenting the result for review. The task brief and closeout record the source revision, changes, and evidence.

The installer remains the initial setup path. Updating needs no prior upstream checkout or installation-state database: the agent reviews differences between the current integration and the selected source. The plan identifies local customizations and seeks approval for their disposition.

An agent may also obtain the source from the public repository at one identified revision and follow the same prompt. A local checkout makes the exact reference available without network access during the task. Keep the source inputs fixed until the update is complete.

For self-updates, finish and close out the source-template development task first. Then start a separate integration-update task using this checkout as the source. Record hashes of the three canonical templates and the source README and prompts at planning time, and recheck them before handing off for review. Only installed integration files and normal task records change during that update. If source inputs need further edits, return to planning and establish a new fixed reference before continuing. See [the update prompt](Update-prompt.md#phase-1-plan-the-update) for source-layout compatibility and provenance checks.

## Development checks

Run the installer regression suite from this checkout:

```bash
python3 -B -m unittest discover -s tests -v
```

Tests use isolated temporary projects and do not update another repository. Git-dependent checks skip when Git is unavailable; evaluation-fixture checks require Bash and Python 3. These tests verify installer and fixture behavior, not the quality of an agent's generated guidance.

### Bootstrap evaluation

Use fresh copies of the [small fixture](tests/fixtures/bootstrap/README.md) to evaluate bootstrap instructions. From this checkout, prepare each trial:

```bash
bootstrap_eval_dir="$(mktemp -d)"
cp -R tests/fixtures/bootstrap/. "$bootstrap_eval_dir/"
# For the control trial, also run this before installation:
# cp tests/fixtures/bootstrap-control.sh "$bootstrap_eval_dir/check.sh"
git -C "$bootstrap_eval_dir" init -q
python3 install.py "$bootstrap_eval_dir"
```

Open only the temporary project in a fresh agent session and use the printed Existing Repo prompt. Follow normal plan, review, and closeout approvals for a documentation-only bootstrap; do not supply the expected findings below as hints. Run both variants repeatedly with the same model/settings and fixed Socrates Loop source inputs. Record outcomes and commands in evaluation task records; do not infer reliability from one successful run.

| Review criterion | Expected evidence |
|---|---|
| Command prerequisites | README Testing explains `EXAMPLE_VALUE=42`, repository-root execution, and discovery under `checks/`. |
| Failure reporting | Default fixture: identify the wrapper's masked failure, provide the direct unittest command, and retain the defect/follow-up under the existing bug policy. Control: recognize correct failure propagation without inventing a wrapper defect. |
| Evidence and scope | Distinguish source inspection from executed checks and unresolved assumptions; preserve application/test scripts during the documentation-only bootstrap. |
| Documentation ownership | Update existing README sections and keep essential references in AGENTS; this fixture needs no separate diagnostics/results documents. |
| Installation and closeout | Preserve shared policy and task templates, retain source provenance, remove only staging after approval, and archive all three task records with working links. |

Without `EXAMPLE_VALUE`, the one test fails. The default wrapper returns 0 afterward; the control and direct unittest command return nonzero. With `EXAMPLE_VALUE=42`, all three succeed. The regression suite verifies these fixture properties; agent evaluation remains a separate exercise.

Feedback and contributions are welcome. [Open an issue](https://github.com/jlong29/socrates-loop/issues/new) to report a problem or suggest an improvement, or [submit a pull request](https://github.com/jlong29/socrates-loop/pulls) with a proposed change.

---

## License

This project is available under the [MIT License](LICENSE).
