#!/usr/bin/env python3
"""Verify that a mechanical transform changed no document content.

Compares the token stream of the working file against a baseline: the
version at git HEAD by default, or a file given with --baseline. Whitespace,
blank lines, and table separator rows are ignored, so a pure formatting pass
(wrapping, table alignment, spacing fixes) reports zero differences.

Run this file in place from the skill repository -
`python <skill-root>/scripts/diff-content.py` - and run it on the edited
file. Copy it under a `.tmp.` name into the working repository's `temp/`
directory (or the repository root when no `temp/` exists) only when the
skill root cannot be invoked, and remove the copy afterward.

Usage: python diff-content.py <file.md> [--baseline <path>]
                                      [--normalize-chars]

Exit code 0 means the token streams are identical - only whitespace, blank
lines, and table separators may differ. Exit 1 lists every token-level
insert, delete, or replace hunk with context, plus warnings for lines that
may have been merged together.

With --normalize-chars both sides are first mapped through the same
typographic-to-ASCII table that normalize-chars.py applies, so a pass that
only converted dashes, arrows, quotes, and Unicode spaces reports a clean
token stream while word-level edits still surface.
"""

import argparse
import difflib
import re
import subprocess
import sys
from pathlib import Path

SEPARATOR_ROW = re.compile(r"^[|\-: ]+$")

# Mirrors the mapping in normalize-chars.py - keep both in sync.
REPLACEMENTS = {
    "„": '"', "“": '"', "”": '"', "‚": '"',
    "«": '"', "»": '"', "‹": "'", "›": "'",
    "‘": "'", "’": "'", "‛": "'",
    "‐": "-", "‑": "-", "–": "-", "—": "-", "−": "-", "―": "-",
    "→": "->", "←": "<-", "↔": "<->", "⇒": "=>", "⇐": "<=",
    "…": "...", "\u00ad": "",
}
SPACE_CHARS = {
    " ", " ", " ", " ", " ", " ", " ", " ", " ",
    " ", " ", " ", " ", " ", " ", "　",
}


def normalize(text):
    return "".join(
        REPLACEMENTS.get(ch, " " if ch in SPACE_CHARS else ch) for ch in text
    )


def tokens(text):
    result = []
    for line in text.split("\n"):
        s = line.strip()
        if not s:
            continue
        if "|" in s and SEPARATOR_ROW.match(s):
            continue
        result.extend(s.split())
    return result


def head_version(path):
    """Return the file's content at git HEAD, or None when unavailable."""
    try:
        root = subprocess.run(
            ["git", "-C", str(path.parent), "rev-parse", "--show-toplevel"],
            capture_output=True, encoding="utf-8", errors="surrogateescape",
            check=True,
        ).stdout.strip()
        rel = path.resolve().relative_to(Path(root).resolve())
        result = subprocess.run(
            ["git", "-C", root, "show", f"HEAD:{rel.as_posix()}"],
            capture_output=True, encoding="utf-8", errors="surrogateescape",
        )
        if result.returncode != 0:
            return None
        return result.stdout
    except (subprocess.CalledProcessError, ValueError):
        return None


def merged_lines(before_text, after_text):
    """Find baseline line pairs whose junction now sits inside one line.

    For consecutive non-blank baseline lines A, B the signature
    `last words of A + first words of B` inside a single target line means
    the two lines were probably merged - the signature may also match when
    the same text legitimately appears twice, so findings need review.
    """
    before = [re.sub(r"\s+", " ", l.strip()) for l in before_text.split("\n")]
    after = [re.sub(r"\s+", " ", l.strip()) for l in after_text.split("\n")]
    after_heads = set()
    for line in after:
        words = line.split()
        if len(words) >= 3:
            after_heads.add(" ".join(words[:3]))
    warnings = []
    prev = None
    for i, line in enumerate(before):
        if not line:
            prev = None
            continue
        if prev is not None:
            tail = prev.split()[-3:]
            head = line.split()[:3]
            if len(tail) == 3 and len(head) == 3:
                sig = " ".join(tail + head)
                if " ".join(head) not in after_heads:
                    for n, candidate in enumerate(after, 1):
                        if sig in candidate:
                            warnings.append(
                                f"possible merged lines: baseline "
                                f"{prev_line}:{i + 1} share line {n}"
                            )
                            break
        prev = line
        prev_line = i + 1
    return warnings


def main(path, baseline_path, normalize_chars=False):
    target = Path(path)
    after = target.read_text(encoding="utf-8")

    if baseline_path:
        before = Path(baseline_path).read_text(encoding="utf-8")
    else:
        before = head_version(target)
        if before is None:
            print(f"FAIL {path}: no git HEAD version found, "
                  "pass --baseline <path> with a pre-edit copy")
            return 1

    if normalize_chars:
        before = normalize(before)
        after = normalize(after)

    warnings = merged_lines(before, after)
    for warning in warnings:
        print(f"WARN {warning}")

    old, new = tokens(before), tokens(after)
    if old == new:
        if warnings:
            print("token stream identical, but line boundaries may have "
                  "moved - review the warnings above")
        else:
            print(f"PASS {path}: token stream identical to baseline")
            print("only whitespace, blank lines, and table separators differ")
        return 0

    matcher = difflib.SequenceMatcher(None, old, new, autojunk=False)
    hunks = 0
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            continue
        hunks += 1
        context = " ".join(old[max(0, i1 - 6) : i1])
        print(f"{tag}: ...{context} [...]")
        if i2 > i1:
            print(f"  - {' '.join(old[i1:i2])[:160]}")
        if j2 > j1:
            print(f"  + {' '.join(new[j1:j2])[:160]}")

    print(f"{hunks} token difference(s) found")
    print("verify each hunk is an intended content change, not a formatting "
          "side effect")
    return 1


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(
        description="Compare document content against a baseline, ignoring "
        "whitespace, blank lines, and table separators."
    )
    parser.add_argument("file")
    parser.add_argument("--baseline", metavar="PATH",
                        help="pre-edit copy; defaults to git HEAD")
    parser.add_argument("--normalize-chars", action="store_true",
                        help="map typographic characters to ASCII before "
                             "comparing, per normalize-chars.py")
    parsed = parser.parse_args()
    raise SystemExit(main(parsed.file, parsed.baseline,
                          parsed.normalize_chars))
