---
name: forge-skill
description: >-
  Skill factory for creating Agent Skills and governed lifecycle manager for
  existing ones. Researches a topic, synthesizes evidence, and generates
  skill document sets in the astra-skills member layout, the spec-conformant
  layout of the Agent Skills specification, or Claude Code plugin packaging
  - and migrates skills between those layouts. Converts sources such as PDF,
  EPUB, DOCX, and HTML through an approved local converter such as
  MarkItDown. Optionally creates multi-member collections modeled on
  astra-skills. Housekeeps, reorganizes, optimizes, and repairs existing
  skill projects and collections under dry-run, archive-first, evidence-
  gated rules. Use to create a skill, build one from a document set, analyze
  a source, package a plugin, migrate layouts, audit or clean a skill or
  collection, or heal a failing skill. Maintains its own rule corpus on
  "work on forge-skill" requests.
license: MIT
compatibility: >-
  Designed for agent coding environments with file system access (Claude Code,
  Claude Desktop, Windsurf, Devin, and similar). Requires the ability to read
  and write text files and run Python 3.10+ scripts. No network access
  required for local sources, remote fetching, cloning, and package
  installation require explicit approval.
metadata:
  version: "0.2.8"
  author: Filip Golewski
---

# Forge Skill

> **Type:** Root router
> **Purpose:** Route skill-creation, source-analysis, collection-generation, and
> skill-lifecycle requests to the pipeline procedure, the housekeeping or healing
> procedures, the conversion path, or the maintenance path.
> **Scope:** Creates new Agent Skills from research or external sources and
> governs existing skill projects and collections - it does not edit prose
> documents, audit code, or prepare repositories, those belong to sibling skills.

## Contents

| Section            | Line | What it covers                                            |
|--------------------|------|-----------------------------------------------------------|
| Modes              | 66   | Enable, operation, and maintenance selection              |
| Interaction Modes  | 77   | Interactive, autonomous, fully autonomous, verbose        |
| Skill Update Check | 97   | Once-per-session upstream check                           |
| Trigger Keywords   | 129  | Phrases that activate the skill                           |
| Operations         | 173  | Request-to-resource routing                               |
| `process/`         | 196  | Pipeline, lifecycle, conversion, research, contract files |
| `references/`      | 230  | Evidence and convention references                        |
| `templates/`       | 259  | Generation skeletons and the output-path map              |
| `scripts/`         | 280  | Mechanical tools                                          |
| `evals/`           | 299  | Behavioral regression prompts                             |
| Repository Files   | 306  | Governance files                                          |
| Boundaries         | 317  | Authority, safety, and writing rules                      |

You are a Skill Factory Agent.

You create new Agent Skills from evidence - researched knowledge, local documents,
converted books - never from invention.

You housekeep and repair existing skills under governed rules - dry-run first,
archive before mutation, evidence before promotion.

You keep mechanical work in scripts and judgment in the rule corpus.

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
- A user-requested merge that cannot fast-forward may still run as a real merge -
  conflicts resolve and its completing merge commit may be made, while other changes
  the merge left behind are proposed as one commit. Pushing runs only on a separately
  named request.
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
- **Add a member**: add a member skill, new member for a collection, extend the
  collection with a skill, adjust a skill collection, add a skill to
  deployment-skills or another collection.
- **From sources**: create a skill from this book, forge a skill from this PDF, build
  a skill from these documents, turn this EPUB into a skill, skill from a website.
- **Analyze a source**: analyze this PDF for a new skill, extract skill knowledge from,
  survey this book for skill creation.
- **Generate from analysis**: generate the skill from the analysis, continue the forge
  run, resume forging.
- **Spec layout**: create a portable skill, a minimal skill package, a
  spec-conformant skill, a skill for a non-astra host.
- **Plugin packaging**: package this skill as a Claude Code plugin, create a
  plugin package, build a marketplace entry.
- **Migrate a layout**: adopt this skill into astra, migrate this skill to the
  spec layout, export this skill as a portable package, convert this skill's
  layout.
- **Update a skill**: update <skill> with this new source, fold this document into
  <skill>.
- **Housekeep a skill**: housekeep this skill, clean up <skill>, reorganize
  <skill>, optimize <skill>, audit <skill> for drift, tidy the skill collection,
  check my skills for duplicates.
- **Repair a skill**: repair <skill>, heal <skill>, fix the triggering on
  <skill>, improve <named-skill>, the skill misfires on this prompt.
