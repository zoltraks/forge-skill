# Skill Housekeeping

## Purpose

> **Scope:** The governed housekeeping procedure for an existing skill project
> or skill collection - inventory, drift, consistency, deduplication, cleanup,
> and optimization
> **Key items:** target resolution, dry-run default, confidence gates,
> archive-before-mutate, collection member boundaries, audit log

This file defines the lifecycle-management path of operation mode: the agent
audits and, on approval, reorganizes, optimizes, and cleans a named target.

Follow it for requests like "housekeep this skill", "clean up the skill
collection", "reorganize <skill>", "optimize <skill>", or "check my skills for
drift".

## Contents

| Section             | What it covers                              |
|---------------------|---------------------------------------------|
| When This Applies   | Target resolution and layout classification |
| Modes               | Interaction-mode resolution for the run     |
| Procedure           | The seven-stage governed loop               |
| Collection Targets  | Index-level checks and member boundaries    |
| Multi-Root          | Cross-platform discovery and drift          |
| What Does Not Apply | Boundaries of the operation                 |

## When This Applies

The target is a named directory that is not this repository - a request whose
target is forge-skill itself stays in maintenance mode per
`process/skill-maintenance.md`.

Classify the target before anything else:

| Target         | Signal                                                       |
|----------------|--------------------------------------------------------------|
| Collection     | Root `SKILL.md` plus `skills/<name>/` member directories     |
| Astra member   | `AGENTS.md`, the shared `process/` contracts, `scripts/` set |
| Spec skill     | `SKILL.md` plus optional resources, no member contract       |
| Plugin package | `.claude-plugin/plugin.json`                                 |
| Foreign        | None of the above - audit only, no mutation proposals        |

A target that carries no `SKILL.md` is not a housekeeping target. Report it as
out of scope rather than treating it as a source for a creation run.

The target's own rules govern its files - this procedure governs how the
housekeeping itself is done.

## Modes

The run resolves its question surfaces through `process/decision-modes.md`:

- Interactive (default) - the audit report and every apply gate ask.
- Autonomous - evidenced recommendations resolve inline, and each resolution
  is reported in the decisions list.
- Fully autonomous - no question surface, every gate that cannot resolve is
  skipped with its dependents and the run is reported partial.
- Verbose - every finding additionally reports evidence, alternatives, and
  rationale.

No mode grants permission to delete, overwrite, commit, or publish. Mutations
are separately gated actions, and in fully autonomous mode an unapproved
mutation is skipped and reported, never performed.

## Procedure

The run is a governed loop: detect, diagnose, plan, apply, verify, report.
Stages 1-4 are read-only - nothing mutates before the plan resolves.

### 1. Intake

Record the operation, mode, target path, and resolved layout in a run ledger at
`work/<YYYY-MM>/<YYYY-MM-DD>/housekeep-run-<id>/state.json` inside this
repository's gitignored workspace.

### 2. Inventory

Run `python3 <skill-root>/scripts/audit-skill.py <target>` - for multi-root
discovery add `--discover` and load `references/platform-paths.md`.

The inventory records per skill: path, layout, lifecycle state, package hash,
file and line counts, token estimates, and copy relationships.

### 3. Audit

Load `references/skill-hygiene.md` - it defines every class below.

- Run `scripts/validate-skill.py --profile <detected>` on each skill, plus the
  target's own validator when it ships one.
- Mechanical findings come from the audit script: broken references, orphans,
  drift verdicts, token overruns.
- Semantic findings are agent work: contradiction tiers, gap classes,
  ownership violations, semantic dedup candidates, description and
  progressive-disclosure weaknesses.
- Classify every finding `HIGH`, `MEDIUM`, or `FALSE_POSITIVE` per the
  confidence matrix.

### 4. Plan

Produce the dry-run report: every finding, its class, the proposed fix, the
gate tier it requires, and the snapshot that precedes it.

Present the plan per the interaction mode. Nothing mutates before this point -
a bare "audit" or "check" request ends here by design.

### 5. Apply

On approval, apply only the approved items, and only through this order:

1. Snapshot every file to be removed or rewritten via
   `scripts/archive-skill.py snapshot <target> --archive-dir <dir> --apply` -
   the archive dir resolves per the target's own conventions (`work/` for
   astra-convention targets, a user-named directory otherwise).
2. Apply the edit, then re-read the changed file to confirm the change
   actually landed - never trust a substitution tool's exit status.
3. Re-validate before the next mutation - the file may have changed since the
   audit.

Ownership duplicates become short pointers to the single owner. Removals are
archived, never deleted. A mutation whose snapshot fails does not run.

### 6. Verify

Re-run `scripts/validate-skill.py` and the audit script on the mutated tree.

For every archived item, exercise the round trip once -
`archive-skill.py list` resolves the snapshot and a `restore` dry-run confirms
the recorded restore path - before marking the item pruned.

### 7. Report

Close with the audit log: findings and their classes, items applied, items
skipped and why, the snapshot identifiers and restore paths, validation
results, and the `Decisions:` recap per `process/decision-modes.md`.

## Collection Targets

A collection adds index-level checks on top of per-member audits:

- The roster table in the index `SKILL.md` matches the member directories one
  to one, and the `README.md` tree mirrors them.
- Recorded pins match member checkouts, per the collection's own
  synchronization rules - a member ahead of its pin is a pending re-pin to
  report, never a checkout to rewind.
- Collection documents carry a single version source per the collection's
  versioning rules.

Member mutations obey the target collection's own membership contract. For
submodule members, per-member findings produce proposals to apply inside the
member's own repository - the collection never patches member checkouts on its
own authority. Tracked members mutate in place under the collection's rules.

## Multi-Root

A `--discover` inventory scans the platform roots table in
`references/platform-paths.md`.

Cross-root findings are reported per that file's precedence and discovery
rules - exact duplicates name the redundant copies, divergent copies name the
hashes and timestamps so the human can pick the canonical one.

Archiving a platform copy respects the platform's load semantics - a cleanup
that ignores read depth or first-file-wins can break resolution even when the
canonical skill is intact.

## What Does Not Apply

- No creation pipeline runs - housekeeping never gathers research, renders
  templates, or writes a new skill.
- No session review runs - findings land through the apply gate, not the
  review procedure.
- Nothing commits, pushes, or publishes - version bumps and changelog entries
  follow the target's own versioning rules and stay uncommitted.
- Nothing hard-deletes - every removal is an archive with a restore path.
- A `Foreign` target yields an audit report only - no mutation proposals for
  layouts this skill does not govern.
