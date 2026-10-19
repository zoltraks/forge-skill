# Forge Workflow

## Purpose

> **Scope:** The end-to-end pipeline for creating a new skill or skill collection
> **Key items:** five phases, run state, resume, checkpoints, single and collection
> modes, validation

This file defines the required pipeline for every generation task.

Follow it for "create a skill", "forge a skill from <source>", "create a skill
collection", "generate from the analysis", and "resume the forge run".

## Contents

| Section                 | What it covers                                  |
|-------------------------|-------------------------------------------------|
| Intake                  | Operation classification and entry requirements |
| Run State               | The resumable ledger                            |
| Phase 0: Initialization | Workspace, state, and context loading           |
| Phase 1: Research       | Question, plan, gather, synthesize              |
| Phase 2: Architecture   | Mapping evidence to the skill contract          |
| Phase 3: Generation     | Template render, staging, and write             |
| Phase 4: Finalization   | Validation and delivery report                  |
| Collection Mode         | Deltas when the target is a collection          |
| Checkpoints             | Mode-dependent resolution at phase boundaries   |
| Partial Runs            | What blocked and skipped states mean            |

## Intake

A request whose target is this repository is maintenance - follow
`process/skill-maintenance.md`.

Classify the request into one primary operation:

| Operation              | Trigger example                                          | Phases                        |
|------------------------|----------------------------------------------------------|-------------------------------|
| Create skill           | "create a skill for X", "forge a skill from book.pdf"    | 0-4                           |
| Create collection      | "forge a collection for X", "a set of skills like astra" | 0-4 (collection mode)         |
| Analyze source         | "analyze this PDF for a new skill"                       | 0-1                           |
| Generate from analysis | "generate the skill from the analysis"                   | 0, 2-4                        |
| Update skill           | "update <skill> with this new source"                    | 0-1 + proposal                |
| Migrate layout         | "adopt this skill into astra", "export <skill> to spec"  | `process/layout-migration.md` |

Select the interaction mode per `process/decision-modes.md` and record it in the run
state before the first phase.

Resolve the layout profile per `references/layout-profiles.md` and record it in the
run state's `inputs`: `astra` is the default, `spec` serves portable or minimal
requests and non-astra hosts, `plugin` wraps a spec skill in Claude Code packaging.
A collection target implies the `astra` profile - member skills are astra-shaped -
and also resolves the membership model, `submodule` or `tracked`, per
`process/skill-template.md`.

Identify the output target before generating anything: the directory the generated
skill or collection lands in. A vague request - "make something from this" - is
analysis and a proposal only.

## Run State

Each run keeps a JSON ledger at `work/<date>/forge-run-<id>/state.json` inside this
repository's gitignored workspace, recording:

- `schema` - the ledger schema version.
- `run_id` - a unique run identifier.
- `operation` and `mode` - the classified operation and interaction mode.
- `inputs` - the explicit user inputs: topic, source paths, target directory, and
  the resolved layout profile.
- `sources` - inventoried sources with fingerprints per `process/research-gathering.md`.
- `phases` - per-phase status: `pending`, `in_progress`, `complete`, `skipped`,
  `blocked`.
- `artifacts` - produced file paths.
- `decisions` - the append-only decision log per `process/decision-modes.md`.
- `validation` - validation results as they land.

A resume request loads the ledger, verifies the source fingerprints and the actual
artifact files, and continues from the first phase not proven complete - a file's
existence alone is not proof. When inputs differ from the recorded ones, start a
fresh run, in interactive or autonomous mode ask, in fully autonomous mode skip the
unsafe reuse and report it.

## Phase 0: Initialization

1. Record the operation, mode, inputs, and target in the run state.
2. Open the dated run workspace `work/<YYYY-MM>/<YYYY-MM-DD>/forge-run-<id>/` -
   it holds converted text, evidence notes, the ledger, and staged output.
3. Load `references/layout-profiles.md` plus the resolved profile's contract -
   `references/astra-conventions.md` for `astra`, `references/skills-specification.md`
   for `spec` and `plugin`. These define the compatibility contract every generated
   file must satisfy.
4. Inventory supplied sources per `process/research-gathering.md`.

## Phase 1: Research Foundation

