# Housekeeping

## Purpose

> **Scope:** Self-repository upkeep for the forge-skill repository - registration
> reconciliation, coverage checks, workspace hygiene, and validation.
> **Key items:** upstream state, registration reconciliation, eval coverage,
> version check, workspace hygiene, proposal report.

Self-repository housekeeping routine for the forge-skill repository, run on a
`housekeep forge-skill` request or as part of a session review's index
partition.

A request to housekeep an external skill or collection routes to
`process/skill-housekeeping.md` instead - this routine owns the repository's
own files only.

## Procedure

1. Run `scripts/check-update.py` once and report upstream state.
2. Reconcile `SKILL.md` against `process/`, `references/`, `templates/`, `scripts/`,
   `tests/`, `docs/`, and `evals/` - every shipped resource must be registered in `SKILL.md` and
   mirrored in `README.md`.
3. Check `evals/evals.json` covers every operation in `operations-catalog.md`.
4. Verify `metadata.version` moved for shipped changes since the last commit.
5. Clean `work/` entries older than the session, and confirm no shipped file
   references `work/` or names another skill package.
6. Validate: `scripts/validate-skill.py .`, `scripts/render-templates.py
   --self-test`, the tests under `tests/`, and `git diff --check`, plus an
   editorial Markdown battery on edited documents where the host provides one.
7. Report findings as a proposal - housekeeping never commits.

## What Does Not Apply

- Housekeeping never edits on its own authority - the report proposes, the
  requester approves.
- No target-repository maintenance runs here - a document or repository named
  by the task is document-mode work, not this routine.
- Nothing commits, pushes, or deletes - every finding lands in the proposal.
