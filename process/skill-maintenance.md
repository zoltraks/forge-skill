# Skill Maintenance Mode

## Purpose

> **Scope:** Procedure for requests that target the forge-skill repository itself
> **Key items:** mode distinction, governing set, registration contract, validation gate

This file defines the intake and execution rules for changes to the skill's own files.

Follow it when the request asks to adjust, extend, fix, or review the skill repository -
`SKILL.md`, the rule corpus, scripts, evals, templates, or the repository documents.

## Mode Distinction

Forge runs in three modes:

- **Enable mode** - the request activates the skill without naming a task. Follow
  `process/skill-activation.md`.
- **Operation mode** - the request names a generation or analysis operation. Follow
  the router in `SKILL.md` and `process/forge-workflow.md`.
- **Maintenance mode** - the request targets this repository's own files. Follow this
  file.

A bare activation request has no target and takes enable mode.

For every other request the target decides the mode, not the trigger phrase.

"Work on forge-skill" phrasing signals the start of adjustment, extension, or fixing
of the skill's documents. Expect the following requests in the same session to stay in
this mode.

A request to create or analyze something outside this repository follows the
Operations table through operation mode instead.

A generic maintenance phrase - "work on this skill", "adjust the skill" with no named
target - resolves to this repository only when the context identifies it, per the
referent rule in `process/skill-activation.md`.

When the target is ambiguous, ask which mode applies - under JSON exchange the question
emits as the `mode-selection` `choice` parameter per `process/json-exchange.md`.

A maintenance request that names a direction routes directly - a skill change continues
under this file, and a request to improve the skill from the current session follows
`process/session-review.md`.

A mode flag named in the request - `autonomous`, `automatic`, `unattended`,
`non-interactive`, `fully autonomous`, or `verbose` - travels with the direction and
modifies that routine's gates per the Modes section of the target procedure file.

## Governing Set

Read the smallest useful set before editing:

| File                              | When to read                                          |
|-----------------------------------|-------------------------------------------------------|
| `AGENTS.md`                       | Always - it is the maintenance entry point            |
| `docs/MAINTENANCE.md`             | Directory roles, naming, registration contract        |
| `docs/STYLE.md`                   | Before writing or editing any owned document          |
| `docs/VERSIONING.md`              | Before the change set lands - the bump rule           |
| `templates/README.md`             | When the change touches `templates/` or the renderer  |
| `references/astra-conventions.md` | When the change touches generated-skill compatibility |

## Execution

1. Read the governing set above.
2. Make the change per `docs/STYLE.md` and `docs/MAINTENANCE.md`.
3. Register every new or renamed resource in `SKILL.md` and mirror it in `README.md`,
   per the registration contract.
4. Renumber every `## Contents` table affected by line shifts.
5. Keep `evals/evals.json` in sync when the change alters skill behavior.
6. When a template changes, check whether Forge's own corresponding file stays the
   reference instance of the same contract, and keep `templates/README.md` and the
   renderer map in sync.
7. Bump `metadata.version` by one patch for the change set, per `docs/VERSIONING.md`.

## Validation Gate

Run the maintenance suite before reporting done, per `AGENTS.md`:

```
python3 scripts/validate-skill.py .
python3 -m unittest discover -s tests -v
python3 scripts/render-templates.py --self-test
git diff --check
```

Do not claim validation that did not run. Report what passed and what was skipped.

Never commit automatically - propose a one-sentence commit message per `AGENTS.md`.
