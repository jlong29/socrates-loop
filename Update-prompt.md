# Update prompt for an installed repository

Update this repository's Socrates Loop integration using the source checkout identified by the user. Read the target repository's `AGENTS.md` and follow its existing four-phase working agreement. Updating Socrates Loop is an ordinary task under that agreement.

Start only when no other task is active. If `.agent/TASK_BRIEF.md` or `.agent/MEMORY.md` exists, establish whether this is a continuation of the same update task; otherwise, complete the existing task's normal closeout first. Never overwrite task records. The update task's own records remain active during implementation and verification.

For a repository without an existing integration, use the source README's installation and bootstrap instructions.

## Phase 1: plan the update

- Read the selected source's `README.md`, `AGENTS_TEMPLATE.md`, `TASK_BRIEF_TEMPLATE.md`, and `MEMORY_TEMPLATE.md`. Treat them as the proposed destination for the integration; the target's existing agreement governs this task's approvals and closeout.
- Record the source location and revision in the task brief. Identify relevant uncommitted source changes or record content hashes so the reference is unambiguous. Use the same source contents throughout the task; do not refresh or modify that checkout mid-update. If supplied a public URL, obtain the required files at one identified revision before comparing them.
- Inspect the target's installed policy, templates, relevant documentation owners, and existing local changes. Record enough of the starting state to distinguish this task's edits from pre-existing work.
- Compare the shared policy from the unique `## Working agreement (four-phase execution)` heading onward, and both templates under `docs/agent/`, with the source. Do not treat headings inside code fences or comments as boundaries. Resolve a missing or ambiguous boundary in the plan.
- Identify repository-specific adaptations needed before that heading. For example, reconcile an existing documentation-routing section into `Documentation ownership`, retaining its useful mappings and unique instructions.
- Describe proposed changes, preserved content, and verification in the normal task brief. Explicitly identify local policy/template customizations and propose whether to retain, relocate, or replace them. An update request alone does not authorize silently discarding those customizations.

Stop for approval under the existing working agreement.

## Phase 2: implement and verify

Make the approved changes in small sets. Copy fixed policy and template text directly from the selected source. Adapt repository-specific sections using actual files, commands, and contracts; remove unused optional roles instead of leaving placeholders or inventing documents.

Preserve unrelated work, historical task records, and unique repository guidance. Keep existing installation metadata unless its disposition is explicitly included in the approved plan. Do not recreate the temporary root `AGENTS_TEMPLATE.md` after bootstrap.

After each change set, use file comparisons and repository inspection to evaluate the result:

| Area | Acceptance check |
|---|---|
| Shared policy | Compare the complete policy region with the selected source; only LF/CRLF differences may be normalized. Explain any deliberate deviation explicitly. |
| Installed templates | Compare `docs/agent/TASK_BRIEF_TEMPLATE.md` and `docs/agent/MEMORY_TEMPLATE.md` with their source files; preserve active task records. |
| Repository-specific guidance | Review every change against the approved scope and the starting content; preserve instructions and constraints outside that scope. |
| Documentation ownership | Confirm one coherent ownership section, populated mappings grounded in actual documentation, and no duplicate routing or unused placeholder roles. Check referenced files/sections where applicable; archive path patterns and future task records are not missing current documents. |
| Change scope | Inspect the diff and file set against the starting state; account for pre-existing edits and confirm unrelated files and archives are unchanged. |

Correct mismatches within the approved scope and repeat the comparisons until no further installation edits are needed. Record the commands, results, and semantic review evidence in task memory. Recheck the source identity before reporting completion; source changes require a new comparison and review of any resulting scope change.

Do not equate textual equality with correct repository-specific mappings, or label an approved policy deviation as an exact match. Report unresolved issues and deliberate deviations separately. A repeat comparison against the same source should require no installation changes; normal task records and closeout artifacts are expected to evolve.

## Phase 3: review

Present the diff, source revision/content identity, verification results, and any remaining issues or deliberate deviations. Follow the existing review/debug loop and wait for approval before closeout.

## Phase 4: close out

Follow the normal documentation reconciliation and archival procedure. Record the source identity, significant adaptations, verification, and any accepted deviations or follow-ups in the closeout. The task brief and closeout provide provenance; this workflow requires no separate installation-state database.
