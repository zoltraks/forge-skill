# Skill Maintenance

## Purpose

> **Scope:** Rules for extending, restructuring, and maintaining the forge-skill
> repository itself
> **Key items:** directory roles, file naming, registration contract, addition
> procedures, validation

These rules apply to the skill's own files. Document-production rules live in
`process/` and `references/`, prose style lives in `docs/STYLE.md`, the intake
procedure is `process/skill-maintenance.md`.

## Directory Roles

| Directory     | Role                                                      |
|---------------|-----------------------------------------------------------|
| `process/`    | Pipeline, lifecycle, conversion, research, contract files |
| `references/` | Specifications, conventions, and methodology evidence     |
| `templates/`  | Generation skeletons and the output-path map              |
| `scripts/`    | Mechanical tools: validation, rendering, conversion       |
| `docs/`       | Repository-governance documents for the skill itself      |
| `evals/`      | Behavioral regression prompts                             |
| `tests/`      | Deterministic unit tests and synthetic fixtures           |

Root files govern the repository: `SKILL.md`, `AGENTS.md`, `README.md`,
`CHANGELOG.md`, `LICENSE`, `.gitignore`.

`work/` is gitignored run scratch - run state, converted text, staged output. Its
content never promotes into tracked files without provenance review.

Keep rule files one level deep under their directory. Do not nest subdirectories
inside `process/`, `references/`, `templates/`, or `tests/` beyond the recorded
`tests/fixtures/` container. A directory that must hold subdirectories keeps only
directories at that level - `README.md` is the standard exception - and files and
child directories do not mix without a recorded reason.

## File Naming

- Rule files under `process/` and `references/`: two-word lowercase kebab-case -
  `skill-activation.md`, `source-conversion.md`. Document exceptions for
  recognized identifiers.
- Tools under `scripts/`: `<verb>-<object>.py` - `validate-skill.py`,
  `render-templates.py`.
- Templates under `templates/`: two words plus `.template` suffix -
  `skill-router.template`, `collection-router.template`.
- Governance files: uppercase conventional names - `STYLE.md`, `VERSIONING.md`,
  `MAINTENANCE.md`, `SECURITY.md`, `CONTRIBUTING.md`, `README.md`.

Every new rule file carries an H1, a `## Purpose` section, and content sections,
files over 300 lines add a `## Contents` table.

## Registration Contract

- Register every new or renamed resource in `SKILL.md` under its directory's
  section, with a line saying what it covers and when to load it.
- Mirror every layout change in the `README.md` directory tree.
- Renumber every `## Contents` table affected by line shifts.
- Keep `evals/evals.json` in sync when behavior changes.
- A template change keeps `templates/README.md` and the renderer's map in sync.

## External Examples

Never embed real project names, paths, or identifiers supplied with a request.
Create anonymized skill-owned examples instead - external material may be
unreachable later and real names do not belong in the rule corpus.

## Adding A Procedure

1. Create `process/<two-words>.md` in the house structure.
2. Register it in `SKILL.md` under `process/` and in `process/README.md`.
3. Route to it from the Operations table when it serves a request class.
4. Update the `README.md` tree and renumber affected Contents tables.

## Adding A Reference

1. Create `references/<two-words>.md`.
2. Register it in `SKILL.md` under `references/` and in `references/README.md`
   with its load trigger.
3. Update the `README.md` tree.

## Adding A Template

1. Create `templates/<two-words>.template` with `{{placeholder}}` markers only.
2. Add its output-path row to `templates/README.md` and the machine map the
   renderer reads.
3. Cover it in `tests/` - render it, check leftover placeholders, check output
   path safety.
4. Register in `SKILL.md` under `templates/` and update `README.md`.

## Adding A Tool

1. Create `scripts/<verb>-<object>.py`, standard library only, Python 3.10+.
2. Keep it a self-contained single file.
3. Under the `__main__` guard, reconfigure `sys.stdout`/`sys.stderr` with
   `errors="backslashreplace"`, pass explicit `encoding=`/`errors=` to every
   subprocess text call.
4. Document it in `scripts/README.md` with its exit statuses and safety class -
   read-only, staged-write, or converter.
5. Reference it from `SKILL.md` and the workflow step where it runs.
6. Cover it in `tests/`, including at least one failing fixture.

## Validation After Changes

Run before every proposed change set:

```bash
python3 scripts/validate-skill.py .
python3 -m unittest discover -s tests -v
python3 scripts/render-templates.py --self-test
git diff --check
```

The gate is manual by design: no CI runs these checks, so the maintainer runs the
full suite before each commit. Report every check that ran, failed, or was
skipped - never claim a check that did not run.
