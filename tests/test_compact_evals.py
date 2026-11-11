"""Tests for scripts/compact-evals.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "compact-evals.py"


def run_compact(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, encoding="utf-8", errors="replace",
        timeout=60,
    )


def write_evals(root: Path, evals: list[dict], name: str = "sample-skill") -> Path:
    skill = root / name
    (skill / "evals").mkdir(parents=True)
    (skill / "evals" / "evals.json").write_text(
        json.dumps({"skill_name": name, "evals": evals}, indent=2) + "\n",
        encoding="utf-8")
    return skill


def make_eval(eval_id: int, prompt: str,
              expectations: list[str] | None = None) -> dict:
    return {"id": eval_id, "prompt": prompt,
            "expected_output": "expected",
            "files": [], "expectations": expectations or ["A check."]}


class CompactEvalsTests(unittest.TestCase):
    def test_forge_itself_analyzes(self) -> None:
        result = run_compact(str(REPO_ROOT))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("entries=", result.stdout)
        self.assertIn("STATUS OK", result.stdout)

    def test_no_arguments_is_usage_error(self) -> None:
        self.assertEqual(run_compact().returncode, 2)

    def test_missing_directory_fails(self) -> None:
        result = run_compact("/nonexistent-skill-dir")
        self.assertEqual(result.returncode, 1)
        self.assertIn("error=", result.stdout)

    def test_invalid_json_fails(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = Path(scratch) / "broken-skill"
            (skill / "evals").mkdir(parents=True)
            (skill / "evals" / "evals.json").write_text("{ not json",
                                                      encoding="utf-8")
            result = run_compact(str(skill))
            self.assertEqual(result.returncode, 1)
            self.assertIn("error=", result.stdout)

    def test_duplicate_prompt_reported(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = write_evals(Path(scratch), [
                make_eval(1, "Use sample.", ["First check."]),
                make_eval(2, "Use sample.", ["Second check."]),
            ])
            result = run_compact(str(skill))
            self.assertEqual(result.returncode, 0)
            self.assertIn("dup_prompt ids=1,2", result.stdout)
            self.assertIn("confidence=HIGH", result.stdout)

    def test_similar_prompt_reported(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = write_evals(Path(scratch), [
                make_eval(1, "Analyze this file, informational mode."),
                make_eval(2, "Analyze this file, timing mode."),
            ])
            result = run_compact(str(skill))
            self.assertEqual(result.returncode, 0)
            self.assertIn("similar_prompt ids=1,2", result.stdout)

    def test_within_eval_duplicate_expectation_reported(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = write_evals(Path(scratch), [
                make_eval(1, "Run it.", ["A check.", "A check."]),
            ])
            result = run_compact(str(skill))
            self.assertEqual(result.returncode, 0)
            self.assertIn("dup_expectation id=1", result.stdout)

    def test_shared_expectation_is_informational(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = write_evals(Path(scratch), [
                make_eval(1, "First run.", ["Same check."]),
                make_eval(2, "Second run.", ["Same check."]),
            ])
            result = run_compact(str(skill))
            self.assertEqual(result.returncode, 0)
            self.assertIn("shared_expectation ids=1,2", result.stdout)

    def test_clean_suite_reports_no_candidates(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = write_evals(Path(scratch), [
                make_eval(1, "First run.", ["Alpha check."]),
                make_eval(2, "Second run.", ["Beta check."]),
            ])
            result = run_compact(str(skill))
            self.assertEqual(result.returncode, 0)
            self.assertNotIn("dup_prompt", result.stdout)
            self.assertNotIn("similar_prompt", result.stdout)

    def test_list_schema_with_query_field(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            skill = Path(scratch) / "query-skill"
            (skill / "evals").mkdir(parents=True)
            (skill / "evals" / "evals.json").write_text(json.dumps([
                {"id": "alpha", "query": "Run alpha.", "should_trigger": True,
                 "expectations": ["First check."]},
                {"id": "beta", "query": "Run alpha.", "should_trigger": True,
                 "expectations": ["Second check."]},
            ]) + "\n", encoding="utf-8")
            result = run_compact(str(skill))
            self.assertEqual(result.returncode, 0)
            self.assertIn("schema=list", result.stdout)
            self.assertIn("dup_prompt ids=alpha,beta", result.stdout)

    def test_json_output_parses(self) -> None:
        result = run_compact(str(REPO_ROOT), "--json")
        self.assertEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        self.assertIn("targets", report)
        self.assertEqual(len(report["targets"]), 1)


if __name__ == "__main__":
    unittest.main()
