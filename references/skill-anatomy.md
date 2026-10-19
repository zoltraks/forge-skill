# Skill Anatomy

## Purpose

> **Scope:** Required and optional components of a generated skill
> **Key items:** file roles, when a directory exists, minimum viable set

This file is the checklist phase 2 designs against and `process/skill-template.md`
enforces.

## Required

| Component                      | Role                                                           |
|--------------------------------|----------------------------------------------------------------|
| `SKILL.md`                     | Router - modes, update check, triggers, operations             |
| `AGENTS.md`                    | Maintenance entry point                                        |
| `README.md`                    | Human-facing overview and directory tree                       |
| `CHANGELOG.md`                 | Release history                                                |
| `LICENSE`                      | License text                                                   |
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

## Optional - Evidence-Justified Only

| Component                 | Exists when                                              |
|---------------------------|----------------------------------------------------------|
| `process/<task>.md`       | The domain has distinct procedures the router dispatches |
| `references/`             | Procedures consult reusable domain knowledge             |
| `scripts/<verb>-<obj>.py` | Mechanical, repeatable work exists - never for reasoning |
| `templates/`              | The skill produces documents from skeletons              |
| `assets/`                 | Static files the skill copies or serves                  |
| `types/`, `languages/`…   | Domain taxonomies like panther's - real evidence only    |
| `tests/`                  | The skill ships its own scripts worth testing            |

A generated skill ships no empty directory and no placeholder file "for later".

## Minimum Viable Set

A minimal generated skill still carries every Required row - the shared contract
is what makes it a collection member, and shrinking it breaks compatibility. What
varies with evidence is the optional layer and the domain content inside the
router's operations table.

## Separation Of Concerns

Scripts do mechanical work: rendering, validation, conversion, state checks. Rule
files do reasoning: procedures, criteria, and judgment the agent applies. Never
write a script that "decides" or a procedure that re-implements what a script can
verify deterministically.
