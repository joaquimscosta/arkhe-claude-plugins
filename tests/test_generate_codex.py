#!/usr/bin/env python3
"""Tests for scripts/generate-codex-agents-md.py.

Runs the generator against the real `plugins/` tree (via a symlink under a
TemporaryDirectory) with output redirected to the temp dir, then asserts
the 32 KiB Codex limit and the bootstrap pointer presence.
"""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "generate-codex-agents-md.py"


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "generate_codex_agents_md", SCRIPT_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GenerateCodexAgentsMdTest(unittest.TestCase):
    """Run the generator once, then assert invariants over the outputs."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.module = _load_module()
        cls._tmpdir = tempfile.TemporaryDirectory()
        cls.tmp_root = Path(cls._tmpdir.name)
        cls.output_dir = cls.tmp_root / ".codex-marketplace"
        # Symlink plugins/ to the real plugins dir so REPO_ROOT-relative path
        # math (`md_path.relative_to(REPO_ROOT)`) stays inside the temp tree.
        (cls.tmp_root / "plugins").symlink_to(
            REPO_ROOT / "plugins", target_is_directory=True
        )

        cls._patches = [
            patch.object(cls.module, "REPO_ROOT", cls.tmp_root),
            patch.object(cls.module, "PLUGINS_DIR", cls.tmp_root / "plugins"),
            patch.object(cls.module, "OUTPUT_ROOT", cls.output_dir),
        ]
        for p in cls._patches:
            p.start()
        try:
            rc = cls.module.main()
        except SystemExit as exc:
            cls._teardown_patches()
            raise AssertionError(
                f"generate-codex-agents-md main() raised SystemExit: {exc}"
            ) from exc
        except Exception:
            cls._teardown_patches()
            raise
        if rc != 0:
            cls._teardown_patches()
            raise AssertionError(
                f"generate-codex-agents-md main() returned {rc}"
            )

    @classmethod
    def _teardown_patches(cls) -> None:
        for p in cls._patches:
            p.stop()
        cls._tmpdir.cleanup()

    @classmethod
    def tearDownClass(cls) -> None:
        cls._teardown_patches()

    def test_no_agents_md_exceeds_32kib(self) -> None:
        """All generated AGENTS.md / AGENTS.override.md are <= 32 KiB."""
        files = sorted(self.output_dir.rglob("AGENTS*.md"))
        self.assertGreater(len(files), 0, "no AGENTS.md files were generated")
        limit = self.module.SIZE_LIMIT_BYTES
        for f in files:
            size = f.stat().st_size
            self.assertLessEqual(
                size,
                limit,
                f"{f.relative_to(self.output_dir)} is {size} bytes "
                f"(limit {limit})",
            )

    def test_bootstrap_pointer_in_each_agents_md(self) -> None:
        """Every primary AGENTS.md includes the using-arkhe-skills pointer."""
        files = sorted(self.output_dir.rglob("AGENTS.md"))
        self.assertGreater(len(files), 0, "no primary AGENTS.md files generated")
        for f in files:
            content = f.read_text(encoding="utf-8")
            self.assertIn(
                "using-arkhe-skills",
                content,
                f"{f.relative_to(self.output_dir)} missing bootstrap pointer",
            )
            self.assertIn(
                "Bootstrap:",
                content,
                f"{f.relative_to(self.output_dir)} missing Bootstrap header",
            )

    def test_override_files_also_carry_bootstrap_pointer(self) -> None:
        """When an override file is emitted, it also includes the pointer."""
        for f in sorted(self.output_dir.rglob("AGENTS.override.md")):
            content = f.read_text(encoding="utf-8")
            self.assertIn(
                "using-arkhe-skills",
                content,
                f"{f.relative_to(self.output_dir)} missing bootstrap pointer",
            )


if __name__ == "__main__":
    unittest.main()
