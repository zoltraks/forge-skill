#!/usr/bin/env python3
"""Canonical table formatter implementing the table rules in the language
files (languages/en.md, languages/pl.md, languages/de.md).

Run this file in place from the skill repository -
`python <skill-root>/scripts/format-table.py` - and run it on the document
file, verifying that all `|` separators align vertically. Copy it under a
`.tmp.` name into the working repository's `temp/` directory (or the
repository root when no `temp/` exists) only when the skill root cannot be
invoked, and remove the copy afterward.

Usage: python format-table.py <document.md> [--check] [--payload-markdown]
                                     [--drop-empty-columns]

  --check              report tables that would be reformatted and exit 1,
                       without writing the file
  --payload-markdown   also format tables inside ```markdown fenced blocks
                       (embedded payload documents); other fence languages
                       always stay opaque
  --drop-empty-columns remove columns that are empty in every non-separator
                       row (a spurious column, never a spacer); without the
                       flag such columns are reported as warnings only

Separator rows are normalized on every run: a separator-row cell that lacks
hyphens is rebuilt with the correct hyphen count, since only a dashed cell
declares its column.
"""

import argparse
import os
import re
import sys

FENCE = re.compile(r"^\s*(`{3,}|~{3,})\s*(\w*)")


def decode(raw):
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16"), "utf-16"
    return raw.decode("utf-8"), "utf-8"


def parse_row(line):
    parts = line.split("|")
    cells = parts[1:-1] if parts and parts[-1].strip() == "" else parts[1:]
    return [c.strip() for c in cells]


def is_sep(cells):
    return len(cells) > 0 and all(set(c) <= set("-:") and "-" in c for c in cells)


def sep_like(cells):
    return (
        len(cells) > 0
        and all(set(c) <= set("-:") for c in cells)
        and any("-" in c for c in cells)
    )


def format_block(block, start, drop_empty):
    warnings = []
    rows = [parse_row(l) for l in block]
    for k, line in enumerate(block):
        if line.startswith("||"):
            warnings.append(
                f"line {start + k + 1}: row starts with '||' - "
                "double pipe parses as an empty first cell"
            )
    for k, r in enumerate(rows):
        if sep_like(r) and not is_sep(r):
            warnings.append(
                f"line {start + k + 1}: separator row cell(s) lacked hyphens - "
                "normalized"
            )
    ncols = max(len(r) for r in rows)
    rows = [r + [""] * (ncols - len(r)) for r in rows]
    empty = [
        j
        for j in range(ncols)
        if all(r[j] == "" for r in rows if not sep_like(r))
    ]
    if empty:
        cols = ", ".join(str(j + 1) for j in empty)
        if drop_empty and len(empty) < ncols:
            drop = set(empty)
            rows = [
                [c for j, c in enumerate(r) if j not in drop] for r in rows
            ]
            ncols -= len(empty)
            warnings.append(
                f"line {start + 1}: dropped empty column(s) {cols}"
            )
        elif drop_empty:
            warnings.append(
                f"line {start + 1}: every column is empty - "
                "table left unchanged"
            )
        else:
            warnings.append(
                f"line {start + 1}: column(s) {cols} empty in every row "
                "(use --drop-empty-columns to remove)"
            )
    widths = [1] * ncols
    for r in rows:
        if sep_like(r):
            continue
        for j, c in enumerate(r):
            widths[j] = max(widths[j], len(c))
    out = []
    for r in rows:
        if sep_like(r):
            out.append("|" + "|".join("-" * (w + 2) for w in widths) + "|")
        else:
            out.append(
                "| " + " | ".join(c.ljust(widths[j]) for j, c in enumerate(r)) + " |"
            )
    return out, warnings


def in_payload(fences, payload_markdown):
    return payload_markdown and bool(fences) and all(
        lang == "markdown" for _, lang, *_ in fences
    )


def main(path, check_only, payload_markdown, drop_empty, excludes=None):
    if os.path.isdir(path):
        from pathlib import Path
        files = [str(p) for p in sorted(Path(path).rglob("*.md"))
                 if not (({"work", ".git"} | set(excludes or ()))
                 & set(p.parts))]
        if not files:
            print(f"PASS {path}: no markdown files")
            return 0
        worst = 0
        for f in files:
            worst = max(worst, main(f, check_only, payload_markdown,
                                    drop_empty,
                                    excludes))
        return worst
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    try:
        text, encoding = decode(raw)
    except UnicodeDecodeError:
        print(f"FAIL {path}: not decodable as UTF-8 or UTF-16, "
              "check encoding first (see conventions/file-encoding.md)")
        return 1
    lines = text.replace("\r\n", "\n").split("\n")

    out, i, tables = [], 0, 0
    fences = []
    changed = []
    while i < len(lines):
        line = lines[i]
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
            i += 1
            continue
        if (not fences or in_payload(fences, payload_markdown)) \
                and line.startswith("|"):
            block = []
            start = i
            while i < len(lines) and lines[i].startswith("|"):
                block.append(lines[i])
                i += 1
            formatted, warnings = format_block(block, start, drop_empty)
            for message in warnings:
                print(message)
            if formatted != block:
                changed.append(start + 1)
            out.extend(formatted)
            tables += 1
        else:
            out.append(line)
            i += 1

    if check_only:
        for n in changed:
            print(f"line {n}: table would be reformatted")
        if changed:
            print(f"{len(changed)} table(s) need formatting")
            return 1
        print(f"PASS {path}: {tables} table(s) already aligned")
        return 0

    eol = "\r\n" if crlf else "\n"
    tmp = path + ".tmp-write"
    try:
        with open(tmp, "wb") as handle:
            handle.write(eol.join(out).encode(encoding))
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    if crlf:
        print("note: file uses CRLF line endings - preserved")
    print(f"formatted {tables} tables")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(
        description="Format Markdown tables with source-width alignment."
    )
    parser.add_argument("file")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--exclude", action="append", default=[],
                        metavar="NAME", help="skip files whose path contains a component with this name (repeatable, directory mode)")
    parser.add_argument("--payload-markdown", action="store_true")
    parser.add_argument("--drop-empty-columns", action="store_true",
                        help="remove columns that are empty in every "
                             "non-separator row")
    parsed = parser.parse_args()
    raise SystemExit(main(parsed.file, parsed.check, parsed.payload_markdown,
                          parsed.drop_empty_columns, parsed.exclude))
