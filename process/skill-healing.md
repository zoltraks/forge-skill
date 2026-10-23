# Skill Healing

## Purpose

> **Scope:** The evidence-gated repair and improvement procedure for an
> existing skill that is not this repository
> **Key items:** safety taxonomy, healing directives, the evaluate-patch-
> replay-promote loop, external verifiers, continuous improvement, rollback

This file defines the repair path of operation mode: the agent diagnoses a
named skill's defect, produces minimal patches, verifies each against an
external signal, and promotes only what improves without regression.

Follow it for requests like "repair <skill>", "heal <skill>", "fix the
triggering on <skill>", or "improve <named-skill>".

A request to improve forge-skill itself stays in maintenance mode - the
session-review path in `process/session-review.md` owns it.

## Contents

| Section                | What it covers                                    |
|------------------------|---------------------------------------------------|
| Safety Taxonomy        | Which self-repair patterns are allowed            |
| Healing Directives     | Request-carried patch rules that outrank defaults |
| The Healing Loop       | Evaluate, patch, replay, promote                  |
| External Verifiers     | What counts as evidence                           |
| Continuous Improvement | Attribution and the propose-probe-compose mode    |
| What Does Not Apply    | Boundaries of the operation                       |

## Safety Taxonomy

Not every self-repair pattern is safe. The run classifies its approach first:

| Pattern                         | Verdict     | Constraint                                   |
|---------------------------------|-------------|----------------------------------------------|
| Retry plus error classification | Endorsed    | Universal baseline, no verification burden   |
| Reflection / self-correction    | Conditional | Only with an external verifier               |
| Autonomous skill auto-creation  | Rejected    | Requires explicit human-in-the-loop approval |
| Learned-state promotion         | HITL        | Human approval before promotion              |

A patch is never promoted on reflection alone - an internal judgment that a
patch "looks right" is not evidence.

## Healing Directives

The request may carry high-priority patch rules - "never remove existing
constraints", "prioritize citation accuracy over completeness".

Record each directive in the run ledger. Directives outrank the patcher's
defaults and travel with every candidate patch.

## The Healing Loop

Run state lives at `work/<YYYY-MM>/<YYYY-MM-DD>/heal-run-<id>/state.json` and
follows the ledger contract of `process/forge-workflow.md`.

### 1. Evaluate

Score the skill against its own constraints: its `SKILL.md` contract, its
evals where present, and the named defect or regression.

Use structured failure tags - "missed-trigger", "contradiction", "stale-
reference" - not regex heuristics over prose.

### 2. Patch

Generate two or three minimal, targeted patches - a constraint, an example,
an output format, a routing line. Never rewrite the skill wholesale.

Each candidate records what it changes and the failure tag it addresses.

### 3. Replay

Verify every candidate against an external verifier (below) before it touches
the target: re-run the failing path, the target's own validation suite, or
the recorded trace.

A patch that improves the target metric without regressing others passes the
gate. A patch with no measurable improvement is not promoted - report it as
inconclusive rather than applying it.

### 4. Promote

Apply the winning patch. Snapshot the target first via
`scripts/archive-skill.py` - the snapshot is the rollback path.

Record the change per the target's own versioning rules: bump its version
once, write its changelog entry with the before/after, the rationale (which
failure tag triggered it), and the evidence (replay results).

Never commit - propose the commit message and report the restore command.

## External Verifiers

Acceptable signals, in order of strength:

1. The target's own test or validation suite re-run before and after.
2. `scripts/validate-skill.py --profile <detected>` re-run before and after.
3. A replayed execution trace showing the defect resolved.
4. Explicit human confirmation that the observed behavior is the fix.

Every behavioral change requires human approval plus replay evidence, per the
apply-gate table in `references/skill-hygiene.md`.

## Continuous Improvement

For repeated or systematic improvement requests, run the wider loop:

1. Evaluate - effectiveness, efficiency, and cost of the skill as observed.
2. Attribute - classify each failure as skill design, model capability, or
   environment. A model-limitation failure is never "fixed" by editing the
   skill - report it.
3. Optimize - apply the targeted fix: patch, split, merge, or reroute.
4. Re-evaluate - confirm the fix held and nothing else regressed.

For targets that ship evals, an optional deeper pass runs propose, probe,
compose: propose several candidate modifications, probe each against the same
task for behavioral evidence, compose the improvements that measured better.

Execution traces - step-by-step runs compared against the expected workflow -
feed all three stages when the user supplies them.

## What Does Not Apply

- Nothing heals this repository - "improve forge-skill" routes to
  `process/session-review.md` through maintenance mode.
- No auto-created skills - generation stays in `process/forge-workflow.md`.
- No promotion without an external signal - reflection alone is not healing.
- No commits, pushes, or version edits in repositories whose own rules forbid
  them - the target's boundaries apply throughout.
- No hard deletion - every mutation archives first.
