#!/usr/bin/env python3
"""Install Socrates Loop's files in a project and display its zero prompts."""

import argparse
from pathlib import Path
import sys


TEMPLATES = (
    ("AGENTS_TEMPLATE.md", "AGENTS_TEMPLATE.md"),
    ("TASK_BRIEF_TEMPLATE.md", "docs/agent/TASK_BRIEF_TEMPLATE.md"),
    ("MEMORY_TEMPLATE.md", "docs/agent/MEMORY_TEMPLATE.md"),
)
DIRECTORIES = ("docs", "docs/agent", ".agent", ".agent/logs")


def check_destination(path, directory=False):
    """Check types without following installation paths through symlinks."""
    if path.is_symlink():
        raise ValueError("Installation path is a symbolic link: {}".format(path))
    if path.exists():
        correct_type = path.is_dir() if directory else path.is_file()
        if not correct_type:
            expected = "directory" if directory else "file"
            raise ValueError("Expected a {} at: {}".format(expected, path))
        return True
    return False


def ignore_addition(contents):
    """Preserve existing bytes and append an effective root ignore rule."""
    lines = contents.splitlines()
    rules = (b".agent/", b"/.agent/", b".agent", b"/.agent")
    for index in range(len(lines) - 1, -1, -1):
        if lines[index] in rules:
            # A later negation may undo the rule; append ours after it.
            if not any(line.startswith(b"!") for line in lines[index + 1:]):
                return b""
            break
    newline = b"\r\n" if b"\r\n" in contents else b"\n"
    separator = newline if contents and not contents.endswith(b"\n") else b""
    return separator + b"/.agent/" + newline


def install(target, dry_run=False):
    source = Path(__file__).resolve().parent
    target = target.expanduser().resolve()
    if not target.is_dir():
        raise ValueError("Target must be an existing project directory: {}".format(target))

    # Read all inputs and check all destinations before changing the project.
    templates = [
        (target / destination, (source / name).read_bytes())
        for name, destination in TEMPLATES
    ]
    prompts = (source / "Agent-Zero-prompt.md").read_text(encoding="utf-8")
    directories = []
    for name in DIRECTORIES:
        path = target / name
        if not check_destination(path, directory=True):
            directories.append(path)

    files = []
    unchanged = []
    for path, contents in templates:
        if check_destination(path):
            if path.read_bytes() != contents:
                raise ValueError(
                    "Refusing to overwrite a different file: {}\n"
                    "Reconcile it with the supplied template before installing.".format(path)
                )
            unchanged.append(path)
        else:
            files.append((path, contents))

    gitignore = target / ".gitignore"
    existing_ignore = gitignore.read_bytes() if check_destination(gitignore) else b""
    addition = ignore_addition(existing_ignore)

    print("{}: {}".format("Installation preview" if dry_run else "Installing Socrates Loop", target))
    for path in directories:
        if not dry_run:
            path.mkdir()
        print("  {} {}/".format("Would create" if dry_run else "Created", path.relative_to(target)))
    for path, contents in files:
        if not dry_run:
            with path.open("xb") as handle:
                handle.write(contents)
        print("  {} {}".format("Would create" if dry_run else "Created", path.relative_to(target)))
    for path in unchanged:
        print("  Unchanged {}".format(path.relative_to(target)))
    if addition:
        if not dry_run:
            with gitignore.open("ab") as handle:
                handle.write(addition)
        print("  {} /.agent/ to .gitignore".format("Would append" if dry_run else "Appended"))
    else:
        print("  Unchanged .gitignore")

    if dry_run:
        print("\nPreview only. Run without --dry-run to install and display the zero prompts.")
        return

    print("\nFiles are ready in: {}".format(target))
    if (target / "AGENTS.md").exists():
        print(
            "Existing AGENTS.md was preserved. Ask your agent to preserve its repository "
            "guidance when planning the integration."
        )
    if any((target / ".agent" / name).exists() for name in ("TASK_BRIEF.md", "MEMORY.md")):
        print(
            "Existing task records were preserved. Resume or close out that task "
            "before starting a bootstrap task."
        )
    print("\nOpen this project in your coding agent and copy the appropriate zero prompt below.")
    print("For a new project, replace MY_DESIGN.md with the path to your design specification.\n")
    print(prompts.strip())


def main():
    parser = argparse.ArgumentParser(
        description="Install Socrates Loop in a project and display the available zero prompts."
    )
    parser.add_argument(
        "target", type=Path,
        help="existing project directory; relative paths are resolved from your current directory",
    )
    parser.add_argument("--dry-run", action="store_true", help="preview changes without writing files")
    args = parser.parse_args()
    try:
        install(args.target, dry_run=args.dry_run)
    except (OSError, ValueError) as error:
        print("Error: {}".format(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
