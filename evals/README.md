# Evals

## Purpose

> **Scope:** Behavioral regression prompts for forge-skill
> **Key items:** schema, coverage, execution honesty

`evals.json` holds prompts exercised after changes that alter skill behavior -
routing, gates, interaction modes.

## Schema

```json
{ "skill_name": "forge-skill", "evals": [ { "id": 1, "prompt": "...",
  "expected_output": "...", "files": [], "expectations": ["..."] } ] }
```

`skill_name` must match the `SKILL.md` frontmatter `name`. Each eval carries a
unique integer `id`, a `prompt`, an `expected_output` description, and an
`expectations` list of observable checks.

## Coverage

The suite covers: bare activation, single-skill creation, collection creation,
analyze-only, near-miss routing, each interaction mode (`autonomous`,
`fully autonomous`, `verbose` stacked), resume, update-skill, JSON exchange, and
permission boundaries.

## Execution

Walk prompts manually or through the environment's harness when one exists and
is approved. Report which prompts ran and which were skipped - a prompt that did
not run is recorded as skipped, never as passed.
