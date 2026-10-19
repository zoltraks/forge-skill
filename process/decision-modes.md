# Decision Modes

## Purpose

> **Scope:** The interaction-mode contract for every Forge operation - how routine
> decisions, checkpoints, missing inputs, and gated actions resolve in each mode
> **Key items:** mode matrix, recommendation precedence, decision log, verbose
> reporting, permission boundary

This file is the authoritative definition of the interaction modes named in
`SKILL.md`. Every operation-mode procedure resolves its question surfaces through
this matrix.

The session review keeps the shared two-flag review contract of
`process/session-review.md`, the `autonomous` and `verbose` semantics there and here
are the same.

## Mode Selection

Classify the operation first, then select the interaction mode once at intake and
carry it through the run, including resume.

- An explicit "fully autonomous", "no questions", or "without asking" wins over a
  bare "autonomous".
- `verbose` modifies reporting, never authorization.
- Explicit user instructions and governing project rules outrank detected defaults.
- A bare activation with no task stays informational standby in every mode - no
  decision surfaces exist to resolve.

## The Matrix

| Interaction mode      | Routine decisions and phase checkpoints                                     | Essential missing inputs                                           | Separately gated actions                                                  |
|-----------------------|-----------------------------------------------------------------------------|--------------------------------------------------------------------|---------------------------------------------------------------------------|
| Interactive (default) | Show recommendations and ask at material checkpoints.                       | Ask before dependent work.                                         | Seek the required permission.                                             |
| Autonomous            | Choose each evidenced recommendation without asking, explain inline.        | Ask only if there is no safe, usable default.                      | Seek the required permission.                                             |
| Fully autonomous      | Choose each evidenced recommendation without any questions, explain inline. | Skip the blocked step and dependents, continue and report partial. | Skip the unauthorized action and dependents, continue and report partial. |

A material checkpoint is a point where the run changes what it produces - the
gathering plan, the architecture design, the generation write - not every routine
sub-step.

## Recommendation Precedence

Resolve each surface in this order, and record which tier supplied the answer:

1. An explicit user choice.
2. The target's own rules and conventions.
3. Verified source evidence.
4. A documented Forge default.
5. Unresolved.

Never manufacture a recommendation from a missing or failed source, invent domain
facts, or claim a draft skill is complete when a blocked step is essential to its
validity.

## Decision Log

Record every resolved or skipped decision in the run-state ledger with:

- `surface` - the parameter id or checkpoint name.
- `selected` or `skipped` - the value taken, or the skip verdict.
- `evidence` or `default` - which precedence tier supplied it.
- `reason` - one line.
- `mode` - the interaction mode in effect.
- `impact` - what the choice or skip changes downstream.

Report a brief reason inline at each phase and a compact `Decisions:` recap at the
end of the run.

## Verbose Reporting

`verbose` adds, for every decision row: the complete options considered, the evidence
and trade-offs behind the recommendation, why each alternative was not selected, and
the impact of any skipped step.

It never adds a question, changes a selected answer, or changes permissions.

## Permission Boundary

No mode grants permission to access the network, install tools, use credentials,
overwrite existing data, delete files, publish, or commit. Even on a no-question run,
a separately gated action requires its own approval or is skipped.

The Skill Update Check runs normally when network access is already authorized. When
it is not, fully autonomous mode records a `network-check-skipped` decision instead of
fetching or asking, then uses the loaded router.

## Worked Examples

Inline decisions read:

```text
Decisions:
- research-depth -> focused (recommended; two supplied sources cover the requested scope).
- pdf-conversion -> skipped (converter unavailable without approved network access; book-only synthesis blocked).
```

If a PDF is the only source but its converter would require an unapproved install, a
fully autonomous run reports conversion skipped and generation blocked, rather than
emitting an ungrounded "complete" skill. If other independent, already readable
sources exist, continue synthesizing them and label the coverage gap.

`fully autonomous` means zero question surfaces, not unconditional success.
