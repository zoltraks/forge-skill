#!/usr/bin/env python3
"""Renumber a Markdown fragment's section headings and internal references.

Prepares a fragment for insertion into a host document under a target chapter
number - the mechanical half of a document merge. Run in place:

  python <skill-root>/scripts/renumber-sections.py FRAGMENT --prefix N [options]

Operations:

- numbered headings gain the prefix: `## 4. Title` becomes `## 6.4 Title`
  under `--prefix 6`, `### 4.1 Title` becomes `### 6.4.1 Title`
- `section N` and `section N.M` references gain the prefix
- `--number-unnumbered` numbers bare `##` headings sequentially under the
  prefix, in document order
- `--ref-parens` remaps bare `(N)` references to `(<prefix>.N)`
- `--ref-cells` remaps table cells that carry only a section number or a
  comma-separated list of them
- `--check` reports the planned edits without writing

H1 headings are never touched - dropping or retitling the fragment title is a
merge decision, not a mechanical one. Code spans, fenced code, and table
separator rows are exempt from reference remapping.

Line endings are detected and preserved.

Usage: python3 renumber-sections.py FILE --prefix P [options]
"""

from __future__ import annotations

import argparse
import os
import re
import sys

HEADING = re.compile(r"^(#{2,6}) (\d+(?:\.\d+)*)\.? (.*)$")
BARE_H2 = re.compile(r"^## (?!#)(?!\d+\.? )(.+)$")
FENCE = re.compile(r"^(\s*)(`{3,}|~{3,})")
SECTION_REF = re.compile(r"(section )(\d+(?:\.\d+)*)")
PAREN_REF = re.compile(r"\((\d+(?:\.\d+)*)\)")
NUM_CELL = re.compile(r"^\s*\d+(?:\.\d+)?(?:\s*,\s*\d+(?:\.\d+)?)*\s*$")
PREFIX_RE = re.compile(r"^\d+(?:\.\d+)*$")


def remap_refs(line: str, prefix: str, parens: bool, in_table: bool,
               ref_cells: bool) -> str:
    line = SECTION_REF.sub(lambda m: m.group(1) + prefix + "." + m.group(2), line)
    if parens:
        line = PAREN_REF.sub(lambda m: "(" + prefix + "." + m.group(1) + ")", line)
    if in_table and ref_cells:
        cells = line.split("|")
        for i, cell in enumerate(cells):
            if NUM_CELL.match(cell):
                cells[i] = " " + ", ".join(
                    prefix + "." + p.strip() for p in cell.strip().split(",")
                ) + " "
        line = "|".join(cells)
    return line


def renumber(lines, prefix, number_unnumbered, parens, ref_cells):
    out, changes = [], []
    seq = 0
    fences = []
    for n, line in enumerate(lines, 1):
        fence = FENCE.match(line)
        if fence:
            marker = fence.group(2)
            if fences and marker[0] == fences[-1][0] and len(marker) >= len(fences[-1]):
                fences.pop()
            elif not fences:
                fences.append(marker)
            out.append(line)
            continue
        if fences or line.lstrip().startswith("# "):
            out.append(line)
            continue
        m = HEADING.match(line)
        if m:
            hashes, num, title = m.groups()
            new = f"{hashes} {prefix}.{num} {title}"
            if new != line:
                changes.append((n, line, new))
            out.append(new)
            continue
        if number_unnumbered and BARE_H2.match(line):
            seq += 1
            new = f"## {prefix}.{seq} {BARE_H2.match(line).group(1)}"
            changes.append((n, line, new))
            out.append(new)
            continue
        in_table = line.startswith("|") and not re.match(r"^\|[\s:|-]+\|$", line)
        new = remap_refs(line, prefix, parens, in_table, ref_cells)
        if new != line:
            changes.append((n, line, new))
        out.append(new)
    return out, changes


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Renumber a Markdown fragment's headings and section references.")
    ap.add_argument("file", help="fragment to renumber, edited in place")
    ap.add_argument("--prefix", required=True,
                    help="target chapter or section number, e.g. 6 or 6.1")
    ap.add_argument("--number-unnumbered", action="store_true",
                    help="number bare ## headings sequentially under the prefix")
    ap.add_argument("--ref-parens", action="store_true",
                    help="remap bare (N) references to (PREFIX.N)")
    ap.add_argument("--ref-cells", action="store_true",
                    help="remap numeric-only table cells as section references")
    ap.add_argument("--check", action="store_true",
                    help="report planned edits without writing")
    args = ap.parse_args()

    if not PREFIX_RE.match(args.prefix):
        print(f"renumber-sections: invalid --prefix '{args.prefix}'")
        return 2

    raw = open(args.file, "rb").read()
    crlf = b"\r\n" in raw
    lines = raw.decode("utf-8").replace("\r\n", "\n").split("\n")

    out, changes = renumber(lines, args.prefix, args.number_unnumbered,
                            args.ref_parens, args.ref_cells)

    if args.check:
        for n, old, new in changes:
            print(f"line {n}: {old!r} -> {new!r}")
        print(f"renumber-sections: {len(changes)} planned edit(s)")
        return 1 if changes else 0

    if changes:
        eol = "\r\n" if crlf else "\n"
        tmp = args.file + ".tmp-write"
        try:
            with open(tmp, "wb") as handle:
                handle.write(eol.join(out).encode("utf-8"))
            os.replace(tmp, args.file)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)
        if crlf:
            print("note: file uses CRLF line endings - preserved")
    print(f"renumber-sections: {len(changes)} edit(s) applied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
