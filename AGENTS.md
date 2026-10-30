# Agent Instructions

## Purpose

> **Scope:** Agent-facing entry point for authoring and maintaining this skill repository.
> **Key items:** governing documents, boundaries, local workspace, validation, improvement.

This repository is the Forge skill, an Agent Skills package that creates new Agent
Skills from research or external sources, optionally generates skill collections,
and governs existing skill projects and collections through housekeeping and
evidence-gated repair.

`SKILL.md` is the runtime router read by agents that use the skill.

This file is the entry point for agents that modify the skill.

## Governing Documents

| Document               | Owns                                                                |
|------------------------|---------------------------------------------------------------------|
| `docs/CONTRIBUTING.md` | Issue reporting, development setup, pull-request rules              |
| `docs/STYLE.md`        | Prose, tables, headings, and encoding for the skill's own documents |
| `docs/MAINTENANCE.md`  | Directory roles, file naming, registration, validation procedures   |
| `docs/VERSIONING.md`   | Version format, bump rules, and release anchoring                   |
| `docs/SECURITY.md`     | Vulnerability reporting and the untrusted-source trust boundary     |
| `docs/README.md`       | Index of the repository-governance documents under `docs/`          |

Keep each rule in its owning document and link to it instead of duplicating it.

## Boundaries

- The skill is a routed instruction set: Markdown content becomes agent instructions,
  so content integrity issues are security issues - follow `docs/SECURITY.md` for them.
- Maintenance-mode work on this repository follows `process/skill-maintenance.md` -
  the generation machinery in `process/forge-workflow.md` does not apply to the
  skill's own files.
- Keep `SKILL.md` lean: it routes and stays below 500 lines.
- Register every new or renamed resource in `SKILL.md` and mirror it in the `README.md`
  tree, per `docs/MAINTENANCE.md`.
- Follow `docs/STYLE.md` for every shipped file: H1 plus Purpose, one sentence per
  paragraph, prose wrapped at 100 characters, tables aligned by source width.
- Never embed example files, paths, or project names supplied with a request - create
  anonymized skill-owned examples instead, per `docs/MAINTENANCE.md`.
- Scripts stay standard-library only, Python 3.10 or newer.
- Keep `evals/evals.json` in sync when a change alters skill behavior.
- Bump `metadata.version` by one patch with every change set that modifies skill
  document contents, per `docs/VERSIONING.md` - a change set is the edits delivered
  together, and the version moves at most once until the set is committed.
- A request that names no concrete operation authorizes analysis and proposals only -
  files in this repository change on an explicit, confirmed instruction.
- Do not claim validation that did not run.
- Never commit automatically - propose a one-sentence commit message without trailers.
  The one exception is a commit completing a user-approved upstream merge, which may be
  made - pushing always runs on a separate request.
- A bare `work on forge-skill` request that names no operation is standby - read this
  file, `SKILL.md`, and `process/skill-activation.md`, confirm readiness, and wait for
  the named operation rather than resuming plans or editing on assumption.

## Local Workspace

Run state, converted source text, research artifacts, and throwaway scripts live in the
gitignored `work/` directory, organized as `work/YYYY-MM/YYYY-MM-DD/`.

Shipped skill files never depend on workspace content and never reference it.

Temporary script copies carry a `.tmp.` infix and are removed after use.

## Validation

Run the skill-maintenance suite before proposing a change:

```
python3 scripts/validate-skill.py .
python3 -m unittest discover -s tests -v
git diff --check
```

Run `python3 scripts/render-templates.py --self-test` to verify the renderer and the
template set still agree.

An editorial Markdown battery applies to every edited owned document where the
host provides one - report it skipped otherwise.

Changes that alter skill behavior also exercise the regression prompts in
`evals/evals.json`.

## Skill Improvement

Structural, naming, registration, or layout changes follow the procedures in
`docs/MAINTENANCE.md` and the intake procedure in `process/skill-maintenance.md`.

A request to improve the skill from this session follows `process/session-review.md`.
