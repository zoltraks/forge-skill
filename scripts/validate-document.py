#!/usr/bin/env python3
"""Mechanical style checker for Markdown documents produced by this skill.

Covers the scriptable items of process/document-checklist.md: structure,
spacing, characters, lists, code fences, and table structure and alignment.

Non-ASCII characters in prose (outside inline code spans) are reported as
warnings, not failures - they may be a deliberate document convention.
Letters (typically language diacritics) aggregate into a single summary
warning, while non-ASCII punctuation and symbols still report per line.
Box-drawing characters (U+2500-U+257F) are exempt.

`text`/`txt` fence tags are warnings for the same reason - an existing
document may carry them as its established convention, while new content
defaults to untagged fences for plain text.

Run this file in place from the skill repository -
`python <skill-root>/scripts/validate-document.py` - and run it on the
document file. Copy it under a `.tmp.` name into the working
repository's `temp/` directory (or the repository root when no `temp/`
exists) only when the skill root cannot be invoked, and remove the copy
afterward.

Usage: python validate-document.py <file.md> [--width N] [--payload-markdown]

  --width N            flag lines longer than N characters (tables excluded)
  --payload-markdown   apply a curated subset of checks inside ```markdown
                       fenced blocks (embedded payload documents): trailing
                       whitespace, consecutive blank lines, lone list
                       markers, and heading checks
"""

import argparse
import json
import re
import sys
from pathlib import Path

FENCE = re.compile(r"^\s*(`{3,}|~{3,})\s*(\w*)")
HEADING = re.compile(r"^(#{1,6})\s")
BULLET = re.compile(r"^\s*[-*+] ")
ORDERED = re.compile(r"^\s*\d+\. ")
LONE_ITEM = re.compile(r"^\s*[-*+][ \t]*$")
LONE_ORDERED = re.compile(r"^\d+[.)][ \t]*$")
TYPO_QUOTES = "“”‘’‚„«»"
INLINE_CODE = re.compile(r"`[^`]*`")


def sep_like(cells):
    stripped = [c.strip() for c in cells]
    return (
        len(stripped) > 0
        and all(set(c) <= set("-:") for c in stripped)
        and any("-" in c for c in stripped)
    )


def parse_row(line):
    parts = line.split("|")
    cells = parts[1:-1] if parts and parts[-1].strip() == "" else parts[1:]
    return [c.strip() for c in cells]


def raw_cells(line):
    parts = line.split("|")
    return parts[1:-1] if parts and parts[-1].strip() == "" else parts[1:]


def in_payload(fences, payload_markdown):
    return payload_markdown and bool(fences) and all(
        lang == "markdown" for _, lang, *_ in fences
    )


def check_tables(lines, issues):
    i = 0
    fences = []
    sep_styles = set()
    while i < len(lines):
        fence = FENCE.match(lines[i])
        if fence:
            marker = len(fence.group(1))
            if fences:
                if marker >= fences[-1][0]:
                    fences.pop()
            else:
                fences.append((marker, fence.group(2)))
            i += 1
            continue
        if fences or not lines[i].startswith("|"):
            i += 1
            continue
        block = []
        start = i
        while i < len(lines) and lines[i].startswith("|"):
            block.append(lines[i])
            i += 1
        rows = [raw_cells(l) for l in block]
        ncols = max(len(r) for r in rows)

        for offset, line in enumerate(block):
            if line.startswith("||"):
                issues.append(
                    f"line {start + offset + 1}: row starts with a double pipe"
                )
            piped = next(
                (s for s in INLINE_CODE.findall(line) if "|" in s), None)
            if piped is not None:
                issues.append(
                    f"line {start + offset + 1}: literal pipe inside "
                    f"code span {piped[:40]} inflates the column count "
                    "- use `&#124;` or a different layout")
            if "\\|" in line:
                issues.append(
                    f"line {start + offset + 1}: escaped pipe \\| still "
                    "splits the row on `|` - use `&#124;`")

        sep_idx = next((k for k, r in enumerate(rows) if sep_like(r)), None)
        if sep_idx is None:
            issues.append(f"line {start + 1}: table has no separator row")
        else:
            if sep_idx != 1:
                issues.append(
                    f"line {start + sep_idx + 1}: separator row is not the "
                    "second table row"
                )
            missing = [
                str(j + 1) for j, c in enumerate(rows[sep_idx]) if "-" not in c
            ]
            if missing:
                issues.append(
                    f"line {start + sep_idx + 1}: separator cell(s) "
                    + ", ".join(missing) + " lack(s) hyphens"
                )

        for j in range(ncols):
            if all(
                j >= len(r) or r[j].strip() == ""
                for r in rows
                if not sep_like(r)
            ):
                issues.append(
                    f"line {start + 1}: column {j + 1} is empty in every row"
                )

        widths = [0] * ncols
        for r in rows:
            if sep_like(r):
                for c in r:
                    if "-" in c:
                        sep_styles.add(
                            "spaced" if c != c.strip() else "compact"
                        )
                continue
            for j in range(ncols):
                cell = r[j].strip() if j < len(r) else ""
                widths[j] = max(widths[j], len(cell))
        for offset, r in enumerate(rows):
            if len(r) != ncols:
                issues.append(f"line {start + offset + 1}: ragged table row")
                continue
            if sep_like(r):
                for j, cell in enumerate(r):
                    if len(cell) != widths[j] + 2:
                        issues.append(
                            f"line {start + offset + 1}: separator cell width mismatch"
                        )
                        break
                continue
            for j, cell in enumerate(r):
                if len(cell) != widths[j] + 2:
                    issues.append(
                        f"line {start + offset + 1}: table cell not padded to column width"
                    )
                    break
    if len(sep_styles) > 1:
        issues.append("document mixes spaced and compact table separators")


