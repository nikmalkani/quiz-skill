import importlib.util
from pathlib import Path
import random
import subprocess
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("sampler", Path(__file__).resolve().parents[1] / "scripts/sample.py")
sampler = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sampler)


class SamplingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        subprocess.run(["git", "init", "-q", str(self.root)], check=True)

    def write(self, name, content="def example():\n    return 42\n"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        return path

    def test_exclusions_and_untracked_source(self):
        self.write("src/app.py")
        self.write("tests/test_app.py")
        self.write(".gitignore", "ignored.py\n")
        for name in ["ignored.py", "node_modules/lib/a.js", "generated/a.py", "dist/a.js", "src/secrets.py", "src/a.min.js"]:
            self.write(name)
        self.write("src/linked.py").unlink()
        (self.root / "src/linked.py").symlink_to(self.root / "src/app.py")
        # Even tracked build files must stay excluded.
        subprocess.run(["git", "-C", str(self.root), "add", "dist/a.js"], check=True)
        _, groups = sampler.inventory(self.root)
        found = {p.as_posix() for paths in groups.values() for p in paths}
        self.assertEqual(found, {"src/app.py", "tests/test_app.py"})

    def test_variety_and_no_writes(self):
        for name in ["src/api/a.py", "src/ui/b.py", "tests/test_a.py"]:
            self.write(name)
        def snapshot():
            return {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        before = snapshot()
        draws = [sampler.sample(self.root, random.Random(i)) for i in range(80)]
        self.assertEqual({d["correct_option"] for d in draws}, set("ABCD"))
        self.assertEqual(len({d["file"] for d in draws}), 3)
        self.assertGreater(len({d["category_order"][0] for d in draws}), 8)
        self.assertEqual(snapshot(), before)
        for draw in draws:
            self.assertLessEqual(draw["read_lines"]["start"], draw["anchor_line"])
            self.assertGreaterEqual(draw["read_lines"]["end"], draw["anchor_line"])

    def test_reject_generated_binary_and_empty(self):
        with self.assertRaises(ValueError):
            sampler.sample(self.root)
        self.write("src/a.py", "# AUTO-GENERATED; DO NOT EDIT\nvalue = 1\n")
        self.write("src/b.py", "binary\0data")
        with self.assertRaises(ValueError):
            sampler.sample(self.root)
        self.write("src/good.py")
        self.assertEqual(sampler.sample(self.root)["file"], "src/good.py")


if __name__ == "__main__":
    unittest.main()
