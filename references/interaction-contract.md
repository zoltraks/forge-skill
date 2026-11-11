# Interaction Contract

## Purpose

> **Scope:** The question-surface contract a skill teaches its agent - detection signals for audits
> and per-layout repair shapes for healing
> **Key items:** menu shape, paging, cancel class, multi-answer exclusivity, proceed
> variant, resume, JSON parity

This file is the canonical definition of how a skill instructs its agent to ask the user for
confirmation or selection.

The housekeeping and healing procedures load it when an audit or repair reaches a
question-surface finding.

## The Contract

Interactive intake is the default - a request may name a quieter mode,
but absent such a name the agent asks.

Every material confirmation or selection emits as an option question,
never as a prose-only proceed request and never as a silent apply.

**Menu shape**

- One question carries at most four selectable entries.
- The last entry is usually a cancel-class option - `Cancel`, `Pause`, `Skip`, `None`, `Break`,
  `Stop` - which means no answer was given and the operation pauses for the next user prompt.
- A `Proceed` entry may replace the cancel entry where skipping is meaningful - it accepts every
  recommendation and answers this and all remaining questions at once.
- Questions are single-answer or multi-answer - the surface states which it is.

**Paging**

A decision carrying five or more candidates splits into sequential questions.

Non-final pages end with a `Next` continuation entry, the final page carries the cancel-class entry,
and a page emits only when `Next` was actually selected - at every point the user may cancel and the
agent sends nothing.

A five-option decision over `A`, `B`, `C`, `D`, `E` pages as:

- Question one: `A`, `B`, `C`, `Next`.
- Question two, shown only after `Next` was selected: `D`, `E`, `Cancel`.

**Multi-answer exclusivity**

A no-answer entry never mixes with content entries.

A selection combining `None` with `A` or `B` conflicts - the agent warns and repeats the question
rather than resolving the mix itself.

A cancel-class selection ends the questionnaire immediately.

**Resume**

A canceled questionnaire repeats on a `repeat` call - the agent re-emits the last question and
continues the questionnaire and the task it was working on.

**JSON parity**

A skill whose intake runs a JSON parameter exchange carries the same rules in both directions -
emitted menus stay letter-keyed and bounded, the cancel entry is last and never the default,
returned answers that mix a no-answer entry with content entries re-emit or warn the same way,
and a returned document is accepted on any surface per the skill's own exchange contract.

## Detection

Classify the target's corpus for question-surface coverage.

- **Present** - a recorded contract names the menu shape, the cancel class,
  multi-answer exclusivity, and resume - astra-layout members normally carry it inside their
  interaction-mode and JSON-exchange surfaces.
- **Partial** - questions are asked but one or more rules are unrecorded - the gap names each
  missing rule, never the whole contract.
- **Absent** - no question-surface instruction exists anywhere in the corpus.

A skill that never asks questions - a purely mechanical generator,
a validator wrapper - has no surface to cover and reports `FALSE_POSITIVE`.

## Repair Shapes

The repair inserts the smallest compatible contract in the target's own document shape.

| Target layout  | Repair shape                                                                                            |
|----------------|---------------------------------------------------------------------------------------------------------|
| Astra member   | Extend the member-owned sections of its interaction-mode and JSON-exchange surfaces, skeleton untouched |
| Spec skill     | A compact question-surface section in `SKILL.md` or the skill's own rules file                          |
| Plugin package | The same compact section in the package's instruction file                                              |
| Foreign        | Report the gap only - no mutation proposal                                                              |

The repair text keeps the member-owned vocabulary the target already uses - a target calling its
cancel entry `Skip` keeps `Skip`, it is not rewritten to `Cancel`.

## Confidence And Gates

Detection confidence follows `references/skill-hygiene.md`.

- `HIGH` - no question-surface instruction found and the skill demonstrably asks questions.
- `MEDIUM` - a partial contract, or presence unclear without running the skill.
- `FALSE_POSITIVE` - the contract is present, recorded variance covers the difference,
  or the skill has no question surfaces.

Every repair is behavior-touching - it changes what the skill's agent is instructed to do - so it
gates on human approval with the replay evidence the healing procedure requires.
