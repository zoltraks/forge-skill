#!/usr/bin/env python3
"""Split packed sentences inside prose paragraphs onto individual logical lines.

Two sentence-layout dialects exist. The house convention (docs/STYLE.md, the
`languages/` baselines) is paragraph-per-sentence: every sentence is its own
paragraph, separated from the next by one empty line. Repositories in the wild
also use sentence-per-line: each sentence starts on its own logical line but
shares the paragraph block with its neighbors. The default mode serves the
second dialect; `--paragraphs` produces the first.

Documents that follow either convention may contain lines packing two or more
sentences, either written that way or produced by a mechanical rewrap. The tool
detects mid-line sentence boundaries inside plain paragraph blocks and emits
each sentence starting on its own line, re-wrapping the affected sentences to
the document's width convention in default mode.

In `--paragraphs` mode every multi-sentence paragraph block - packed or
already line-split - becomes one sentence per paragraph, sentences separated
by one empty line. Sentences are emitted verbatim as single logical lines and
are never re-wrapped; apply `wrap-prose.py` separately when the document's
dialect sets a width limit.

In `--flow` mode the block's sentences pack onto shared logical lines instead:
every sentence joins the current line when it still fits --width (default 80)
and starts a new line otherwise - sentences are never split. This produces the
`flowing` prose convention, the inverse of the default split.

Only plain paragraph blocks are processed. List items and their continuation
lines, headings, tables, blockquotes, fenced blocks, indented code, HTML
comments, and frontmatter stay opaque - packed sentences inside list items are
an element-level convention, not a defect (see
conventions/markdown-dialects.md).

Sentence detection is heuristic: a boundary inside parentheses or a code
span never splits, but an uncommon abbreviation not in the recognized list
can still produce a false boundary. Review proposed splits before applying
them.

Run this file in place from the skill repository -
`python <skill-root>/scripts/split-sentences.py` - and run it on the
document file. Copy it under a `.tmp.` name into the working
repository's `temp/` directory (or the repository root when no `temp/`
exists) only when the skill root cannot be invoked, and remove the copy
afterward.

Usage: python split-sentences.py <file.md> [--check] [--paragraphs | --flow]
                                   [--width N] [--payload-markdown]

  --check              report lines or blocks needing a change, without
                       writing, exit 1 when any exist
  --paragraphs         emit one sentence per paragraph, sentences separated
                       by one empty line; combines with --check
  --flow               pack each block's sentences onto shared logical lines
                       up to --width without splitting them
  --width N            re-wrap split sentences to this limit, default 100,
                       or the packing limit in --flow mode, default 80;
                       ignored in --paragraphs mode
  --payload-markdown   also process prose inside ```markdown fenced blocks
                       (embedded payload documents); other fence languages
                       always stay opaque
"""

import argparse
import os
import re
import sys

FENCE = re.compile(r"^\s*(`{3,}|~{3,})\s*(\w*)")
ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])([ \t]+)(.*)$")
LONE_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s*$")
QUOTE = re.compile(r"^(\s*)((?:>\s*)+)(.*)$")
HEADING = re.compile(r"^\s*#")
CODE_SPAN = re.compile(r"`+[^`]*`+")
BOUNDARY = re.compile(r"[.!?][\"')\]]*\s+(?=[A-Z\"'(\[*`0-9])")
ABBR = re.compile(
    r"(e\.g|i\.e|etc|vs|cf|approx|No|Nos|Fig|fig|Dr|Mr|Mrs|St"
    r"|vol|pp|sec|al|ed)\.\s*$"
)
TERMINAL = re.compile(r"[.!?:][\"')\]]*$")

