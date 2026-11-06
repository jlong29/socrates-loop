"""Check evaluation inputs, not an LLM's ability to bootstrap them."""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


FIXTURES = Path(__file__).resolve().parent / "fixtures"


@unittest.skipUnless(shutil.which("bash") and shutil.which("python3"), "Fixture needs Bash and Python 3")
class BootstrapFixtureTests(unittest.TestCase):
    def test_wrappers_and_direct_command_under_failure_and_success(self):
        with tempfile.TemporaryDirectory(prefix="socrates-bootstrap-test-") as directory:
            root = Path(directory) / "repo"
            shutil.copytree(FIXTURES / "bootstrap", root)
            for control in (False, True):
                if control:
                    shutil.copyfile(FIXTURES / "bootstrap-control.sh", root / "check.sh")
                for configured in (False, True):
                    with self.subTest(control=control, configured=configured):
                        env = dict(os.environ)
                        env.pop("EXAMPLE_VALUE", None)
                        if configured:
                            env["EXAMPLE_VALUE"] = "42"
                        direct = subprocess.run(
                            ["python3", "-B", "-m", "unittest", "discover", "-s", "checks", "-v"],
                            cwd=root, env=env, capture_output=True, text=True,
                        )
                        wrapper = subprocess.run(
                            ["bash", "check.sh"], cwd=root, env=env, capture_output=True, text=True,
                        )
                        self.assertEqual(direct.returncode == 0, configured)
                        self.assertEqual(wrapper.returncode == 0, configured or not control)
                        for result in (direct, wrapper):
                            self.assertIn("Ran 1 test", result.stderr)
                            self.assertIn("OK" if configured else "FAILED (failures=1)", result.stderr)


if __name__ == "__main__":
    unittest.main()
