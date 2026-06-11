import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from discover_packages import detect_release_type, detect_version, discover_packages


class DetectReleaseTypeTest(unittest.TestCase):
    def _mk(self, files):
        import tempfile
        d = Path(tempfile.mkdtemp())
        for name, content in files.items():
            (d / name).write_text(content)
        return d

    def test_node_when_package_json(self):
        d = self._mk({"package.json": '{"name": "@scope/foo", "version": "1.2.3"}'})
        self.assertEqual(detect_release_type(d), "node")

    def test_python_when_pyproject(self):
        d = self._mk({"pyproject.toml": '[project]\nname = "foo"\nversion = "0.4.0"\n'})
        self.assertEqual(detect_release_type(d), "python")

    def test_simple_when_gradle(self):
        d = self._mk({"build.gradle.kts": "plugins { java }"})
        self.assertEqual(detect_release_type(d), "simple")

    def test_simple_fallback(self):
        d = self._mk({"README.md": "x"})
        self.assertEqual(detect_release_type(d), "simple")


class DetectVersionTest(unittest.TestCase):
    def _mk(self, files):
        import tempfile
        d = Path(tempfile.mkdtemp())
        for name, content in files.items():
            (d / name).write_text(content)
        return d

    def test_node_version_from_package_json(self):
        d = self._mk({"package.json": '{"name": "foo", "version": "1.2.3"}'})
        self.assertEqual(detect_version(d, "node"), "1.2.3")

    def test_python_version_from_pyproject_project(self):
        d = self._mk({"pyproject.toml": '[project]\nname = "foo"\nversion = "0.4.0"\n'})
        self.assertEqual(detect_version(d, "python"), "0.4.0")

    def test_python_version_from_poetry(self):
        d = self._mk({"pyproject.toml": '[tool.poetry]\nname = "foo"\nversion = "9.9.9"\n'})
        self.assertEqual(detect_version(d, "python"), "9.9.9")

    def test_gradle_version_from_properties(self):
        d = self._mk({"build.gradle": "java", "gradle.properties": "version=2.0.1\n"})
        self.assertEqual(detect_version(d, "simple"), "2.0.1")

    def test_returns_none_when_unknown(self):
        d = self._mk({"build.gradle": "java"})
        self.assertIsNone(detect_version(d, "simple"))


class DiscoverPackagesTest(unittest.TestCase):
    def test_discovers_node_name_strips_scope(self):
        import tempfile
        root = Path(tempfile.mkdtemp())
        pkg = root / "packages" / "text-cli"
        pkg.mkdir(parents=True)
        (pkg / "package.json").write_text('{"name": "@papia/text-cli", "version": "0.3.0"}')
        result = discover_packages(str(root), ["packages/*"])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["path"], "packages/text-cli")
        self.assertEqual(result[0]["name"], "text-cli")
        self.assertEqual(result[0]["release_type"], "node")
        self.assertEqual(result[0]["current_version"], "0.3.0")


if __name__ == "__main__":
    unittest.main()
