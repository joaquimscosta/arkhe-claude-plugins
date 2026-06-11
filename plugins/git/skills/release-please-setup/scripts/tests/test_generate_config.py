#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from generate_config import DEFAULT_CHANGELOG_SECTIONS, generate_config


def _pkg(path, name, rtype="simple", ver="0.0.0"):
    return {"path": path, "name": name, "release_type": rtype, "current_version": ver}


class GenerateConfigTest(unittest.TestCase):
    def test_single_package_is_minimal(self):
        pkgs = [_pkg(".", "myapp", "node")]
        cfg = generate_config(pkgs, single=True)
        entry = cfg["packages"]["."]
        self.assertEqual(entry["release-type"], "node")
        self.assertEqual(entry["package-name"], "myapp")
        self.assertNotIn("include-component-in-tag", entry)
        self.assertNotIn("exclude-paths", entry)

    def test_monorepo_sets_component_tag_flags(self):
        pkgs = [_pkg("backend/a", "a"), _pkg("backend/b", "b")]
        cfg = generate_config(pkgs, single=False)
        a = cfg["packages"]["backend/a"]
        self.assertTrue(a["include-component-in-tag"])
        self.assertEqual(a["tag-separator"], "-")
        self.assertTrue(a["bump-minor-pre-major"])
        self.assertTrue(a["bump-patch-for-minor-pre-major"])

    def test_monorepo_exclude_paths_is_mutual_matrix(self):
        # Mirrors sellabella: each package excludes every OTHER package path.
        pkgs = [_pkg("backend/a", "a"), _pkg("backend/b", "b"), _pkg("backend/c", "c")]
        cfg = generate_config(pkgs, single=False)
        self.assertEqual(cfg["packages"]["backend/a"]["exclude-paths"], ["backend/b", "backend/c"])
        self.assertEqual(cfg["packages"]["backend/b"]["exclude-paths"], ["backend/a", "backend/c"])
        self.assertEqual(cfg["packages"]["backend/c"]["exclude-paths"], ["backend/a", "backend/b"])

    def test_includes_schema_and_changelog_sections(self):
        cfg = generate_config([_pkg("backend/a", "a")], single=False)
        self.assertIn("$schema", cfg)
        self.assertEqual(cfg["changelog-sections"], DEFAULT_CHANGELOG_SECTIONS)

    def test_preserves_release_type_per_package(self):
        pkgs = [_pkg("packages/cli", "cli", "node"), _pkg("packages/svc", "svc", "python")]
        cfg = generate_config(pkgs, single=False)
        self.assertEqual(cfg["packages"]["packages/cli"]["release-type"], "node")
        self.assertEqual(cfg["packages"]["packages/svc"]["release-type"], "python")


if __name__ == "__main__":
    unittest.main()
