# Source Conversion

## Purpose

> **Scope:** Converting local external sources into readable text for gathering
> **Key items:** converter location, preflight, authorization, extraction quality,
> scratch boundary

This file defines how binary and markup sources become text the gathering pass can
read. The mechanical preflight and invocation live in `scripts/convert-source.py`,
the converter reference is `references/markitdown-reference.md`.

## When This Applies

A source whose `format` in the inventory is `pdf`, `epub`, `docx`, `pptx`, `html`,
or another binary/markup format needs conversion before extraction. `markdown` and
`text` sources read directly - no converter runs.

## Converter Location

Resolve a converter in this order:

1. An installed `markitdown` CLI or importable module already on the host.
2. A previously approved local clone, recorded in the run ledger.
3. Otherwise - conversion is blocked pending approval.

An install, clone, or environment change is a separately gated action: interactive
and autonomous modes ask first, fully autonomous mode skips it and records the
blocker. Never silently modify the host's Python environment, and never fetch on
assumption.

## Preflight

Before invoking a converter:

- Resolve the source path to an absolute path inside the allowed area, reject
  escapes and missing files.
- Record the size and extension - an unexpected type goes back to the inventory.
- Confirm the converter's version satisfies the reference constraints (Python
  3.10-3.14, format extras such as `[pdf]` or `[docx]` when required).

## Invocation

Run the converter as a subprocess with the absolute source path, capture the text,
and write it only into the run workspace - `work/<date>/forge-run-<id>/sources/<id>.md`
with a per-source digest recorded in the inventory.

Pass no document-derived string as an argument. The converter performs I/O with the
process's privileges, so the input is the file path alone.

## Extraction Quality

After conversion, inspect the output before extraction relies on it:

- Empty or near-empty output from a non-empty file - likely scanned images, a
  separate approved OCR path would be needed, record `blocked`.
- Missing tables, broken ordering, truncated sections, malformed structure.
- Residual invisible or tag-range Unicode - flag per `references/source-integrity.md`.

Record an `extraction-quality` note per source: `clean`, `lossy` (with the lost
elements named), or `failed`. Lossy output is usable with its losses named, failed
output degrades per `process/research-gathering.md`.

## Scratch Boundary

Converted text, source digests, and long excerpts stay in the run workspace - they
never land in shipped files or generated skill content. Only derived, cited
knowledge moves forward into `evidence.md`.

Never ship raw copyrighted source text in a generated skill - paraphrased,
attributed knowledge only, per `references/source-integrity.md`.
