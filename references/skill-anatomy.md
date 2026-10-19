# Skill Anatomy

## Purpose

> **Scope:** Required and optional components of a generated skill, per layout
> profile
> **Key items:** universal vs astra components, file roles, when a directory
> exists, minimum viable set, separation of concerns

This file is the checklist phase 2 designs against and `process/skill-template.md`
enforces.

The layout profile decides which table applies - `references/layout-profiles.md`
defines the profiles and the selection rules.

## Universal - Every Profile

| Component   | Role                                                            |
|-------------|-----------------------------------------------------------------|
| `SKILL.md`  | Router - frontmatter, modes, triggers, operations               |
| `README.md` | Human-facing overview - optional in `spec`, required in `astra` |
| `LICENSE`   | License text - optional in `spec`, required in `astra`          |

Domain directories are evidence-justified in every profile:

| Component                 | Exists when                                                                                            |
|---------------------------|--------------------------------------------------------------------------------------------------------|
| `process/<task>.md`       | The domain has distinct procedures the router dispatches                                               |
| `references/`             | Procedures consult reusable domain knowledge                                                           |
| `scripts/<verb>-<obj>.py` | Mechanical, repeatable work exists - never for reasoning                                               |
| `templates/`              | The skill produces documents from skeletons                                                            |
| `assets/`                 | Static files the skill copies or serves                                                                |
| `types/`, `languages/`…   | Domain taxonomies like panther's - real evidence only                                                  |
| `tests/`                  | The skill ships its own scripts worth testing                                                          |
| `evals/`                  | Always for `astra`, and for `spec` when assertions are designed, per `references/evaluation-design.md` |

A generated skill ships no empty directory and no placeholder file "for later".

## Astra Profile Adds

The member contract on top of the universal set:

| Component                      | Role                                                           |
|--------------------------------|----------------------------------------------------------------|
| `AGENTS.md`                    | Maintenance entry point                                        |
| `CHANGELOG.md`                 | Release history                                                |
| `.gitignore`                   | Excludes the runtime `work/` tree and Python artifacts         |
| `process/skill-activation.md`  | Bare-activation standby contract                               |
| `process/json-exchange.md`     | Parameter exchange contract                                    |
| `process/session-review.md`    | Improvement-routine contract                                   |
| `process/decision-modes.md`    | Interaction-mode matrix                                        |
| `process/skill-maintenance.md` | Self-maintenance intake                                        |
| `process/README.md`            | Procedure index                                                |
| `scripts/check-update.py`      | Once-per-session upstream check                                |
| `scripts/validate-skill.py`    | Read-only validator                                            |
| `scripts/README.md`            | Tool index                                                     |
| `docs/` governance set         | STYLE, VERSIONING, MAINTENANCE, CONTRIBUTING, SECURITY, README |
| `evals/evals.json`             | Behavioral regression prompts                                  |

## Plugin Profile

A `plugin` package is a `spec` skill nested under `skills/<name>/` inside a
Claude Code plugin root carrying `.claude-plugin/plugin.json`, plus an optional
`.claude-plugin/marketplace.json` in a marketplace root - per
`references/layout-profiles.md`.

## Minimum Viable Set

A minimal `astra` skill still carries every member-contract row - the shared
contract is what makes it a collection member, and shrinking it breaks
compatibility.

A minimal `spec` skill is `SKILL.md` alone - everything else waits for
evidence.

## Separation Of Concerns

Scripts do mechanical work: rendering, validation, conversion, fetching,
state checks. Rule files do reasoning: procedures, criteria, and judgment the
agent applies. Never write a script that "decides" or a procedure that
re-implements what a script can verify deterministically.

The boundary is measured, not just principled - moving mechanical steps from
inference into scripts has cut skill cost by roughly a quarter in published
experiments while improving accuracy.

Bundled scripts are non-interactive, accept input via flags or stdin, document
themselves through `--help`, and pin their dependencies, per the upstream
guidance `references/skills-specification.md` condenses.
