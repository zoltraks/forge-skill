# Optimization Patterns

## Purpose

> **Scope:** The context-diet taxonomy and restructure recipe for optimizing an
> existing skill's context consumption
> **Key items:** load-surface model, measurement surfaces, finding classes,
> restructure patterns, layout variants, verification contract

This file is the evidence layer for `process/skill-optimization.md`. The
procedure cites these tables, it does not restate them.

Load it whenever an optimization run reaches the diagnose or plan stage.

## Load-Surface Model

A skill occupies context on three levels:

- **Metadata** - `name` and `description` load into the host at startup, before
  any request. Every character here costs in every session.
- **Router** - `SKILL.md` loads when the skill is triggered. Every section in it
  costs on every activation, maintenance request, and operation.
- **Resources** - bundled files load on demand. They cost only when a route,
  procedure, or index names them.

Optimization moves weight down the model: out of metadata into the router where
it belongs, out of the router into on-demand resources, and out of unconditional
load paths into conditional ones.

The token budgets in `references/skill-hygiene.md` set the targets - ~100
tokens of metadata, `SKILL.md` under 500 lines and roughly 5,000 tokens,
references loaded on demand.

## Measurement Surfaces

`scripts/audit-skill.py --load-profile <target>` reports the surfaces
mechanically:

- `description_chars` - frontmatter description length.
- `skill_md_bytes` / `skill_md_lines` - the router's total weight.
- `sections[]` - bytes per `## ` section, showing which sections carry the
  weight.
- `dir_bytes{}` - per top-level directory totals, the on-demand corpus size.
- `indexes[]` - resource directories carrying a `README.md` index.

Baselines are recorded before diagnosis - the report's byte deltas compare
against them.

## Finding Classes

| Class                 | Signal                                                        | Default confidence |
|-----------------------|---------------------------------------------------------------|--------------------|
| `description-overrun` | `description` over ~700 chars, or over the 1024-char limit    | `HIGH`             |
| `catalog-duplication` | Per-file resource listings in `SKILL.md` duplicating indexes  | `HIGH`             |
| `missing-index`       | Resource directory without a `README.md` index                | `HIGH` (astra)     |
| `unconditional-load`  | Instructions that bulk-read directories or unnamed files      | `MEDIUM`           |
| `trigger-bloat`       | Exhaustive trigger-phrase catalogs in the router              | `HIGH`             |
| `contents-overhead`   | Line-numbered Contents, or Contents on a file under 300 lines | `HIGH`             |
| `inline-detail`       | Large detail blocks in the router that belong in a resource   | `MEDIUM`           |
| `monolith-reference`  | Reference over ~10 KB with no section-level load note         | `MEDIUM`           |

`catalog-duplication` fires when the router enumerates files a directory index
can own - an operations route table is registration, not duplication, and never
classifies as this finding.

`unconditional-load` covers blanket references ("see `references/` for
details") and routes that pull a whole corpus for a narrow request.

A finding never fires on structure the target's own contract mandates - a
collection index's member roster or a spec router's workflow table is the
contract, not bloat.

## Restructure Patterns

- **Resource-map relocation** - per-file catalogs leave `SKILL.md` for the
  owning directory's `README.md` index. The router keeps a compact map table:
  directory, its index, what it holds. Routed procedures stay registered as
  operations-table rows.
- **Index per directory** - every resource directory gains a `README.md` index
  naming each file with its load trigger when the target's conventions allow.
  A target whose own contract registers resources in the router plus a
  directory tree needs no per-directory index - its absence classifies
  `FALSE_POSITIVE`, never `missing-index`.
- **Conditional pointers** - references resolve through the index or through
  "read `<file>` when `<condition>`" wording, never blanket directory
  references.
- **Description diet** - the description answers what the skill does, when to
  use it, and when not to use it. Compress toward ~600 chars while keeping the
  trigger vocabulary - every removed phrase must leave its routing family
  covered.
- **Trigger compression** - keyword lists compress to one line per family plus
  the near-miss list. Scope-match wording carries the coverage.
- **Contents rule** - drop Contents tables from files under 300 lines and drop
  line numbers from any that remain, per the target's own style rules.
- **Inline-detail extraction** - detail blocks over a few lines move from the
  router into a `process/` or `references/` file the route names on demand.
- **Section-level reads** - references over ~10 KB gain a load note directing
  readers to grep the section they need.
- **Load-discipline clause** - the router states it plainly: load only the file
  a route names plus the files it names in turn, indexes resolve names on
  demand, nothing bulk-reads.

## Layout Variants

| Layout    | What the run applies                                          |
|-----------|---------------------------------------------------------------|
| `astra`   | Full index contract - every resource directory indexes, the   |
|           | resource map carries index paths                              |
| `spec`    | Slim router plus an optional `references/` split, validated   |
|           | against the `spec` profile - no member-contract files added   |
| `plugin`  | Optimize the wrapped `spec` skill payload, never the manifest |
| `foreign` | Report only - patterns are proposed, nothing is applied       |

A collection target audits per member. Findings land as proposals inside each
member's own repository - the collection's membership contract decides where
mutations run, per `process/skill-housekeeping.md`.

## Gates

The confidence matrix, apply gates, and safety rules of
`references/skill-hygiene.md` govern every mutation - they are cited, not
restated.

The behavioral-preservation prime rule applies with full force: optimization
changes how a skill is instructed, never what it does. A restructure that drops
a route, a gate, or a boundary is a defect, not a diet.

## Verification Contract

A run is verified when:

- Every routed path and registered resource still resolves - no operation row,
  procedure, or referenced file was lost.
- Every `## ` heading an index or Contents anchors still exists.
- The target's own validation suite and `scripts/validate-skill.py --profile
  <detected>` pass as before, or better.
- The byte delta per surface is reported against the recorded baseline -
  description, `SKILL.md`, and each touched directory.
