# Skill Activation

## Purpose

> **Scope:** Enablement procedure for requests that activate the skill without naming a
> task
> **Key items:** bare activation, referent resolution, update check, enablement response,
> standby contract, mode hand-off

This file defines the intake for a request that names the skill but no work.

Follow it when the request is a bare activation phrase - "use forge", "work with
forge", "activate forge", "use this skill" - or an equivalent.

## When This Applies

Resolve the referent of a generic phrase before treating the request as a Forge
activation - "use skill", "work with skill", "use this skill", and "work on this skill"
name no skill by themselves.

A phrase that names Forge - "use forge", "work with forge", "work on
forge-skill" - binds directly.

A generic phrase binds to this skill only when the context identifies it - the
forge-skill repository is the working target, the session already treats Forge as
the skill in play, or no other skill competes for the referent.

When another skill's repository is the working context, or several skills could equally
be meant, the referent is ambiguous - ask which skill the request means and wait,
instead of enabling Forge on assumption.

Under JSON exchange the referent ask emits as the `skill-selection` `choice` parameter
per `process/json-exchange.md`.

A bare activation names the skill and nothing else - no skill to create, no source to
analyze, no collection to generate, and no maintenance request.

An activation may also name a working target - a repository, directory, or document
set - while still naming no operation: "use forge on the docs repository".

Naming a target is not a task, so the request stays in enable mode with the target held
as context for the next request.

A purpose qualifier such as "for skill creation" is not a task either. It names a mode,
not an operation, and the request stays in enable mode.

A request that combines activation with a task is a task request - "use forge,
create a skill for X" enters operation mode directly and this procedure does not
run.

Ambiguity asks are rare - `mode-selection` fires only when the request mixes genuinely
conflicting signals, such as an activation phrase joined to an operation verb whose
object is missing.

A named target without a named operation resolves to standby with the operation
question pending, never to a mode-selection question.

A target whose own agent-facing rules define bare-request behavior confirms the same
answer without any scan.

Under JSON exchange a genuine ambiguity emits as the `mode-selection` `choice`
parameter per `process/json-exchange.md`.

## Procedure

1. Run the once-per-session Skill Update Check from `SKILL.md` - the gate applies in
   every mode.
2. Confirm the router state - the loaded `SKILL.md` is the enabled state, re-read it
   when it may have changed during the session.
3. Answer with the enablement response below, then wait for the next request.

## Enablement Response

Open with one sentence confirming the skill is enabled.

Follow with one sentence describing the skill. It creates new Agent Skills from
research or external sources and optionally generates skill collections - and name the
skill version read from `metadata.version` in the loaded `SKILL.md`.

Follow with a compact operations table - one row per family, columns `Operation` and
`What it covers`, aligned by source width:

| Operation              | What it covers                                              |
|------------------------|-------------------------------------------------------------|
| Create a skill         | Research a topic and generate a complete skill document set |
| Create a collection    | Generate an index plus independently owned member skills    |
| Analyze a source       | Convert and survey a document into an evidence report       |
| Generate from analysis | Render a skill from recorded analysis or resumed run state  |
| Update a skill         | Propose folding a new source into an existing skill         |
| Maintain the skill     | Changes and session reviews of this skill repository        |

Close with a line inviting the task request.

A target-scoped activation answers with a minimal standby instead: one or two lines
confirming the skill is enabled on the named target, then the operation question -
which operation to run on it, with the operation families from the router offered as
a selectable menu rather than a printed capability list.

Under JSON exchange the operation question emits as the `operation-selection`
`choice` parameter per `process/json-exchange.md`.

The standby never scans or surveys the target to infer the intended task - guessing
intent from the repository's state is analysis the request did not ask for.

A bare reply confirms enablement and waits for the next request, or asks what to do.

A target-scoped reply always asks what to do - the operation question is part of the
standby, not an optional addition.

A read-only survey with proposed work belongs in the reply only when the request names
that operation itself - "take a look around" asks for the survey, a purpose qualifier
does not.

A diagnostic, timing, or informational flag folds into the opening sentence -
"enabled in diagnostic mode", "enabled in timing mode", or "enabled in
informational mode" - and adds no intake-state preamble, since a bare activation
has no pending surface to report.

Write the response in the language of the request.

## What Does Not Apply

- No operation classification, parameter resolution, or target discovery runs - the
  request named no task.
- No read or scan of the named target runs. A bare activation does not open the target
  to guess the task.
- No rule files load beyond the router and this file - progressive disclosure stays
  lazy, the next request selects its own rule set.
- A diagnostic, timing, or verbose flag adds `process/json-exchange.md` to the
  loaded set and nothing else - no scan of the target runs and no operation-mode
  files load, and no parameter document emits while no question surface is
  pending.
- An informational flag adds `process/operation-timing.md` to the loaded set and
  nothing else - the standby reply itself emits no timing line.
- A target-scoped activation leaves the `operation-selection` surface pending, so a
  diagnostic or timing flag emits its parameter document for it.
- No file is written. A proposed change waits for a request that names the operation
  and confirms it.

## Relation To The Modes

Enable mode is the standby state. It precedes operation mode and maintenance mode.

A task-bearing request that follows enters operation mode or maintenance mode per the
mode rules in `SKILL.md`, without repeating the update check this session.
