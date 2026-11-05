#!/usr/bin/env python3
"""Reflow Markdown prose between wrapped and logical-line layouts.

Two directions exist:

--wrap    rewraps each prose block to --width: the block's lines re-derive
          their logical lines first - separate sentences, `**Label:**`
          field lines, and list items stay on their own lines - then each
          logical line splits at whitespace, preferring clause boundaries,
          so a block wrapped at a different width or with ragged break
          points normalizes; continuation lines indent to the item's text
          column and blockquote continuations repeat the quote marker.

--unwrap  joins hard-wrapped continuation lines back into single logical
          lines inside paragraphs, list items, and blockquotes.

--justify wraps like --wrap and additionally stretches inter-word spacing
          on every line of a block except its last, so both edges of the
          block sit flush - the justified prose convention.

Both directions preserve the document's structure: fenced code blocks,
frontmatter, HTML comments, headings, tables, indented code blocks, setext
underlines, horizontal rules, and bold pseudo-headings stay opaque, and so
does every fenced block whose language is not `markdown` unless
--payload-markdown is given.

--unwrap only ever joins a line into the previous one when the accumulated
text does not end with sentence-final punctuation (`.`, `!`, `?`) or a
label colon (`:`), so separate sentences sharing one paragraph block stay
on their own lines - it converts wrapping, not sentence layout. Combine
with `split-sentences.py --paragraphs` when the task also asks for one
sentence per paragraph.

The wrap direction joins physical continuation lines inside each block
only to rewrap that block's logical lines - it never merges separate
blocks, sentences, or field lines - and the unwrap direction never splits
them, so a document that already matches its own convention is unchanged.
Run `--unwrap --check` on a logical-line document to find wrapped
fragments, or `--wrap --check` on a wrapped document to find blocks that
would rewrap and lines whose unbreakable spans exceed the width.

Run this file in place from the skill repository -
`python <skill-root>/scripts/reflow-prose.py` - and run it on the
document file. Copy it under a `.tmp.` name into the working
repository's `temp/` directory (or the repository root when no `temp/`
exists) only when the skill root cannot be invoked, and remove the copy
afterward.

Usage: python reflow-prose.py <file.md> (--wrap | --unwrap | --justify)
                                [--width N] [--payload-markdown] [--check]

  --wrap               rewrap prose blocks to the width (a superset of the
                       deprecated wrap-prose.py's line splitting)
  --unwrap             join wrapped continuation lines into logical lines
  --justify            wrap to the width and stretch inter-word spacing so
                       every line of a block but its last reaches it exactly
  --width N            maximum line length for --wrap and --justify,
                       default 100
  --payload-markdown   also process prose inside ```markdown fenced blocks
                       (embedded payload documents); other fence languages
                       always stay opaque
  --check              report findings without writing, exit 1 when the
                       file does not match the requested direction
"""

import argparse
import os
import re
import sys

FENCE = re.compile(r"^\s*(`{3,}|~{3,})\s*(\w*)")
ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])([ \t]+)(.*)$")
LONE_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s*$")
QUOTE = re.compile(r"^(\s*)((?:>\s*)+)(.*)$")
RULE_LINE = re.compile(r"^\s*(={2,}|-{2,}|\*{3,}|_{3,})\s*$")
PSEUDO_HEAD = re.compile(r"^\*{1,2}[^*\n]+\*{1,2}:?\s*$")
SENT_END = re.compile(r"[.!?:][\"')\]`}*]*\s*$")
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
    return rebalance(out, prefix, cont, width)


def rebalance(out, prefix, cont, width):
    """Move atoms from the previous line onto a too-short final line.

    A wrap that leaves a single word or tiny fragment on the last line reads
    as a broken sentence - atoms shift down until the tail carries enough
    text, while the head keeps at least 45 characters and the tail stays
    within the width.
    """
    if len(out) < 2:
        return out
    tail = out[-1][len(cont) :]
    if len(tail) >= 20:
        return out
    pfx = prefix if len(out) == 2 else cont
    head = out[-2][len(pfx) :]
    parts = atoms(head)
    while len(parts) > 3 and len(tail) < 20:
        candidate = parts[-1] + " " + tail
        if len(pfx) + len(" ".join(parts[:-1])) < 45 or len(cont) + len(candidate) > width:
            break
        tail = candidate
        parts = parts[:-1]
    out[-2] = pfx + " ".join(parts)
    out[-1] = cont + tail
    return out


GAP = re.compile(r"(?<=\S) (?=\S)")


