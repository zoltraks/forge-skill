# Development Mode

## Purpose

> **Scope:** Standby-for-specification mode for developing this skill.
> **Key items:** trigger, start-up check, readiness report, specification,
> boundaries.

This file is the contract for a development request aimed at forge-skill.

A development request names the mode but no change yet - the change arrives
described once the mode has reported readiness.

## When This Applies

The request aims at this skill and names development - "work on forge-skill
development", "develop forge-skill", "development mode", or an equivalent.

A bare `work on forge-skill` names no operation and stays the plain standby of
`AGENTS.md` - development mode is the named operation, never the default
reading.

## Procedure

1. Run the once-per-session `scripts/check-update.py` per `SKILL.md` - a skill
   whose check cannot fast-forward is reported, never blocking the rest.
2. Report readiness - repository state, version, and any uncommitted in-flight
   work the tree carries.
3. Wait for the described change.

## The Specification

The description the mode waits for names what to change or adjust - a rule, a
procedure, a script, a type file, a registration.

The target is this repository's own files, edited under `docs/MAINTENANCE.md`
and `docs/STYLE.md` through `process/skill-maintenance.md`.

## What Does Not Apply

- The mode never edits on assumption - standby ends at a described change, not
  before.
- Session review stays a separate operation - development mode delivers a
  described change, while "improve forge-skill" gathers lessons.
- Timing follows `process/operation-timing.md` - the start-up check is the
  operation the readiness report's closing line times.