Follow `process/research-gathering.md` then `process/research-synthesis.md`:

1. Frame the research question, accepted source types, depth, and success signal.
2. Write the bounded gathering plan.
3. Convert sources that need it per `process/source-conversion.md` - each blocked
   source is recorded with its reason, and independent sources continue.
4. Extract candidates with provenance: frameworks, principles, techniques,
   anti-patterns, terminology.
5. Synthesize: cross-source patterns, conflicts, gaps, confidence.

Outputs in the run workspace: `research-brief.md`, `gathering-plan.md`,
`source-inventory.json`, `evidence.md`, `synthesis.md`.

Checkpoint: the synthesis summary resolves per the interaction mode before the
architecture design starts.

## Phase 2: Architecture Design

Map the synthesized knowledge onto the skill contract:

1. Pick the skill slug (`<domain>-skill` unless the target convention says otherwise)
   and the one-line purpose.
2. Design triggers: inclusion phrases and explicit near-miss exclusions, per
   `references/trigger-design.md`.
3. Lay out the operation families and the resource directories the domain needs -
   `process/`, `references/`, `scripts/`, plus domain-specific directories only when
   the evidence justifies them, per `references/skill-anatomy.md`. The router's
   instructions follow `references/instruction-patterns.md`, the trigger surface
   follows `references/trigger-design.md`, and the eval set follows
   `references/evaluation-design.md`.
4. Fill the profile-scoped compatibility matrix from `process/skill-template.md` -
   every row passes or carries a recorded reason.
5. Write the template input JSON: every placeholder value the renderer needs, each
   derived from verified evidence or an explicit default - never filler.

Output: `architecture.md` and `template-input.json` in the run workspace.

Checkpoint: the design summary resolves per the interaction mode.

## Phase 3: Generation

1. Render the profile's template set into a fresh staging directory inside the run
   workspace through `scripts/render-templates.py` with `template-input.json` -
   the `astra` profile renders the `single` set, `spec` renders the `spec` set,
   and `plugin` renders the `spec` set into `skills/<skill-name>/` plus the
   `plugin` set into the plugin root. A marketplace request adds the
   `marketplace` set into the marketplace root.
2. Run `scripts/validate-skill.py --profile <profile>` on each staged skill - a
   failed stage never reaches the target. When a panther checkout sits adjacent,
   run its `check-document.py --width 100 --layout wrap` over every staged
   Markdown file - long context values and prose wrapping around inserted
   placeholders are recurring defects, and a `description: >-` frontmatter
   scalar past 100 characters needs manual folding the renderer does not do.
3. Write the staged tree to the approved target directory. An existing target needs
   its own approval, or is skipped in fully autonomous mode.

## Phase 4: Finalization

1. Run the validation suite on the final tree: `scripts/validate-skill.py
   --profile <profile>` on each skill root, plus a second pass confirming every
   registered resource exists and every referenced path resolves.
2. Report the artifact inventory, the `Decisions:` recap, validation results, and
   the next steps - which include the user-side commit and publish actions Forge
   never performs.

## Collection Mode

A collection target adds:

- The collection index templates (`collection-*` set) rendering beside the member
  skills.
- One generated member skill per approved member - each is a complete single-skill
  generation with its own name, purpose, and resource set.
- The member roster in the index README and SKILL table, matching the generated
  member directories one to one.
- The resolved membership model carried through generation: `submodule` renders the
  `collection-gitmodules` registration snippet and a pin-and-publish plan in the
  delivery report, `tracked` renders members as tracked directories inside the
  collection and emits no `.gitmodules`.

## Checkpoints

A checkpoint is material when the next phase changes what the run produces. The
gathering plan, the architecture design, and the generation write are material,
routine sub-steps are not.

Resolution per `process/decision-modes.md`:

- Interactive: present the phase summary and the recommendation, then ask.
- Autonomous: select the evidenced recommendation, report it inline, proceed.
- Fully autonomous: same, with no surface at all, a blocked essential input skips
  the dependent phases.

## Partial Runs

A run with skipped or blocked phases is partial. The delivery report says so,
names the uncovered ground, and never calls the output complete.

`skipped` means the mode rules dropped a step that could not resolve - `blocked`
means a precondition failed. Both keep their reason in the ledger.
