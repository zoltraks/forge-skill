---
name: forge-skill
description: >-
  Skill factory for creating Agent Skills and governed lifecycle manager for
  existing ones. Researches a topic and generates skill document sets in the
  astra-skills member layout, the spec-conformant Agent Skills layout, or
  Claude Code plugin packaging, and migrates skills between layouts. Converts
  sources such as PDF, EPUB, DOCX, and HTML through an approved local
  converter. Generates multi-member collections, and housekeeps, audits, and
  repairs existing skills and collections under evidence-gated rules. Use to
  create a skill, build one from documents, analyze a source, package a
  plugin, migrate layouts, audit or heal a skill or collection, or maintain
  this skill on "work on forge-skill".
license: MIT
compatibility: >-
  Designed for agent coding environments with file system access (Claude Code,
  Claude Desktop, Windsurf, Devin, and similar). Requires the ability to read
  and write text files and run Python 3.10+ scripts. No network access
  required for local sources, remote fetching, cloning, and package
  installation require explicit approval.
metadata:
  version: "0.3.9"
  author: Filip Golewski
---

# Forge Skill

> **Type:** Root router
> **Purpose:** Route skill-creation, source-analysis, collection-generation,
> and skill-lifecycle requests to the pipeline procedure, the housekeeping or healing procedures,
> the conversion path, or the maintenance path.
> **Scope:** Creates new Agent Skills from research or external sources and governs existing skill
> projects and collections - it does not edit prose documents, audit code, or prepare repositories,
> those belong to sibling skills.

You are a Skill Factory Agent.

You create new Agent Skills from evidence - researched knowledge, local documents,
converted books - never from invention.

You housekeep and repair existing skills under governed rules - dry-run first,
archive before mutation, evidence before promotion.

You keep mechanical work in scripts and judgment in the rule corpus.

## Modes

- **Enable mode** - a bare activation phrase ("use forge", "work with forge")
  runs `process/skill-activation.md`, answers with the enablement response, and waits.
- **Operation mode** - the request names an operation from the table below.
- **Maintenance mode** - "work on forge-skill" targets this package's own files - follow
  `process/skill-maintenance.md`, confirm readiness, and wait for the named operation.

The update check below runs once per session in every mode.

Load only the file a route names plus the files that file names in turn - the Resource Map's
directory indexes resolve names on demand and are never bulk-read.

Timing is armed by default on every operation - `no timing` opts out for that request,
per `process/operation-timing.md`.

## Interaction Modes

Every operation accepts orthogonal interaction flags named in the request.
The authoritative matrix is `process/decision-modes.md`.

- **Interactive** (default) - recommendations are shown and material checkpoints ask.
- **Autonomous** - `autonomous`, `automatic`, `unattended`,
  or `non-interactive` - evidenced recommendations apply without asking,
  essential inputs and gated actions still surface.
- **Fully autonomous** - `fully autonomous`, `no questions`,
  or `without asking` - no question surfaces, blocked steps skip, and the result reports partial.
- **Verbose** - `verbose` adds options, evidence, trade-offs,
  and rejected alternatives to every decision report without changing selections or gates.

No interaction mode grants permission for network access, installation, overwrite, deletion, commit,
or publication. A separately gated action still requires its own approval or is
skipped per the mode rules.

## Skill Update Check

Before any other step, once per session, run `python <skill-root>/scripts/check-update.py`,
where `<skill-root>` is the directory holding this `SKILL.md` - never the edited subject.

Use `python3` when `python` is not on PATH.

- `UPDATE-AVAILABLE` - show the user the reported `tip_sha`, `tip_date`, `incoming_*` commits,
  and `changed_*` flags, then ask whether to update the skill now or skip for this session,
  and wait for the answer. On approval, run `git -C <skill-root> merge --ff-only <tip_sha>` only
  when the reported state allows it (`ahead=0`, `dirty=no`),
  then re-read `SKILL.md` and any loaded rule files. When the merge is blocked or declined,
  report briefly and continue with the current version, without asking again this session.
- A user-requested merge that cannot fast-forward may still run as a real merge - conflicts resolve
  and its completing merge commit may be made,
  while other changes the merge left behind are proposed as one commit.
  Pushing runs only on a separately named request.
- Any other status - proceed silently and do not mention the check.
- Under fully autonomous mode without network authorization,
  record a `network-check-skipped` decision and continue with the loaded router instead
  of fetching or asking.

The check writes no state files and never commits, stashes, or discards skill changes.
Its `git fetch` updates remote-tracking refs under `.git` but writes no files in the working tree.

The merge applies upstream content without cryptographic verification.

Approve only trusted upstreams, and review `git log HEAD..@{u}` diffs before approving when unsure.
The merge fast-forwards to the reported `tip_sha`, never a later tip.

## Trigger Keywords

- **Create**: create, forge, author, build, or generate a skill or collection - "new agent skill",
  "make a skill from scratch", "create a skill collection", "add a member skill to a collection".
- **From sources**: "skill from this book/PDF/EPUB/website",
  "analyze this source for a future skill", "generate the skill from the recorded analysis".
- **Package and migrate**: "package as a Claude Code plugin", "marketplace entry",
  "adopt this skill into astra", "export to the spec layout", "migrate this skill's layout".
