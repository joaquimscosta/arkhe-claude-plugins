#!/usr/bin/env python3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from seed_manifest import seed_manifest


def _pkg(path, ver):
    return {"path": path, "name": path.split("/")[-1], "release_type": "node", "current_version": ver}


class SeedManifestTest(unittest.TestCase):
    def test_greenfield_uses_initial_zero(self):
        pkgs = [_pkg("packages/a", "1.2.3"), _pkg("packages/b", None)]
        m = seed_manifest(pkgs, mode="greenfield")
        self.assertEqual(m, {"packages/a": "0.0.0", "packages/b": "0.0.0"})

    def test_greenfield_respects_custom_initial(self):
        m = seed_manifest([_pkg("packages/a", None)], mode="greenfield", initial="0.1.0")
        self.assertEqual(m, {"packages/a": "0.1.0"})

    def test_migration_uses_detected_versions(self):
        pkgs = [_pkg("packages/a", "1.2.3"), _pkg("packages/b", "4.0.0")]
        m = seed_manifest(pkgs, mode="migration")
        self.assertEqual(m, {"packages/a": "1.2.3", "packages/b": "4.0.0"})

    def test_migration_falls_back_to_initial_when_version_missing(self):
        pkgs = [_pkg("packages/a", "1.2.3"), _pkg("packages/b", None)]
        m = seed_manifest(pkgs, mode="migration")
        self.assertEqual(m, {"packages/a": "1.2.3", "packages/b": "0.0.0"})


if __name__ == "__main__":
    unittest.main()
