#!/usr/bin/env python3
"""Wrap Markdown prose lines to a maximum width for documents whose own
conventions declare one.

Deprecated: superseded by `reflow-prose.py`, whose `--wrap` mode runs the
same algorithm and whose `--unwrap` mode performs the inverse join. This
file stays for compatibility with documents that already reference it.

The tool only ever splits a line - it never joins lines. Every output line
is therefore a prefix of a source line, which makes the operation safe on
documents mixing prose with opaque blocks such as tables, headings, fenced
code, indented code blocks, frontmatter, and embedded payload documents.

Run this file in place from the skill repository -
`python <skill-root>/scripts/wrap-prose.py` - and run it on the document
file. Copy it under a `.tmp.` name into the working repository's `temp/`
directory (or the repository root when no `temp/` exists) only when the
skill root cannot be invoked, and remove the copy afterward.

Usage: python wrap-prose.py <file.md> [--width N] [--payload-markdown]
                                  [--check]

  --width N            maximum line length, default 100
  --payload-markdown   also wrap prose inside ```markdown fenced blocks
                       (embedded payload documents); other fence languages
                       always stay opaque
  --check              report over-width lines without writing, exit 1 when
                       any line exceeds the width
"""

import argparse
import os
import re
import sys

FENCE = re.compile(r"^\s*(`{3,}|~{3,})\s*(\w*)")
ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])([ \t]+)(.*)$")
LONE_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s*$")
QUOTE = re.compile(r"^(\s*)((?:>\s*)+)(.*)$")
LEAD_PUNCT = r"[(\[{'\"]*"
TRAIL_PUNCT = r"[\")\].,;:!?}\"]*(?:'[a-zA-Z]*)?[\"')\].,;:!?}]*"
PROTECTED = re.compile(
    r"(" + LEAD_PUNCT + r"`+[^`]*`+" + TRAIL_PUNCT + r")"           # code span + adjacent punct
    r"|(" + LEAD_PUNCT + r"\[[^]]*\]\([^)]*\)" + TRAIL_PUNCT + r")"  # inline link + adjacent punct
    r"|(https?://\S+)"                                              # bare URL
)
BOUNDARY_END = ",.:;?!)]}"


def decode(raw):
    if raw.startswith(b"\xff\xfe") or raw.startswith(b"\xfe\xff"):
        return raw.decode("utf-16"), "utf-16"
    return raw.decode("utf-8"), "utf-8"


def atoms(text):
    """Split text into atoms. Protected spans are single unbreakable atoms."""
    result = []
    pos = 0
    for match in PROTECTED.finditer(text):
        result.extend(text[pos:match.start()].split(" "))
        result.append(match.group(0))
        pos = match.end()
    result.extend(text[pos:].split(" "))
    return [a for a in result if a != ""]


def boundary_split(parts, width):
    """Prefer breaking after an atom ending with a clause-boundary mark.

    Returns (head_atoms, tail_atoms) or None when no good boundary exists.
    """
    for j in range(len(parts) - 1, 0, -1):
        head_len = len(" ".join(parts[: j + 1]))
        if head_len < width * 2 // 5:
            return None
        if parts[j].rstrip()[-1:] in BOUNDARY_END:
            return parts[: j + 1], parts[j + 1 :]
    return None


