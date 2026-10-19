# Layout Migration

## Purpose

> **Scope:** Converting an existing skill between layout profiles
> **Key items:** layout detection, adopt and export directions, delta plan,
> content preservation, validation

Follow it for requests like "adopt this skill into astra", "migrate this skill
to the spec layout", "export <skill> as a portable package", or "package this
skill as a Claude plugin".

Migration works on a copy or on the source in place only when the user
explicitly approves it - the source skill's own repository rules always apply,
and Forge never commits the result.

## Directions

| Direction | From                    | To                                   |
|-----------|-------------------------|--------------------------------------|
| Adopt     | Foreign or `spec` skill | `astra` member layout                |
| Export    | `astra` member          | `spec` minimal package               |
| Package   | `spec` or `astra` skill | `plugin` - Claude Code plugin layout |

`layout-profiles.md` in `references/` defines what each profile carries - the
migration computes the delta between the source's layout and the target
profile's contract.

## Procedure

### Inspect

Read the source skill: `SKILL.md` frontmatter and body, the directory tree,
any scripts, evals, and governance files.

Classify the current layout - an astra member carries the shared procedures
and `docs/` set, a spec skill is `SKILL.md` plus optional resources, a plugin
root carries `.claude-plugin/plugin.json`.

A source that is not a skill at all - no `SKILL.md` - is not a migration. It
is either an analysis source for a fresh run or out of scope. Report which.

### Plan The Delta

Name every file the migration adds, rewrites, or drops, and why:

- **Adopt** adds the member surface: `AGENTS.md`, `CHANGELOG.md`, `.gitignore`,
  the shared `process/` contracts, `scripts/check-update.py`,
  `scripts/validate-skill.py`, the `docs/` governance set, and astra-schema
  `evals/evals.json`. The router body is re-shaped to the astra skeleton while
  its domain triggers, operations, and listings survive verbatim or adapted.
- **Export** keeps `SKILL.md`, the domain directories, and `evals/` - the
  router body is rewritten without the astra machinery (update check, shared
  procedures, autonomy matrix) while preserving domain routing, and
  `expectations` entries map to `assertions`. Member-contract files are left
  behind in the source, not copied.
- **Package** keeps the skill tree as-is under `skills/<name>/` and adds only
  the `.claude-plugin/` manifests - a package step never rewrites the payload.
  Render order matters because the renderer refuses a non-empty target: render
  the `plugin` set into the fresh plugin root first, then render the `spec`
  payload into `skills/<name>/`, which is still empty. For an existing skill
  the payload is copied, not re-rendered.

Present the delta plan per the interaction mode before touching anything.

### Apply

Write the target tree into the approved output directory - never back over the
source unless the user approved an in-place migration.

Preserve domain content verbatim wherever it fits the target contract - the
migration changes packaging, not knowledge.

Anonymization still applies: recorded identifiers from the source stay out of
generated prose unless the source skill is the user's own and they say keep.

### Validate

Run `scripts/validate-skill.py --profile <target>` on the result - `spec` for
export and for the skill inside a package, `astra` for an adoption.

Report the applied delta: files added, rewritten, left behind, and every
validation result - never claim a check that did not run.

## What Does Not Apply

- No research pipeline runs - migration converts layout, it does not gather or
  synthesize domain evidence. Missing domain content is a gap to report, not
  to invent.
- A migration never publishes, commits, registers submodules, or touches the
  collection - those stay user-side steps named in the report.
