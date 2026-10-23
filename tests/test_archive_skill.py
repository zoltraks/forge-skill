"""Tests for scripts/archive-skill.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "archive-skill.py"


def run_archive(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, encoding="utf-8", errors="replace", timeout=60,
    )


def make_source(root: Path, name: str = "tool-skill") -> Path:
    source = root / name
    source.mkdir(parents=True)
    (source / "SKILL.md").write_text("# Tool\n", encoding="utf-8")
    (source / "process").mkdir()
    (source / "process" / "run.md").write_text("# Run\n", encoding="utf-8")
    return source


class ArchiveSkillTests(unittest.TestCase):
    def test_snapshot_dry_run_writes_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            base = Path(scratch)
            source = make_source(base)
            archive = base / "archive"
            result = run_archive("snapshot", str(source),
                                 "--archive-dir", str(archive))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("STATUS DRY-RUN", result.stdout)
            self.assertFalse(archive.exists())

    def test_snapshot_and_list(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            base = Path(scratch)
            source = make_source(base)
            archive = base / "archive"
            result = run_archive("snapshot", str(source),
                                 "--archive-dir", str(archive), "--apply")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("STATUS SNAPSHOT", result.stdout)
            snapshots = [p for p in archive.iterdir() if p.is_dir()]
            self.assertEqual(len(snapshots), 1)
            self.assertTrue((snapshots[0] / "SKILL.md").is_file())
            self.assertTrue((snapshots[0] / "process" / "run.md").is_file())
            listing = run_archive("list", "--archive-dir", str(archive))
            self.assertEqual(listing.returncode, 0)
            self.assertIn("STATUS LIST snapshots=1", listing.stdout)

    def test_snapshot_missing_source_fails(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            result = run_archive("snapshot", "/nonexistent-skill-dir",
                                 "--archive-dir", str(Path(scratch) / "a"),
                                 "--apply")
            self.assertEqual(result.returncode, 1)

    def test_restore_preserves_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            base = Path(scratch)
            source = make_source(base)
            archive = base / "archive"
            snap = run_archive("snapshot", str(source),
                               "--archive-dir", str(archive), "--apply")
            self.assertEqual(snap.returncode, 0, snap.stdout)
            snapshot_id = next(p.name for p in archive.iterdir() if p.is_dir())
            (source / "SKILL.md").write_text("# Changed locally\n",
                                           encoding="utf-8")
            dry = run_archive("restore", snapshot_id,
                              "--archive-dir", str(archive))
            self.assertIn("STATUS DRY-RUN", dry.stdout)
            self.assertIn("conflicts=1", dry.stdout)
            result = run_archive("restore", snapshot_id,
                                 "--archive-dir", str(archive), "--apply")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("conflicts_preserved=1", result.stdout)
            self.assertEqual((source / "SKILL.md").read_text(encoding="utf-8"),
                             "# Tool\n")
            conflicts = list(source.glob("SKILL.md.conflict-*"))
            self.assertEqual(len(conflicts), 1)
            self.assertEqual(conflicts[0].read_text(encoding="utf-8"),
                             "# Changed locally\n")

    def test_restore_missing_snapshot_fails(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            result = run_archive("restore", "nope-0000",
                                 "--archive-dir", str(Path(scratch)), "--apply")
            self.assertEqual(result.returncode, 1)


if __name__ == "__main__":
    unittest.main()
