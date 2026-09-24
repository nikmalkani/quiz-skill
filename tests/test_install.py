import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location("installer", Path(__file__).resolve().parents[1] / "scripts/install.py")
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)
        self.config = self.home / "config"

    def run_installer(self, *args):
        with patch.object(installer.Path, "home", return_value=self.home), \
             patch.dict(os.environ, {"XDG_CONFIG_HOME": str(self.config),
                                    "OPENCODE_CONFIG_DIR": str(self.config / "opencode")}, clear=False), \
             patch.object(sys, "argv", ["install.py", *args]):
            return installer.main()

    def test_installs_and_checks_shared_claude_and_opencode_links(self):
        self.assertEqual(self.run_installer(), 0)
        source = Path(__file__).resolve().parents[1]
        self.assertEqual((self.home / ".agents/skills/quiz").resolve(), source)
        self.assertEqual((self.home / ".claude/skills/quiz").resolve(), source)
        self.assertEqual((self.config / "opencode/commands/quiz.md").resolve(), source / "integrations/opencode/quiz.md")
        self.assertEqual(self.run_installer("--check"), 0)

    def test_conflict_prevents_partial_install(self):
        conflict = self.home / ".claude/skills/quiz"
        conflict.parent.mkdir(parents=True)
        conflict.write_text("another skill")
        self.assertEqual(self.run_installer(), 1)
        self.assertEqual(conflict.read_text(), "another skill")
        self.assertFalse((self.home / ".agents/skills/quiz").exists())


if __name__ == "__main__":
    unittest.main()
