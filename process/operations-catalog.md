# Operations Catalog

## Purpose

> **Scope:** Response contract for requests that ask for the skill's complete
> list of operations
> **Key items:** catalog triggers, canonical operations table, inline delivery

This file defines the answer produced when the request asks what operations the
skill performs or assists with.

Follow it when the request says "list all operations", "show all capabilities",
"what operations can this skill perform", "list everything this skill can do",
or an equivalent.

## When This Applies

The request names the skill and asks for the complete list of its operations.

A partial question - "can forge convert a PDF" - is not a catalog request.

Answer it directly instead of reproducing the table.

The catalog is a query surface, not a task - no pipeline phase, housekeeping
stage, or run-state machinery runs.

When the catalog request is the session's first action, the once-per-session
Skill Update Check from `SKILL.md` runs first.

When it follows an activation or another task, the check is not repeated.

## The Catalog

Answer with the operations table below, reproduced inline and re-aligned to
source width when the request's language changes the cell text.

| Family   | Operation          | What it covers                                              |
|----------|--------------------|-------------------------------------------------------------|
| Create   | create a skill     | research a topic and generate a complete skill document set |
| Create   | spec skill         | portable, minimal, spec-conformant package                  |
| Create   | plugin package     | Claude Code plugin or marketplace entry                     |
| Create   | collection         | generate an index plus independently owned member skills    |
| Source   | analyze a source   | convert and survey a document into an evidence report       |
| Source   | convert a source   | local source conversion through an approved converter       |
| Source   | generate from run  | render a skill from recorded analysis or resumed run state  |
| Source   | update with source | propose folding a new source into an existing skill         |
| Layout   | migrate layouts    | adopt into astra, export to spec, package as plugin         |
| Govern   | housekeep          | clean, reorganize, or optimize a skill or collection        |
| Govern   | inventory          | multi-root skill discovery and drift check                  |
| Govern   | heal               | evidence-gated repair of a named external skill             |
| Govern   | validate           | check a skill against the generation contract               |
| Enable   | enablement         | bare-activation standby with version and operations table   |
| Enable   | self-update check  | once-per-session upstream check                             |
| Enable   | operations catalog | this table                                                  |
| Maintain | skill maintenance  | changes and session reviews of this skill repository        |

## Response

Deliver the catalog inline.

Write the response in the language of the request - family and operation names
render in that language while the `Family` column keeps its canonical
grouping.

Close with one line inviting a task request.

## What Does Not Apply

- No pipeline phase, housekeeping stage, or run-state machinery runs - the
  request named a query.
- No rule files beyond the router and this file load. The catalog table is
  canonical and is not rebuilt by rescanning the repository.
- No file is written and no target is surveyed.