def stretch_line(line, width):
    """Stretch inter-word gaps so the line reaches exactly width.

    The marker prefix of a list item or blockquote is part of the left edge
    and never absorbs padding. Single-word lines and lines already at width
    stay untouched.
    """
    need = width - len(line)
    if need <= 0:
        return line
    item = ITEM.match(line)
    quote = QUOTE.match(line)
    if item:
        prefix_end = item.end(3) if item.lastindex >= 3 else item.end(2)
    elif quote:
        prefix_end = quote.end(2)
    else:
        prefix_end = len(line) - len(line.lstrip())
    gaps = [m.start() for m in GAP.finditer(line) if m.start() >= prefix_end]
    if not gaps:
        return line
    extra = [1] * len(gaps)
    for k in range(need):
        extra[k % len(gaps)] += 1
    out = []
    prev = 0
    for pos, count in zip(gaps, extra):
        out.append(line[prev:pos])
        out.append(" " * count)
        prev = pos + 1
    out.append(line[prev:])
    return "".join(out)


def unit_bodies(unit_lines):
    """Extract the text body of each line in a justify unit.

    Returns (lead, marker, bodies) - the first line's structural prefix and
    each line's prose text without its own marker or indent.
    """
    first = unit_lines[0]
    bodies = []
    item = ITEM.match(first) or LONE_ITEM.match(first)
    quote = QUOTE.match(first)
    for k, line in enumerate(unit_lines):
        i = ITEM.match(line) or LONE_ITEM.match(line)
        q = QUOTE.match(line)
        if i:
            bodies.append((i.group(4) if i.lastindex >= 4 else "").strip())
        elif q:
            bodies.append(q.group(3).strip())
        else:
            bodies.append(line.strip())
    if item:
        lead = item.group(1)
        marker = item.group(2)
    elif quote:
        lead, marker = quote.group(1), quote.group(2)
    else:
        lead = first[: len(first) - len(first.lstrip())]
        marker = ""
    return lead, marker, [b for b in bodies if b]


FIELD_LABEL = re.compile(r"^\*\*[^*]+:\*\*")


def logical_lines(unit_lines):
    """Re-derive the logical lines inside a unit before re-wrapping.

    A physical line continues the previous logical line only while the
    accumulated text does not end with sentence-final punctuation or a
    label colon and the line opens no structural boundary - a `**Label:**`
    field or a list marker. These are the same boundary rules `--unwrap`
    applies, so separate sentences and field lines stay on their own lines.
    """
    _, _, bodies = unit_bodies(unit_lines)
    logical = []
    for body in bodies:
        boundary = (FIELD_LABEL.match(body) or ITEM.match(body)
                    or LONE_ITEM.match(body))
        if logical and not boundary and not SENT_END.search(logical[-1]):
            logical[-1] += " " + body
        else:
            logical.append(body)
    return logical


def unit_prefixes(unit_lines):
    """Return (first, later) prefixes for the unit's logical lines.

    A list item repeats its marker only on the first logical line - later
    logical lines are continuations and indent to the text column - while
    a blockquote repeats its marker on every logical line.
    """
    lead, marker, _ = unit_bodies(unit_lines)
    gap = " " if marker and not marker.endswith(" ") else ""
    first = lead + marker + gap
    if marker and not marker.startswith(">"):
        return first, " " * len(first)
    return first, first


def reflow_unit(unit_lines, width, stretch):
    """Reflow one unit's logical lines to the width.

    Each logical line wraps (and optionally justifies) on its own, so the
    unit's sentence and field-line boundaries survive the pass.
    """
    first_p, later_p = unit_prefixes(unit_lines)
    out = []
    for k, logical in enumerate(logical_lines(unit_lines)):
        prefix = first_p if k == 0 else later_p
        pieces = wrap_line((prefix + logical).rstrip(), width)
        if stretch and len(pieces) > 1:
            pieces = ([stretch_line(p, width) for p in pieces[:-1]]
                      + [pieces[-1]])
        out.extend(pieces)
    return out


def justify_unit(unit_lines, width):
    """Reflow a block of prose lines and justify every line but its last.

    The unit is one paragraph run, one list item with its continuations, or
    one blockquote run. Its lines re-derive their logical lines first -
    wrapping already-wrapped text at any width requires the unwrap before
    the wrap, or each physical line breaks on its own and fragments remain -
    and every physical line of each logical line except its last stretches
    to exactly the width.
    """
    return reflow_unit(unit_lines, width, stretch=True)


