# Changelog

## [0.1.6] - 2026-10-22

### Added

- `process/operation-timing.md` records operation timing: under a verbose,
  informational, or diagnostic flag a named operation's response ends with a
  separate paragraph reporting `<description> operation took <m:ss>` as its
  last sentence.
- `evals/evals.json` gains a diagnostic-timing regression prompt.

## [0.1.4] - 2026-10-21

### Changed

- `references/astra-conventions.md` gains a Sister Collections section - the astra
  profile applies as a conformance check to collections modeled on the same member
  contract, with the target collection's own contract winning on conflicts.
- `SKILL.md` triggers cover member-addition and collection-adjustment requests
  in any collection, and the operations table gains a conformance-check row
  (validator plus conventions file, verdict only, no writes).
- `evals/evals.json` adds a member-addition regression prompt.

## [0.1.3] - 2026-10-19

### Changed

- Collection generation gains a membership model resolved at intake: `submodule`
  keeps members as pinned external repositories, `tracked` renders members as
  tracked `skills/<name>/` directories inside the collection repository and emits
  no `.gitmodules`. `process/skill-template.md`, `process/forge-workflow.md`,
  `references/astra-conventions.md`, and `references/layout-profiles.md` record the
  contract.
- The `collection` template set is membership-aware through new placeholders
  (`membership-prose`, `membership-usage`, `membership-hint`, `membership-rule`,
  `membership-install`, `membership-tree`, `membership-contract`,
  `membership-update`, `membership-sync`) registered in `templates/README.md`.
- Member directory naming follows two-word kebab-case - the `-skill` suffix is a
  standalone-repository convention, not required inside a collection.
- `evals/evals.json` adjusts the collection eval for both models and adds a
  tracked-membership regression prompt.
- `templates/collection-readme.template` and `templates/decision-modes.template`
  drop the `text` fence tag - plain-text blocks ship untagged fences.
- `process/skill-template.md` records the required context keys every render
  input carries, and `process/forge-workflow.md` adds the staged-tree editorial
  pass to phase 3.

## [0.1.2] - 2026-10-19

### Changed

- `CHANGELOG.md` drops the `Unreleased` section: change-set entries record directly under
  `## [<version>] - <date>` headings opened with the set's version bump, and
  `docs/VERSIONING.md` and `SKILL.md` carry the new release-record rule. The `0.1.1`
  release entries are re-anchored to their shipped version heading.
- `references/skill-anatomy.md` records the collection test layout: script tests live in
  `tests/` at the repository root, with subdirectory containers such as `fixtures/`.

## [0.1.1] - 2026-10-19

### Added

- Layout profiles: generation targets now include the astra member layout
  (default), a minimal spec-conformant package per the Agent Skills
  specification, and Claude Code plugin/marketplace packaging - resolved at
  intake and recorded in the run state.
- `process/layout-migration.md` migrates existing skills between layouts in
  both directions - adopt a foreign skill into astra, export a member to a
  minimal spec package, or package a skill as a plugin.
- `references/layout-profiles.md`, `references/instruction-patterns.md`, and
  `references/evaluation-design.md` codify the profile contracts, process-driven
  instruction design, and evaluation/security guardrails for generated skills.
- `references/skills-specification.md` now condenses the canonical
  `agentskills.io/specification` - full field table, naming limits,
  progressive-disclosure budgets, file-reference rules, and the `skills-ref`
  validator.
- New template sets `spec`, `plugin`, and `marketplace` render the minimal
  package and the `.claude-plugin/` manifests.
- `scripts/validate-skill.py` gains `--profile astra|spec` - the spec profile
  enforces only the portable specification surface.

### Changed

- Resource names spell out full words: `references/skills-specification.md`
  replaces `skills-spec.md`, and templates `specification-router`,
  `specification-readme`, `specification-evaluation`, `skill-evaluation`,
  and `collection-synchronization` replace their abbreviated predecessors.
  The `spec` layout profile keeps its name - only file names changed.

### Fixed

- `CHANGELOG.md` anchors the `## [0.1.0]` release heading: the initial package
  change set shipped under `0.1.0` while its entries still sat under
  `## [Unreleased]`.

## [0.1.0] - 2026-10-19

### Added

- Initial Forge skill package: five-phase skill-creation pipeline, shared member
  contracts (activation, JSON exchange, session review, update check), the
  interaction-mode matrix (interactive, autonomous, fully autonomous, verbose),
  source conversion through an approved local MarkItDown, single-skill and
  collection template sets, the read-only skill validator, the deterministic
  template renderer, the source converter, behavioral evals, and the test suite.
