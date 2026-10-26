#!/usr/bin/env python3
"""Inventory and audit one or more skill directories - read-only.

Reports per-skill facts: layout, lifecycle state, file inventory, package
hash, referenced-path resolution, orphans, line counts, and a rough token
estimate. With --discover it additionally scans the platform roots table and
reports cross-root duplicates, stale twins, and name collisions.

Never writes, never executes target scripts, never fetches.

Usage:
  python3 scripts/audit-skill.py <dir> [<dir> ...]
  python3 scripts/audit-skill.py --discover [--json]
  python3 scripts/audit-skill.py <dir> ... --discover

Exit statuses: 0 = inspection completed (findings may exist), 1 = no target
could be inspected, 2 = usage error.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REFERENCE_PATTERN = re.compile(
    r"(?<![A-Za-z0-9:/])([A-Za-z0-9_.-]+/[A-Za-z0-9_./-]+\.(?:md|py|json|txt))(?![A-Za-z0-9])"
)
LINK_PATTERN = re.compile(r"\]\(([^)]+)\)")

IGNORED_NAMES = {".git", "work", "__pycache__", ".DS_Store"}
RESOURCE_DIRS = {"process", "references", "scripts", "templates", "docs",
                 "evals", "assets", "resources", "examples"}
RULE_DIRS = {".cursor/rules", ".kilocode/rules"}

PLATFORM_ROOTS = [
    ("claude-code", "project", ".claude/skills"),
    ("claude-code", "user", "~/.claude/skills"),
    ("codex", "project", ".agents/skills"),
    ("codex", "user", "~/.agents/skills"),
    ("codex", "user", "~/.codex/skills"),
    ("cursor", "project", ".cursor/rules"),
    ("antigravity", "user", "~/.gemini/antigravity/skills"),
    ("kilo-code", "project", ".kilocode/rules"),
    ("windsurf", "project", ".windsurf/skills"),
    ("windsurf", "user", "~/.windsurf/skills"),
    ("opencode", "project", ".opencode/skills"),
    ("opencode", "user", "~/.opencode/skills"),
]

MAX_DISCOVER_DEPTH = 6
CHARS_PER_TOKEN = 4


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    try:
        digest.update(path.read_bytes())
    except OSError:
        return "unreadable"
    return digest.hexdigest()


def list_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for current, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d not in IGNORED_NAMES]
        base = Path(current)
        for name in names:
            if name in IGNORED_NAMES:
                continue
            files.append(base / name)
    return sorted(files)


def package_hash(root: Path, files: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in files:
        relative = path.relative_to(root).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(sha256_file(path).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def parse_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.DOTALL)
    if not match:
        return {}
    fields: dict[str, str] = {}
    current_map: str | None = None
    lines = match.group(1).splitlines()
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or line.lstrip().startswith("#"):
            index += 1
            continue
        if line.startswith("  "):
            sub = re.match(r"^\s+([A-Za-z][A-Za-z0-9-]*):\s*(.*)$", line)
            if current_map and sub:
                fields[f"{current_map}.{sub.group(1)}"] = sub.group(2).strip().strip('"').strip("'")
            index += 1
            continue
        field = re.match(r"^([A-Za-z][A-Za-z0-9-]*):(?:\s*(.*))?$", line)
        if not field:
            index += 1
            continue
        key, value = field.group(1), field.group(2) or ""
        if value in {">-", ">", "|-", "|"}:
            parts: list[str] = []
            index += 1
            while index < len(lines) and (lines[index].startswith("  ") or not lines[index].strip()):
                parts.append(lines[index][2:] if lines[index].startswith("  ") else "")
                index += 1
            fields[key] = (" " if value.startswith(">") else "\n").join(parts).strip()
            current_map = None
            continue
        current_map = key if value == "" else None
        fields[key] = value.strip().strip('"').strip("'")
        index += 1
    return fields


def detect_layout(root: Path) -> str:
    members = root / "skills"
    if members.is_dir() and any((child / "SKILL.md").is_file()
                                for child in members.iterdir() if child.is_dir()):
        return "collection"
    if (root / ".claude-plugin" / "plugin.json").is_file():
        return "plugin"
    if (root / "AGENTS.md").is_file() and (root / "scripts" / "check-update.py").is_file():
        return "astra"
    return "spec"


def referenced_paths(body: str) -> set[str]:
    references = set(REFERENCE_PATTERN.findall(body))
    references.update(
        match.group(1)
        for match in LINK_PATTERN.finditer(body)
        if not match.group(1).startswith(("http://", "https://", "#", "mailto:"))
    )
    return references


def audit_skill(root: Path) -> dict:
    record: dict = {
        "path": str(root),
        "name": root.name,
        "layout": "unknown",
        "state": "invalid",
        "files": 0,
        "lines": 0,
        "tokens_estimate": 0,
        "package_hash": "",
        "broken_refs": [],
        "note_refs": [],
        "orphans": [],
        "operations_surface": "unknown",
    }
    skill_file = root / "SKILL.md"
    if not root.is_dir() or not skill_file.is_file():
        return record
    try:
        text = skill_file.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return record

    fields = parse_frontmatter(text)
    if fields.get("name"):
        record["name"] = fields["name"]
    record["layout"] = detect_layout(root)
    if record["layout"] == "astra":
        record["operations_surface"] = (
            "ok" if (root / "process" / "operations-catalog.md").is_file()
            else "missing-catalog"
        )
    else:
        has_enum = re.search(
            r"(?im)^\s*(#+\s*.*operations|\|\s*operation)", text
        )
        record["operations_surface"] = "ok" if has_enum else "unstated"

    files = list_files(root)
    record["files"] = len(files)
    record["package_hash"] = package_hash(root, files)

    for relative in sorted(referenced_paths(text)):
        candidate = Path(relative.replace("\\", "/"))
        if candidate.is_absolute() or ".." in candidate.parts:
            record["broken_refs"].append(f"{relative} (escapes root)")
            continue
        if not (root / candidate).is_file():
            first = candidate.parts[0] if candidate.parts else ""
            if first == "work":
                record["note_refs"].append(f"{relative} (workspace)")
            elif first and first not in RESOURCE_DIRS:
                record["note_refs"].append(f"{relative} (no known root)")
            else:
                record["broken_refs"].append(relative)

    corpus = text
    for path in files:
        if path.suffix == ".md" and path != skill_file:
            try:
                corpus += "\n" + path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
    for path in files:
        relative = path.relative_to(root)
        if relative.parts[0] not in RESOURCE_DIRS or relative.name == "README.md":
            continue
        if relative.as_posix() not in corpus and path.stem not in corpus:
            convention = re.match(r"([a-z]+-\d+)\b", path.stem)
            if convention and re.search(
                rf"\b{re.escape(convention.group(1))}\b", corpus
            ):
                continue
            record["orphans"].append(relative.as_posix())

    body_chars = len(text)
    total_chars = len(text)
    lines = len(text.splitlines())
    for path in files:
        if path.suffix in {".md", ".py", ".json", ".txt", ".template"}:
            try:
                content = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            total_chars += len(content)
    record["lines"] = lines
    record["body_tokens_estimate"] = body_chars // CHARS_PER_TOKEN
    record["tokens_estimate"] = total_chars // CHARS_PER_TOKEN
    record["state"] = "active" if fields.get("name") and fields.get("description") else "invalid"
    if fields:
        record["description_chars"] = len(fields.get("description", ""))
    return record


def discover_roots() -> list[dict]:
    found: list[dict] = []
    cwd = Path.cwd()
    for platform, scope, relative in PLATFORM_ROOTS:
        root = Path(relative).expanduser() if scope == "user" else cwd / relative
        if not root.is_dir():
            continue
        if relative in RULE_DIRS:
            rules = sorted(p for p in root.iterdir()
                           if p.is_file() and p.suffix in {".md", ".mdc"})
            for rule in rules:
                found.append({"kind": "rule", "platform": platform, "scope": scope,
                              "path": str(rule), "name": rule.stem})
            continue
        root_depth = len(root.parts)
        for current, dirs, _names in os.walk(root, followlinks=False):
            dirs[:] = [d for d in dirs if d not in IGNORED_NAMES]
            if len(Path(current).parts) - root_depth >= MAX_DISCOVER_DEPTH:
                dirs[:] = []
            skill_file = Path(current) / "SKILL.md"
            if skill_file.is_file() and not skill_file.is_symlink():
                found.append({"kind": "skill", "platform": platform, "scope": scope,
                              "path": current})
    return found


def collision_verdicts(entries: list[dict]) -> list[dict]:
    groups: dict[str, list[dict]] = {}
    for entry in entries:
        if entry.get("kind") != "skill":
            continue
        record = audit_skill(Path(entry["path"]))
        entry.update(record)
        groups.setdefault(record["name"], []).append(entry)
    verdicts: list[dict] = []
    for name, members in sorted(groups.items()):
        if len(members) < 2:
            continue
        hashes = {member["package_hash"] for member in members}
        verdict = "exact-duplicate" if len(hashes) == 1 else "divergent-copies"
        copies = [{"path": member["path"],
                   "hash": member["package_hash"][:16],
                   "files": member["files"],
                   "mtime": datetime.fromtimestamp(
                       Path(member["path"]).stat().st_mtime,
                       tz=timezone.utc).isoformat(timespec="seconds")}
                  for member in members]
        verdicts.append({"name": name, "verdict": verdict, "copies": copies})
    return verdicts


def audit_target(raw: str) -> list[dict]:
    root = Path(raw).resolve()
    if not root.is_dir():
        return [{"path": str(root), "name": root.name, "state": "invalid",
                 "error": "directory does not exist"}]
    if (root / "skills").is_dir() and any(
            (child / "SKILL.md").is_file()
            for child in (root / "skills").iterdir() if child.is_dir()):
        records = [audit_skill(root)]
        for child in sorted((root / "skills").iterdir()):
            if child.is_dir() and (child / "SKILL.md").is_file():
                records.append(audit_skill(child))
        return records
    return [audit_skill(root)]


def print_record(record: dict) -> None:
    base = (f"skill={record.get('name', '?')} path={record.get('path', '?')} "
            f"layout={record.get('layout', '?')} state={record.get('state', '?')}")
    if record.get("state") == "invalid":
        print(f"{base} error={record.get('error', 'missing or unreadable SKILL.md')}")
        return
    print(f"{base} files={record['files']} lines={record['lines']} "
          f"body_tokens~{record['body_tokens_estimate']} "
          f"package_tokens~{record['tokens_estimate']} "
          f"package_hash={record['package_hash'][:16]} "
          f"broken_refs={len(record['broken_refs'])} orphans={len(record['orphans'])}")
    for ref in record["broken_refs"]:
        print(f"  broken_ref={ref}")
    for ref in record["note_refs"]:
        print(f"  note_ref={ref}")
    for orphan in record["orphans"]:
        print(f"  orphan={orphan}")
    if record["operations_surface"] not in ("ok", "unknown"):
        print(f"  operations_surface={record['operations_surface']}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("targets", nargs="*", help="skill or collection directories")
    parser.add_argument("--discover", action="store_true",
                        help="scan the platform roots table for skills and rule artifacts")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of key=value lines")
    args = parser.parse_args()

    if not args.targets and not args.discover:
        parser.print_usage(sys.stderr)
        return 2

    inspected = 0
    report: dict = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "targets": [], "discovery": [], "collisions": []}

    for raw in args.targets:
        records = audit_target(raw)
        report["targets"].extend(records)
        if not args.json:
            for record in records:
                print_record(record)
        inspected += sum(1 for r in records if r.get("state") != "invalid" or "error" not in r)

    if args.discover:
        entries = discover_roots()
        for entry in entries:
            if entry["kind"] == "skill":
                entry.update(audit_skill(Path(entry["path"])))
        report["discovery"] = entries
        report["collisions"] = collision_verdicts(entries)
        if not args.json:
            for entry in entries:
                if entry["kind"] == "rule":
                    print(f"rule={entry['name']} platform={entry['platform']} "
                          f"scope={entry['scope']} path={entry['path']}")
                else:
                    print(f"found={entry['name']} platform={entry['platform']} "
                          f"scope={entry['scope']} state={entry['state']} path={entry['path']}")
            for verdict in report["collisions"]:
                print(f"collision={verdict['name']} verdict={verdict['verdict']} "
                      f"copies={len(verdict['copies'])}")
                for copy in verdict["copies"]:
                    print(f"  copy={copy['path']} hash={copy['hash']} "
                          f"files={copy['files']} mtime={copy['mtime']}")

    total = len(report["targets"]) + sum(1 for e in report["discovery"] if e["kind"] == "skill")
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"STATUS OK skills={total} collisions={len(report['collisions'])}")

    return 0 if (inspected or args.discover) else 1


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(errors="backslashreplace")
    raise SystemExit(main())
