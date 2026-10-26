# Instruction Patterns

## Purpose

> **Scope:** How generated skill content is written - process-driven design,
> calibrated control, and reusable instruction patterns
> **Key items:** procedures over declarations, specificity to fragility,
> defaults not menus, pattern catalog, skill granularity

A generated skill teaches the agent how to approach a class of problems, not
what to produce for one instance.

Load this file in phase 2 when designing a generated skill's router and
procedures - it is the quality bar the rule corpus is written against.

## Procedures Over Declarations

Write the exact sequence of operational steps, not vague behavioral traits -
"run `scripts/validate.py`, fix what it reports, re-run until clean" beats
"ensure quality".

Describe a reusable method, not a specific answer - a procedure that names how
to find the right table generalizes, a baked-in query does not.

Concrete output templates, hard constraints, and tool-specific steps are
exempt - those are legitimately specific.

## Specificity To Fragility

Match prescriptiveness to how much variation the task tolerates:

- Fragile sequences get exact commands and "do not modify" boundaries -
  migrations, state changes, irreversible writes.
- Judgment work gets freedom plus the reason why - an agent that understands
  the purpose makes better context-dependent calls than one following "ALWAYS /
  NEVER" rules it cannot apply.

A generated skill mixes both - calibrate each section independently.

## Defaults Not Menus

Pick one default tool or approach and mention alternatives briefly as escape
hatches - a row of equal options forces the agent to re-derive a decision the
skill should have made.

When evidence supports no default, say so and give the selection criterion -
never present a menu that hides a known preference.

## Pattern Catalog

Apply the patterns the domain's procedures need - not all of them:

| Pattern               | Use when                                                                                                             |
|-----------------------|----------------------------------------------------------------------------------------------------------------------|
| Gotchas section       | Environment facts defy reasonable assumptions - keep them in `SKILL.md` where they are read before the mistake       |
| Output template       | The skill produces a fixed-format artifact - a literal template beats prose description                              |
| Checklist             | Multi-step workflows with dependencies or gates - progress is tracked explicitly                                     |
| Validation loop       | A script or checklist can verify the work - do, validate, fix, repeat until clean                                    |
| Plan-validate-execute | Batch or destructive operations - intermediate plan artifact validated against a source of truth before execution    |
| Operations catalog    | Broad operation surfaces - a dedicated file answers list-all-operations requests with the canonical operations table |
| Conditional branch    | The process forks on an evaluated condition - triage, classification                                                 |
| Loop                  | A step repeats until a condition holds - research-until-confident                                                    |
| Parallel              | Independent sub-tasks whose outputs combine - speed with a merge step                                                |

## Skill Granularity

Scope one skill to one coherent unit of work - a skill that also covers a
neighboring domain triggers imprecisely, and a skill split too fine forces
several loads for one task.

A task should typically need one to three skills - beyond that, conflicting
instructions and load failures cost more than the split gains.

Distinguish capability skills (compensating for what the model cannot do
reliably - they deprecate as models improve) from preference skills (encoding
workflows and institutional knowledge - durable value). Ground generation in
the durable kind.

In a crowded skill set, namespace names by domain and put negative constraints
in the description ("do NOT use for X") so selection stays precise.

## Context Economy

Write only what the agent would get wrong without it - omit explanations of
what a format or concept is, the agent already knows.

Moderate detail beats exhaustive coverage - instructions that do not apply to
the current task still consume attention and can send the agent down wrong
paths.

Ungated resource files are the largest token sink - everything not needed on
every invocation moves to `references/` or `assets/` with an explicit load
trigger.