def wrap_line(line, width):
    """Split one logical line into physical lines no longer than width.

    The list marker or blockquote marker is part of the protected prefix and
    is never separated from the first atom. Continuation lines indent to the
    column where the item's text starts; blockquote continuations repeat the
    quote marker.
    """
    if len(line) <= width:
        return [line]
    item = ITEM.match(line) or LONE_ITEM.match(line)
    quote = QUOTE.match(line)
    if item:
        lead = item.group(1)
        marker = item.group(2) + (item.group(3) if item.lastindex >= 3 else "")
        body = item.group(4) if item.lastindex >= 4 else ""
        task = re.match(r"\[[ xX]\][ \t]+", body)
        if task:
            marker += task.group(0)
            body = body[task.end() :]
        cont = lead + " " * len(marker)
    elif quote:
        lead, marker = quote.group(1), quote.group(2)
        body = quote.group(3)
        cont = lead + marker
    else:
        lead = line[: len(line) - len(line.lstrip())]
        marker = ""
        body = line[len(lead) :]
        cont = lead
    prefix = lead + marker
    if not body.strip():
        return [line]
    out = []
    cur = prefix
    parts = []
    for atom in atoms(body):
        if not parts:
            cur = prefix + atom
            parts = [atom]
            continue
        if len(cur) + 1 + len(atom) <= width:
            cur += " " + atom
            parts.append(atom)
            continue
        split = boundary_split(parts, width - len(prefix))
        if split:
            head, tail = split
            out.append((prefix if not out else cont) + " ".join(head))
            carry = tail + [atom]
        else:
            out.append(cur)
            carry = [atom]
        cur = cont + carry[0]
        parts = [carry[0]]
        for extra in carry[1:]:
            if len(cur) + 1 + len(extra) <= width:
                cur += " " + extra
                parts.append(extra)
            else:
                out.append(cur)
                cur = cont + extra
                parts = [extra]
    out.append(cur)
    return out


def processable(fences, payload_markdown):
    """A line is prose when every open fence is a markdown payload fence."""
    if not fences:
        return True
    if not payload_markdown:
        return False
    return all(lang == "markdown" for _, lang, *_ in fences)


def main(path, width, payload_markdown, check_only):
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
    fences = []          # stack of (marker length, language)
    in_front = lines[0].strip() == "---" if lines else False
    in_comment = False
    list_stack = []      # content columns of open list items
    wrapped = 0
    unbreakable = []

    for n, line in enumerate(lines, 1):
        s = line.strip()
        indent = len(line) - len(line.lstrip())

        fence = FENCE.match(line)
        if fence:
            marker_len, lang = len(fence.group(1)), fence.group(2)
            if fences:
                if marker_len >= fences[-1][0]:
                    fences.pop()
            else:
                fences.append((marker_len, lang))
            list_stack = []
            out.append(line)
            continue

        if in_front:
            if n != 1 and s == "---":
                in_front = False
            out.append(line)
            continue

        if in_comment:
            if "-->" in line:
                in_comment = False
            out.append(line)
            continue
        if s.startswith("<!--") or ("<!--" in line and "-->" not in line):
            in_comment = "-->" not in line
            out.append(line)
            continue

        if not processable(fences, payload_markdown):
            out.append(line)
            continue

        if not s:
            out.append(line)
            continue

        item = ITEM.match(line)
        if item:
            content_col = indent + len(item.group(2)) + len(item.group(3))
            while list_stack and list_stack[-1] > indent:
                list_stack.pop()
            list_stack.append(content_col)
        else:
            while list_stack and indent < list_stack[-1]:
                list_stack.pop()
            base = list_stack[-1] if list_stack else 0
            if s.startswith(("#", "|")) or indent >= base + 4:
                out.append(line)    # heading, table row, or indented code
                continue
        if len(line) > width:
            if check_only:
                unbreakable.append((n, len(line), line.strip()[:60]))
            else:
                parts = wrap_line(line, width)
                if len(parts) > 1:
                    wrapped += 1
                for piece in parts:
                    if len(piece) > width:
                        unbreakable.append((n, len(piece), piece.strip()[:60]))
                out.extend(parts)
                continue
        out.append(line)

    if check_only:
        for n, size, preview in unbreakable:
            print(f"line {n}: {size} chars > {width}: {preview}...")
        if unbreakable:
            print(f"{len(unbreakable)} line(s) exceed {width}")
            return 1
        print(f"PASS {path}: no line exceeds {width}")
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
    print(f"wrapped {wrapped} lines to width {width}")
    for n, size, preview in unbreakable:
        print(f"note: line {n} still {size} chars (unbreakable span): {preview}...")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(
        description="Wrap Markdown prose to a maximum width (split only)."
    )
    parser.add_argument("file")
    parser.add_argument("--width", type=int, default=100)
    parser.add_argument("--payload-markdown", action="store_true")
    parser.add_argument("--check", action="store_true")
    parsed = parser.parse_args()
    raise SystemExit(
        main(parsed.file, parsed.width, parsed.payload_markdown, parsed.check)
    )
