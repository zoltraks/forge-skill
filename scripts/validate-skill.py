#!/usr/bin/env python3
"""Validate Forge or a generated skill tree against a layout profile.

Read-only inspection: frontmatter, shared procedures, decision modes,
structure, evals, root references, naming, and leftover placeholders.
Never executes target scripts, never fetches, never writes.

Usage: python3 scripts/validate-skill.py <skill-directory> [--profile astra|spec]

The default `astra` profile enforces the full member contract. The `spec`
profile enforces only the portable Agent Skills specification surface - the
member-contract checks do not apply.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ALLOWED_FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}
REFERENCE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9:/])([A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+\.(?:md|py|json|txt))(?![A-Za-z0-9])"
)
LINK_PATTERN = re.compile(r"\]\(([^)]+)\)")
PLACEHOLDER_PATTERN = re.compile(r"\{\{[A-Za-z0-9_-]+\}\}")

SHARED_PROCEDURES = [
    "process/skill-activation.md",
    "process/json-exchange.md",
    "process/operation-timing.md",
    "process/session-review.md",
    "process/operations-catalog.md",
    "process/decision-modes.md",
]

REQUIRED_FILES = [
    "SKILL.md",
    "AGENTS.md",
    "README.md",
    "LICENSE",
    "scripts/check-update.py",
    "evals/evals.json",
]

GOVERNANCE_DOCS = [
    "docs/STYLE.md",
    "docs/VERSIONING.md",
    "docs/MAINTENANCE.md",
    "docs/CONTRIBUTING.md",
    "docs/SECURITY.md",
    "docs/README.md",
]

KNOWN_DIRS = {"process", "references", "scripts", "templates", "docs",
              "evals", "assets", "resources", "examples"}

# Conventional names exempt from the two-word advisory.
NAMING_EXEMPTIONS = {
    "SKILL.md", "AGENTS.md", "README.md", "CHANGELOG.md", "LICENSE",
    "STYLE.md", "VERSIONING.md", "MAINTENANCE.md", "CONTRIBUTING.md",
    "SECURITY.md", "COPYRIGHTS.md",
}


def issue(message: str, issues: list[str]) -> None:
    issues.append(message)


def parse_frontmatter(text: str, issues: list[str]) -> tuple[dict[str, str], str]:
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        issue("SKILL.md has no YAML frontmatter block", issues)
        return {}, text

    raw = match.group(1).splitlines()
    fields: dict[str, str] = {}
    nested: dict[str, str] = {}
    current_map: str | None = None
    index = 0
    while index < len(raw):
        line = raw[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if line.startswith("  "):
            sub_match = re.match(r"^\s+([A-Za-z][A-Za-z0-9-]*):\s*(.*)$", line)
            if current_map and sub_match:
                nested[f"{current_map}.{sub_match.group(1)}"] = (
                    sub_match.group(2).strip().strip('"').strip("'")
                )
            index += 1
            continue
        field_match = re.match(r"^([A-Za-z][A-Za-z0-9-]*):(?:\s*(.*))?$", line)
        if not field_match:
            issue(f"frontmatter line {index + 1} is not a simple field: {line}", issues)
            index += 1
            continue
        key, value = field_match.group(1), field_match.group(2) or ""
        if value in {">-", ">", "|-", "|"}:
            parts: list[str] = []
            index += 1
            while index < len(raw) and (raw[index].startswith("  ") or not raw[index].strip()):
                parts.append(raw[index][2:] if raw[index].startswith("  ") else "")
                index += 1
            separator = " " if value.startswith(">") else "\n"
            fields[key] = separator.join(parts).strip()
            current_map = None
            continue
        if value == "":
            current_map = key
            fields[key] = ""
            index += 1
            continue
        current_map = None
        fields[key] = value.strip().strip('"').strip("'")
        index += 1
    fields.update(nested)
    return fields, text[match.end():]


def validate_frontmatter(root: Path, fields: dict[str, str], issues: list[str],
                         profile: str) -> None:
    missing = {"name", "description"} - fields.keys()
    for key in sorted(missing):
        issue(f"frontmatter is missing required field: {key}", issues)

    top_level = {key for key in fields if "." not in key}
    unexpected = top_level - ALLOWED_FIELDS
    for key in sorted(unexpected):
        issue(f"frontmatter has unsupported top-level field: {key}", issues)

    nested = {key for key in fields if "." in key}
    unexpected_nested = {key for key in nested if not key.startswith("metadata.")}
    for key in sorted(unexpected_nested):
        issue(f"frontmatter has unsupported nested field: {key}", issues)

    name = fields.get("name", "")
    if name:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            issue("name must contain lowercase letters, digits, and single hyphens only", issues)
        if len(name) > 64:
            issue(f"name is {len(name)} characters, maximum is 64", issues)
        if name != root.name:
            issue(f"name {name!r} does not match directory {root.name!r}", issues)

    description = fields.get("description", "")
    if not description:
        issue("description must not be empty", issues)
    if len(description) > 1024:
        issue(f"description is {len(description)} characters, maximum is 1024", issues)
    if "<" in description or ">" in description:
        issue("description must not contain angle brackets", issues)

    compatibility = fields.get("compatibility", "")
    if compatibility and len(compatibility) > 500:
        issue(f"compatibility is {len(compatibility)} characters, maximum is 500", issues)

    if profile == "astra" and "metadata.version" not in fields:
        issue("frontmatter metadata carries no version", issues)


def referenced_paths(body: str) -> set[str]:
    references = set(REFERENCE_PATTERN.findall(body))
    references.update(
        match.group(1)
        for match in LINK_PATTERN.finditer(body)
        if not match.group(1).startswith(("http://", "https://", "#", "mailto:"))
    )
    return references


def validate_structure(root: Path, issues: list[str], profile: str) -> None:
    required = REQUIRED_FILES if profile == "astra" else ["SKILL.md"]
    for relative in required:
        if not (root / relative).is_file():
            issue(f"required file missing: {relative}", issues)
    if profile != "astra":
        return
    for relative in SHARED_PROCEDURES:
        path = root / relative
        if not path.is_file():
            issue(f"shared procedure missing: {relative}", issues)
    for relative in GOVERNANCE_DOCS:
        if not (root / relative).is_file():
            issue(f"governance document missing: {relative}", issues)

    modes_file = root / "process" / "decision-modes.md"
    if modes_file.is_file():
        content = modes_file.read_text(encoding="utf-8")
        for term in ("autonomous", "fully autonomous", "verbose"):
            if term not in content:
                issue(f"decision-modes.md does not document '{term}'", issues)


def validate_body(root: Path, body: str, issues: list[str]) -> None:
    skill_file = root / "SKILL.md"
    total_lines = len(skill_file.read_text(encoding="utf-8").splitlines())
    if total_lines > 500:
        issue(f"SKILL.md is {total_lines} lines, maximum is 500", issues)

    advisory: list[str] = []
    for relative in sorted(referenced_paths(body)):
        candidate = Path(relative.replace("\\", "/"))
        if candidate.is_absolute() or ".." in candidate.parts:
            issue(f"root reference escapes the skill directory: {relative}", issues)
            continue
        if (root / candidate).is_file():
            continue
        first = candidate.parts[0] if candidate.parts else ""
        if first == "work":
            advisory.append(
                f"root reference targets the workspace: {relative} "
                "(convention statement or workspace dependency)"
            )
        elif first and first not in KNOWN_DIRS:
            advisory.append(
                f"root reference resolves in no known root: {relative} "
                "(possibly an external-root path)"
            )
        else:
            issue(f"root reference does not resolve: {relative}", issues)
    for message in advisory:
        print(f"ADVISORY {message}")

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        parts = relative.parts
        if "work" in parts or ".git" in parts or "templates" in parts or "tests" in parts:
            continue
        if path.suffix in {".md", ".json"}:
            try:
                content = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                issue(f"file is not UTF-8: {relative}", issues)
                continue
            stripped = strip_code(content) if path.suffix == ".md" else content
            if PLACEHOLDER_PATTERN.search(stripped):
                issue(f"unresolved template placeholder in shipped file: {relative}", issues)


def strip_code(content: str) -> str:
    """Remove fenced code blocks and inline code spans from Markdown text."""
    without_fences = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    return re.sub(r"`[^`\n]*`", "", without_fences)


def validate_naming(root: Path, issues: list[str]) -> None:
    advisory: list[str] = []
    for directory in ("process", "references"):
        base = root / directory
        if not base.is_dir():
            continue
        for path in sorted(base.glob("*.md")):
            if path.name in NAMING_EXEMPTIONS:
                continue
            stem = path.stem
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", stem):
                issue(f"{relative_name(path, root)} is not lowercase kebab-case", issues)
                continue
            if len(stem.split("-")) < 2:
                advisory.append(
                    f"{relative_name(path, root)} uses a one-word name, two words preferred"
                )
    for path in sorted((root / "scripts").glob("*.py")) if (root / "scripts").is_dir() else []:
        stem = path.stem
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", stem):
            issue(f"{relative_name(path, root)} is not lowercase kebab-case", issues)
    for message in advisory:
        print(f"ADVISORY {message}")


def relative_name(path: Path, root: Path) -> str:
    return str(path.relative_to(root))


def validate_evals(root: Path, fields: dict[str, str], issues: list[str],
                   profile: str) -> None:
    evals_file = root / "evals" / "evals.json"
    if not evals_file.is_file():
        return
    try:
        data = json.loads(evals_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        issue(f"evals/evals.json is not valid JSON: {error}", issues)
        return
    if not isinstance(data, dict) or not isinstance(data.get("evals"), list):
        issue("evals/evals.json must contain an evals array", issues)
        return
    if data.get("skill_name") != fields.get("name"):
        issue("evals/evals.json skill_name does not match frontmatter name", issues)
    assertion_key = "expectations" if profile == "astra" else "assertions"
    identifiers: set[int] = set()
    for position, item in enumerate(data["evals"], start=1):
        if not isinstance(item, dict):
            issue(f"eval {position} is not an object", issues)
            continue
        identifier = item.get("id")
        if not isinstance(identifier, int) or identifier in identifiers:
            issue(f"eval {position} has a missing or duplicate integer id", issues)
        else:
            identifiers.add(identifier)
        if not isinstance(item.get("prompt"), str) or not item["prompt"].strip():
            issue(f"eval {position} has no prompt", issues)
        if profile == "spec" and (
            not isinstance(item.get("expected_output"), str)
            or not item["expected_output"].strip()
        ):
            issue(f"eval {position} has no expected_output", issues)
        if not isinstance(item.get(assertion_key), list) or not item[assertion_key]:
            issue(f"eval {position} has no {assertion_key}", issues)


def validate_json_files(root: Path, issues: list[str]) -> None:
    for path in sorted(root.rglob("*.json")):
        relative = path.relative_to(root)
        if "work" in relative.parts or ".git" in relative.parts:
            continue
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            issue(f"invalid JSON at {relative}: {error}", issues)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("skill_dir", help="skill directory to validate")
    parser.add_argument("--profile", choices=["astra", "spec"], default="astra",
                        help="layout profile to enforce (default: astra)")
    args = parser.parse_args()

    root = Path(args.skill_dir).resolve()
    skill_file = root / "SKILL.md"
    issues: list[str] = []
    if not root.is_dir():
        issue(f"skill directory does not exist: {root}", issues)
    if not skill_file.is_file():
        issue("SKILL.md is missing", issues)
    else:
        text = skill_file.read_text(encoding="utf-8")
        fields, body = parse_frontmatter(text, issues)
        validate_frontmatter(root, fields, issues, args.profile)
        validate_body(root, body, issues)
        validate_structure(root, issues, args.profile)
        validate_naming(root, issues)
        validate_evals(root, fields, issues, args.profile)
        validate_json_files(root, issues)

    if issues:
        for message in issues:
            print(f"FAIL {message}")
        print(f"{len(issues)} issue(s) found")
        return 1

    print(f"PASS {args.profile} profile: frontmatter, structure, references, "
          "and naming")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(errors="backslashreplace")
    raise SystemExit(main())