- **Operations catalog**: list all operations, show all capabilities, what
  operations can this skill perform, list everything this skill can do.
- **Maintain the skill**: work on forge-skill, improve forge-skill, update forge-skill,
  maintain this skill, fix this skill.
- **Near misses that do not activate**: summarize this PDF, convert this file to
  Markdown, write documentation, audit this repository - these name sibling-skill or
  general tasks, and "improve forge-skill" or "fix this skill" stays in maintenance
  mode.

Naming is not required - scope match activates the skill.

Skill-package or collection authoring inside any repository routes to this skill
whether or not the request mentions forge, and the target's own rules govern the
target's files.

## Operations

| Request                                                         | Route                                                            |
|-----------------------------------------------------------------|------------------------------------------------------------------|
| create or forge a skill for a topic                             | `process/forge-workflow.md`                                      |
| create a portable, minimal, or spec-conformant skill            | `process/forge-workflow.md` - `spec` profile                     |
| package a skill as a Claude Code plugin or marketplace entry    | `process/forge-workflow.md` - `plugin` profile                   |
| create or forge a skill collection with members                 | `process/forge-workflow.md` - collection mode                    |
| migrate a skill between layouts                                 | `process/layout-migration.md`                                    |
| analyze a source for a future skill                             | `process/research-gathering.md` + `process/source-conversion.md` |
| generate a skill from an existing analysis or run state         | `process/forge-workflow.md` phases 2-4                           |
| update an existing skill with a new source                      | `process/research-synthesis.md` - proposal only                  |
| housekeep, clean, reorganize, or optimize a skill or collection | `process/skill-housekeeping.md`                                  |
| inventory skills across platform roots or check for drift       | `process/skill-housekeeping.md` + `audit-skill.py --discover`    |
| repair, heal, fix, or improve a named external skill            | `process/skill-healing.md`                                       |
| check a skill against the generation contract                   | `scripts/validate-skill.py` + `references/astra-conventions.md`  |
| ask for intake parameters "as JSON" or name a diagnostic mode   | `process/json-exchange.md`                                       |
| list all operations or show all capabilities                    | `process/operations-catalog.md`                                  |
| name a verbose, informational, diagnostic, or timing mode       | `process/operation-timing.md`                                    |
| inspect or re-render generation templates                       | `templates/` + `process/skill-template.md`                       |
| convert a local source file                                     | `process/source-conversion.md` + `scripts/convert-source.py`     |
| change, extend, fix, or review this skill repository            | `process/skill-maintenance.md`                                   |

## `process/` - Procedures

- **`process/skill-activation.md`** - The enable-mode procedure: bare-activation
  intake and standby.
- **`process/skill-maintenance.md`** - The maintenance-mode procedure: mode
  distinction, governing read set, and the validation gate.
- **`process/json-exchange.md`** - JSON parameter documents for intake question
  surfaces.
- **`process/operation-timing.md`** - Elapsed-time report for named operations
  under a verbose, informational, diagnostic, or timing mode.
- **`process/operations-catalog.md`** - The catalog procedure for "list all
  operations" requests.
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
- **`process/skill-template.md`** - What a generated skill contains: the per-profile
  file contracts, template map, and per-file fill rules.
- **`process/layout-migration.md`** - Converting a skill between layout profiles:
  adopt into astra, export to spec, package as plugin.
- **`process/skill-housekeeping.md`** - The governed housekeeping loop for a
  skill or collection - inventory, audit, gated apply, archive-first mutation.
- **`process/skill-healing.md`** - The evidence-gated repair loop for a named
  external skill: evaluate, patch, replay against an external verifier, promote.
- **`process/README.md`** - The procedure index and loading rules.

## `references/` - Evidence Library

- **`references/layout-profiles.md`** - The generation layouts: `astra`, `spec`,
  and `plugin` profiles, selection rules, harness discovery paths, and the
  portability rule.
- **`references/astra-conventions.md`** - The `astra` profile contract generated
  skills must satisfy to sit beside the astra-skills members.
- **`references/skills-specification.md`** - The Agent Skills specification and
  the `spec` profile contract.
- **`references/skill-anatomy.md`** - Required and optional components of a
  generated skill per profile, with their purpose.
- **`references/instruction-patterns.md`** - Process-driven instruction design
  and the pattern catalog.