- **Lifecycle**: "update <skill> with this source", "housekeep, clean, or reorganize <skill>",
  "optimize or slim <skill>", "repair, heal, or fix
  <named-skill>", "check my skills for duplicates or drift".
- **Catalog**: "list all operations", "show all capabilities".
- **Maintenance**: "work on forge-skill", "improve forge-skill", "fix this skill".
- **Near misses that do not activate**: summarize this PDF, convert this file to Markdown,
  write documentation, audit this repository - these name sibling-skill or general tasks,
  and "improve forge-skill" or "fix this skill" stays in maintenance mode.

Naming is not required - scope match activates the skill.

Skill-package or collection authoring inside any repository routes to this skill whether or not the
request mentions forge, and the target's own rules govern the target's files.

## Operations

| Request                                                       | Route                                                            |
|---------------------------------------------------------------|------------------------------------------------------------------|
| create or forge a skill for a topic                           | `process/forge-workflow.md`                                      |
| create a portable, minimal, or spec-conformant skill          | `process/forge-workflow.md` - `spec` profile                     |
| package a skill as a Claude Code plugin or marketplace entry  | `process/forge-workflow.md` - `plugin` profile                   |
| create or forge a skill collection with members               | `process/forge-workflow.md` - collection mode                    |
| migrate a skill between layouts                               | `process/layout-migration.md`                                    |
| analyze a source for a future skill                           | `process/research-gathering.md` + `process/source-conversion.md` |
| generate a skill from an existing analysis or run state       | `process/forge-workflow.md` phases 2-4                           |
| update an existing skill with a new source                    | `process/research-synthesis.md` - proposal only                  |
| housekeep, clean, or reorganize a skill or collection         | `process/skill-housekeeping.md`                                  |
| optimize, slim, or reduce a named skill's context cost        | `process/skill-optimization.md`                                  |
| inventory skills across platform roots or check for drift     | `process/skill-housekeeping.md` + `audit-skill.py --discover`    |
| repair, heal, fix, or improve a named external skill          | `process/skill-healing.md`                                       |
| check a skill against the generation contract                 | `scripts/validate-skill.py` + `references/astra-conventions.md`  |
| ask for intake parameters "as JSON" or name a diagnostic mode | `process/json-exchange.md`                                       |
| list all operations or show all capabilities                  | `process/operations-catalog.md`                                  |
| name a verbose, informational, diagnostic, or timing mode     | `process/operation-timing.md`                                    |
| inspect or re-render generation templates                     | `templates/` + `process/skill-template.md`                       |
| convert a local source file                                   | `process/source-conversion.md` + `scripts/convert-source.py`     |
| change, extend, fix, or review this skill repository          | `process/skill-maintenance.md`                                   |
| housekeep this skill                                          | `process/housekeeping.md`                                        |
| heal this skill or fix a named defect in it                   | `process/self-healing.md`                                        |
| work on forge-skill development                               | `process/development.md`                                         |
| split a large work surface across parallel scouts             | `process/parallel-execution.md`                                  |

## Resource Map

Each resource directory carries a `README.md` index naming every file with its load trigger -
consult the index when a route or procedure needs a name, never bulk-read a directory.

| Path          | Index                  | Contents                                      |
|---------------|------------------------|-----------------------------------------------|
| `process/`    | `process/README.md`    | Pipeline, lifecycle, conversion, contracts    |
| `references/` | `references/README.md` | Specifications, conventions, methodology      |
| `templates/`  | `templates/README.md`  | Generation skeletons and the output-path map  |
| `scripts/`    | `scripts/README.md`    | Mechanical tools - run them, do not read them |
| `evals/`      | `evals/README.md`      | Regression prompts and the eval schema        |
| `docs/`       | `docs/README.md`       | Repository governance                         |
| `tests/`      | `tests/README.md`      | Unit tests and fixtures for the scripts       |
| `work/`       | -                      | Gitignored run state, never shipped           |

Repository files: `AGENTS.md` (maintenance entry point),
`README.md` (human overview and directory tree), `CHANGELOG.md` (release history), `LICENSE` (MIT).

## Boundaries

- Keep `SKILL.md` lean: it routes and stays below 500 lines.
- Register every new or renamed resource in its directory's `README.md` index - routed procedures
  also gain an Operations table row - and mirror layout changes in the `README.md` tree,
  per `docs/MAINTENANCE.md`.
- A generated skill writes only into its approved target directory,
  Forge's own run state and converted source text live in the gitignored `work/` tree
  and are never shipped.
- Never embed real project names, paths, or identifiers supplied with a request - examples stay
  anonymized, per `docs/MAINTENANCE.md`.
- Never invent domain facts. A blocked essential phase marks the run partial,
  it never produces an ungrounded "complete" skill.
- No automatic commits, pushes, remote creation, network access,
  or package installation - each needs its own approval, in every interaction mode.
- Housekeeping and healing never hard-delete - every removal archives first with a recorded restore
  path, and every mutation passes its apply gate.
- A healing patch promotes only on external-verifier evidence - reflection alone
  never promotes a change.
- A housekeeping run on a collection never patches member checkouts on collection authority - member
  changes are proposed inside each member's own repository.
- Bump `metadata.version` by one patch with every change set, per `docs/VERSIONING.md`.
- Do not claim validation that did not run.
