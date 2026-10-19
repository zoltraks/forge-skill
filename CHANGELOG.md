# Changelog

## [Unreleased]

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
