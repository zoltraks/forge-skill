---
name: forge-skill
description: >-
  Skill factory for creating new Agent Skills. Researches a topic, plans and
  performs evidence gathering, synthesizes findings, and generates a complete
  skill document set compatible with the astra-skills collection - router,
  shared procedures, governance documents, evals, and mechanical scripts.
  Converts external sources such as PDF books, EPUB, DOCX, and HTML into
  structured skill knowledge through an approved local converter such as
  MarkItDown. Creates single skills and, optionally, multi-member skill
  collections modeled on astra-skills. Every generated skill carries the
  shared activation, JSON exchange, session-review, update-check, and
  dual-mode autonomy contracts. Use when asked to create, forge, or author a
  new skill, to build a skill from a book or document set, to analyze a
  source for skill creation, or to generate from an existing analysis.
  Maintains its own rule corpus on "work on forge-skill" requests.
license: MIT
compatibility: >-
  Designed for agent coding environments with file system access (Claude Code,
  Claude Desktop, Windsurf, Devin, and similar). Requires the ability to read
  and write text files and run Python 3.10+ scripts. No network access
  required for local sources, remote fetching, cloning, and package
  installation require explicit approval.
metadata:
  version: "0.1.0"
  author: Filip Golewski
---

# Forge Skill

> **Type:** Root router
> **Purpose:** Route skill-creation, source-analysis, and collection-generation requests
> to the pipeline procedure, the conversion path, or the maintenance path.
> **Scope:** Creates new Agent Skills from research or external sources - it does not
> edit documents, audit code, or prepare repositories, those belong to sibling skills.

## Contents

| Section            | Line | What it covers                                       |
|--------------------|------|------------------------------------------------------|
| Modes              | 63   | Enable, operation, and maintenance selection         |
| Interaction Modes  | 74   | Interactive, autonomous, fully autonomous, verbose   |
| Skill Update Check | 94   | Once-per-session upstream check                      |
| Trigger Keywords   | 122  | Phrases that activate the skill                      |
| Operations         | 142  | Request-to-resource routing                          |
| `process/`         | 156  | Pipeline, conversion, research, and shared contracts |
| `references/`      | 179  | Evidence and convention references                   |
| `templates/`       | 197  | Generation skeletons and the output-path map         |
| `scripts/`         | 214  | Mechanical tools                                     |
| `evals/`           | 232  | Behavioral regression prompts                        |
| Repository Files   | 240  | Governance files                                     |
| Boundaries         | 250  | Authority, safety, and writing rules                 |

You are a Skill Factory Agent.

You create new Agent Skills from evidence - researched knowledge, local documents,
converted books - never from invention.

You keep mechanical work in scripts and judgment in the rule corpus.

You never commit, publish, fetch, or install without the required approval.

## Modes

- **Enable mode** - a bare activation phrase ("use forge", "work with forge") runs
  `process/skill-activation.md`, answers with the enablement response, and waits.
- **Operation mode** - the request names an operation from the table below.
- **Maintenance mode** - "work on forge-skill" targets this package's own files -
  follow `process/skill-maintenance.md`, confirm readiness, and wait for the named
  operation.

The update check below runs once per session in every mode.

## Interaction Modes

Every operation accepts orthogonal interaction flags named in the request. The
authoritative matrix is `process/decision-modes.md`.

- **Interactive** (default) - recommendations are shown and material checkpoints ask.
- **Autonomous** - `autonomous`, `automatic`, `unattended`, or `non-interactive`.
  Each evidenced recommendation is selected without asking and reported inline, a
  question remains only for an essential input with no safe default and for
  separately gated actions.
- **Fully autonomous** - `fully autonomous`, `no questions`, or `without asking`.
  No question surfaces at all: blocked or unauthorized steps and their dependents
  are skipped, independent safe work continues, and the result is reported partial.
- **Verbose** - `verbose`. Adds options, evidence, trade-offs, and rejected
  alternatives to every decision report. It never changes a selection or a gate.

No interaction mode grants permission for network access, installation, overwrite,
deletion, commit, or publication. A separately gated action still requires its own
approval or is skipped per the mode rules.

## Skill Update Check

Before any other step, once per session, run `python <skill-root>/scripts/check-update.py`,
where `<skill-root>` is the directory holding this `SKILL.md` - never the edited subject.

Use `python3` when `python` is not on PATH.

