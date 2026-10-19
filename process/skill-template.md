# Skill Template Contract

## Purpose

> **Scope:** What a generated skill contains - the file contract and fill rules
> **Key items:** required files, optional directories, template map, fill rules,
> compatibility matrix

This file defines the artifact Forge produces. The templates themselves live in
`templates/`, the canonical template-to-path map is `templates/README.md`.

## The Generated File Contract

A generated single skill carries:

| File / directory               | Required     | Template                     |
|--------------------------------|--------------|------------------------------|
| `SKILL.md`                     | yes          | `skill-router`               |
| `AGENTS.md`                    | yes          | `skill-agents`               |
| `README.md`                    | yes          | `skill-readme`               |
| `CHANGELOG.md`                 | yes          | `skill-changelog`            |
| `LICENSE`                      | yes          | `skill-license`              |
| `.gitignore`                   | yes          | `skill-gitignore`            |
| `process/skill-activation.md`  | yes          | `skill-activation`           |
| `process/json-exchange.md`     | yes          | `exchange-procedure`         |
| `process/session-review.md`    | yes          | `review-procedure`           |
| `process/decision-modes.md`    | yes          | `decision-modes`             |
| `process/skill-maintenance.md` | yes          | `skill-maintainer`           |
| `process/README.md`            | yes          | written by the agent         |
| `scripts/check-update.py`      | yes          | `skill-updater`              |
| `scripts/validate-skill.py`    | yes          | `skill-validator`            |
| `scripts/README.md`            | yes          | written by the agent         |
| `docs/` (governance set)       | yes          | `skill-docs-index` + 5 files |
| `evals/evals.json`             | yes          | `skill-evals`                |
| domain directories             | as evidenced | written by the agent         |

Domain-specific directories - `types/`, `languages/`, `conventions/`, additional
`process/` or `references/` files - exist only when the evidence justifies them, per
`references/skill-anatomy.md`. A generated skill does not ship empty directories.

## Collection Mode

A generated collection carries the index set - `collection-router`,
`collection-readme`, `collection-agents`, `collection-contract`,
`collection-review`, `collection-sync` - plus one complete single-skill generation
per member and a staged `collection-gitmodules` registration snippet.

Members are independently owned repositories. The generated collection never
contains member sources as plain files, the delivery report names the pin and
publish steps the user performs.

## Fill Rules

- The renderer substitutes `{{placeholder}}` values from `template-input.json` -
  the agent writes that file from verified evidence.
- Every generated skill ships both autonomy modes in its router and
  `process/decision-modes.md`, even when its own procedures ask nothing - the
  modes are documented no-ops with identical safety semantics.
- Frontmatter follows `references/skills-spec.md`: `name` matches the directory
  slug, `description` states purpose and triggers within limits,
  `metadata.version` starts at `0.1.0`.
- Author metadata comes from the target's convention or an explicit value - never
  guessed or hardcoded from Forge's own author.
- Generated prose follows the shipped style contract: one sentence per paragraph,
  wrapped at 100 characters, tables aligned by source width.
- Runtime scratch belongs to the generated skill's own gitignored `work/`, never
  to Forge's workspace and never to a collection's.

## Compatibility Matrix

Phase 2 fills this matrix before generation - every row must pass:

| Check             | Requirement                                              |
|-------------------|----------------------------------------------------------|
| Router            | `SKILL.md` routes, frontmatter complete, under 500 lines |
| Shared procedures | activation, JSON exchange, session review present        |
| Decision modes    | both autonomy modes plus verbose documented              |
| Update check      | `check-update.py` present with shared verdict semantics  |
| Registration      | every resource registered in router and README           |
| Evals             | `evals/evals.json` valid, `skill_name` matches           |
| Naming            | two-word kebab-case rule files, `verb-object.py` tools   |
| Governance        | full `docs/` set present                                 |
| Independence      | self-contained - no sibling paths, no Forge paths        |

A row that cannot pass carries a recorded reason and the run reports partial.

## Render Discipline

Templates render to a staging directory first, `scripts/validate-skill.py` checks
the stage, only a passing stage writes to the target. `scripts/render-templates.py`
owns the mechanical rules - placeholder resolution, path safety, overwrite
protection.
