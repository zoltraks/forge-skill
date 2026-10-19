"""Tests for scripts/convert-source.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "convert-source.py"


def run_script(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )


class ConvertSourceTests(unittest.TestCase):
    def test_check_reports_converter_state(self) -> None:
        result = run_script("--check")
        self.assertIn(result.returncode, (0, 2))
        self.assertIn("CONVERTER", result.stdout)

    def test_missing_source_fails(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            result = run_script("/nonexistent.pdf", "--out", scratch)
            self.assertEqual(result.returncode, 1)
            self.assertIn("does not exist", result.stdout)

    def test_empty_source_fails(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            source = Path(scratch) / "empty.md"
            source.write_text("", encoding="utf-8")
            result = run_script(str(source), "--out", scratch)
            self.assertEqual(result.returncode, 1)
            self.assertIn("empty", result.stdout)

    def test_markdown_passthrough(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            scratch_dir = Path(scratch)
            source = scratch_dir / "notes.md"
            source.write_text("# Notes\n\nSome content.\n", encoding="utf-8")
            out_dir = scratch_dir / "out"
            result = run_script(str(source), "--out", str(out_dir))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((out_dir / "notes.md").is_file())
            self.assertIn("sha256=", result.stdout)

    def test_text_passthrough(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            scratch_dir = Path(scratch)
            source = scratch_dir / "notes.txt"
            source.write_text("plain text content\n", encoding="utf-8")
            out_dir = scratch_dir / "out"
            result = run_script(str(source), "--out", str(out_dir))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unsupported_format_fails(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            source = Path(scratch) / "data.bin"
            source.write_bytes(b"\x00\x01\x02")
            result = run_script(str(source), "--out", scratch)
            self.assertEqual(result.returncode, 1)
            self.assertIn("unsupported", result.stdout)


if __name__ == "__main__":
    unittest.main()
