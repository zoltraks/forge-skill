# MarkItDown Reference

## Purpose

> **Scope:** The external document converter Forge may use for binary and markup
> sources
> **Key items:** identity, upstream, version constraints, invocation, output shape,
> security

## Identity

MarkItDown is Microsoft's document-to-Markdown converter, used by Forge as the
preferred converter for PDF, EPUB, DOCX, PPTX, and HTML sources.

- Upstream repository: `https://github.com/microsoft/markitdown`
- Distribution: `pip install markitdown` or `pip install 'markitdown[all]'`
- Python requirement: >= 3.10 and < 3.15
- Format extras: `[pdf]`, `[docx]`, `[pptx]`, `[xlsx]`, and others - install the
  extra matching the source format.

## Invocation

CLI usage:

```bash
markitdown path-to-file.pdf > document.md
markitdown path-to-file.pdf -o document.md
cat path-to-file.pdf | markitdown
```

`scripts/convert-source.py` locates the CLI (`markitdown` on PATH) or the module
(`python3 -c "import markitdown"`) before invoking. Conversion output reliably
exposes `text_content`, do not assume title, author, or page-count metadata -
read only fields actually present or derive metadata from approved sources.

## Security Notes

MarkItDown performs file and network I/O with the calling process's privileges.
Forge therefore:

- Passes only an absolute, preflighted local file path - never document-derived
  strings, never URLs the document itself supplied.
- Writes output into the gitignored run workspace, never into shipped files.
- Treats converted text as untrusted content per `references/source-integrity.md`.
- Never installs or clones the tool without the gated approval of
  `process/decision-modes.md`.

## Fallbacks

When MarkItDown is unavailable and installation is not approved, conversion is
blocked - the source records `blocked` and the run degrades per
`process/research-gathering.md`. Plain text and Markdown sources never need it.
