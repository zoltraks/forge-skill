"""Tests for scripts/audit-skill.py."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "audit-skill.py"


def run_audit(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, encoding="utf-8", errors="replace",
        timeout=60, cwd=str(cwd) if cwd else None,
    )


def make_skill(root: Path, name: str = "sample-skill") -> Path:
    skill = root / name
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        f'---\nname: {name}\ndescription: >-\n  A sample skill.\nlicense: MIT\n'
        'metadata:\n  version: "0.1.0"\n---\n\n# Sample\n\nSee process/notes.md.\n',
        encoding="utf-8",
    )
    (skill / "process").mkdir()
    (skill / "process" / "notes.md").write_text("# Notes\n", encoding="utf-8")
    return skill


class AuditSkillTests(unittest.TestCase):
    def test_forge_itself_audits(self) -> None:
        result = run_audit(str(REPO_ROOT))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("STATUS OK", result.stdout)
        self.assertIn("layout=astra", result.stdout)

    def test_no_arguments_is_usage_error(self) -> None:
        result = run_audit()
        self.assertEqual(result.returncode, 2)

    def test_missing_directory_fails(self) -> None:
        result = run_audit("/nonexistent-skill-dir")
        self.assertEqual(result.returncode, 1)
        self.assertIn("state=invalid", result.stdout)

    def test_reports_orphan_and_broken_ref(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = make_skill(Path(scratch))
            (skill / "references").mkdir()
            (skill / "references" / "unused.md").write_text("# Unused\n",
                                                          encoding="utf-8")
            result = run_audit(str(skill))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("orphan=references/unused.md", result.stdout)
            self.assertNotIn("orphan=process/notes.md", result.stdout)

    def test_workspace_and_external_refs_become_notes(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = make_skill(Path(scratch))
            skill.joinpath("SKILL.md").write_text(
                "---\nname: sample-skill\ndescription: >-\n  A sample skill.\n"
                'license: MIT\nmetadata:\n  version: "0.1.0"\n---\n\n'
                "# Sample\n\nSee process/notes.md, emit work/out.md, and read "
                "settings/lucy/tools.json from the memory repository.\n",
                encoding="utf-8",
            )
            result = run_audit(str(skill))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("broken_refs=0", result.stdout)
            self.assertIn("note_ref=work/out.md (workspace)", result.stdout)
            self.assertIn("note_ref=settings/lucy/tools.json (no known root)",
                          result.stdout)

    def test_convention_addressed_record_is_not_orphan(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = make_skill(Path(scratch))
            (skill / "docs").mkdir()
            (skill / "docs" / "changes").mkdir()
            (skill / "docs" / "changes" / "change-007-widget-fix.md").write_text(
                "# Change\n", encoding="utf-8",
            )
            skill.joinpath("SKILL.md").write_text(
                "---\nname: sample-skill\ndescription: >-\n  A sample skill.\n"
                'license: MIT\nmetadata:\n  version: "0.1.0"\n---\n\n'
                "# Sample\n\nSee process/notes.md. Shipped as change-007.\n",
                encoding="utf-8",
            )
            result = run_audit(str(skill))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("orphan=docs/changes/change-007-widget-fix.md",
                             result.stdout)

    def test_collection_audits_root_and_members(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch) / "my-collection"
            root.mkdir()
            (root / "SKILL.md").write_text(
                "---\nname: my-collection\ndescription: >-\n  Index.\n---\n# Index\n",
                encoding="utf-8",
            )
            make_skill(root / "skills", "member-one")
            make_skill(root / "skills", "member-two")
            result = run_audit(str(root))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("layout=collection", result.stdout)
            self.assertIn("skill=member-one", result.stdout)
            self.assertIn("skill=member-two", result.stdout)

    def test_discover_reports_exact_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            base = Path(scratch)
            make_skill(base / ".claude" / "skills", "dup-skill")
            twin = make_skill(base / ".agents" / "skills", "dup-skill")
            source = base / ".claude" / "skills" / "dup-skill"
            for path in source.rglob("*"):
                if path.is_file():
                    (twin / path.relative_to(source)).write_bytes(path.read_bytes())
            result = run_audit("--discover", cwd=base)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("collision=dup-skill verdict=exact-duplicate", result.stdout)



    def test_astra_missing_catalog_flagged(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill = Path(tmp) / "skill"
            (skill / "process").mkdir(parents=True)
            (skill / "scripts").mkdir()
            fm = "---" + chr(10) + "name: fixture" + chr(10) + "description: x" + chr(10) + "---" + chr(10)
            (skill / "SKILL.md").write_text(fm, encoding="utf-8")
            (skill / "AGENTS.md").write_text("# A" + chr(10), encoding="utf-8")
            (skill / "scripts" / "check-update.py").write_text("", encoding="utf-8")
            result = run_audit(str(skill))
            self.assertIn("operations_surface=missing-catalog", result.stdout)
            (skill / "process" / "operations-catalog.md").write_text("# C" + chr(10), encoding="utf-8")
            result = run_audit(str(skill))
            self.assertNotIn("operations_surface=", result.stdout)

if __name__ == "__main__":
    unittest.main()
