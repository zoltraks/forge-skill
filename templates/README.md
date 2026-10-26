# Templates

## Purpose

> **Scope:** Index of the generation skeletons and the canonical output-path map
> **Key items:** template sets, placeholder vocabulary, render contract

Templates render through `scripts/render-templates.py` with a context document the
agent writes from verified evidence. A `{{placeholder}}` is a named value, never
logic - the renderer is a substitution engine.

## Sets

| Set           | Target                                             |
|---------------|----------------------------------------------------|
| `single`      | One complete member skill tree (`astra` profile)   |
| `spec`        | One minimal spec-conformant skill (`spec` profile) |
| `plugin`      | Claude Code plugin manifest packaging              |
| `marketplace` | Claude Code marketplace catalog entry              |
| `collection`  | A collection index beside member skills            |

## Single Set - Template To Output Map

| Template                      | Output path                     |
|-------------------------------|---------------------------------|
| `skill-router.template`       | `SKILL.md`                      |
| `skill-agents.template`       | `AGENTS.md`                     |
| `skill-readme.template`       | `README.md`                     |
| `skill-changelog.template`    | `CHANGELOG.md`                  |
| `skill-license.template`      | `LICENSE`                       |
| `skill-gitignore.template`    | `.gitignore`                    |
| `skill-activation.template`   | `process/skill-activation.md`   |
| `exchange-procedure.template` | `process/json-exchange.md`      |
| `operation-timing.template`   | `process/operation-timing.md`   |
| `operations-catalog.template` | `process/operations-catalog.md` |
| `review-procedure.template`   | `process/session-review.md`     |
| `decision-modes.template`     | `process/decision-modes.md`     |
| `skill-maintainer.template`   | `process/skill-maintenance.md`  |
| `skill-docs-index.template`   | `docs/README.md`                |
| `skill-contributing.template` | `docs/CONTRIBUTING.md`          |
| `skill-style.template`        | `docs/STYLE.md`                 |
| `skill-maintenance.template`  | `docs/MAINTENANCE.md`           |
| `skill-versioning.template`   | `docs/VERSIONING.md`            |
| `skill-security.template`     | `docs/SECURITY.md`              |
| `skill-evaluation.template`   | `evals/evals.json`              |
| `skill-updater.template`      | `scripts/check-update.py`       |
| `skill-validator.template`    | `scripts/validate-skill.py`     |

The agent-written files beside them - `process/README.md`, `scripts/README.md`,
domain `process/` and `references/` files - come from the rule map, not templates.

## Spec Set - Template To Output Map

| Template                            | Output path        |
|-------------------------------------|--------------------|
| `specification-router.template`     | `SKILL.md`         |
| `specification-readme.template`     | `README.md`        |
| `skill-license.template`            | `LICENSE`          |
| `specification-evaluation.template` | `evals/evals.json` |

The `spec` set emits the minimal spec-conformant package - no member-contract
files. Domain directories are written by the agent beside the rendered set.

## Plugin Set - Template To Output Map

| Template                   | Output path                  |
|----------------------------|------------------------------|
| `plugin-manifest.template` | `.claude-plugin/plugin.json` |

The `plugin` set renders into a plugin root whose `skills/<name>/` payload is a
separate `spec` render - the plugin packaging wraps the skill, it never
rewrites it.

## Marketplace Set - Template To Output Map

| Template                      | Output path                       |
|-------------------------------|-----------------------------------|
| `plugin-marketplace.template` | `.claude-plugin/marketplace.json` |

The `marketplace` set renders into a marketplace root - a separate directory
that lists plugin sources by path.

## Collection Set - Template To Output Map

| Template                              | Output path                  |
|---------------------------------------|------------------------------|
| `collection-router.template`          | `SKILL.md`                   |
| `collection-readme.template`          | `README.md`                  |
| `collection-agents.template`          | `AGENTS.md`                  |
| `collection-contract.template`        | `process/member-contract.md` |
| `collection-review.template`          | `process/session-review.md`  |
| `collection-synchronization.template` | `process/synchronization.md` |
| `collection-gitmodules.template`      | `.gitmodules`                |

Each collection member additionally renders the full `single` set into its own
`skills/<name>/` directory - into the member's own repository checkout under the
`submodule` membership model, or straight into the collection staging tree under the
`tracked` model. The `collection-gitmodules` output is emitted only for `submodule`
collections - a `tracked` run drops the staged `.gitmodules` and records the decision.

## Placeholder Vocabulary

| Placeholder              | Source                                                        |
|--------------------------|---------------------------------------------------------------|
| `skill-name`             | Validated slug matching the target directory                  |
| `skill-title`            | Title Case display name                                       |
| `skill-purpose`          | One-line purpose sentence                                     |
| `skill-description`      | Frontmatter description                                       |
| `skill-version`          | Initial version - `0.1.0`                                     |
| `skill-author`           | Target's author convention, never guessed                     |
| `year`                   | License year                                                  |
| `trigger-keywords`       | Grouped trigger phrase list                                   |
| `operations-table`       | Operations table rows                                         |
| `process-listings`       | Extra `process/` bullet rows                                  |
| `parameter-rows`         | Extra parameter-catalog rows                                  |
| `collection-name`        | Collection slug                                               |
| `collection-title`       | Collection display name                                       |
| `collection-description` | Collection frontmatter description                            |
| `collection-purpose`     | Collection purpose line                                       |
| `member-table`           | Collection member roster rows                                 |
| `gitmodules-entries`     | `.gitmodules` section blocks - `submodule` membership only    |
| `membership-prose`       | Router paragraph describing the collection's membership model |
| `membership-hint`        | Router enablement hint shown for an absent member             |
| `membership-rule`        | AGENTS membership bullet under Adding a Skill                 |
| `membership-install`     | README Installation section body                              |
| `membership-tree`        | README directory-tree comment for `skills/`                   |
| `membership-contract`    | member-contract opening block describing the model            |
| `membership-update`      | member-contract tracked-member upstream resolution            |
| `membership-sync`        | synchronization scope note per membership model               |
| `workflow-steps`         | Spec router's ordered procedure list                          |
| `resource-listings`      | Spec router's on-demand resource bullets                      |
| `plugin-name`            | Claude Code plugin slug                                       |
| `plugin-version`         | Plugin version string                                         |
| `plugin-description`     | Plugin manifest description                                   |
| `plugin-author`          | Plugin author name                                            |
| `marketplace-name`       | Claude Code marketplace slug                                  |
| `plugin-source-path`     | Plugin path relative to the marketplace root                  |

The machine-readable map is `templates/map.json`, keep both in sync per
`docs/MAINTENANCE.md`.
