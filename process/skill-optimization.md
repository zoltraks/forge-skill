# Skill Optimization

## Purpose

> **Scope:** The context-diet procedure for a named external skill - measure
> its load surfaces, classify findings, restructure for lazy loading, and
> verify the delta
> **Key items:** target resolution, mechanical measurement, dry-run plan,
> archive-before-mutate, byte-delta report

This file defines the optimization path of operation mode: the agent reduces a
named skill's context consumption while preserving its behavior.

Follow it for requests like "optimize <skill>", "slim <skill>", "reduce
<skill>'s context cost", or "make <skill> lazy-load".

## When This Applies

The target is a named directory carrying a `SKILL.md`.

A request whose target is this repository stays in maintenance mode per
`process/skill-maintenance.md` - self-upkeep routes to `process/housekeeping.md`
or `process/self-healing.md`.

A request to repair a defect or misfiring trigger routes to
`process/skill-healing.md`, and a general cleanup, drift, or deduplication
request routes to `process/skill-housekeeping.md`.

Classify the target's layout per the table in `process/skill-housekeeping.md` -
collection, astra member, spec skill, plugin package, or foreign - before
anything else.

A foreign target receives a proposal report only, never a mutation.

The target's own rules govern its files - this procedure governs how the
optimization itself is done.

## Modes

The run resolves its question surfaces through `process/decision-modes.md`:

- Interactive (default) - the findings report and the apply gate ask.
- Autonomous - evidenced recommendations resolve inline with a `Decisions:`
  list.
- Fully autonomous - no question surface, unresolvable gates skip with their
  dependents and the run reports partial.
- Verbose - every finding additionally reports evidence and rejected
  alternatives.

No mode grants permission to delete, overwrite, commit, or publish. Mutations
are separately gated actions.

## Procedure

The run is a governed loop: measure, diagnose, plan, apply, verify, report.
Stages 1-4 are read-only - nothing mutates before the plan resolves.

### 1. Intake

Record the operation, mode, target path, and resolved layout in a run ledger at
`work/<YYYY-MM>/<YYYY-MM-DD>/optimize-run-<id>/state.json` inside this
repository's gitignored workspace.

Record any request-carried directives - "keep the description under 500
chars", "never touch the templates" - which outrank pattern defaults.

### 2. Measure

Run `python3 <skill-root>/scripts/audit-skill.py --load-profile <target>` and
`python3 <skill-root>/scripts/validate-skill.py --profile <detected>`.

Record the baseline surfaces the profile reports: `description_chars`, router
bytes and lines, per-`## ` section bytes, per-directory totals, and index
presence, plus the baseline validation verdict.

### 3. Diagnose

Load `references/optimization-patterns.md` - it defines the load-surface model,
the finding classes, the restructure patterns, and the layout variants.

Classify every surfaced issue by finding class, and assign each a confidence
per the matrix in `references/skill-hygiene.md`.

Structure the target's own contract mandates is not a finding - recorded
variance resolves `FALSE_POSITIVE` the same way it does in housekeeping.

### 4. Plan

Produce the dry-run report: every finding, its class and confidence, the
pattern that resolves it, the gate tier it requires, and the estimated byte
delta per surface.

Present the plan per the interaction mode. A bare "audit" or "check" phrasing
ends here - no mutation is proposed or applied without the plan's approval.

### 5. Apply

On approval, apply only the approved items, and only through this order:

1. Snapshot every file to be rewritten via
   `scripts/archive-skill.py snapshot <target> --archive-dir <dir> --apply` -
   the archive dir resolves per the target's own conventions.
2. Apply the edit, then re-read the changed file to confirm the change landed.
3. Re-validate before the next mutation - the file may have changed since the
   diagnosis.

Removals are archived, never deleted.

### 6. Verify

Re-run `--load-profile` and both validators on the mutated tree.

Confirm the verification contract of `references/optimization-patterns.md` -
every routed path resolves, every registered resource stays indexed, and no
operation row, gate, or boundary was lost.

### 7. Report

Close with the delta report: before and after bytes for the description, the
router, and each touched directory, findings applied and skipped with reasons,
snapshot identifiers and restore paths, validation results, and the
`Decisions:` recap.

## Collection Targets

Per-member findings produce proposals inside each member's own repository,
under the member's own governing documents - the collection never patches a
member checkout on its own authority.

Collection-index findings mutate the root files only.

## What Does Not Apply

- No creation pipeline runs - optimization never gathers research, renders
  templates, or writes a new skill.
- No defect repair runs - a misfiring trigger is healing work, not diet work.
- Nothing commits, pushes, or publishes - version bumps and changelog entries
  follow the target's own versioning rules and stay uncommitted.
- Nothing hard-deletes - every removal is an archive with a restore path.
- A `Foreign` target yields a proposal report only - no mutations for layouts
  this skill does not govern.
