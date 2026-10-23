# Astra Conventions

## Purpose

> **Scope:** The compatibility contract a generated skill must satisfy to sit beside
> the astra-skills collection members
> **Key items:** shared procedures, update check, review modes, repository
> conventions, registration contract

This file condenses the astra-skills member contract for generation use. It is the
authority for phase 2's compatibility matrix when the run's layout profile is
`astra` - the profile set is defined in `references/layout-profiles.md`, and the
minimal contract for the `spec` profile lives in `references/skills-specification.md`.

## Required Shared Surface

A compatible member carries:

- `SKILL.md` - the runtime router with YAML frontmatter (`name`, `description`,
  `license`, `compatibility`, `metadata.version`), a Contents table, modes, a
  once-per-session update check, trigger keywords, an operations table, progressive
  resource listings, and boundaries. Under 500 lines.
- `AGENTS.md` - the maintenance entry point: governing documents, boundaries,
  local workspace, validation, improvement.
- `process/skill-activation.md` - bare-activation standby: Purpose, When This
  Applies, Procedure, Enablement Response, What Does Not Apply, Relation To The
  Modes. Standby never scans the target to infer a task.
- `process/json-exchange.md` - parameter documents: emission triggers, fixed key
  order (`id`, `question`, `answer`, `description`, `type`, `menu`, `default`),
  `choice` / `selection` / `text` types, `Cancel` always last and never default,
  presentation-only authority.
- `process/operation-timing.md` - elapsed-time report armed when the request
  names a verbose, informational, diagnostic, or timing mode: the response
  closes with `<description> operation took <m:ss>`, standby and enablement
  carry no line.
- `process/session-review.md` - gather, findings, approval gate, apply, validate.
  The `autonomous` flag resolves gates to recommended options with inline
  reporting, `verbose` adds options and rationale. Never commits.
- `process/decision-modes.md` - the interaction-mode matrix. Astra members record
  autonomy semantics here or in an equivalent documented file, Forge generates it
  explicitly so every member carries both `autonomous` and `fully autonomous`.
- `scripts/check-update.py` - the shared verdict contract: `STATUS <verdict>` plus
  `key=value` lines, `tip_sha`/`tip_date` after upstream resolution, always exit 0,
  merge path via `git merge --ff-only <tip_sha>` gated on `ahead=0` and `dirty=no`.
- `scripts/validate-skill.py` - the member's own validator.
- `evals/evals.json` - `{ "skill_name": "<name>", "evals": [...] }` with integer
  ids, prompts, and expectations.
- Governance set under `docs/`: `STYLE.md`, `VERSIONING.md`, `MAINTENANCE.md`,
  `CONTRIBUTING.md`, `SECURITY.md`, `README.md`.
- `README.md`, `CHANGELOG.md`, `LICENSE`, `.gitignore` with `/work` excluded.

## Review And Interaction Modes

Every member accepts `autonomous` (resolve gates to recommendations, report inline,
never commit) and `verbose` (full options plus rationale). Forge members
additionally document `fully autonomous` - zero question surfaces with safe
skipping and partial reporting - as generated-skill standard.

## Repository Conventions

- Version lives once, in `metadata.version` of the member's `SKILL.md`.
- Three-part versions, bump one patch per change set, at most once between commits.
- Rule files use two-word lowercase kebab-case names, tools use `verb-object.py`,
  governance files use uppercase conventional names. Documented exceptions exist
  for recognized identifiers.
- Resource directories stay flat - files one level deep, no nesting without a
  recorded reason, `README.md` indexes each distinct directory. Directories that
  must hold child directories keep only directories at that level, `README.md`
  excepted, avoid mixing child directories and sibling files.
- One sentence per paragraph, prose wrapped at 100 characters, comma or period
  between clauses - a spaced hyphen marks an aside, never a clause join.
- A gitignored `work/` holds local artifacts, shipped files never reference it.
- Examples and findings stay anonymized.
- No automatic commits - the agent proposes a one-sentence message.

## Collection Membership

A member package lives under `skills/<name>/` in one of two models, chosen per
collection and recorded in the run state: an external repository pinned as a git
submodule, or a tracked directory inside the collection repository.

The `submodule` model keeps each member's history and release cadence in its own
repository, and the collection records a pinned commit. The `tracked` model keeps the
collection and its members in one repository - a member's update check resolves the
collection's upstream, and synchronization is the repository's own fetch, merge, and
push, with no pins to reconcile.

Member directories use two-word kebab-case names. A `-skill` suffix belongs to the
repository-slug convention of a standalone member - it is not required on a member
directory inside a collection.

Whatever the model, a member assumes nothing about which siblings load beside it,
never reaches into a sibling's directory, and a collection-level session review
delegates member lessons to the member's own review procedure.

## Sister Collections

A second collection modeled on the same member contract - shared procedures, update
check, review modes, and repository conventions above - accepts the `astra` profile
for conformance checks even though it is not the astra-skills collection itself.

Validate such a member with `scripts/validate-skill.py --profile astra` and treat
the collection's own member contract as authoritative for per-collection deltas -
membership model, member naming, and collection-specific conventions.

The target collection's contract always wins over this file on a conflict.