def load_config(path):
    """Find document-format.json in the document's directory or an ancestor.

    Returns (config dict, config path or None). Keys are single English
    words; the format is draft: ``width`` overrides a missing --width and
    ``findings`` lists issue substrings suppressed from the FAIL report.
    """
    directory = Path(path).resolve().parent
    for candidate in (directory, *directory.parents):
        cfg = candidate / "document-format.json"
        if cfg.is_file():
            try:
                data = json.loads(cfg.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                return {}, cfg
            return (data if isinstance(data, dict) else {}), cfg
    return {}, None


def main(path, width, payload_markdown):
    config, config_path = load_config(path)
    if not width and isinstance(config.get("width"), int):
        width = config["width"]
    suppress = config.get("findings")
    suppress = suppress if isinstance(suppress, list) else []
    raw = open(path, "rb").read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        print(f"FAIL {path}: not decodable as UTF-8, check encoding first "
              "(see conventions/file-encoding.md)")
        return 1

    lines = text.replace("\r\n", "\n").split("\n")
    issues = []
    warnings = []
    foreign_letters = {}

    h1 = 0
    h1_heads: list[str] = []
    fences = []
    fence_first = -1
    in_indented = False
    last_open_heading = -1
    last_open_level = 0
    prev = ""
    for i, line in enumerate(lines):
        n = i + 1
        fence = FENCE.match(line)
        if fence:
            marker = len(fence.group(1))
            if fences:
                if marker >= fences[-1][0]:
                    if i > fence_first + 1 and lines[i - 1].strip() == "":
                        issues.append(f"line {n}: blank line at end of code block")
                    if i + 1 < len(lines) and lines[i + 1].strip() != "":
                        issues.append(f"line {n}: no blank line after code block")
                    fences.pop()
            else:
                if prev.strip() != "" and not HEADING.match(prev):
                    issues.append(f"line {n}: no blank line before code block")
                if fence.group(2) in ("text", "txt"):
                    warnings.append(
                        f"line {n}: '{fence.group(2)}' tag on fenced block - "
                        "plain-text blocks default to untagged fences in new content"
                    )
                fence_first = i
                fences.append((marker, fence.group(2)))
            prev = line
            continue

        if line != line.rstrip(" \t"):
            issues.append(f"line {n}: trailing whitespace")

        if fences and not in_payload(fences, payload_markdown):
            if i == fence_first + 1 and line.strip() == "":
                issues.append(f"line {n}: blank line at start of code block")
            prev = line
            continue

        payload = in_payload(fences, payload_markdown)
        indent = len(line) - len(line.lstrip())
        indented_code = indent >= 4 and (
            payload
            or (
                not (BULLET.match(line) or ORDERED.match(line))
                and (in_indented or prev.strip() == "")
            )
        )
        if indented_code:
            in_indented = True
        elif line.strip():
            in_indented = False

        if line.strip() == "" and prev.strip() == "":
            issues.append(f"line {n}: consecutive blank lines")

        if LONE_ITEM.match(line) or LONE_ORDERED.match(line):
            issues.append(f"line {n}: lone list marker")

        heading = HEADING.match(line)
        if heading:
            level = len(heading.group(1))
            if last_open_heading >= 0 and level <= last_open_level and all(
                    lines[j].strip() == ""
                    for j in range(last_open_heading + 1, i)):
                warnings.append(
                    f"line {last_open_heading + 1}: empty heading")
            last_open_heading = i
            last_open_level = level
            if not payload:
                if level == 1:
                    h1 += 1
                    h1_heads.append(line.lstrip("#").strip())
                if level >= 4:
                    issues.append(f"line {n}: heading deeper than H3")
                if line.rstrip().endswith((".", ",", ":", ";", "!", "?")):
                    issues.append(f"line {n}: heading ends with punctuation")

        if not payload and not indented_code:
            prose = INLINE_CODE.sub("", line)
            if any(q in prose for q in TYPO_QUOTES):
                issues.append(f"line {n}: typographic quote or apostrophe")

            if ";" in prose and not line.startswith("|"):
                issues.append(f"line {n}: semicolon in prose")

            if not line.lstrip().startswith("|") \
                    and line.rstrip().endswith("|"):
                issues.append(
                    f"line {n}: stranded table fragment - "
                    "line ends with a bare pipe")

            if re.search(r"[\U0001F300-\U0001FAFF☀-➿⬀-⯿]", line):
                issues.append(f"line {n}: emoji or pictograph")

            prev_heading = HEADING.match(prev)
            if prev_heading and not heading and line.strip() != "":
                issues.append(f"line {n - 1}: no blank line after heading")
            if (
                heading
                and prev.strip() != ""
                and not prev_heading
                and prev.strip() not in ("---", "+++")
            ):
                issues.append(f"line {n}: no blank line before heading")

            foreign = [
                c for c in dict.fromkeys(prose)
                if ord(c) > 127
                and not 0x2500 <= ord(c) <= 0x257F  # box-drawing
                and not 0x2190 <= ord(c) <= 0x21FF  # arrows
            ]
            symbols = [c for c in foreign if not c.isalpha()]
            if symbols:
                warnings.append(
                    f"line {n}: non-ASCII character(s) in prose: "
                    + " ".join(f"U+{ord(c):04X} '{c}'" for c in symbols)
                )
            for c in foreign:
                if c.isalpha():
                    foreign_letters[c] = foreign_letters.get(c, 0) + 1

        if width and not line.startswith("|") and not indented_code \
                and len(line) > width:
            issues.append(f"line {n}: {len(line)} chars exceeds width {width}")

        if indented_code:
            prev = line
            continue

        structural = BULLET.match(line) or ORDERED.match(line) or line.startswith("|")
        prev_structural = BULLET.match(prev) or ORDERED.match(prev) or prev.startswith("|")
        continuation = line[:1] in (" ", "\t") and line.strip() != ""
        prev_continuation = prev[:1] in (" ", "\t") and prev.strip() != ""
        if (
            structural
            and not payload
            and prev.strip() != ""
            and not prev_structural
            and not prev_continuation
        ):
            issues.append(f"line {n}: no blank line before list or table")
        if (
            prev_structural
            and not structural
            and not payload
            and not continuation
            and line.strip() != ""
        ):
            issues.append(f"line {n}: no blank line after list or table")

        prev = line

    if last_open_heading >= 0 and all(
            line.strip() == ""
            for line in lines[last_open_heading + 1:]):
        warnings.append(f"line {last_open_heading + 1}: empty heading")

    if foreign_letters:
        warnings.append(
            "non-ASCII letter(s) in prose (often diacritics - expected for "
            "non-English documents): "
            + " ".join(f"U+{ord(c):04X} '{c}'" for c in foreign_letters)
        )

    if h1 == 0:
        warnings.append("document has no H1 title (allowed for notes, verify the type)")
    if h1 > 1:
        chapter_numbers = []
        for text in h1_heads[1:]:
            match = re.match(r"^(\d+)[\s.:]", text)
            if match:
                chapter_numbers.append(int(match.group(1)))
        if len(chapter_numbers) == h1 - 1:
            if chapter_numbers != sorted(set(chapter_numbers)):
                warnings.append(
                    "numbered-chapter dialect: H1 chapter numbers are not strictly increasing"
                )
        else:
            warnings.append(f"document has {h1} H1 headings (verify numbered-chapter dialect)")

    check_tables(lines, issues)

    if suppress:
        kept = []
        dropped = 0
        for message in issues:
            if any(str(entry) in message for entry in suppress):
                dropped += 1
            else:
                kept.append(message)
        issues = kept
        if dropped:
            print(f"note: {dropped} finding(s) suppressed by {config_path}")

    for message in warnings:
        print(f"WARN {path}:{message}")
    if issues:
        for message in issues:
            print(f"FAIL {path}:{message}")
        print(f"{len(issues)} issue(s) found")
        return 1
    print(f"PASS {path}")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(
        description="Mechanical style checker for Markdown documents."
    )
    parser.add_argument("file")
    parser.add_argument("--width", type=int, default=0,
                        help="flag lines longer than N characters")
    parser.add_argument("--payload-markdown", action="store_true",
                        help="apply curated checks inside ```markdown blocks")
    parsed = parser.parse_args()
    raise SystemExit(main(parsed.file, parsed.width, parsed.payload_markdown))