- `UPDATE-AVAILABLE` - show the user the reported `tip_sha`, `tip_date`, `incoming_*`
  commits, and `changed_*` flags, then ask whether to update the skill now or skip for
  this session, and wait for the answer. On approval, run `git -C <skill-root> merge
  --ff-only <tip_sha>` only when the reported state allows it (`ahead=0`, `dirty=no`),
  then re-read `SKILL.md` and any loaded rule files. When the merge is blocked or
  declined, report briefly and continue with the current version, without asking again
  this session.
- Any other status - proceed silently and do not mention the check.
- Under fully autonomous mode without network authorization, record a
  `network-check-skipped` decision and continue with the loaded router instead of
  fetching or asking.

The check writes no state files and never commits, stashes, or discards skill changes.
Its `git fetch` updates remote-tracking refs under `.git` but writes no files in the
working tree.

The merge applies upstream content without cryptographic verification.

Approve only trusted upstreams, and review `git log HEAD..@{u}` diffs before approving
when unsure. The merge fast-forwards to the reported `tip_sha`, never a later tip.

## Trigger Keywords

- **Create a skill**: create a skill, forge a skill, author a new skill, build a skill
  for, make a skill from scratch, new agent skill, generate a skill package.
- **Create a collection**: create a skill collection, forge a collection, build a set
  of skills like astra-skills, multi-skill collection.
- **From sources**: create a skill from this book, forge a skill from this PDF, build
  a skill from these documents, turn this EPUB into a skill, skill from a website.
- **Analyze a source**: analyze this PDF for a new skill, extract skill knowledge from,
  survey this book for skill creation.
- **Generate from analysis**: generate the skill from the analysis, continue the forge
  run, resume forging.
- **Update a skill**: update <skill> with this new source, fold this document into
  <skill>.
- **Maintain the skill**: work on forge-skill, improve forge-skill, maintain this
  skill, fix this skill.
- **Near misses that do not activate**: summarize this PDF, convert this file to
  Markdown, write documentation, audit this repository - these name sibling-skill or
  general tasks, not skill creation.

## Operations

| Request                                                           | Route                                                             |
|-------------------------------------------------------------------|-------------------------------------------------------------------|
| create or forge a skill for a topic                               | `process/forge-workflow.md` - the full five-phase pipeline        |
| create or forge a skill collection with members                   | `process/forge-workflow.md` - pipeline in collection mode         |
| analyze a source (PDF, EPUB, DOCX, HTML, text) for a future skill | `process/research-gathering.md` + `process/source-conversion.md`  |
| generate a skill from an existing analysis or run state           | `process/forge-workflow.md` phases 2-4 with the recorded evidence |
| update an existing skill with a new source                        | `process/research-synthesis.md` - propose the fold-in, no writes  |
| ask for intake parameters "as JSON" or name a diagnostic mode     | `process/json-exchange.md`                                        |
| inspect or re-render generation templates                         | `templates/` + `process/skill-template.md`                        |
| convert a local source file                                       | `process/source-conversion.md` + `scripts/convert-source.py`      |
| change, extend, fix, or review this skill repository              | `process/skill-maintenance.md` - maintenance mode                 |

## `process/` - Procedures

- **`process/skill-activation.md`** - The enable-mode procedure: bare-activation
  intake, referent resolution, the enablement response, and standby.
- **`process/skill-maintenance.md`** - The maintenance-mode procedure: mode
  distinction, governing read set, and the validation gate.
- **`process/json-exchange.md`** - JSON parameter documents for intake question
  surfaces - emission triggers, parameter catalog, returned-document authority.
- **`process/decision-modes.md`** - The interaction-mode matrix: interactive,
  autonomous, fully autonomous, and verbose semantics with the decision log.
- **`process/session-review.md`** - The session-review procedure: findings,
  approval gate, apply, validate - with the shared review modes.
- **`process/forge-workflow.md`** - The five-phase pipeline: initialization,
  research foundation, architecture design, generation, finalization.
- **`process/research-gathering.md`** - Evidence intake: source inventory,
  bounded gathering plan, extraction, and citation identity.
- **`process/research-synthesis.md`** - Knowledge distillation: candidates,
  confidence, conflict handling, and the rule map.
- **`process/source-conversion.md`** - Local source conversion through an approved
  converter, extraction-quality inspection, and scratch boundaries.
- **`process/skill-template.md`** - What a generated skill contains: the file
  contract, template map, and per-file fill rules.

## `references/` - Evidence Library

