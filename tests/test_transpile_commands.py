#!/usr/bin/env python3
"""Tests for scripts/transpile-commands.py.

Verifies idempotency and the subagent-heavy banner+inline behavior in
isolation against synthetic plugin layouts in a TemporaryDirectory.
"""
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "transpile-commands.py"


def _load_module():
    spec = importlib.util.spec_from_file_location("transpile_commands", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TranspileCommandsTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmp_root = Path(self._tmpdir.name)
        self.plugins_dir = self.tmp_root / "plugins"
        self.output_dir = self.tmp_root / ".gemini-extensions"
        self.module = _load_module()
        self._patches = [
            patch.object(self.module, "REPO_ROOT", self.tmp_root),
            patch.object(self.module, "PLUGINS_DIR", self.plugins_dir),
            patch.object(self.module, "OUTPUT_ROOT", self.output_dir),
        ]
        for p in self._patches:
            p.start()
        self.addCleanup(self._cleanup)

    def _cleanup(self) -> None:
        for p in self._patches:
            p.stop()
        self._tmpdir.cleanup()

    def _make_command(self, plugin: str, name: str, description: str, body: str) -> Path:
        cmd_dir = self.plugins_dir / plugin / "commands"
        cmd_dir.mkdir(parents=True, exist_ok=True)
        path = cmd_dir / f"{name}.md"
        path.write_text(
            f"---\ndescription: {description}\n---\n\n{body}\n",
            encoding="utf-8",
        )
        return path

    def _make_agent(self, plugin: str, name: str, body: str) -> Path:
        agent_dir = self.plugins_dir / plugin / "agents"
        agent_dir.mkdir(parents=True, exist_ok=True)
        path = agent_dir / f"{name}.md"
        path.write_text(
            f"---\nname: {name}\ndescription: agent\n---\n\n{body}\n",
            encoding="utf-8",
        )
        return path

    def test_idempotent_no_diff(self) -> None:
        """Running transpile twice produces no diff in output files."""
        self._make_command("alpha", "hello", "Says hello", "Hello {{name}}!")
        self._make_command(
            "alpha", "build", "Builds something", "Build with $ARGUMENTS"
        )

        self.assertEqual(self.module.main(), 0)
        snapshot = {
            p: p.read_bytes() for p in sorted(self.output_dir.rglob("*.toml"))
        }
        self.assertGreater(len(snapshot), 0, "first run produced no .toml files")

        self.assertEqual(self.module.main(), 0)
        for path, expected in snapshot.items():
            self.assertEqual(
                path.read_bytes(),
                expected,
                f"second run changed {path.relative_to(self.output_dir)}",
            )

    def test_idempotent_skips_writes_on_second_run(self) -> None:
        """transpile_command returns wrote=False when output is already current."""
        cmd = self._make_command("alpha", "hello", "Says hello", "body")

        _, wrote_first = self.module.transpile_command(cmd)
        self.assertTrue(wrote_first)

        _, wrote_second = self.module.transpile_command(cmd)
        self.assertFalse(wrote_second, "second invocation re-wrote unchanged output")

    def test_subagent_heavy_includes_banner(self) -> None:
        """Subagent-heavy commands prepend the banner and inline agent body."""
        # `plugins/core/commands/debug.md` is in SUBAGENT_HEAVY ->
        # ("core", "systematic-debugger").
        self._make_command("core", "debug", "Debug things", "Original debug body")
        self._make_agent(
            "core", "systematic-debugger", "Debugger agent prompt body."
        )

        self.assertEqual(self.module.main(), 0)
        toml_path = self.output_dir / "core" / "commands" / "debug.toml"
        self.assertTrue(toml_path.is_file())
        content = toml_path.read_text(encoding="utf-8")

        self.assertIn(self.module.BANNER, content)
        self.assertIn("Inlined agent: `core:systematic-debugger`", content)
        self.assertIn("Debugger agent prompt body.", content)
        self.assertIn("Original debug body", content)

    def test_non_subagent_command_has_no_banner(self) -> None:
        """Plain commands do not get the banner or inlined agent block."""
        self._make_command("alpha", "simple", "Simple cmd", "Just do the thing")

        self.assertEqual(self.module.main(), 0)
        content = (
            self.output_dir / "alpha" / "commands" / "simple.toml"
        ).read_text(encoding="utf-8")

        self.assertNotIn(self.module.BANNER, content)
        self.assertNotIn("Inlined agent:", content)
        self.assertIn("Just do the thing", content)


if __name__ == "__main__":
    unittest.main()
