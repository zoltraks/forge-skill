# Trigger Design

## Purpose

> **Scope:** Writing the routing surface of a generated skill - the description and
> keyword lists that decide activation
> **Key items:** inclusion scope, exclusion scope, near misses, description shape

The frontmatter `description` is the only always-visible text - it decides whether
the skill loads at all. Trigger quality is routing quality.

## Description Shape

A good description carries, in order:

1. What the skill is - one line.
2. What it does - the operation families, concretely.
3. When to use it - the trigger conditions in the user's own words.
4. Maintenance scope - the "work on <name>" boundary.

Stay under 1024 characters. Prefer specific verbs ("converts PDF books into skills")
over capabilities adjectives ("powerful document processor").

Phrase the description as an instruction to the agent - "Use this skill when..."
reads as a routing rule, "This skill does..." reads as documentation.

Describe what the user is trying to achieve, not the skill's internals - the
agent matches against the user's request.

Err on the pushy side: name the contexts where the skill applies, including
requests that need it without naming the domain.

In a crowded skill set, negative constraints earn their characters - an explicit
"do NOT use for X" boundary keeps selection precise.

## Inclusion Criteria

Trigger phrases should match how users actually ask:

- Imperative verbs naming the operation: "create a skill", "audit this repository".
- Object nouns from the domain vocabulary found in the evidence.
- The bare-activation family: "use <name>", "work with <name>", "run <name>".
- The maintenance family: "work on <name>", "improve <name>".

Group keywords by intent in the router's Trigger Keywords section - grouped lists
beat flat dumps for both readability and coverage review.

## Exclusion Criteria

Every generated router names its near misses - requests that look similar but
belong elsewhere:

- A skill that summarizes PDFs should exclude "create a skill from this PDF".
- A document-authoring skill excludes "audit this codebase".
- State exclusions where the boundary is genuinely confusable, not for every
  imaginable non-task.

Near-miss entries belong in `evals/evals.json` too - a regression prompt per
boundary verifies the skill declines correctly.

## Evidence For Triggers

Draw trigger vocabulary from the synthesis, not invention: the terminology the
sources actually use is what users of that domain will type. When evidence is
thin, mark trigger coverage as a gap rather than padding with guesses.

## Test Cases

Design at least: one positive prompt per operation family, one near-miss prompt
per exclusion boundary, and one prompt per interaction mode the skill supports.
These land in the generated `evals/evals.json`.

Description wording is tested like code - `references/evaluation-design.md` defines
the trigger-eval loop: a split query set, repeated runs, and a trigger-rate
threshold.