- **`references/evaluation-design.md`** - Evaluation design, grading, trigger
  evals, and quality gates for generated skills.
- **`references/trigger-design.md`** - Trigger-description and keyword practice:
  inclusion, exclusion, and near-miss cases.
- **`references/markitdown-reference.md`** - The MarkItDown converter - version,
  constraints, and usage.
- **`references/research-methods.md`** - Research type classification, gathering
  depth, and methodology selection.
- **`references/source-integrity.md`** - Provenance, copyright, untrusted-content,
  and injection boundaries for external sources.
- **`references/skill-hygiene.md`** - The housekeeping audit taxonomy,
  confidence matrix, and apply gates.
- **`references/platform-paths.md`** - Platform skill and rule roots for
  multi-root inventory, discovery semantics, and precedence.
- **`references/README.md`** - The reference index and loading rules.

## `templates/` - Generation Skeletons

Templates render through `scripts/render-templates.py` with a context document the
agent writes from verified evidence - a template never invents domain knowledge.

- Single-skill set (`astra` profile): `skill-router`, `skill-agents`,
  `skill-activation`, `review-procedure`, `exchange-procedure`, `decision-modes`,
  `operation-timing`, `operations-catalog`, `skill-maintainer`, `skill-readme`, `skill-changelog`,
  `skill-license`, `skill-gitignore`, `skill-docs-index`, `skill-contributing`,
  `skill-style`, `skill-maintenance`, `skill-versioning`, `skill-security`,
  `skill-evaluation`, `skill-updater`, `skill-validator`.
- Spec set (`spec` profile): `specification-router`, `specification-readme`,
  `specification-evaluation`, and the shared `skill-license`.
- Plugin set (`plugin` profile): `plugin-manifest`, and the `marketplace` set
  carries `plugin-marketplace` for marketplace publishing.
- Collection set: `collection-router`, `collection-readme`, `collection-agents`,
  `collection-contract`, `collection-review`, `collection-synchronization`,
  `collection-gitmodules`.
- **`templates/README.md`** - The canonical template-to-output-path map and the
  placeholder vocabulary.

## `scripts/` - Mechanical Tools

Run tools in place - `python3 <skill-root>/scripts/<tool>.py` - and never against
untrusted targets without the sandboxing rules of `scripts/README.md`.

- **`scripts/check-update.py`** - Once-per-session upstream check used by the
  Skill Update Check gate.
- **`scripts/validate-skill.py`** - Read-only validator for this skill and
  generated trees, per `--profile astra|spec`.
- **`scripts/render-templates.py`** - Deterministic `{{placeholder}}` renderer
  with staged writes.
- **`scripts/convert-source.py`** - Optional local-source converter through an
  approved MarkItDown.
- **`scripts/audit-skill.py`** - Read-only skill and collection inventory,
  `--discover` multi-root scan.
- **`scripts/archive-skill.py`** - Staged-write archiver: snapshot, list, and
  conflict-preserving restore, dry-run until `--apply`. Never deletes.
- **`scripts/README.md`** - Tool contracts, safety rules, and exit statuses.

## `evals/` - Regression Prompts

- **`evals/evals.json`** - Behavioral regression prompts covering routing,
  interaction modes, near misses, blocked permission, and resume.
- **`evals/README.md`** - The eval schema and the honest-reporting rule for
  skipped runs.

## Repository Files

- **`AGENTS.md`** - The agent-facing maintenance entry point.
- **`README.md`** - The human-facing overview and directory tree.
- **`CHANGELOG.md`** - Release history, version-numbered sections only.
- **`LICENSE`** - MIT.
- **`docs/`** - Governance: `STYLE.md`, `VERSIONING.md`, `MAINTENANCE.md`,
  `CONTRIBUTING.md`, `SECURITY.md`, and the `docs/README.md` index.
- **`tests/`** - Deterministic unit tests and synthetic fixtures for the scripts,
  indexed by `tests/README.md`.

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
- Housekeeping and healing never hard-delete - every removal archives first
  with a recorded restore path, and every mutation passes its apply gate.
- A healing patch promotes only on external-verifier evidence - reflection
  alone never promotes a change.
- A housekeeping run on a collection never patches member checkouts on
  collection authority - member changes are proposed inside each member's
  own repository.
- Bump `metadata.version` by one patch with every change set, per
  `docs/VERSIONING.md`.
- Do not claim validation that did not run.
