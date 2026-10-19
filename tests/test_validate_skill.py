"""Tests for scripts/validate-skill.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "validate-skill.py"


def run_validator(target: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), str(target)],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )


def make_skill(root: Path, name: str = "sample-skill", **overrides: str) -> Path:
    skill = root / name
    skill.mkdir(parents=True)
    frontmatter = overrides.get(
        "frontmatter",
        f'---\nname: {name}\ndescription: >-\n  A sample skill.\nlicense: MIT\n'
        f'metadata:\n  version: "0.1.0"\n---\n\n# Sample\n',
    )
    (skill / "SKILL.md").write_text(frontmatter, encoding="utf-8")
    for filename in ("AGENTS.md", "README.md", "LICENSE"):
        (skill / filename).write_text(f"# {filename}\n", encoding="utf-8")
    for directory in ("process", "scripts", "docs", "evals"):
        (skill / directory).mkdir()
    for proc in ("skill-activation", "json-exchange", "session-review",
                 "decision-modes"):
        content = "# Procedure\n\nautonomous fully autonomous verbose\n"
        (skill / "process" / f"{proc}.md").write_text(content, encoding="utf-8")
    for doc in ("STYLE", "VERSIONING", "MAINTENANCE", "CONTRIBUTING", "SECURITY",
                "README"):
        (skill / "docs" / f"{doc}.md").write_text(f"# {doc}\n", encoding="utf-8")
    (skill / "scripts" / "check-update.py").write_text("# checker\n",
                                                     encoding="utf-8")
    evals = {"skill_name": name, "evals": [
        {"id": 1, "prompt": "p", "expected_output": "e", "files": [],
         "expectations": ["x"]},
    ]}
    (skill / "evals" / "evals.json").write_text(json.dumps(evals),
                                              encoding="utf-8")
    return skill


class ValidateSkillTests(unittest.TestCase):
    def test_forge_itself_passes(self) -> None:
        result = run_validator(REPO_ROOT)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_missing_directory_fails(self) -> None:
        result = run_validator(Path("/nonexistent-skill-dir"))
        self.assertEqual(result.returncode, 1)

    def test_missing_skill_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch) / "empty-skill"
            root.mkdir()
            result = run_validator(root)
            self.assertEqual(result.returncode, 1)
            self.assertIn("SKILL.md is missing", result.stdout)

    def test_name_directory_mismatch_fails(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = Path(scratch) / "wrong-name"
            skill.mkdir()
            (skill / "SKILL.md").write_text(
                "---\nname: right-name\ndescription: x\n---\n# t\n",
                encoding="utf-8",
            )
            result = run_validator(skill)
            self.assertEqual(result.returncode, 1)
            self.assertIn("does not match directory", result.stdout)

    def test_missing_shared_procedure_fails(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = make_skill(Path(scratch))
            (skill / "process" / "json-exchange.md").unlink()
            result = run_validator(skill)
            self.assertEqual(result.returncode, 1)
            self.assertIn("json-exchange", result.stdout)

    def test_missing_governance_doc_fails(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = make_skill(Path(scratch))
            (skill / "docs" / "SECURITY.md").unlink()
            result = run_validator(skill)
            self.assertEqual(result.returncode, 1)
            self.assertIn("SECURITY.md", result.stdout)

    def test_valid_synthetic_skill_passes(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = make_skill(Path(scratch))
            result = run_validator(skill)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_leftover_placeholder_fails(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = make_skill(Path(scratch))
            (skill / "README.md").write_text("# {{skill-name}}\n",
                                           encoding="utf-8")
            result = run_validator(skill)
            self.assertEqual(result.returncode, 1)
            self.assertIn("placeholder", result.stdout)

    def test_invalid_evals_json_fails(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = make_skill(Path(scratch))
            (skill / "evals" / "evals.json").write_text("{not json",
                                                      encoding="utf-8")
            result = run_validator(skill)
            self.assertEqual(result.returncode, 1)
            self.assertIn("JSON", result.stdout)

    def test_decision_modes_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = make_skill(Path(scratch))
            (skill / "process" / "decision-modes.md").write_text(
                "# Modes\n\ninteractive only\n", encoding="utf-8",
            )
            result = run_validator(skill)
            self.assertEqual(result.returncode, 1)
            self.assertIn("fully autonomous", result.stdout)


if __name__ == "__main__":
    unittest.main()
