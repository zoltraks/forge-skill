# Skill Template Contract

## Purpose

> **Scope:** What a generated skill contains - the file contract per layout
> profile and the fill rules
> **Key items:** astra, spec, and plugin contracts, template map, fill rules,
> compatibility matrices

This file defines the artifact Forge produces per layout profile - the profiles
and selection rules live in `references/layout-profiles.md`. The templates
themselves live in `templates/`, the canonical template-to-path map is
`templates/README.md`.

## Astra Profile - The Member Contract

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
| `evals/evals.json`             | yes          | `skill-evaluation`           |
| domain directories             | as evidenced | written by the agent         |

## Spec Profile - The Minimal Contract

| File / directory   | Required                     | Template                   |
|--------------------|------------------------------|----------------------------|
| `SKILL.md`         | yes                          | `specification-router`     |
| `README.md`        | recommended                  | `specification-readme`     |
| `LICENSE`          | recommended                  | `skill-license`            |
| `evals/evals.json` | when assertions are designed | `specification-evaluation` |
| domain directories | as evidenced                 | written by the agent       |

A spec skill carries no member-contract surface - no `AGENTS.md`, no
`CHANGELOG.md`, no `docs/`, no shared `process/` procedures, no Forge scripts.
Domain directories remain evidence-justified per
`references/skill-anatomy.md`.

## Plugin Profile - Claude Code Packaging

| File / directory                  | Required        | Template             |
|-----------------------------------|-----------------|----------------------|
| `skills/<name>/` (spec skill)     | yes             | the `spec` set       |
| `.claude-plugin/plugin.json`      | yes             | `plugin-manifest`    |
| `README.md`                       | recommended     | written by the agent |
| `.claude-plugin/marketplace.json` | when publishing | `plugin-marketplace` |

The plugin root's manifest names the plugin and its metadata, and the payload is
an unmodified spec render. Render the `plugin` set into the empty plugin root
before the `spec` payload, since the renderer refuses a non-empty target. A
marketplace request renders `plugin-marketplace` into a separate marketplace
root.

## Collection Mode

A generated collection carries the index set - `collection-router`,
`collection-readme`, `collection-agents`, `collection-contract`,
`collection-review`, `collection-synchronization` - plus one complete single-skill
generation per member.

Collections imply the `astra` profile - member skills are astra-shaped.

The run resolves one of two membership models at intake and records it in the run
state's `inputs`:

- `submodule` - members are independently owned repositories pinned as git
  submodules. Member trees render into each member's own repository checkout, the
  `collection-gitmodules` template renders the registration snippet, and the
  delivery report names the pin and publish steps the user performs.
- `tracked` - members are tracked `skills/<name>/` directories inside the
  collection repository. Member trees render straight into the collection staging
  tree, no `.gitmodules` is emitted, and the generated membership placeholders
  record the tracked model throughout the index documents.

## Fill Rules

- The renderer substitutes `{{placeholder}}` values from `template-input.json` -
  the agent writes that file from verified evidence.
- Every context file carries the renderer's required keys - `skill-name`,
  `skill-title`, `skill-purpose`, `skill-description` - whichever set renders.
  A collection context aliases them to the collection values, while the
  `collection-*` keys carry the real text the index templates consume.
- Frontmatter follows `references/skills-specification.md`: `name` matches the directory
  slug, `description` states purpose and triggers within limits,
  `metadata.version` starts at `0.1.0` where the profile carries one.
- Every `astra` skill ships both autonomy modes in its router and
  `process/decision-modes.md`, even when its own procedures ask nothing - the
  modes are documented no-ops with identical safety semantics.
- Router instructions follow `references/instruction-patterns.md`: procedures
  over declarations, calibrated prescriptiveness, defaults over menus.
- Author metadata comes from the target's convention or an explicit value - never
  guessed or hardcoded from Forge's own author.
- Generated prose follows the shipped style contract: one sentence per paragraph,
  wrapped at 100 characters, tables aligned by source width.
- Runtime scratch belongs to the generated skill's own gitignored `work/`, never
  to Forge's workspace and never to a collection's.

## Compatibility Matrices

Phase 2 fills the matrix for the resolved profile before generation - every
row must pass.

### Astra

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

### Spec

| Check        | Requirement                                                       |
|--------------|-------------------------------------------------------------------|
| Frontmatter  | `name` and `description` per `references/skills-specification.md` |
| Router       | `SKILL.md` under 500 lines, routes to on-demand resources         |
| References   | every referenced path resolves inside the skill directory         |
| Evals        | `evals/evals.json` (when present) carries the canonical schema    |
| Independence | self-contained - no member-contract files, no Forge paths         |

### Plugin

| Check     | Requirement                                                    |
|-----------|----------------------------------------------------------------|
| Payload   | `skills/<name>/` passes the spec matrix                        |
| Manifest  | `.claude-plugin/plugin.json` parses, names the plugin          |
| Packaging | the payload is unmodified - manifests only wrap, never rewrite |

A row that cannot pass carries a recorded reason and the run reports partial.

## Render Discipline

Templates render to a staging directory first, `scripts/validate-skill.py
--profile <profile>` checks the stage, only a passing stage writes to the
target. `scripts/render-templates.py` owns the mechanical rules - placeholder
resolution, path safety, overwrite protection.
