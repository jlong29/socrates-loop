"""Exercise the installer CLI in isolated project directories."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO = Path(__file__).resolve().parents[1]
DEPLOYED = {
    "AGENTS_TEMPLATE.md": "AGENTS_TEMPLATE.md",
    "docs/agent/TASK_BRIEF_TEMPLATE.md": "TASK_BRIEF_TEMPLATE.md",
    "docs/agent/MEMORY_TEMPLATE.md": "MEMORY_TEMPLATE.md",
}


def snapshot(root):
    entries = {}
    for path in root.rglob("*"):
        if path.is_symlink():
            value = ("link", os.readlink(path))
        elif path.is_dir():
            value = ("directory",)
        else:
            value = ("file", path.read_bytes(), path.stat().st_mtime_ns)
        entries[str(path.relative_to(root))] = value
    return entries


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="socrates-install-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "installer checkout"
        self.target = self.root / "target project"
        self.caller = self.root / "caller"
        for directory in (self.source, self.target, self.caller):
            directory.mkdir()
        for name in ("install.py", "Agent-Zero-prompt.md", *DEPLOYED.values()):
            shutil.copyfile(REPO / name, self.source / name)

    def run_installer(self, *args):
        return subprocess.run(
            [sys.executable, "-B", str(self.source / "install.py"), *map(str, args)],
            cwd=self.caller, capture_output=True, text=True, encoding="utf-8",
        )

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")

    def test_installs_files_and_prints_both_zero_prompts(self):
        result = self.run_installer(self.target)
        self.assert_success(result)
        for destination, source in DEPLOYED.items():
            self.assertEqual(
                (self.target / destination).read_bytes(),
                (self.source / source).read_bytes(),
            )
        self.assertTrue((self.target / ".agent/logs").is_dir())
        self.assertEqual((self.target / ".gitignore").read_bytes(), b"/.agent/\n")
        self.assertFalse((self.target / "AGENTS.md").exists())
        self.assertFalse((self.target / ".agent/TASK_BRIEF.md").exists())
        self.assertFalse((self.target / ".agent/MEMORY.md").exists())
        prompts = (self.source / "Agent-Zero-prompt.md").read_text(encoding="utf-8")
        self.assertIn(prompts.strip(), result.stdout)
        self.assertIn("## Existing Repo", result.stdout)
        self.assertIn("## New Repo with design specification", result.stdout)
        self.assertIn(str(self.target), result.stdout)

    def test_relative_target_is_resolved_from_the_callers_directory(self):
        result = self.run_installer("../target project")
        self.assert_success(result)
        self.assertTrue((self.target / "AGENTS_TEMPLATE.md").is_file())
        self.assertEqual(list(self.caller.iterdir()), [])
        self.assertFalse((self.source / "docs").exists())

    def test_dry_run_does_not_modify_the_project(self):
        (self.target / "README.md").write_text("Project documentation\n")
        before = snapshot(self.target)
        result = self.run_installer("--dry-run", self.target)
        self.assert_success(result)
        self.assertIn("Would create", result.stdout)
        self.assertIn("Would append", result.stdout)
        self.assertIn("Preview only", result.stdout)
        self.assertEqual(snapshot(self.target), before)

    def test_repeat_install_preserves_guidance_task_records_and_logs(self):
        preserved = {
            "AGENTS.md": "Existing project guidance\n",
            ".agent/TASK_BRIEF.md": "Unfinished task\n",
            ".agent/MEMORY.md": "Investigation evidence\n",
            ".agent/logs/experiment.log": "Experiment output\n",
            "docs/agent/tasks/earlier/CLOSEOUT.md": "Earlier task\n",
        }
        for name, contents in preserved.items():
            path = self.target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(contents)
        self.assert_success(self.run_installer(self.target))
        for name, contents in preserved.items():
            self.assertEqual((self.target / name).read_text(), contents)
        before = snapshot(self.target)
        result = self.run_installer(self.target)
        self.assert_success(result)
        self.assertEqual(snapshot(self.target), before)
        self.assertIn("Existing AGENTS.md was preserved", result.stdout)
        self.assertIn("Existing task records were preserved", result.stdout)

    def test_preserves_ignore_contents_and_line_endings(self):
        cases = (
            (b"build/", b"build/\n/.agent/\n"),
            (b"build/\r\n", b"build/\r\n/.agent/\r\n"),
            (b"# non-UTF8: \xff\n", b"# non-UTF8: \xff\n/.agent/\n"),
            (b".agent/\nbuild/\n", b".agent/\nbuild/\n"),
            (b"/.agent/\r\n", b"/.agent/\r\n"),
            (b".agent", b".agent"),
            (b".agent/\n!.agent/\n", b".agent/\n!.agent/\n/.agent/\n"),
        )
        for initial, expected in cases:
            with self.subTest(initial=initial):
                ignore = self.target / ".gitignore"
                ignore.write_bytes(initial)
                self.assert_success(self.run_installer(self.target))
                self.assertEqual(ignore.read_bytes(), expected)
                before = snapshot(self.target)
                self.assert_success(self.run_installer(self.target))
                self.assertEqual(snapshot(self.target), before)

    @unittest.skipUnless(shutil.which("git"), "Git is needed to check ignore behavior")
    def test_git_ignores_agent_records_even_after_a_negated_rule(self):
        subprocess.run(["git", "init", "--quiet", str(self.target)], check=True, capture_output=True)
        (self.target / ".gitignore").write_text(".agent/\n!.agent/\n")
        self.assert_success(self.run_installer(self.target))
        result = subprocess.run(
            ["git", "check-ignore", ".agent/MEMORY.md"],
            cwd=self.target, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), ".agent/MEMORY.md")

    def test_conflicting_template_stops_before_any_changes(self):
        conflict = self.target / "docs/agent/MEMORY_TEMPLATE.md"
        conflict.parent.mkdir(parents=True)
        conflict.write_text("A customized memory template\n")
        before = snapshot(self.target)
        result = self.run_installer(self.target)
        self.assertEqual(result.returncode, 1)
        self.assertIn("Refusing to overwrite", result.stderr)
        self.assertIn(str(conflict), result.stderr)
        self.assertEqual(snapshot(self.target), before)

    def test_destination_type_conflicts_stop_before_any_changes(self):
        conflicts = (
            ("docs", False), ("docs/agent", False),
            (".agent", False), (".agent/logs", False),
            ("AGENTS_TEMPLATE.md", True), (".gitignore", True),
            ("docs/agent/MEMORY_TEMPLATE.md", True),
        )
        for index, (name, is_directory) in enumerate(conflicts):
            with self.subTest(name=name):
                target = self.root / ("collision-{}".format(index))
                conflict = target / name
                conflict.parent.mkdir(parents=True)
                if is_directory:
                    conflict.mkdir()
                else:
                    conflict.write_text("Existing content\n")
                before = snapshot(target)
                result = self.run_installer(target)
                self.assertEqual(result.returncode, 1)
                self.assertIn("Expected a", result.stderr)
                self.assertEqual(snapshot(target), before)

    def test_symlink_destinations_stop_before_any_changes(self):
        outside = self.root / "outside"
        outside.mkdir()
        sentinel = outside / "keep.txt"
        sentinel.write_text("Keep this file\n")
        original = snapshot(outside)
        for index, name in enumerate(("docs", ".agent/logs", "AGENTS_TEMPLATE.md", ".gitignore")):
            with self.subTest(name=name):
                target = self.root / ("symlink-{}".format(index))
                link = target / name
                link.parent.mkdir(parents=True)
                directory = name in ("docs", ".agent/logs")
                try:
                    link.symlink_to(outside if directory else sentinel, target_is_directory=directory)
                except (OSError, NotImplementedError):
                    self.skipTest("Symbolic links are unavailable")
                before = snapshot(target)
                result = self.run_installer(target)
                self.assertEqual(result.returncode, 1)
                self.assertIn("symbolic link", result.stderr)
                self.assertEqual(snapshot(target), before)
                self.assertEqual(snapshot(outside), original)

    def test_missing_source_file_stops_before_any_changes(self):
        for name in ("MEMORY_TEMPLATE.md", "Agent-Zero-prompt.md"):
            with self.subTest(name=name):
                path = self.source / name
                contents = path.read_bytes()
                path.unlink()
                result = self.run_installer(self.target)
                self.assertEqual(result.returncode, 1)
                self.assertIn(name, result.stderr)
                self.assertEqual(snapshot(self.target), {})
                path.write_bytes(contents)

    def test_missing_or_non_directory_targets_are_rejected(self):
        missing = self.root / "missing project"
        file_target = self.root / "file.txt"
        file_target.write_text("Keep this file\n")
        for target in (missing, file_target):
            with self.subTest(target=target):
                result = self.run_installer(target)
                self.assertEqual(result.returncode, 1)
                self.assertIn("existing project directory", result.stderr)
        self.assertFalse(missing.exists())
        self.assertEqual(file_target.read_text(), "Keep this file\n")

    def test_new_zero_prompts_are_printed_from_the_source_document(self):
        with (self.source / "Agent-Zero-prompt.md").open("a", encoding="utf-8") as handle:
            handle.write("\n## Another zero prompt\n\nA newly available prompt.\n")
        result = self.run_installer(self.target)
        self.assert_success(result)
        self.assertIn("## Another zero prompt\n\nA newly available prompt.", result.stdout)

    def test_help_and_required_target(self):
        result = self.run_installer("--help")
        self.assert_success(result)
        self.assertIn("--dry-run", result.stdout)
        self.assertIn("zero prompts", result.stdout)
        result = self.run_installer()
        self.assertEqual(result.returncode, 2)
        self.assertIn("target", result.stderr)
        self.assertEqual(snapshot(self.target), {})


if __name__ == "__main__":
    unittest.main()