def wrap_unit(unit_lines, width):
    """Reflow a block of prose lines to the width without stretching.

    The unit is one paragraph run, one list item with its continuations, or
    one blockquote run. Its lines re-derive their logical lines first -
    wrapping already-wrapped text at any width requires the unwrap before
    the wrap, or each physical line breaks on its own and fragments remain -
    and every logical line wraps on its own, so separate sentences and
    `**Label:**` field lines stay on their own lines.
    """
    return reflow_unit(unit_lines, width, stretch=False)


def processable(fences, payload_markdown):
    """A line is prose when every open fence is a markdown payload fence."""
    if not fences:
        return True
    if not payload_markdown:
        return False
    return all(lang == "markdown" for _, lang, *_ in fences)


def unwrapped_signature(lines, width, payload_markdown):
    """Detect an unwrapped document layout.

    Returns (prose, cont, over_starts): counts of processable prose lines,
    continuation lines inside prose units, and over-width lines that open a
    prose unit - a line that follows a block boundary rather than continuing
    wrapped text. A bounded document wraps its long blocks into
    continuations, so almost every long line is one; an unwrapped document
    carries every sentence on its own line, so its lines almost never
    continue anything.
    """
    fences = []
    in_front = lines and lines[0].strip() == "---"
    in_comment = False
    list_stack = []
    prose = 0
    cont = 0
    over_starts = 0
    open_unit = False
    unit_col = 0
    for n, line in enumerate(lines, 1):
        s = line.strip()
        indent = len(line) - len(line.lstrip())
        f = FENCE.match(line)
        if f:
            open_unit = False
            ml, lang = len(f.group(1)), f.group(2)
            if fences:
                if ml >= fences[-1][0] and f.group(1)[0] == fences[-1][2]:
                    fences.pop()
                elif fences[-1][1] == "markdown":
                    fences.append((ml, lang, f.group(1)[0]))
            else:
                fences.append((ml, lang, f.group(1)[0]))
            list_stack = []
            continue
        if in_front:
            open_unit = False
            if n != 1 and s == "---":
                in_front = False
            continue
        if in_comment:
            open_unit = False
            if "-->" in line:
                in_comment = False
            continue
        if s.startswith("<!--") or ("<!--" in line and "-->" not in line):
            open_unit = False
            in_comment = "-->" not in line
            continue
        if fences and not processable(fences, payload_markdown):
            continue
        if fences:
            continue
        if not s:
            open_unit = False
            continue
        item = ITEM.match(line)
        if item or LONE_ITEM.match(line):
            prose += 1
            if len(line.rstrip()) > width:
                over_starts += 1
            open_unit = True
            unit_col = (indent + len(item.group(2)) + len(item.group(3))
                        if item else indent)
            if item:
                while list_stack and list_stack[-1] > indent:
                    list_stack.pop()
                list_stack.append(unit_col)
            continue
        if QUOTE.match(line):
            prose += 1
            if open_unit:
                cont += 1
            if len(line.rstrip()) > width and not open_unit:
                over_starts += 1
            open_unit = True
            continue
        if (s.startswith(("#", "|", "<")) or RULE_LINE.match(s)
                or PSEUDO_HEAD.match(s)):
            open_unit = False
            while list_stack and indent < list_stack[-1]:
                list_stack.pop()
            continue
        while list_stack and indent < list_stack[-1]:
            list_stack.pop()
        base = list_stack[-1] if list_stack else 0
        if indent >= base + 4:
            open_unit = False
            continue
        prose += 1
        if open_unit:
            cont += 1
            continuation = True
        else:
            continuation = False
        if len(line.rstrip()) > width and not continuation:
            over_starts += 1
        open_unit = True
    return prose, cont, over_starts


