#!/usr/bin/env python3
"""Render Forge templates into a staged skill or collection tree.

Deterministic `{{placeholder}}` substitution driven by an explicit
template-to-output-path map and a context document the agent writes from
verified evidence. Renders into a staging directory, reports, and writes the
approved target only when asked.

Usage:
    python3 scripts/render-templates.py --self-test
    python3 scripts/render-templates.py --context ctx.json --target DIR \
        [--set single|collection] [--staging DIR] [--write] [--overwrite]
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z][A-Za-z0-9_-]*)\s*\}\}")
NAME_PATTERN = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
TEMPLATE_SUFFIX = ".template"
MAP_FILE = "map.json"

REQUIRED_CONTEXT = ["skill-name", "skill-title", "skill-purpose", "skill-description"]


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def load_map(templates_dir: Path, failures: list[str]) -> dict[str, dict[str, str]]:
    map_path = templates_dir / MAP_FILE
    if not map_path.is_file():
        fail(f"template map missing: {map_path}", failures)
        return {}
    try:
        data = json.loads(map_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        fail(f"template map is not valid JSON: {error}", failures)
        return {}
    if not isinstance(data, dict):
        fail("template map must be an object of sets", failures)
        return {}
    for set_name, mapping in data.items():
        if not isinstance(mapping, dict):
            fail(f"template set {set_name!r} is not an object", failures)
            continue
        for template, output in mapping.items():
            if not template.endswith(TEMPLATE_SUFFIX):
                fail(f"map key is not a template file: {template}", failures)
            if not isinstance(output, str) or not output:
                fail(f"map value for {template} is not an output path", failures)
    return data


def check_output_paths(mapping: dict[str, str], failures: list[str]) -> None:
    seen: set[str] = set()
    for template, output in sorted(mapping.items()):
        candidate = Path(output)
        if candidate.is_absolute():
            fail(f"output path is absolute: {output}", failures)
            continue
        if ".." in candidate.parts:
            fail(f"output path escapes the target: {output}", failures)
            continue
        if output in seen:
            fail(f"duplicate output path: {output}", failures)
        seen.add(output)


def load_context(path: Path, failures: list[str]) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"context file unreadable: {error}", failures)
        return {}
    if not isinstance(data, dict):
        fail("context must be a JSON object of placeholder values", failures)
        return {}
    context: dict[str, str] = {}
    for key, value in data.items():
        if not isinstance(value, str):
            fail(f"context value for {key!r} is not a string", failures)
            continue
        context[key] = value
    for required in REQUIRED_CONTEXT:
        if required not in context or not context[required].strip():
            fail(f"required context value missing or empty: {required}", failures)
    name = context.get("skill-name", "")
    if name and not NAME_PATTERN.fullmatch(name):
        fail(f"skill-name {name!r} is not a valid slug", failures)
    return context


def render(mapping: dict[str, str], context: dict[str, str],
           templates_dir: Path, staging: Path, failures: list[str]) -> None:
    for template_name, output in sorted(mapping.items()):
        template_path = templates_dir / template_name
        if not template_path.is_file():
            fail(f"template missing: {template_name}", failures)
            continue
        try:
            text = template_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            fail(f"template is not UTF-8: {template_name}", failures)
            continue

        used = set(PLACEHOLDER.findall(text))

        def substitute(match: re.Match[str]) -> str:
            key = match.group(1)
            if key not in context:
                return match.group(0)
            return context[key]

        rendered = PLACEHOLDER.sub(substitute, text)

        for leftover in PLACEHOLDER.findall(rendered):
            fail(f"{template_name}: unresolved placeholder {leftover!r}", failures)
        for key in used - set(context):
            fail(f"{template_name}: placeholder {key!r} has no context value", failures)

        destination = staging / output
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")


def target_is_safe(target: Path, overwrite: bool, failures: list[str]) -> bool:
    resolved = target.resolve()
    for parent in [resolved, *resolved.parents]:
        if parent.is_symlink():
            fail(f"target path traverses a symlink: {parent}", failures)
            return False
    if resolved.exists() and not resolved.is_dir():
        fail(f"target exists and is not a directory: {resolved}", failures)
        return False
    if resolved.is_dir() and any(resolved.iterdir()) and not overwrite:
        fail(f"target is not empty: {resolved} (pass --overwrite to allow)", failures)
        return False
    return True


def copy_staging(staging: Path, target: Path) -> int:
    count = 0
    for path in sorted(staging.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(staging)
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, destination)
        count += 1
    return count


def self_test(templates_dir: Path) -> int:
    failures: list[str] = []
    sets = load_map(templates_dir, failures)
    base_context = {
        "skill-name": "sample-skill",
        "skill-title": "Sample Skill",
        "skill-purpose": "A synthetic skill used to verify the renderer.",
        "skill-description": "Synthetic skill for renderer verification.",
        "skill-version": "0.1.0",
        "skill-author": "AUTHOR PLACEHOLDER",
        "year": "2026",
        "collection-name": "sample-collection",
        "collection-title": "Sample Collection",
        "collection-description": "Synthetic collection for renderer verification.",
        "collection-purpose": "Route requests to member skills.",
    }
    if failures:
        for message in failures:
            print(f"FAIL {message}")
        return 1
    for set_name, mapping in sorted(sets.items()):
        check_output_paths(mapping, failures)
        for template_name in mapping:
            if not (templates_dir / template_name).is_file():
                fail(f"{set_name}: template missing: {template_name}", failures)
        context = dict(base_context)
        for template_name in mapping:
            path = templates_dir / template_name
            if not path.is_file():
                continue
            for key in PLACEHOLDER.findall(path.read_text(encoding="utf-8")):
                context.setdefault(key, f"SYNTHETIC {key}")
        with tempfile.TemporaryDirectory(prefix="forge-selftest-") as scratch:
            staging = Path(scratch) / "staging"
            staging.mkdir()
            render(mapping, context, templates_dir, staging, failures)
    if failures:
        for message in failures:
            print(f"FAIL {message}")
        print(f"{len(failures)} issue(s) found")
        return 1
    print(f"PASS rendered {sum(len(m) for m in sets.values())} templates across "
          f"{len(sets)} set(s)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--context", help="JSON context file of placeholder values")
    parser.add_argument("--target", help="target directory for the generated tree")
    parser.add_argument("--set", dest="template_set", default="single",
                        help="template set to render (default: single)")
    parser.add_argument("--staging", help="staging directory (default: temp dir)")
    parser.add_argument("--write", action="store_true",
                        help="copy staged output into the target")
    parser.add_argument("--overwrite", action="store_true",
                        help="allow writing into a non-empty target")
    parser.add_argument("--self-test", action="store_true",
                        help="render every set with a synthetic context")
    args = parser.parse_args()

    templates_dir = Path(__file__).resolve().parent.parent / "templates"

    if args.self_test:
        return self_test(templates_dir)

    failures: list[str] = []
    if not args.context or not args.target:
        parser.error("--context and --target are required unless --self-test")

    sets = load_map(templates_dir, failures)
    mapping = sets.get(args.template_set)
    if mapping is None:
        fail(f"unknown template set {args.template_set!r} - "
             f"available: {', '.join(sorted(sets))}", failures)
        mapping = {}
    check_output_paths(mapping, failures)
    context = load_context(Path(args.context), failures)

    if failures:
        for message in failures:
            print(f"FAIL {message}")
        return 1

    if args.staging:
        staging = Path(args.staging)
        if staging.exists() and any(staging.iterdir()):
            fail(f"staging directory is not empty: {staging}", failures)
        staging.mkdir(parents=True, exist_ok=True)
        cleanup = False
    else:
        scratch = tempfile.TemporaryDirectory(prefix="forge-render-")
        staging = Path(scratch.name) / "staging"
        staging.mkdir()
        cleanup = True

    render(mapping, context, templates_dir, staging, failures)
    if failures:
        for message in failures:
            print(f"FAIL {message}")
        print(f"{len(failures)} issue(s) found")
        return 1

    rendered = sum(1 for p in staging.rglob("*") if p.is_file())
    print(f"STAGED {rendered} file(s) in {staging}")

    if not args.write:
        print("NEXT inspect the stage, run validate-skill.py on it, then rerun with --write")
        return 0

    target = Path(args.target)
    if not target_is_safe(target, args.overwrite, failures):
        for message in failures:
            print(f"FAIL {message}")
        return 1
    count = copy_staging(staging, target)
    if cleanup:
        scratch.cleanup()
    print(f"WROTE {count} file(s) to {target.resolve()}")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(errors="backslashreplace")
    raise SystemExit(main())
