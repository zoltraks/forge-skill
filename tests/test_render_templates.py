"""Tests for scripts/render-templates.py."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "render-templates.py"
TEMPLATES = REPO_ROOT / "templates"

BASE_CONTEXT = {
    "skill-name": "sample-skill",
    "skill-title": "Sample Skill",
    "skill-purpose": "A synthetic skill for tests.",
    "skill-description": "Synthetic skill for tests.",
    "skill-version": "0.1.0",
    "skill-author": "Test Author",
    "year": "2026",
    "trigger-keywords": "- \"do the sample thing\"",
    "operations-table": "| do a sample thing | `process/sample-thing.md` |",
    "process-listings": "- **`process/sample-thing.md`** - The sample procedure.",
    "parameter-rows": "",
    "collection-name": "sample-collection",
    "collection-title": "Sample Collection",
    "collection-description": "Synthetic collection for tests.",
    "collection-purpose": "Route requests to member skills.",
    "member-table": "| `sample-skill` | `skills/sample-skill` | Sample purposes |",
    "gitmodules-entries": (
        '[submodule "skills/sample-skill"]\n'
        "\tpath = skills/sample-skill\n"
        "\turl = git@example.invalid:org/sample-skill.git"
    ),
}


def collect_extra_placeholders() -> set[str]:
    keys: set[str] = set()
    import re

    pattern = re.compile(r"\{\{\s*([A-Za-z][A-Za-z0-9_-]*)\s*\}\}")
    for path in TEMPLATES.glob("*.template"):
        keys.update(pattern.findall(path.read_text(encoding="utf-8")))
    return keys - set(BASE_CONTEXT)


def run_script(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )


class RenderTemplatesTests(unittest.TestCase):
    def write_context(self, directory: Path, overrides: dict | None = None) -> Path:
        context = dict(BASE_CONTEXT)
        for key in collect_extra_placeholders():
            context.setdefault(key, f"SYNTHETIC {key}")
        if overrides:
            context.update(overrides)
        path = directory / "context.json"
        path.write_text(json.dumps(context), encoding="utf-8")
        return path

    def test_self_test_passes(self) -> None:
        result = run_script("--self-test")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS", result.stdout)

    def test_render_stages_single_set(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            scratch_dir = Path(scratch)
            context = self.write_context(scratch_dir)
            staging = scratch_dir / "staging"
            target = scratch_dir / "sample-skill"
            result = run_script(
                "--context", str(context), "--target", str(target),
                "--staging", str(staging),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("STAGED", result.stdout)
            self.assertTrue((staging / "SKILL.md").is_file())
            self.assertTrue((staging / "process" / "decision-modes.md").is_file())
            self.assertFalse(target.exists(), "staging must not write the target")

    def test_render_writes_target_with_flag(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            scratch_dir = Path(scratch)
            context = self.write_context(scratch_dir)
            staging = scratch_dir / "staging"
            target = scratch_dir / "sample-skill"
            result = run_script(
                "--context", str(context), "--target", str(target),
                "--staging", str(staging), "--write",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((target / "SKILL.md").is_file())
            body = (target / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("name: sample-skill", body)
            self.assertNotIn("{{", body)

    def test_non_empty_target_refused_without_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            scratch_dir = Path(scratch)
            context = self.write_context(scratch_dir)
            target = scratch_dir / "sample-skill"
            target.mkdir()
            (target / "existing.txt").write_text("occupied", encoding="utf-8")
            result = run_script(
                "--context", str(context), "--target", str(target), "--write",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("not empty", result.stdout)

    def test_missing_context_value_fails(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            scratch_dir = Path(scratch)
            context = self.write_context(scratch_dir, {"skill-name": ""})
            target = scratch_dir / "out"
            result = run_script(
                "--context", str(context), "--target", str(target),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("skill-name", result.stdout)

    def test_invalid_slug_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            scratch_dir = Path(scratch)
            context = self.write_context(scratch_dir, {"skill-name": "Bad Name!"})
            target = scratch_dir / "out"
            result = run_script(
                "--context", str(context), "--target", str(target),
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("slug", result.stdout)

    def test_unknown_set_fails(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            scratch_dir = Path(scratch)
            context = self.write_context(scratch_dir)
            target = scratch_dir / "out"
            result = run_script(
                "--context", str(context), "--target", str(target),
                "--set", "nonexistent",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("unknown template set", result.stdout)

    def test_rendered_single_set_validates(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            scratch_dir = Path(scratch)
            context = self.write_context(scratch_dir)
            target = scratch_dir / "sample-skill"
            result = run_script(
                "--context", str(context), "--target", str(target), "--write",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            validator = subprocess.run(
                [sys.executable, str(REPO_ROOT / "scripts" / "validate-skill.py"),
                 str(target)],
                capture_output=True, encoding="utf-8", errors="replace", timeout=60,
            )
            # Agent-written files (process/README.md etc.) are absent in a pure
            # render, so structural failures are acceptable - placeholder and
            # frontmatter failures are not.
            for line in validator.stdout.splitlines():
                self.assertNotIn("unresolved template placeholder", line)
                self.assertNotIn("frontmatter", line)

    def test_collection_set_renders(self) -> None:
        with tempfile.TemporaryDirectory() as scratch:
            scratch_dir = Path(scratch)
            context = self.write_context(scratch_dir)
            target = scratch_dir / "sample-collection"
            result = run_script(
                "--context", str(context), "--target", str(target),
                "--set", "collection", "--write",
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((target / "SKILL.md").is_file())
            self.assertTrue((target / "process" / "member-contract.md").is_file())
            self.assertTrue((target / ".gitmodules").is_file())


if __name__ == "__main__":
    unittest.main()
