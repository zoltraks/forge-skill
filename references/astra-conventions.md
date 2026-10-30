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
- `process/json-exchange.md` - parameter documents: emission triggers, context
  fields `target`, `task`, `date`, `time`, fixed key order (`id`, `question`,
  `answer`, `description`, optional `when`, `type`, `menu`, `open`, `default`),
  `choice` / `selection` / `text` types, `Cancel` always last and never default,
  both return forms accepted (answer-filled document and `response` wrapper),
  presentation-only authority.
- `process/operation-timing.md` - elapsed-time report armed by default on every
  operation with a `no timing` per-request opt-out: the response closes with
  `<description> operation took <m:ss>` and a bare activation times its update
  check. Operations past three minutes add a stage breakdown table,
  backgrounded commands get a ~60-second output heartbeat, and verbose reports
  carry an agent/model identity block resolved through the marker ladder.
- `process/operations-catalog.md` - the canonical operations table for
  "list all operations" requests: `Family | Operation | What it covers`,
  concrete operations over family names, Enable family rows included,
  delivered inline with a closing invitation line.
- `process/session-review.md` - gather, findings, approval gate, apply, validate.
  The `autonomous` flag resolves gates to recommended options with inline
  reporting, `verbose` adds options and rationale. Never commits.
- `process/decision-modes.md` - the interaction-mode matrix. The canonical
  autonomous tier is named `autonomous` with `automatic`, `unattended`,
  `non-interactive`, and `automated` as accepted aliases; Forge additionally
  documents `fully autonomous` as a real second tier.
- `process/parallel-execution.md` - the delegated scout model for large work
  surfaces: applicability gate, scout contract (read-only or scratch-only,
  text findings, scoped brief), single-writer merge discipline, provenance,
  sequential fallback.
- `process/housekeeping.md` - self-repository upkeep: upstream report,
  registration reconciliation, evals coverage, version check, workspace
  hygiene, the member's own validation suite, proposal-only report.
- `process/self-healing.md` - the member self-repair loop: evaluate, patch,
  replay, promote, with the safety taxonomy and external-verifier rule.
- `process/development.md` - standby-for-specification mode: the named trigger
  runs the update check, reports readiness, and waits for a described change.
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

A member is a standalone package: a shipped member file never names a sibling
member, never carries a `../<sibling>` path, and never assumes collection files
exist - cross-member composition is orchestrated only by collection documents.

## Sister Collections

A second collection modeled on the same member contract - shared procedures, update
check, review modes, and repository conventions above - accepts the `astra` profile
for conformance checks even though it is not the astra-skills collection itself.

Validate such a member with `scripts/validate-skill.py --profile astra` and treat
the collection's own member contract as authoritative for per-collection deltas -
membership model, member naming, and collection-specific conventions.

The target collection's contract always wins over this file on a conflict.
