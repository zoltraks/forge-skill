# Templates

## Purpose

> **Scope:** Index of the generation skeletons and the canonical output-path map
> **Key items:** template sets, placeholder vocabulary, render contract

Templates render through `scripts/render-templates.py` with a context document the
agent writes from verified evidence. A `{{placeholder}}` is a named value, never
logic - the renderer is a substitution engine.

## Sets

| Set          | Target                                  |
|--------------|-----------------------------------------|
| `single`     | One complete member skill tree          |
| `collection` | A collection index beside member skills |

## Single Set - Template To Output Map

| Template                      | Output path                    |
|-------------------------------|--------------------------------|
| `skill-router.template`       | `SKILL.md`                     |
| `skill-agents.template`       | `AGENTS.md`                    |
| `skill-readme.template`       | `README.md`                    |
| `skill-changelog.template`    | `CHANGELOG.md`                 |
| `skill-license.template`      | `LICENSE`                      |
| `skill-gitignore.template`    | `.gitignore`                   |
| `skill-activation.template`   | `process/skill-activation.md`  |
| `exchange-procedure.template` | `process/json-exchange.md`     |
| `review-procedure.template`   | `process/session-review.md`    |
| `decision-modes.template`     | `process/decision-modes.md`    |
| `skill-maintainer.template`   | `process/skill-maintenance.md` |
| `skill-docs-index.template`   | `docs/README.md`               |
| `skill-contributing.template` | `docs/CONTRIBUTING.md`         |
| `skill-style.template`        | `docs/STYLE.md`                |
| `skill-maintenance.template`  | `docs/MAINTENANCE.md`          |
| `skill-versioning.template`   | `docs/VERSIONING.md`           |
| `skill-security.template`     | `docs/SECURITY.md`             |
| `skill-evals.template`        | `evals/evals.json`             |
| `skill-updater.template`      | `scripts/check-update.py`      |
| `skill-validator.template`    | `scripts/validate-skill.py`    |

The agent-written files beside them - `process/README.md`, `scripts/README.md`,
domain `process/` and `references/` files - come from the rule map, not templates.

## Collection Set - Template To Output Map

| Template                         | Output path                  |
|----------------------------------|------------------------------|
| `collection-router.template`     | `SKILL.md`                   |
| `collection-readme.template`     | `README.md`                  |
| `collection-agents.template`     | `AGENTS.md`                  |
| `collection-contract.template`   | `process/member-contract.md` |
| `collection-review.template`     | `process/session-review.md`  |
| `collection-sync.template`       | `process/synchronization.md` |
| `collection-gitmodules.template` | `.gitmodules`                |

Each collection member additionally renders the full `single` set into its own
`skills/<name>/` directory in the member's own repository - never as tracked files
inside the collection checkout.

## Placeholder Vocabulary

| Placeholder              | Source                                       |
|--------------------------|----------------------------------------------|
| `skill-name`             | Validated slug matching the target directory |
| `skill-title`            | Title Case display name                      |
| `skill-purpose`          | One-line purpose sentence                    |
| `skill-description`      | Frontmatter description                      |
| `skill-version`          | Initial version - `0.1.0`                    |
| `skill-author`           | Target's author convention, never guessed    |
| `year`                   | License year                                 |
| `trigger-keywords`       | Grouped trigger phrase list                  |
| `operations-table`       | Operations table rows                        |
| `process-listings`       | Extra `process/` bullet rows                 |
| `parameter-rows`         | Extra parameter-catalog rows                 |
| `collection-name`        | Collection slug                              |
| `collection-title`       | Collection display name                      |
| `collection-description` | Collection frontmatter description           |
| `collection-purpose`     | Collection purpose line                      |
| `member-table`           | Collection member roster rows                |
| `gitmodules-entries`     | `.gitmodules` section blocks                 |

The machine-readable map is `templates/map.json`, keep both in sync per
`docs/MAINTENANCE.md`.
