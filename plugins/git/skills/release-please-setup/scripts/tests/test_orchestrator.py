import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from release_please_setup import build_artifacts, version_from_git_tag  # noqa: E402


def _mk_monorepo():
    root = Path(tempfile.mkdtemp())
    a = root / "packages" / "cli"
    a.mkdir(parents=True)
    (a / "package.json").write_text('{"name": "@x/cli", "version": "1.4.0"}')
    b = root / "packages" / "svc"
    b.mkdir(parents=True)
    (b / "pyproject.toml").write_text('[project]\nname = "svc"\nversion = "2.0.1"\n')
    return root


class BuildArtifactsTest(unittest.TestCase):
    def test_migration_monorepo_produces_config_and_manifest(self):
        root = _mk_monorepo()
        config, manifest = build_artifacts(
            str(root), globs=["packages/*"], single=False, mode="migration"
        )
        # Two packages discovered, correct release-types
        self.assertEqual(config["packages"]["packages/cli"]["release-type"], "node")
        self.assertEqual(config["packages"]["packages/svc"]["release-type"], "python")
        # Mutual exclude-paths
        self.assertEqual(config["packages"]["packages/cli"]["exclude-paths"], ["packages/svc"])
        # Manifest carries migrated versions
        self.assertEqual(manifest, {"packages/cli": "1.4.0", "packages/svc": "2.0.1"})

    def test_greenfield_zeros_manifest(self):
        root = _mk_monorepo()
        _, manifest = build_artifacts(
            str(root), globs=["packages/*"], single=False, mode="greenfield"
        )
        self.assertEqual(set(manifest.values()), {"0.0.0"})


if __name__ == "__main__":
    unittest.main()