def main(path, mode, width, payload_markdown, check_only, convert=False,
         excludes=None, loose=False):
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
            worst = max(worst, main(f, mode, width, payload_markdown,
                                    check_only, convert,
                                    excludes, loose))
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

    if mode in ("wrap", "justify") and not convert:
        prose, cont, over = unwrapped_signature(lines, width, payload_markdown)
        if prose and over >= 1 and cont * 4 < prose:
            print(f"note: {path} reads as unwrapped - {over} prose line(s) "
                  f"exceed the {width} width but {cont} of {prose} prose "
                  f"lines continue a unit, so --{mode} would convert the "
                  "layout rather than fix wrapping; pass --convert to apply "
                  "it anyway")
            if check_only:
                print(f"PASS {path}: unwrapped document layout, wrap check "
                      "not applicable")
                return 0
            return 1

    out = []
    fences = []          # stack of (marker length, language)
    in_front = lines[0].strip() == "---" if lines else False
    in_comment = False
    list_stack = []      # content columns of open list items
    wrapped = 0
    unbreakable = []
    joins = []           # unwrap: line numbers merged into a previous line
    open_ok = False      # unwrap: last emitted line may absorb a continuation
    open_min = 0         # unwrap: minimum indent a continuation must reach
    open_quote = False   # unwrap: last emitted line is a quote line
    unit = []            # wrap/justify: buffered (line number, line) of the open unit
    unit_kind = ""       # wrap/justify: "para", "item", or "quote"
    unit_col = 0         # wrap/justify: item content column or paragraph indent
    unit_marker = ""     # wrap/justify: quote marker of the open quote unit
    justified = []       # justify: (first line, last line) of changed units
    rewrapped = []       # wrap: (first line, last line) of changed units

    def flush_unit():
        nonlocal wrapped
        if not unit:
            return
        body = [ln for _, ln in unit]
        if mode == "justify":
            pieces = justify_unit(body, width)
            if pieces != body:
                justified.append((unit[0][0], unit[-1][0]))
        else:
            pieces = wrap_unit(body, width)
            flagged = pieces != body and \
                (not loose or (len(body) > 1
                               and any(len(l) > width for l in body)))
            if flagged:
                wrapped += 1
                rewrapped.append((unit[0][0], unit[-1][0]))
            for piece in pieces:
                if len(piece) > width:
                    unbreakable.append((unit[0][0], len(piece), piece.strip()[:60]))
        if check_only:
            out.extend(ln for _, ln in unit)
        else:
            out.extend(pieces if flagged or not loose else body)
        unit.clear()

    for n, line in enumerate(lines, 1):
        s = line.strip()
        indent = len(line) - len(line.lstrip())

        fence = FENCE.match(line)
        if fence:
            flush_unit()
            marker_len, lang = len(fence.group(1)), fence.group(2)
            if fences:
                if marker_len >= fences[-1][0] and fence.group(1)[0] == fences[-1][2]:
                    fences.pop()
                elif fences[-1][1] == "markdown":
                    fences.append((marker_len, lang, fence.group(1)[0]))
            else:
                fences.append((marker_len, lang, fence.group(1)[0]))
            list_stack = []
            open_ok = False
            out.append(line)
            continue

        if in_front:
            flush_unit()
            if n != 1 and s == "---":
                in_front = False
            out.append(line)
            open_ok = False
            continue

        if in_comment:
            flush_unit()
            if "-->" in line:
                in_comment = False
            out.append(line)
            open_ok = False
            continue
        if s.startswith("<!--") or ("<!--" in line and "-->" not in line):
            flush_unit()
            in_comment = "-->" not in line
            out.append(line)
            open_ok = False
            continue

        if not processable(fences, payload_markdown):
            flush_unit()
            out.append(line)
            open_ok = False
            continue

        if not s:
            flush_unit()
            out.append(line)
            open_ok = False
            continue

        item = ITEM.match(line)
        quote = QUOTE.match(line)

        if mode in ("wrap", "justify"):
            if item or LONE_ITEM.match(line):
                flush_unit()
                unit_kind = "item"
                if item:
                    unit_col = indent + len(item.group(2)) + len(item.group(3))
                    while list_stack and list_stack[-1] > indent:
                        list_stack.pop()
                    list_stack.append(unit_col)
                else:
                    unit_col = indent
                unit.append((n, line))
                continue
            if quote:
                marker = quote.group(1) + quote.group(2)
                if unit_kind != "quote" or marker != unit_marker:
                    flush_unit()
                    unit_kind = "quote"
                    unit_marker = marker
                unit.append((n, line))
                continue
            if s.startswith(("#", "|", "<")) or RULE_LINE.match(s) or \
                    PSEUDO_HEAD.match(s):
                flush_unit()
                while list_stack and indent < list_stack[-1]:
                    list_stack.pop()
                out.append(line)
                continue
            while list_stack and indent < list_stack[-1]:
                list_stack.pop()
            base = list_stack[-1] if list_stack else 0
            if indent >= base + 4:
                flush_unit()
                out.append(line)
                continue
            if unit_kind == "item" and indent >= unit_col:
                unit.append((n, line))
                continue
            if unit_kind != "para" or indent != unit_col:
                flush_unit()
                unit_kind = "para"
                unit_col = indent
            unit.append((n, line))
            continue

        # --unwrap mode below this point
        if item or LONE_ITEM.match(line):
            # A list item never joins a previous line, it starts a new
            # logical line whose continuations align to its text column.
            if item:
                content_col = indent + len(item.group(2)) + len(item.group(3))
                task = re.match(r"\[[ xX]\][ \t]+", item.group(4))
                if task:
                    content_col += len(task.group(0))
                while list_stack and list_stack[-1] > indent:
                    list_stack.pop()
                list_stack.append(content_col)
                open_ok = not SENT_END.search(item.group(4).strip())
            else:
                open_ok = False
                content_col = indent
            open_min = content_col
            open_quote = False
            out.append(line)
            continue

        while list_stack and indent < list_stack[-1]:
            list_stack.pop()
        base = list_stack[-1] if list_stack else 0

        if quote:
            body = quote.group(3).strip()
            if open_ok and open_quote:
                out[-1] = out[-1].rstrip() + " " + body
                joins.append(n)
                open_ok = not SENT_END.search(body)
                continue
            out.append(line)
            open_ok = not SENT_END.search(body)
            open_min = indent
            open_quote = True
            continue

        if s.startswith(("#", "|", "<")) or RULE_LINE.match(s) or \
                PSEUDO_HEAD.match(s) or indent >= base + 4:
            # heading, table row, HTML line, horizontal rule or setext
            # underline, pseudo-heading, or indented code block
            out.append(line)
            open_ok = False
            continue

        if open_ok and not open_quote and open_min <= indent < open_min + 4:
            out[-1] = out[-1].rstrip() + " " + s
            joins.append(n)
            open_ok = not SENT_END.search(s)
            continue

        out.append(line)
        open_ok = not SENT_END.search(s)
        open_min = indent
        open_quote = False

    flush_unit()

    if check_only:
        if mode == "wrap":
            for first, last in rewrapped:
                span = f"{first}" if first == last else f"{first}-{last}"
                print(f"lines {span}: block is not wrapped at {width}")
            for n, size, preview in unbreakable:
                print(f"note: line {n}: {size} chars > {width} "
                      f"(unbreakable span): {preview}...")
            if rewrapped:
                print(f"{len(rewrapped)} block(s) would rewrap")
                return 1
            print(f"PASS {path}: every block is wrapped at {width}")
            return 0
        if mode == "justify":
            for first, last in justified:
                span = f"{first}" if first == last else f"{first}-{last}"
                print(f"lines {span}: block is not justified at {width}")
            if justified:
                print(f"{len(justified)} block(s) would justify")
                return 1
            print(f"PASS {path}: every block is justified at {width}")
            return 0
        for n in joins:
            print(f"line {n}: wrapped continuation joins into a previous line")
        if joins:
            print(f"{len(joins)} line(s) would join")
            return 1
        print(f"PASS {path}: no wrapped continuations")
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
    if mode == "wrap":
        print(f"rewrapped {wrapped} block(s) to width {width}")
        for n, size, preview in unbreakable:
            print(f"note: line {n} still {size} chars (unbreakable span): {preview}...")
    elif mode == "justify":
        print(f"justified {len(justified)} block(s) at width {width}")
        for first, last in justified[:20]:
            span = f"{first}" if first == last else f"{first}-{last}"
            print(f"note: lines {span} justified")
        if len(justified) > 20:
            print(f"note: ... and {len(justified) - 20} more")
    else:
        print(f"unwrapped {len(joins)} continuation line(s)")
        for n in joins[:20]:
            print(f"note: line {n} joined into a previous line")
        if len(joins) > 20:
            print(f"note: ... and {len(joins) - 20} more")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(errors="backslashreplace")
    parser = argparse.ArgumentParser(
        description="Reflow Markdown prose: wrap to a width, unwrap "
                    "wrapped continuations into logical lines, or justify."
    )
    parser.add_argument("file")
    direction = parser.add_mutually_exclusive_group(required=True)
    direction.add_argument("--wrap", action="store_true")
    direction.add_argument("--unwrap", action="store_true")
    direction.add_argument("--justify", action="store_true")
    parser.add_argument("--width", type=int, default=100)
    parser.add_argument("--convert", action="store_true",
                        help="apply --wrap or --justify even when the "
                             "document reads as unwrapped (a layout "
                             "conversion)")
    parser.add_argument("--payload-markdown", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--loose", action="store_true",
                        help="loose wrap convention: only reflow blocks "
                        "inside a multi-line block that contains an over-width line")
    parser.add_argument("--exclude", action="append", default=[],
                        metavar="NAME", help="skip files whose path contains a component with this name (repeatable, directory mode)")
    parsed = parser.parse_args()
    mode = "wrap" if parsed.wrap else "justify" if parsed.justify else "unwrap"
    raise SystemExit(
        main(parsed.file, mode, parsed.width, parsed.payload_markdown,
             parsed.check, parsed.convert, parsed.exclude, parsed.loose)
    )
