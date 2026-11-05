#!/usr/bin/env python3
"""Run the standard non-mutating document checks in one command.

Executes the mechanical battery from process/document-checklist.md against a
single file and prints a consolidated verdict line per tool, so one invocation
replaces a run of each checker separately:

    detect-encoding.py            report only, never gates
    validate-document.py          gates
    format-table.py --check       gates
    align-comments.py --check     gates
    reflow-prose.py --wrap/--unwrap --check   advisory unless --layout picks a side
    split-sentences.py --check    runs only with --split
    lint-polish.py                runs only with --polish
    lint-english.py               runs only with --english
    check-consistency.py          runs only with --consistency
    check-sections.py             runs only with --type
    diff-content.py               runs only with --baseline
    check-parity.py               runs only with --parity <source.md>
    check-titles.py      runs only with --title-agreement

Sibling tools are located next to this script, else under ``--skill-root <dir>``
or ``SKILL_ROOT`` - running from the skill tree needs no flag at all.
A missing sibling reports SKIP and never gates.

Usage:
    python check-document.py <file.md> [--width N] [--payload-markdown]
        [--layout wrap|unwrap] [--split] [--polish] [--english]
        [--consistency] [--type <slug-or-path>]
        [--language <code-or-path>] [--baseline <file>] [--normalize-chars]
        [--parity <source.md>] [--terms <glossary.md> ...]
        [--expect-map <file> ...] [--eol lf|crlf] [--title-agreement]
        [--skill-root <dir>]
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

POLISH_RULES = ("languages/pl.md", "translations/en-pl/en-pl-software.md")
ENGLISH_RULES = ("languages/en.md",)


def reconfigure_stdio():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="backslashreplace")
        except Exception:
            pass


def resolve(name: str, skill_root: Path | None) -> Path | None:
    """Locate a sibling script beside this file or under the skill root."""
    here = Path(__file__).resolve().parent / name
    if here.is_file():
        return here
    if skill_root is not None:
        for probe in (skill_root / "scripts" / name, skill_root / name):
            if probe.is_file():
                return probe
    return None


def rule_path(relative: str, skill_root: Path | None) -> Path | None:
    """Resolve a rule file - in place it sits next to scripts/, copied it
    needs the skill root."""
    for base in (Path(__file__).resolve().parent.parent, skill_root):
        if base is None:
            continue
        probe = base / relative
        if probe.is_file():
            return probe
    return None


def run(script: Path, args: list[str], cwd: Path) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, str(script), *args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
        timeout=120,
    )
    return result.returncode, (result.stdout or "").strip()


def report(label: str, code: int | None, output: str, gated: bool) -> int:
    """Print one consolidated line plus detail lines on failure.

    Returns 1 when a gated check reported findings.
    """
    if code is None:
        print(f"SKIP {label} - tool not found")
        return 0
    first = output.split("\n", 1)[0] if output else ""
    detail = output.split("\n", 1)[1] if "\n" in output else ""
    if code == 0:
        print(f"PASS {label}" + (f" - {first}" if first.startswith("WARN") else ""))
        return 0
    verdict = "FAIL" if gated else "NOTE"
    print(f"{verdict} {label}" + (f" - {first}" if first else ""))
    if detail:
        detail_lines = detail.split("\n")
        for line in detail_lines[:12]:
            print(f"    {line}")
        if len(detail_lines) > 12:
            print(f"    ... {len(detail_lines) - 12} more finding(s)")
    return 1 if gated else 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file", type=Path, help="document to check")
    parser.add_argument("--width", type=int, default=None)
    parser.add_argument("--payload-markdown", action="store_true")
    parser.add_argument("--layout", choices=("wrap", "unwrap"), default=None,
                        help="gate on the reflow check matching this convention")
    parser.add_argument("--split", action="store_true",
                        help="also run split-sentences --check")
    parser.add_argument("--polish", action="store_true",
                        help="also run lint-polish.py with skill rule tables")
    parser.add_argument("--english", action="store_true",
                        help="also run lint-english.py with the English "
                             "rule tables")
    parser.add_argument("--consistency", action="store_true",
                        help="also run check-consistency.py for internal "
                             "references and terminology drift")
    parser.add_argument("--type", dest="type_arg", default=None,
                        help="type slug or path for check-sections.py")
    parser.add_argument("--language", default=None,
                        help="language code or path for localized sections")
    parser.add_argument("--baseline", type=Path, default=None,
                        help="baseline file for diff-content.py")
    parser.add_argument("--normalize-chars", action="store_true",
                        help="pass --normalize-chars to diff-content.py")
    parser.add_argument("--parity", type=Path, default=None, metavar="SOURCE",
                        help="source document for the check-parity.py "
                             "structural diff")
    parser.add_argument("--terms", type=Path, action="append", default=[],
                        metavar="GLOSSARY",
                        help="glossary file for check-parity concordance "
                             "hints and expected-translation seeding "
                             "(repeatable)")
    parser.add_argument("--expect-map", type=Path, action="append",
                        default=[], metavar="FILE",
                        help="declared SRC -> TGT translation map for "
                             "check-parity (repeatable)")
    parser.add_argument("--eol", choices=("lf", "crlf"), default=None,
                        help="declared line-ending convention forwarded "
                             "to check-parity")
    parser.add_argument("--title-agreement", action="store_true",
                        help="also run check-titles.py for "
                             "summary-table/heading title parity")
    parser.add_argument("--skill-root", type=Path, default=None)
    args = parser.parse_args(argv)

    if not args.file.is_file():
        print(f"ERROR document not found: {args.file}")
        return 1

    skill_root = args.skill_root or (
        Path(os.environ["SKILL_ROOT"]) if os.environ.get("SKILL_ROOT")
        else None
    )
    cwd = args.file.resolve().parent
    payload = ["--payload-markdown"] if args.payload_markdown else []
    width = ["--width", str(args.width)] if args.width else []
    doc = str(args.file.resolve())
    failures = 0
    print(f"check-document: {args.file}")

    script = resolve("detect-encoding.py", skill_root)
    if script is None:
        print("SKIP detect-encoding - tool not found")
    else:
        code, output = run(script, [doc], cwd)
        first = output.split("\n", 1)[0] if output else ""
        print(f"INFO detect-encoding - {first}")

    script = resolve("validate-document.py", skill_root)
    if script is None:
        print("SKIP validate-document - tool not found")
    else:
        code, output = run(script, [doc, *width, *payload], cwd)
        failures += report("validate-document", code, output, gated=True)

    script = resolve("format-table.py", skill_root)
    if script is None:
        print("SKIP format-table - tool not found")
    else:
        code, output = run(script, [doc, "--check", *payload], cwd)
        failures += report("format-table --check", code, output, gated=True)

    script = resolve("align-comments.py", skill_root)
    if script is None:
        print("SKIP align-comments - tool not found")
    else:
        code, output = run(script, [doc, "--check", *payload], cwd)
        failures += report("align-comments --check", code, output, gated=True)

    script = resolve("reflow-prose.py", skill_root)
    if script is None:
        print("SKIP reflow-prose - tool not found")
    else:
        for direction in ("wrap", "unwrap"):
            gated = args.layout == direction
            code, output = run(script, [doc, f"--{direction}", "--check",
                                        *width, *payload], cwd)
            failures += report(f"reflow-prose --{direction} --check",
                               code, output, gated=gated)

    if args.split:
        script = resolve("split-sentences.py", skill_root)
        if script is None:
            print("SKIP split-sentences - tool not found")
        else:
            code, output = run(script, [doc, "--check", *payload], cwd)
            failures += report("split-sentences --check", code, output, gated=True)

    if args.polish:
        script = resolve("lint-polish.py", skill_root)
        if script is None:
            print("SKIP lint-polish - tool not found")
        else:
            rules = [rule_path(r, skill_root) for r in POLISH_RULES]
            rule_args = [a for r in rules if r for a in ("--rules", str(r))]
            code, output = run(script, [doc, *rule_args], cwd)
            failures += report("lint-polish", code, output, gated=True)

    if args.english:
        script = resolve("lint-english.py", skill_root)
        if script is None:
            print("SKIP lint-english - tool not found")
        else:
            rules = [rule_path(r, skill_root) for r in ENGLISH_RULES]
            rule_args = [a for r in rules if r for a in ("--rules", str(r))]
            code, output = run(script, [doc, *rule_args, *payload], cwd)
            failures += report("lint-english", code, output, gated=True)

    if args.consistency:
        script = resolve("check-consistency.py", skill_root)
        if script is None:
            print("SKIP check-consistency - tool not found")
        else:
            code, output = run(script, [doc, *payload], cwd)
            failures += report("check-consistency", code, output,
                               gated=True)

    if args.type_arg:
        script = resolve("check-sections.py", skill_root)
        if script is None:
            print("SKIP check-sections - tool not found")
        else:
            section_args = [doc, "--type", args.type_arg]
            if args.language:
                section_args += ["--language", args.language]
            code, output = run(script, [*section_args, *payload], cwd)
            failures += report("check-sections", code, output, gated=True)

    if args.baseline:
        script = resolve("diff-content.py", skill_root)
        if script is None:
            print("SKIP diff-content - tool not found")
        else:
            diff_args = [doc, "--baseline", str(args.baseline)]
            if args.normalize_chars:
                diff_args.append("--normalize-chars")
            code, output = run(script, diff_args, cwd)
            failures += report("diff-content", code, output, gated=True)

    if args.parity:
        script = resolve("check-parity.py", skill_root)
        if script is None:
            print("SKIP check-parity - tool not found")
        else:
            parity_args = [str(args.parity.resolve()), doc]
            for glossary in args.terms:
                parity_args += ["--terms", str(glossary)]
            for expect_map in args.expect_map:
                parity_args += ["--expect-map", str(expect_map)]
            if args.eol:
                parity_args += ["--eol", args.eol]
            code, output = run(script, parity_args, cwd)
            failures += report("check-parity", code, output, gated=True)

    if args.title_agreement:
        script = resolve("check-titles.py", skill_root)
        if script is None:
            print("SKIP check-titles - tool not found")
        else:
            code, output = run(script, [doc], cwd)
            failures += report("check-titles", code, output,
                               gated=True)

    print(f"check-document: {'PASS' if not failures else 'FAIL'} "
          f"({failures} gated check(s) reporting)")
    return 1 if failures else 0


if __name__ == "__main__":
    reconfigure_stdio()
    sys.exit(main(sys.argv[1:]))
