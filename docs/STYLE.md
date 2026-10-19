# Style

## Purpose

> **Scope:** Prose, tables, headings, and encoding for this repository's documents
> **Key items:** document structure, sentence layout, wrapping, tables, characters,
> file encoding

These rules apply to every shipped file in this repository, and they are the
contract `templates/` encodes for generated skills.

## Document Structure

- One H1 title (`#`) at the top of the file, concise and descriptive.
- A `## Purpose` section immediately after, using the blockquote `Scope:` /
  `Key items:` shape where the file is a rule file.
- Main sections at H2 (`##`), subsections at H3 (`###`). No H4 or deeper.
- Headings use Title Case, carry no trailing punctuation, and no parenthesized
  qualifiers.
- Files over 300 lines carry a `## Contents` table right after the title block,
  anchored to real headings.

## Prose

- One sentence per paragraph - separate sentences with a blank line.
- A sentence may hold several clauses expressing one thought.
- Wrap prose at 100 characters, tables, code blocks, and frontmatter are exempt.
- Prefer a comma or a period between clauses. A spaced hyphen (` - `) marks an
  aside or a definitional separator, never a clause join.
- No semicolons in running prose.
- Straight ASCII quotes and apostrophes. No emoji unless a file's subject
  requires one.
- Mark missing information explicitly: `NOT SPECIFIED` or `TBD` - never invented
  content.

## Tables

- Align columns by source width, the delimiter row matches the header width.
- Keep cell text short, detail belongs in prose, not cells.

## Code Blocks

- Use fenced blocks with a language tag (`bash`, `json`, `text`, `markdown`).
- Commands are copyable as-is - no prompt characters, no line-continuation
  tricks.

## File Encoding

- UTF-8 without BOM, LF line endings.
- Preserve the existing encoding and line-ending style of a file being edited.