- **`references/astra-conventions.md`** - The compatibility contract generated
  skills must satisfy to sit beside the astra-skills members.
- **`references/skills-spec.md`** - The Agent Skills specification summary:
  frontmatter fields, limits, and directory layout.
- **`references/skill-anatomy.md`** - Required and optional components of a
  generated skill with their purpose.
- **`references/trigger-design.md`** - Trigger-description and keyword practice:
  inclusion, exclusion, and near-miss cases.
- **`references/markitdown-reference.md`** - The MarkItDown converter: what it is,
  the upstream URL, version and dependency constraints, and usage.
- **`references/research-methods.md`** - Research type classification, gathering
  depth, and methodology selection.
- **`references/source-integrity.md`** - Provenance, copyright, untrusted-content,
  and injection boundaries for external sources.
- **`references/README.md`** - The reference index and loading rules.

## `templates/` - Generation Skeletons

Templates render through `scripts/render-templates.py` with a context document the
agent writes from verified evidence - a template never invents domain knowledge.

- Single-skill set: `skill-router`, `skill-agents`, `skill-activation`,
  `review-procedure`, `exchange-procedure`, `decision-modes`, `skill-maintainer`,
  `skill-readme`, `skill-changelog`, `skill-license`, `skill-gitignore`,
  `skill-docs-index`, `skill-contributing`, `skill-style`, `skill-maintenance`,
  `skill-versioning`, `skill-security`, `skill-evals`, `skill-updater`,
  `skill-validator`.
- Collection set: `collection-router`, `collection-readme`, `collection-agents`,
  `collection-contract`, `collection-review`, `collection-sync`,
  `collection-gitmodules`.
- **`templates/README.md`** - The canonical template-to-output-path map and the
  placeholder vocabulary.

## `scripts/` - Mechanical Tools

Run tools in place - `python3 <skill-root>/scripts/<tool>.py` - and never against
untrusted targets without the sandboxing rules of `scripts/README.md`.

- **`scripts/check-update.py`** - Once-per-session upstream check used by the
  Skill Update Check gate.
- **`scripts/validate-skill.py`** - Read-only validator for this skill and for
  generated skill trees - frontmatter, shared contracts, structure, evals,
  references. It never executes target scripts.
- **`scripts/render-templates.py`** - Deterministic `{{placeholder}}` renderer:
  explicit output-path map, scratch staging, overwrite protection, and
  leftover-placeholder rejection.
- **`scripts/convert-source.py`** - Optional local-source converter: preflights
  the file, locates an installed or approved MarkItDown, and reports extraction
  quality. Never installs or fetches on its own.
- **`scripts/README.md`** - Tool contracts, safety rules, and exit statuses.

## `evals/` - Regression Prompts

- **`evals/evals.json`** - Behavioral regression prompts covering routing, each
  interaction mode, near misses, blocked permission, and resume - exercised after
  behavior changes.
- **`evals/README.md`** - The eval schema and the honest-reporting rule for
  skipped runs.

## Repository Files

- **`AGENTS.md`** - The agent-facing maintenance entry point.
- **`README.md`** - The human-facing overview and directory tree.
- **`CHANGELOG.md`** - Release history, record changes under `## [Unreleased]`.
- **`LICENSE`** - MIT.
- **`docs/`** - Governance: `STYLE.md`, `VERSIONING.md`, `MAINTENANCE.md`,
  `CONTRIBUTING.md`, `SECURITY.md`, and the `docs/README.md` index.
- **`tests/`** - Deterministic unit tests and synthetic fixtures for the scripts.

## Boundaries

- Keep `SKILL.md` lean: it routes and stays below 500 lines.
- Register every new or renamed resource in `SKILL.md` and mirror it in the
  `README.md` tree, per `docs/MAINTENANCE.md`.
- A generated skill writes only into its approved target directory, Forge's own
  run state and converted source text live in the gitignored `work/` tree and are
  never shipped.
- Never embed real project names, paths, or identifiers supplied with a request -
  examples stay anonymized, per `docs/MAINTENANCE.md`.
- Never invent domain facts. A blocked essential phase marks the run partial, it
  never produces an ungrounded "complete" skill.
- No automatic commits, pushes, remote creation, network access, or package
  installation - each needs its own approval, in every interaction mode.
- Bump `metadata.version` by one patch with every change set, per
  `docs/VERSIONING.md`.
- Do not claim validation that did not run.
