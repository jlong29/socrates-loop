# Zero prompt for repo setup

## Existing Repo

Read `AGENTS_TEMPLATE.md` and follow its four-phase working agreement:

1. **Plan:** Inspect the repository and existing documentation without editing tracked files. Initialize `.agent/` as directed by Phase 1. Write a task brief for creating a repo-specific root `AGENTS.md`, mapping documentation ownership to existing files or sections; stop for approval.
2. **Implement:** Follow the template's instantiation instructions: customize repository guidance and ownership, prune unused roles, and preserve all policy from `## Working agreement` onward unless the user explicitly changes it.
3. **Review:** Incorporate feedback and use the debugging loop for problems found during review. Wait for approval.
4. **Close out:** Remove `AGENTS_TEMPLATE.md`, retain the finalized root `AGENTS.md`, and complete Phase 4 reconciliation and archival.

## New Repo with design specification

Read `AGENTS_TEMPLATE.md` and `MY_DESIGN.md`, then follow the template's four-phase working agreement:

1. **Plan:** Inspect the design and existing repository files without editing tracked files. Initialize `.agent/` as directed by Phase 1. Write a task brief for creating a repo-specific root `AGENTS.md`, identifying applicable documentation owners and unmet needs; stop for approval.
2. **Implement:** Follow the template's instantiation instructions: customize repository guidance and ownership, prune unused roles, and preserve all policy from `## Working agreement` onward unless the user explicitly changes it. Base guidance on the design without presenting unimplemented files or commands as existing functionality.
3. **Review:** Incorporate feedback and use the debugging loop for problems found during review. Wait for approval.
4. **Close out:** Remove `AGENTS_TEMPLATE.md`, retain the finalized root `AGENTS.md`, and complete Phase 4 reconciliation and archival.