LEAD_PUNCT = r"[(\[{'\"]*"
TRAIL_PUNCT = r"[\")\].,;:!?}\"]*(?:'[a-zA-Z]*)?[\"')\].,;:!?}]*"
PROTECTED = re.compile(
    r"(" + LEAD_PUNCT + r"`+[^`]*`+" + TRAIL_PUNCT + r")"
    r"|(" + LEAD_PUNCT + r"\[[^]]*\]\([^)]*\)" + TRAIL_PUNCT + r")"
    r"|(https?://\S+)"
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
    """Prefer breaking after an atom ending with a clause-boundary mark."""
    for j in range(len(parts) - 1, 0, -1):
        head_len = len(" ".join(parts[: j + 1]))
        if head_len < width * 2 // 5:
            return None
        if parts[j].rstrip()[-1:] in BOUNDARY_END:
            return parts[: j + 1], parts[j + 1 :]
    return None


def wrap_text(text, width):
    """Wrap one sentence's text into physical lines no longer than width."""
    if len(text) <= width:
        return [text]
    out = []
    cur = ""
    parts = []
    for atom in atoms(text):
        if not parts:
            cur, parts = atom, [atom]
            continue
        if len(cur) + 1 + len(atom) <= width:
            cur += " " + atom
            parts.append(atom)
            continue
        split = boundary_split(parts, width)
        if split:
            head, tail = split
            out.append(" ".join(head))
            carry = tail + [atom]
        else:
            out.append(cur)
            carry = [atom]
        cur = carry[0]
        parts = [carry[0]]
        for extra in carry[1:]:
            if len(cur) + 1 + len(extra) <= width:
                cur += " " + extra
                parts.append(extra)
            else:
                out.append(cur)
                cur = extra
                parts = [extra]
    out.append(cur)
    return out


def boundary_positions(line):
    """Column positions where a new sentence starts inside the line."""
    spans = [(m.start(), m.end()) for m in CODE_SPAN.finditer(line)]
    out = []
    for m in BOUNDARY.finditer(line):
        if any(s <= m.start() < e for s, e in spans):
            continue
        if ABBR.search(line[: m.end()].rstrip()):
            continue
        code_masked = list(line[: m.start()])
        for s, e in spans:
            for i in range(min(s, len(code_masked)),
                           min(e, len(code_masked))):
                code_masked[i] = " "
        prefix = "".join(code_masked)
        if prefix.count("(") - prefix.count(")") > 0:
            continue                    # boundary inside parentheses stays
        out.append(m.end())
    return out


def split_line(line):
    """Split a line at its mid-line sentence boundary positions."""
    pts = boundary_positions(line)
    if not pts:
        return [line]
    out = []
    prev = 0
    for p in pts:
        out.append(line[prev:p].rstrip())
        prev = p
    out.append(line[prev:])
    return out


def processable(fences, payload_markdown):
    """A line is prose when every open fence is a markdown payload fence."""
    if not fences:
        return True
    if not payload_markdown:
        return False
    return all(lang == "markdown" for _, lang, *_ in fences)


def paragraph_line(line, list_stack):
    """A split candidate: unindented prose that is not a structural element."""
    if not line.strip():
        return False
    if line != line.lstrip():
        return False                     # list continuation or indented code
    if ITEM.match(line) or LONE_ITEM.match(line):
        return False                     # list item
    if QUOTE.match(line):
        return False                     # blockquote
    if HEADING.match(line):
        return False                     # heading
    if line.startswith("|"):
        return False                     # table row
    if list_stack and list_stack[-1] > 0:
        return False                     # inside a list's content column
    return True


def block_sentences(block, lines):
    """Reconstruct every sentence unit inside a paragraph block."""
    units = []
    cur = []
    for n in block:
        for seg in split_line(lines[n - 1]):
            cur.append(seg.strip())
            if TERMINAL.search(seg.strip()):
                units.append(" ".join(p for p in cur if p).strip())
                cur = []
    if cur:
        units.append(" ".join(p for p in cur if p).strip())
    return units


def flow_pack(units, width):
    """Pack sentence units onto shared lines without splitting a unit."""
    out, cur = [], ""
    for unit in units:
        if not cur:
            cur = unit
        elif len(cur) + 1 + len(unit) <= width:
            cur += " " + unit
        else:
            out.append(cur)
            cur = unit
    if cur:
        out.append(cur)
    return out


def main(path, width, payload_markdown, check_only, paragraphs, flow):
    raw = open(path, "rb").read()
    crlf = b"\r\n" in raw
    try:
        text, encoding = decode(raw)
    except UnicodeDecodeError:
        print(f"FAIL {path}: not decodable as UTF-8 or UTF-16, "
              "check encoding first (see conventions/file-encoding.md)")
        return 1
    lines = text.replace("\r\n", "\n").split("\n")

    # Pass 1 - classify every line and collect paragraph blocks.
    kind = {}
    fences = []
    in_front = lines[0].strip() == "---" if lines else False
    in_comment = False
    list_stack = []
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
            kind[n] = "FENCE"
            continue
        if in_front:
            if n != 1 and s == "---":
                in_front = False
            kind[n] = "FRONT"
            continue
        if in_comment:
            if "-->" in line:
                in_comment = False
            kind[n] = "HTML"
            continue
        if s.startswith("<!--") or ("<!--" in line and "-->" not in line):
            in_comment = "-->" not in line
            kind[n] = "HTML"
            continue
        if not processable(fences, payload_markdown):
            kind[n] = "OPAQUE"
            continue
        if not s:
            kind[n] = "BLANK"
            continue
        item = ITEM.match(line)
        if item:
            content_col = indent + len(item.group(2)) + len(item.group(3))
            while list_stack and list_stack[-1] > indent:
                list_stack.pop()
            list_stack.append(content_col)
            kind[n] = "ITEM"
            continue
        while list_stack and indent < list_stack[-1]:
            list_stack.pop()
        if paragraph_line(line, list_stack):
            kind[n] = "PARA"
        else:
            kind[n] = "OPAQUE"

    blocks = []
    cur_block = []
    for n in range(1, len(lines) + 1):
        if kind[n] == "PARA":
            cur_block.append(n)
        else:
            if cur_block:
                blocks.append(cur_block)
                cur_block = []
    if cur_block:
        blocks.append(cur_block)

    if check_only:
        if flow:
            found = [b[0] for b in blocks
                     if flow_pack(block_sentences(b, lines), width)
                     != [lines[n - 1] for n in b]]
            for n in found:
                print(f"line {n}: block does not follow the packed "
                      f"sentence layout: {lines[n - 1].strip()[:60]}...")
            if found:
                print(f"{len(found)} block(s) would repack to {width}")
                return 1
            print(f"PASS {path}: every block follows the packed layout")
            return 0
        if paragraphs:
            found = [b[0] for b in blocks if len(block_sentences(b, lines)) > 1]
            for n in found:
                print(f"line {n}: paragraph block packs multiple sentences: "
                      f"{lines[n - 1].strip()[:60]}...")
            if found:
                print(f"{len(found)} paragraph block(s) pack multiple sentences")
                return 1
            print(f"PASS {path}: every sentence is its own paragraph")
            return 0
        found = []
        for b in blocks:
            for n in b:
                if len(split_line(lines[n - 1])) > 1:
                    found.append(n)
        for n in found:
            print(f"line {n}: mid-line sentence boundary: "
                  f"{lines[n - 1].strip()[:60]}...")
        if found:
            print(f"{len(found)} line(s) pack multiple sentences")
            return 1
        print(f"PASS {path}: every paragraph sentence starts on a line")
        return 0

    # Pass 2 - rebuild the flagged blocks one sentence per logical line,
    # or one sentence per paragraph when --paragraphs is given.
    repl = {}
    split_count = 0
    for b in blocks:
        if flow:
            units = block_sentences(b, lines)
            packed = flow_pack(units, width)
            if packed != [lines[n - 1] for n in b]:
                split_count += 1
                repl[b[0]] = packed
            continue
        if paragraphs:
            units = block_sentences(b, lines)
            if len(units) <= 1:
                continue
            out_b = []
            for unit in units:
                if out_b:
                    out_b.append("")
                out_b.append(unit)
            split_count += len(units) - 1
            repl[b[0]] = out_b
            continue
        segs_per_line = [(n, split_line(lines[n - 1])) for n in b]
        if not any(len(s) > 1 for _, s in segs_per_line):
            continue
        units = []
        cur_u = None
        for n, segs in segs_per_line:
            for k, seg in enumerate(segs):
                if cur_u is None:
                    cur_u = {"pieces": [], "dirty": k > 0}
                if k == 0 and len(segs) == 1:
                    cur_u["pieces"].append(("orig", n))
                else:
                    cur_u["pieces"].append(("text", seg))
                    cur_u["dirty"] = True
                if TERMINAL.search(seg.strip()):
                    units.append(cur_u)
                    cur_u = None
        if cur_u:
            units.append(cur_u)
        out_b = []
        for u in units:
            if not u["dirty"]:
                out_b.extend(lines[v - 1] for _, v in u["pieces"])
            else:
                split_count += 1
                text = " ".join(
                    (lines[v - 1] if p == "orig" else v).strip()
                    for p, v in u["pieces"]
                ).strip()
                if text:
                    out_b.extend(wrap_text(text, width))
        repl[b[0]] = out_b

    if not repl:
        if flow:
            print(f"PASS {path}: every block follows the packed layout")
        else:
            print(f"PASS {path}: every paragraph sentence starts on a line")
        return 0

    block_starts = {b[0]: b for b in blocks}
    result = []
    i = 1
    while i <= len(lines):
        if i in repl:
            result.extend(repl[i])
            i += len(block_starts[i])
        else:
            result.append(lines[i - 1])
            i += 1

    eol = "\r\n" if crlf else "\n"
    tmp = path + ".tmp-write"
    try:
        with open(tmp, "wb") as handle:
            handle.write(eol.join(result).encode(encoding))
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    if crlf:
        print("note: file uses CRLF line endings - preserved")
    if flow:
        print(f"repacked {split_count} paragraph block(s) to width {width}")
        return 0
    noun = "paragraph(s)" if paragraphs else "paragraph block(s)"
    print(f"split {split_count} sentence(s) across {len(repl)} {noun}")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(
        description="Split packed sentences onto individual logical lines "
                    "or paragraphs, or repack them into the flowing layout."
    )
    parser.add_argument("file")
    parser.add_argument("--check", action="store_true")
    shape = parser.add_mutually_exclusive_group()
    shape.add_argument("--paragraphs", action="store_true")
    shape.add_argument("--flow", action="store_true")
    parser.add_argument("--width", type=int, default=None)
    parser.add_argument("--payload-markdown", action="store_true")
    parsed = parser.parse_args()
    width = parsed.width
    if width is None:
        width = 80 if parsed.flow else 100
    raise SystemExit(
        main(parsed.file, width, parsed.payload_markdown,
             parsed.check, parsed.paragraphs, parsed.flow)
    )
