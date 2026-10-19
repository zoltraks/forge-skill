# Session Review

## Purpose

> **Scope:** Procedure for improving the skill from the current session's history
> **Key items:** session gather, findings, approval gate, review modes, anonymization,
> validation

This file defines the session-review path of maintenance mode: the agent reviews what
happened in this conversation, extracts the lessons worth keeping, and lands them in the
rule corpus.

Follow it when the request asks to improve this skill from this session - "improve
forge-skill", "improve the skill from this session", "review the session for lessons".

## Modes

The review accepts the shared review flags named in the request - "improve forge-skill
from this session, autonomously".

- **Autonomous** - `autonomous`, `automatic`, `unattended`, or `non-interactive`. Every
  gate in this procedure resolves to its recommended option without waiting, and the
  completion report carries a `Decisions:` list naming each resolved surface and the
  option taken.
- **Verbose** - `verbose`. Every surface additionally reports the full option list and
  the rationale for the recommended choice, whether the surface was asked or
  auto-resolved.

The flags may stack. Autonomous plus verbose resolves every gate and reports all
options.

Autonomous mode resolves only this procedure's own gates: it never commits, and a
session that yields no findings still reports and stops rather than inventing changes.

The wider interaction modes of `process/decision-modes.md` apply to operation-mode
work, this procedure keeps the shared two-flag review contract the collection expects.

## Procedure

### Gather

Read the session's conversation history, across thread boundaries when a summary split
occurred.

List what failed, surprised, or needed a workaround, and every assumption the session
made - validated or broken.

Verify real state before recording a lesson: re-check files, rerun commands, confirm the
reported behavior - no guessed findings.

### Findings

Map each durable lesson to the rule file or files it belongs in.

A lesson about the generation pipeline goes to `process/forge-workflow.md`, a lesson
about gathering or synthesis goes to the matching `process/research-*.md` file, a
lesson about conversion goes to `process/source-conversion.md`, a lesson about the
generated contract goes to `references/` or `process/skill-template.md`, a lesson about
interaction modes goes to `process/decision-modes.md`, and a lesson about tool behavior
goes to `scripts/`.

Drop lessons already covered by existing rules - the findings list names gaps, not
repetitions.

The anonymization boundary in `AGENTS.md` applies: findings describe the lesson with
skill-owned examples, never with names or paths the session supplied.

### Approval

Report the findings and the proposed changes per rule file.

Ask for approval before editing. Under JSON exchange the gate emits as the
`session-review-approval` `choice` parameter per `process/json-exchange.md`.

The gate offers `Apply` (recommended), `Adjust`, and `Cancel`.

`Adjust` accepts a free-text correction to the findings or the proposal and re-presents
the report.

Under autonomous mode the gate resolves to `Apply` without asking and the resolution is
recorded in the decisions list, per Modes above.

### Apply

On approval, edit the named files per `docs/STYLE.md` and `docs/MAINTENANCE.md`.

Apply the registration contract when the change adds, removes, or renames a resource -
`SKILL.md`, the `README.md` tree, `## Contents` tables, and `evals/evals.json` move
together.

### Validate

Run the maintenance suite from `AGENTS.md` after the edits and report every
check that ran, failed, or was skipped.

## What Does Not Apply

- No generation machinery runs - pipeline phases, template rendering, and conversion
  do not apply to the skill's own files.
- No separate findings log is kept - findings land directly in the rule files they
  correct.
- The session's produced artifacts are not part of the review - the review extracts
  transferable rules, not a report of the work itself.

## Relation To Maintenance Mode

This file is a path inside maintenance mode, not a mode of its own.

`process/skill-maintenance.md` routes to it, and the governing set read happens under
that intake.
