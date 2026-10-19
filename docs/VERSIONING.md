# Versioning

## Purpose

> **Scope:** Version format, bump rules, and release anchoring for forge-skill
> **Key items:** three-part format, single location, change-set rule

## Format

The skill version is three-part `major.minor.patch` (e.g. `0.1.0`), stored once -
in `metadata.version` of `SKILL.md`. No other document carries a literal copy,
documents and examples use `0.x.y` or `<version>` placeholders.

## Bump Rule

Bump `metadata.version` by one patch with every change set that modifies skill
document contents. A change set is the edits delivered together, the version moves
at most once between two commits - further edits before the commit join the open
set and keep its already-bumped number.

Rollover: `0.1.9` bumps to `0.2.0`, `0.9.9` to `1.0.0` - patch rolls at 9.

## Release Anchoring

`CHANGELOG.md` records each change set under `## [<version>] - <date>` as it lands, where
`<version>` is the version the set bumps to and `<date>` is the delivery date. The heading
opens together with the bump - `CHANGELOG.md` never carries an `Unreleased` section, so a
committed change set can no longer ship under a placeholder. The changelog is release-facing
history, it is not the version source of truth.
