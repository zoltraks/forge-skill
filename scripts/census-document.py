#!/usr/bin/env python3
"""Report a structural census for a Markdown document.

Census only - the agent maps counts to findings, see process/document-audit.md.

Run this file in place from the skill repository -
`python <skill-root>/scripts/census-document.py` - and run it on the
target file. Copy it under a `.tmp.` name into the working repository's
`temp/` directory (or the repository root when no `temp/` exists) only
when the skill root cannot be invoked, and remove the copy afterward.

Usage: python census-document.py <file> [--width N] [--payload-markdown]
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

FENCE = re.compile(r"^\s*([`~]{3,})[ \t]*(.*?)[ \t]*$")
HEADING = re.compile(r"^(#{1,6})[ \t]+(.*?)[ \t]*$")
BULLET = re.compile(r"^\s*([-*+])[ \t]+\S")
ORDERED = re.compile(r"^\s*\d+\.[ \t]+\S")
TABLE_ROW = re.compile(r"^\s*\|.*\|\s*$")
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)[^)]*\)")
MARKER = re.compile(r"\b(TODO|FIXME|TBD|XXX)\b")
SENTENCE_BOUNDARY = re.compile(r"[.!?]['\")]*[ \t]+[A-Z]")
STRETCHED_GAP = re.compile(r"\S {2,}\S")
SENT_END = re.compile(r"[.!?:][\"')\]`}*]*\s*$")
RULE_LINE = re.compile(r"^\s*(={2,}|-{2,}|\*{3,}|_{3,})\s*$")
ITEM_COL = re.compile(r"^\s*(?:[-*+]|\d+[.)])[ \t]+")
CODE_SPAN = re.compile(r"`[^`]*`")
CONTENTS_TITLE = re.compile(r"^(contents|table of contents|spis tre[śs]ci)\b", re.I)

SPECIALS = {
    "—": "em-dash U+2014",
    "–": "en-dash U+2013",
    "‘": "single quote U+2018",
    "’": "single quote U+2019",
    "“": "double quote U+201C",
    "”": "double quote U+201D",
    "…": "ellipsis U+2026",
    "‑": "non-breaking hyphen U+2011",
    " ": "non-breaking space U+00A0",
}
CAP = 30


def classify(lines: list[str]) -> tuple[list[str], list[tuple[int, str]], int]:
    """Tag each line as prose, code, payload, or fence; collect block tags."""
    state = ["prose"] * len(lines)
    blocks: list[tuple[int, str]] = []
    payloads = 0
    fence_marker = ""
    fence_tag = ""
    for i, line in enumerate(lines):
        match = FENCE.match(line)
        if fence_marker:
            if match and match.group(1)[0] == fence_marker[0] and len(match.group(1)) >= len(fence_marker):
                state[i] = "fence"
                blocks.append((i + 1, fence_tag))
                if fence_tag.split(",")[0].strip().lower() == "markdown":
                    payloads += 1
                fence_marker = ""
            else:
                state[i] = "payload" if fence_tag.split(",")[0].strip().lower() == "markdown" else "code"
        elif match:
            state[i] = "fence"
            fence_marker = match.group(1)
            fence_tag = match.group(2)
    return state, blocks, payloads


def refs(items: list[int]) -> str:
    if not items:
        return "none"
    shown = ", ".join(str(n) for n in items[:CAP])
    return f"{shown} (+{len(items) - CAP} more)" if len(items) > CAP else shown


def is_emoji(ch: str) -> bool:
    return ord(ch) >= 0x1F000 or unicodedata.category(ch) == "So"


def main(argv: list[str]) -> int:
    args: list[str] = []
    flags: set[str] = set()
    width = 100
    skip = False
    for i, arg in enumerate(argv):
        if skip:
            skip = False
            continue
        if arg == "--width" and i + 1 < len(argv):
            width = int(argv[i + 1])
            skip = True
        elif arg.startswith("--width="):
            width = int(arg.split("=", 1)[1])
        elif arg.startswith("--"):
            flags.add(arg)
        else:
            args.append(arg)
    if len(args) != 1:
        print("Usage: python census-document.py <file> [--width N] [--payload-markdown]")
        return 1
    path = Path(args[0]).resolve()
    if not path.is_file():
        print(f"not a file: {path}")
        return 1
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print(f"cannot read {path}: {exc}")
        return 1

    lines = text.splitlines()
    state, blocks, payloads = classify(lines)
    host = {i for i, s in enumerate(state) if s == "prose"}
    scan = set(host)
    if "--payload-markdown" in flags:
        scan |= {i for i, s in enumerate(state) if s == "payload"}

    heads, parens, punct, deep, contents = {}, [], [], [], []
    markers: dict[str, int] = {}
    ordered = 0
    tables, blank_runs, wide, multi = 0, [], [], []
    semis, links, anchors, missing = [], [], [], []
    specials: dict[str, list[int]] = {}
    other_nonascii: dict[str, int] = {}
    emoji: list[int] = []
    marker_hits: list[tuple[int, str]] = []
    blank_start = None
    in_table = False
    para_frag: list[int] = []
    list_frag: list[int] = []
    quote_frag: list[int] = []
    para_seen = items_seen = quotes_seen = 0
    prev_open = False
    prev_min = 0
    prev_quote = False
    prev_kind = ""
    list_stack: list[int] = []
    stretch_by_kind: dict[str, list[int]] = {}
    multi_by_kind: dict[str, list[int]] = {}
    wide_by_kind: dict[str, list[int]] = {}
    packed_blocks = 0
    para_run_units = 0
    para_run_multi = False

    def end_para_run() -> None:
        nonlocal para_run_units, para_run_multi, packed_blocks
        if para_run_units > 1 or para_run_multi:
            packed_blocks += 1
        para_run_units = 0
        para_run_multi = False

    for i, line in enumerate(lines):
        if i not in scan:
            end_para_run()
            blank_start = None
            prev_open = False
            if state[i] == "fence":
                in_table = False
            continue
        stripped = CODE_SPAN.sub("", line)
        if not line.strip():
            end_para_run()
            if blank_start is None:
                blank_start = i + 1
            else:
                blank_runs.append(blank_start)
            prev_open = False
            continue
        blank_start = None

        # wrap-convention census - same continuation model as reflow-prose.py
        indent = len(line) - len(line.lstrip())
        content = line.lstrip()
        cur_kind = "other"
        if content.startswith(">"):
            end_para_run()
            qtext = re.sub(r"^(?:>[ \t]*)+", "", content)
            if prev_open and prev_quote:
                quote_frag.append(i + 1)
            quotes_seen += 1
            prev_open = not SENT_END.search(qtext)
            prev_quote = True
            prev_kind = "quote"
            cur_kind = "quote"
        elif content.startswith(("#", "<!--")) or RULE_LINE.match(content):
            end_para_run()
            while list_stack and indent < list_stack[-1]:
                list_stack.pop()
            prev_open = False
            prev_quote = False
        elif ITEM_COL.match(line):
            end_para_run()
            content_col = ITEM_COL.match(line).end()
            while list_stack and list_stack[-1] > indent:
                list_stack.pop()
            list_stack.append(content_col)
            items_seen += 1
            prev_open = not SENT_END.search(line[content_col:].strip())
            prev_min = content_col
            prev_quote = False
            prev_kind = "item"
            cur_kind = "item"
        elif TABLE_ROW.match(line):
            end_para_run()
            prev_open = False
            prev_quote = False
        else:
            while list_stack and indent < list_stack[-1]:
                list_stack.pop()
            base = list_stack[-1] if list_stack else 0
            if indent >= base + 4:
                end_para_run()
                prev_open = False   # indented code block
            elif prev_open and not prev_quote and prev_min <= indent < prev_min + 4:
                (list_frag if prev_kind == "item" else para_frag).append(i + 1)
                prev_open = not SENT_END.search(stripped)
                cur_kind = "item" if prev_kind == "item" else "para"
            else:
                para_seen += 1
                para_run_units += 1
                prev_open = not SENT_END.search(content)
                prev_min = indent
                prev_quote = False
                prev_kind = "para"
                cur_kind = "para"
        if cur_kind in ("para", "item", "quote"):
            if SENTENCE_BOUNDARY.search(stripped):
                multi_by_kind.setdefault(cur_kind, []).append(i + 1)
                if cur_kind == "para":
                    para_run_multi = True
            if STRETCHED_GAP.search(content):
                stretch_by_kind.setdefault(cur_kind, []).append(i + 1)
        if len(line) > width:
            wide.append(i + 1)
            if cur_kind in ("para", "item", "quote"):
                wide_by_kind.setdefault(cur_kind, []).append(i + 1)
        if SENTENCE_BOUNDARY.search(stripped):
            multi.append(i + 1)
        if ";" in stripped:
            semis.append(i + 1)
        for ch in stripped:
            if ch in SPECIALS:
                specials.setdefault(ch, []).append(i + 1)
            elif ord(ch) > 127:
                if is_emoji(ch):
                    emoji.append(i + 1)
                else:
                    other_nonascii[ch] = other_nonascii.get(ch, 0) + 1
        if i not in host:
            continue
        head = HEADING.match(line)
        if head:
            depth = len(head.group(1))
            heads[depth] = heads.get(depth, 0) + 1
            title = head.group(2).strip()
            if "(" in title:
                parens.append(i + 1)
            if title.rstrip().endswith((".", ":", ";", "?", "!")):
                punct.append(i + 1)
            if depth > 3:
                deep.append(i + 1)
            if CONTENTS_TITLE.match(title):
                contents.append(i + 1)
            in_table = False
            continue
        bullet = BULLET.match(line)
        if bullet:
            markers[bullet.group(1)] = markers.get(bullet.group(1), 0) + 1
        elif ORDERED.match(line):
            ordered += 1
        if TABLE_ROW.match(line):
            if not in_table:
                tables += 1
                in_table = True
        else:
            in_table = False
        for hit in MARKER.finditer(stripped):
            marker_hits.append((i + 1, hit.group(1)))
        for url in LINK.findall(line):
            if url.startswith(("http://", "https://", "mailto:")):
                continue
            if url.startswith("#"):
                anchors.append(i + 1)
                continue
            links.append((i + 1, url))
            target = url.split("#", 1)[0].split("?", 1)[0]
            if target and not (path.parent / target).resolve().exists():
                missing.append(i + 1)

    end_para_run()

    print(f"FILE {path}")
    print(f"  lines: {len(lines)}")
    print(f"  bytes: {len(text.encode('utf-8'))}")
    print("HEADINGS")
    print("  depth: " + (", ".join(f"H{d}: {heads.get(d, 0)}" for d in range(1, 7))))
    print(f"  depth>3: {refs(deep)}")
    print(f"  parenthesized: {refs(parens)}")
    print(f"  trailing punctuation: {refs(punct)}")
    print("CONTENTS")
    print(f"  contents section: {'present at ' + str(contents[0]) if contents else 'absent'}")
    print("LISTS")
    print("  bullets: " + (", ".join(f"{k}: {v}" for k, v in sorted(markers.items())) or "none"))
    print(f"  ordered items: {ordered}")
    odd = [k for k in markers if k != "-"]
    print(f"  non-dash markers: {', '.join(odd) if odd else 'none'}")
    print("FENCED BLOCKS")
    tags: dict[str, int] = {}
    for _, tag in blocks:
        key = tag.strip() or "untagged"
        tags[key] = tags.get(key, 0) + 1
    print(f"  total: {len(blocks)}")
    print("  by tag: " + (", ".join(f"{k}: {v}" for k, v in sorted(tags.items())) or "none"))
    print(f"  markdown payloads: {payloads}")
    print("CHARACTERS")
    for ch, name in SPECIALS.items():
        hits = specials.get(ch, [])
        print(f"  {name}: {len(hits)}" + (f" (lines {refs(hits)})" if hits else ""))
    print(f"  semicolons in prose: {len(semis)}" + (f" (lines {refs(semis)})" if semis else ""))
    print(f"  emoji: {len(set(emoji))} line(s)" + (f" (lines {refs(sorted(set(emoji)))})" if emoji else ""))
    if other_nonascii:
        print("  other non-ascii: " + ", ".join(f"{ch} U+{ord(ch):04X} x{n}" for ch, n in sorted(other_nonascii.items())))
    else:
        print("  other non-ascii: none")
    print("PARAGRAPHS")
    print(f"  multi-sentence lines: {len(multi)}" + (f" (lines {refs(multi)})" if multi else ""))
    print(f"  consecutive blank runs: {refs(blank_runs)}")
    print(f"  lines over {width}: {refs(wide)}")
    kinds = [("paragraph", para_frag, para_seen), ("list item", list_frag, items_seen),
             ("blockquote", quote_frag, quotes_seen)]
    wrapped = [name for name, frag, _ in kinds if frag]
    logical = [name for name, frag, seen in kinds if not frag and seen]
    if not any(seen for _, _, seen in kinds):
        conv = "no prose"
    elif wrapped and logical:
        conv = "mixed"
    elif wrapped:
        conv = "fixed width"
    else:
        conv = "logical lines"
    print(f"  wrap convention: {conv}")
    for name, frag, seen in kinds:
        detail = f" (lines {refs(frag)})" if frag else ""
        print(f"    {name}: {seen} element(s), {len(frag)} continuation line(s){detail}")
    print("  prose layout:")
    key_of = {"paragraph": "para", "list item": "item", "blockquote": "quote"}
    for name, frag, seen in kinds:
        key = key_of[name]
        stretched = stretch_by_kind.get(key, [])
        packed = multi_by_kind.get(key, [])
        blocks = packed_blocks if key == "para" else 0
        if not seen:
            layout = "none"
        elif stretched:
            layout = f"justified (stretched lines {refs(stretched)})"
        elif frag:
            wide_k = len(wide_by_kind.get(key, []))
            if wide_k > len(frag):
                layout = "mixed (wrapped continuations amid unwrapped lines)"
            else:
                layout = "bounded"
        elif packed or blocks:
            detail2 = refs(packed) if packed else f"{blocks} block(s)"
            if max(len(packed), blocks) * 2 > seen:
                layout = f"flowing (packed {detail2})"
            else:
                layout = f"separated (packed outlier(s): {detail2})"
        else:
            layout = "separated"
        print(f"    {name}: {layout}")
    print("TABLES")
    print(f"  tables: {tables}")
    print("MARKERS")
    if marker_hits:
        counts: dict[str, int] = {}
        for _, m in marker_hits:
            counts[m] = counts.get(m, 0) + 1
        print("  hits: " + ", ".join(f"{m}: {n}" for m, n in sorted(counts.items())))
        print(f"  lines: {refs(sorted({ln for ln, _ in marker_hits}))}")
    else:
        print("  hits: none")
    print("LINKS")
    print(f"  internal links checked: {len(links)}")
    print(f"  anchor links (not resolved): {len(anchors)}")
    print(f"  missing targets: {refs(missing)}")
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        if hasattr(_stream, "reconfigure"):
            _stream.reconfigure(errors="backslashreplace")
    raise SystemExit(main(sys.argv[1:]))
