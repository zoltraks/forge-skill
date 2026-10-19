# Scripts

## Purpose

> **Scope:** Contracts and safety classes of the tools under `scripts/`
> **Key items:** tool table, safety classes, exit statuses, invocation convention

Run every tool in place - `python3 <skill-root>/scripts/<tool>.py`. The tools are
self-contained single files, standard library only.

## Tools

| Tool                  | Class        | What it does                                             |
|-----------------------|--------------|----------------------------------------------------------|
| `check-update.py`     | read-only*   | Once-per-session upstream check, `STATUS` + key=value    |
| `validate-skill.py`   | read-only    | Validates Forge or a generated tree, never runs targets  |
| `render-templates.py` | staged-write | Renders templates to staging, writes target on `--write` |
| `convert-source.py`   | converter    | Converts a local source via an approved MarkItDown       |

The `check-update.py` footnote: it runs `git fetch`, which writes remote-tracking
refs under `.git` but never touches the working tree.

## Safety Classes

- **read-only** - inspects and reports, no filesystem writes outside `.git`
  remote-tracking refs, no network beyond the documented `git fetch`.
- **staged-write** - writes only inside a staging directory it created or was
  given, the target is written only on explicit `--write` after safety checks.
- **converter** - invokes an external binary via subprocess with a preflighted
  absolute path, never installs, clones, or fetches on its own.

## Exit Statuses

| Tool                  | 0              | 1                     | 2                     |
|-----------------------|----------------|-----------------------|-----------------------|
| `check-update.py`     | always         | -                     | -                     |
| `validate-skill.py`   | pass           | issues found          | -                     |
| `render-templates.py` | staged/written | validation failure    | -                     |
| `convert-source.py`   | converted      | preflight/invoke fail | converter unavailable |

## Boundaries

- No tool commits, pushes, deletes, or overwrites existing files without an
  explicit flag.
- `validate-skill.py` reads target scripts but never executes them.
- `convert-source.py` treats document content as untrusted data - the only
  subprocess argument is the resolved file path.
