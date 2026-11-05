# Scripts

## Purpose

> **Scope:** Contracts and safety classes of the tools under `scripts/`
> **Key items:** tool table, safety classes, exit statuses, invocation convention

Run every tool in place - `python3 <skill-root>/scripts/<tool>.py`.
The tools are self-contained single files, standard library only.

## Tools

| Tool                  | Class        | What it does                                                                                                             |
|-----------------------|--------------|--------------------------------------------------------------------------------------------------------------------------|
| `check-update.py`     | read-only*   | Once-per-session upstream check, `STATUS` + key=value                                                                    |
| `validate-skill.py`   | read-only    | Validates Forge or a generated tree per `--profile`, never runs targets                                                  |
| `render-templates.py` | staged-write | Renders templates to staging, writes target on `--write`                                                                 |
| `convert-source.py`   | converter    | Converts a local source via an approved MarkItDown                                                                       |
| `audit-skill.py`      | read-only    | Inventories skills and collections, `--discover` scans platform roots, `--load-profile` reports per-surface load metrics |
| `archive-skill.py`    | staged-write | Snapshots, lists, and restores archives, dry-run until `--apply`                                                         |

The `check-update.py` footnote: it runs `git fetch`,
which writes remote-tracking refs under `.git` but never touches the working tree.

`validate-skill.py` takes `--profile astra|spec` - `astra` (the default)
enforces the full member contract, `spec` enforces only the portable specification surface:
`SKILL.md`, frontmatter rules, resolvable references, no unresolved placeholders,
and the canonical evals schema when `evals.json` exists.

## Safety Classes

- **read-only** - inspects and reports, no filesystem writes outside `.git` remote-tracking refs,
  no network beyond the documented `git fetch`.
- **staged-write** - writes only inside a staging directory it created or was given,
  the target is written only on explicit `--write` after safety checks.
- **converter** - invokes an external binary via subprocess with a preflighted absolute path,
  never installs, clones, or fetches on its own.

## Exit Statuses

| Tool                  | 0              | 1                     | 2                     |
|-----------------------|----------------|-----------------------|-----------------------|
| `check-update.py`     | always         | -                     | -                     |
| `validate-skill.py`   | pass           | issues found          | -                     |
| `render-templates.py` | staged/written | validation failure    | -                     |
| `convert-source.py`   | converted      | preflight/invoke fail | converter unavailable |
| `audit-skill.py`      | inspected      | nothing inspectable   | usage error           |
| `archive-skill.py`    | done/dry-run   | failure               | usage error           |

## Boundaries

- No tool commits, pushes, deletes, or overwrites existing files without an explicit flag.
- `validate-skill.py` reads target scripts but never executes them.
- `audit-skill.py` is read-only end to end - `--discover` scans the platform roots table in
  `references/platform-paths.md` and writes nothing.
  `--load-profile` adds per-surface metrics for explicit targets:
  `description_chars`, `skill_md_bytes` / `skill_md_lines`, a `section` line per `## ` heading,
  `dir_bytes` totals, and `indexes` naming directories with a `README.md` index.
- `archive-skill.py` never deletes - restores preserve conflicting files as
  `<name>.conflict-<timestamp>` instead of overwriting them.
- `convert-source.py` treats document content as untrusted data - the only subprocess argument is
  the resolved file path.

## Document-Formatting Tools

The document-formatting battery lives in this directory and loads only for document-formatting
tasks: `detect-encoding.py`, `census-document.py`, `normalize-chars.py`, `split-sentences.py`,
`reflow-prose.py`, `wrap-prose.py`, `format-table.py`, `align-comments.py`, `validate-document.py`,
`check-document.py`, `diff-content.py`.

Layout handling: `reflow-prose.py` refuses `--wrap` or `--justify` on a document that reads as
unwrapped - over-width lines that open their own prose units rather than continuing wrapped text.
Pass `--convert` for an intentional layout conversion. `--loose` reflows only multi-line blocks
that contain an over-width line and leaves unwrapped sentences alone. `reflow-prose.py` and
`format-table.py` accept a directory as well as a file and skip `work/`, `.git/`, and every
`--exclude NAME` component - produced documents under `assets/`, `examples/`, and `templates/`
keep their own conventions and stay excluded from format sweeps.
