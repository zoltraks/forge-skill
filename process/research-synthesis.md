# Research Synthesis

## Purpose

> **Scope:** Distilling extracted evidence into an actionable skill design
> **Key items:** candidates, provenance, confidence, conflicts, gaps, the rule map

This file defines how gathered evidence becomes the architecture input of phase 2 in
`process/forge-workflow.md`.

Synthesis is agent reasoning - no script or regex extracts meaning. Scripts count
and correlate, the agent interprets.

## Candidates

Every candidate rule keeps, in `evidence.md` or the synthesis document:

- A one-line paraphrase - the distilled claim, not a copied passage.
- Source id and location.
- Supporting or contradicting evidence from other sources.
- Status: `confirmed`, `likely`, or `uncertain`.

`confirmed` means independent sources genuinely corroborate the same claim, or one
authoritative source states it directly. Multiple citations of one original work are
one source, not corroboration.

## Cross-Source Patterns

Look for:

- Recurring themes across documents - the candidates worth promoting.
- Implicit conventions visible in examples rather than stated rules.
- Terminology agreement and divergence - naming fidelity feeds trigger design.
- Contradictions - record both positions with their sources, resolve explicitly
  with a stated reason or leave a marked gap. Never pick silently.

## The Rule Map

The synthesis document ends in a rule map - the architecture phase's input:

| Candidate | Status   | Lands in                                        |
|-----------|----------|-------------------------------------------------|
| <rule>    | <status> | router, a process file, a reference, or dropped |

Promote only actionable, evidenced rules into the generated skill's resources:

- Router material: what the skill does, when it fires, when it must not.
- `process/` material: deterministic procedures with ordered steps.
- `references/` material: domain knowledge the procedures consult.
- Dropped: everything below the evidence bar, with a one-line reason.

A blank rule never becomes generic best-practice filler. A domain the evidence does
not cover stays a marked gap.

## Confidence

No fixed numeric formula assigns an overall confidence to a generated skill. Each
candidate keeps its own status, and the architecture design reports the confirmed /
likely / uncertain mix so the user sees the evidence shape.

## Gaps

Every uncovered essential area is a marked gap - `TBD` or `NOT SPECIFIED` in the
generated documents, never invented content. A skill shipped over gaps says where
they are.

## Update-Skill Proposals

The update operation uses this file's machinery read-only: extract the new source's
candidates, map them against the existing skill's sections, and deliver a proposed
fold-in - which files gain what and why. Automatic rewriting of an existing skill is
deferred, the proposal is the deliverable.
