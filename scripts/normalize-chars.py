#!/usr/bin/env python3
"""Normalize typographic characters in Markdown prose to ASCII equivalents.

Covers the character substitutions from the Characters section of
process/document-checklist.md and the ASCII convention the language files
declare: typographic quotes and apostrophes, dashes and the minus sign,
arrows, ellipsis, Unicode spaces, and the soft hyphen.

Replacements are literal - one character maps to its ASCII form without
inserting or removing surrounding whitespace, so existing spacing decides the
result: `A — B` becomes `A - B`, `48–49` becomes `48-49`, `A → B` becomes
`A -> B`, `10→5` becomes `10->5`. Table alignment may shift when a
replacement changes cell width - run `format-table.py` afterwards, per the
validation order in scripts/README.md.

Fenced code blocks are opaque. Frontmatter (a `---`/`+++` block at the top of
the file) is opaque. Inline code spans, table cells, link targets, and HTML
comments are normalized like the rest of the prose.

Run this file in place from the skill repository -
`python <skill-root>/scripts/normalize-chars.py` - and run it on the
document file. Copy it under a `.tmp.` name into the working
repository's `temp/` directory (or the repository root when no `temp/`
exists) only when the skill root cannot be invoked, and remove the copy
afterward.

Usage: python normalize-chars.py <file.md> [--check] [--payload-markdown]

  --check              report lines that would change and exit 1, without
                       writing the file
  --payload-markdown   also normalize inside ```markdown fenced blocks
                       (embedded payload documents); other fence languages
                       always stay opaque
"""

import argparse
import os
import re
import sys

FENCE = re.compile(r"^\s*(`{3,}|~{3,})\s*(\w*)")
FRONTMATTER = re.compile(r"^\s*(---|\+\+\+)\s*$")

REPLACEMENTS = {
    # Typographic quotes and apostrophes -> straight ASCII forms.
    "„": '"', "“": '"', "”": '"', "‚": '"',
    "«": '"', "»": '"', "‹": "'", "›": "'",
    "‘": "'", "’": "'", "‛": "'",
    # Dashes and the mathematical minus -> ASCII hyphen.
    "‐": "-", "‑": "-", "–": "-", "—": "-", "−": "-", "―": "-",
    # Arrows -> ASCII sequences.
    "→": "->", "←": "<-", "↔": "<->", "⇒": "=>", "⇐": "<=",
    # Ellipsis character -> three dots.
    "…": "...",
    # Soft hyphen -> removed.
    "\u00ad": "",
}

# Unicode space separators collapse to the plain ASCII space.
SPACE_CHARS = {
    " ", " ", " ", " ", " ", " ",
    " ", " ", " ", " ", " ", " ",
    " ", " ", " ", "　",
}


def decode(raw):
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16"), "utf-16"
    return raw.decode("utf-8"), "utf-8"


def normalize(text):
    return "".join(
        REPLACEMENTS.get(ch, " " if ch in SPACE_CHARS else ch) for ch in text
    )


def in_payload(fences, payload_markdown):
    return payload_markdown and bool(fences) and all(
        lang == "markdown" for _, lang, *_ in fences
    )


def main(path, check_only, payload_markdown):
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    try:
        text, encoding = decode(raw)
    except UnicodeDecodeError:
        print(f"FAIL {path}: not decodable as UTF-8 or UTF-16, "
              "check encoding first (see conventions/file-encoding.md)")
        return 1
    lines = text.replace("\r\n", "\n").split("\n")

    out = []
    changed = []
    fences = []
    in_frontmatter = bool(lines) and bool(FRONTMATTER.match(lines[0]))
    for i, line in enumerate(lines):
        n = i + 1
        if in_frontmatter:
            out.append(line)
            if n > 1 and FRONTMATTER.match(line):
                in_frontmatter = False
            continue
        fence = FENCE.match(line)
        if fence:
            marker = len(fence.group(1))
            if fences:
                if marker >= fences[-1][0] and fence.group(1)[0] == fences[-1][2]:
                    fences.pop()
                elif fences[-1][1] == "markdown":
                    fences.append((marker, fence.group(2), fence.group(1)[0]))
            else:
                fences.append((marker, fence.group(2), fence.group(1)[0]))
            out.append(line)
            continue
        if fences and not in_payload(fences, payload_markdown):
            out.append(line)
            continue
        fixed = normalize(line)
        if fixed != line:
            changed.append(n)
            chars = " ".join(
                f"U+{ord(c):04X}" for c in dict.fromkeys(line)
                if c in REPLACEMENTS or c in SPACE_CHARS
            )
            print(f"line {n}: normalized {chars}")
        out.append(fixed)

    if check_only:
        if changed:
            print(f"{len(changed)} line(s) need normalization")
            return 1
        print(f"PASS {path}: no typographic characters found")
        return 0

    if not changed:
        print(f"PASS {path}: nothing to normalize")
        return 0

    eol = "\r\n" if crlf else "\n"
    tmp = str(path) + ".tmp-write"
    try:
        with open(tmp, "wb") as handle:
            handle.write(eol.join(out).encode(encoding))
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    if crlf:
        print("note: file uses CRLF line endings - preserved")
    print(f"normalized {len(changed)} line(s)")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(
        description="Normalize typographic characters to ASCII equivalents."
    )
    parser.add_argument("file")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--payload-markdown", action="store_true",
                        help="also normalize inside ```markdown blocks")
    parsed = parser.parse_args()
    raise SystemExit(main(parsed.file, parsed.check, parsed.payload_markdown))
