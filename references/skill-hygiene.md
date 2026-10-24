# Skill Hygiene

## Purpose

> **Scope:** The audit taxonomy and rule tables for housekeeping and healing an
> existing skill project or skill collection
> **Key items:** behavioral preservation, lifecycle states, drift classes,
> consistency and gap classes, deduplication passes, confidence matrix, token
> budgets, safety rules

This file is the evidence layer for `process/skill-housekeeping.md` and
`process/skill-healing.md`. The procedures cite these tables, they do not
restate them.

Load it whenever a housekeeping or healing run reaches the audit, plan, or
apply stage.

## Behavioral Preservation

The prime rule overrides every other rule in this file: housekeeping may change
how a skill is instructed, never what the skill does, unless a behavioral
change is explicitly verified and accepted as a fix.

An audit finding is information, not permission to edit.

Every mutation follows detect, diagnose, patch, verify, promote-or-rollback,
with a full undo path recorded before the change lands.

## Lifecycle States

Every inventoried skill carries exactly one state:

| State       | Meaning                                                              |
|-------------|----------------------------------------------------------------------|
| `active`    | Structurally valid and reachable from its registered location        |
| `stale`     | Valid but superseded by a newer copy under another root              |
| `unmanaged` | Valid but not registered or referenced by any owning index           |
| `archived`  | Preserved in an archive, no longer reachable as an active skill      |
| `invalid`   | Fails structural validation - missing `SKILL.md`, broken frontmatter |

The audit script assigns the state mechanically, the run report carries it per
skill.

## Drift Classes

Drift is divergence between copies of what should be the same skill:

- **Exact duplicate** - identical package hash under two or more roots.
- **Stale twin** - same skill name, different package hash, one copy older.
- **Name collision** - same name, materially different skill bodies, different
  provenance.
- **Platform divergence** - the same skill carrying materially different
  instructions in different harnesses.

Package hashing separates exact duplicates from divergent copies mechanically.
Whether a divergence is a stale twin or a name collision is a semantic
classification - the agent decides it from content and provenance, never from
the hash alone.

Name collisions resolve through explicit precedence per
`references/platform-paths.md`, never by silently picking one copy.

## Consistency Classes

A contradiction exists when two current, authoritative locations imply
incompatible actions. Classify before fixing:

| Class   | Definition                                  | Resolution                                             |
|---------|---------------------------------------------|--------------------------------------------------------|
| Hard    | Two rules directly conflict                 | Human decision or explicit precedence - never averaged |
| Soft    | Rules differ in specificity but can coexist | An explicit precedence statement in the corpus         |
| Phantom | Wording differs, intent is identical        | Deduplication candidate, not a contradiction           |

Never average contradictions. Determine which rule reflects current observed
behavior, and when behavior is itself inconsistent, record a known ambiguity
with a decision boundary instead of silently choosing.

### Single Ownership

Every current rule has exactly one maintenance location:

| Rule type                                          | Owner                                      |
|----------------------------------------------------|--------------------------------------------|
| Repository-wide invariant                          | `AGENTS.md` or platform equivalent         |
| Trigger, routing, stage order, stop conditions     | Exactly one `SKILL.md`                     |
| Domain detail needed only in a specific mode       | One reference file under that owner        |
| Deterministic transform, threshold, schema         | One script or config, constrained by tests |
| Volatile facts - accounts, versions, service state | A live source, never a skill               |

Secondary copies are replaced by short pointers to the owner, never
synchronized by hand.

Any instruction containing "keep in sync", "update both copies", or "the same
file also needs changing" is a multi-maintenance defect signal.

A deliberately mirrored pair is not that signal - a prose contract stating a
bound and a checking script enforcing the same bound is a sanctioned parity
when the pairing is recorded in the document and the check is constrained by
tests, so it classifies `FALSE_POSITIVE`. The signal fires only on unguarded
hand synchronization between authoritative copies.

A pairing the owning contract itself mandates classifies `FALSE_POSITIVE` the
same way - a registration rule that requires an index and a tree to update in
one change set produces "keep in sync" instructions that state the contract,
and the same words carried into a scope file that teaches the convention to
other repositories are that convention applied, not a defect.

### Workspace References

A `work/` path inside a shipped file divides by direction. An instruction that
directs generated artifacts, run state, or scratch into the gitignored
workspace states the workspace convention itself, it is not a violation. A
shipped file that reads from, links to, or otherwise depends on workspace
content is a defect - the workspace never ships.

### Mechanical False-Positive Classes

The mechanical checks surface three recurring reference and pointer shapes that
usually classify `FALSE_POSITIVE` - the scripts now carry them as notes or
advisories instead of findings, and the human classification stays the same:

- **Workspace-direction references** - a `work/…` root reference never resolves
  in a fresh checkout, because the workspace is gitignored by contract. Directing
  output there is the convention statement above. Only a reference that depends
  on workspace content is a defect, and that judgment is semantic.
- **External-root references** - a root reference whose first path segment
  exists nowhere in the skill tree often names a path inside another repository
  the skill documents - a memory repository, a platform directory, a settings
  root. The prose should name its root. When it does, classify `FALSE_POSITIVE`,
  when it does not, the reference is a clarity defect, not a broken link.
- **Convention-addressed records** - a numbered archive record
  (`change-042-slug.md`, `plan-007-slug.md`, and the like) is pointed at by its
  identifier `change-042`, not by path or stem. The audit counts a file as
  referenced when its leading `<word>-<number>` identifier appears in the corpus,
  so such records no longer surface as orphans.

## Gap Classes

A gap is information the skill should provide but does not:

- Referenced scripts, references, or templates that do not exist.
- Workflow branches with no instructions.
- Trigger conditions with no corresponding action.
- Inputs the skill assumes but never documents.
- Orphaned resources - files present but never pointed to, where a pointer
  means the relative path or the file stem appearing in the union of the
  skill's Markdown files.

A gap is reported as a gap. Missing domain content is named, never invented.

## Deduplication Passes

Deduplication is three distinct passes with different risk levels:

1. **Exact** - complete-package hashing finds byte-identical skills across
   roots. Deterministic, reported automatically, safe to archive on approval.
2. **Ownership** - rules living in multiple locations collapse to the single
   owner per the table above, copies become pointers.
3. **Semantic** - overlapping skills are classified `duplicate`, `neighbor`,
   or `merge-candidate` from trigger, scope, and instruction-similarity
   evidence. The agent proposes, the human confirms - semantic merges never
   auto-apply.

Artifacts also coexist legitimately when the corpus records why. A documented
deprecation marker - `superseded by`, `deprecated`, kept for compatibility -
makes a file a sanctioned compatibility twin, never a dedup candidate. Two
tools whose documented scopes differ - a single-check validator beside a
one-command battery - are recorded distinct roles, not overlap. Both classify
`FALSE_POSITIVE`.

Batch generation deduplicates during generation, merging similar content
before separate skills form, per `process/research-synthesis.md`.

## Token Budgets

| Layer                            | Target                         | Action when exceeded                 |
|----------------------------------|--------------------------------|--------------------------------------|
| Metadata - `name`, `description` | ~100 tokens per skill          | Shorten, add negative constraints    |
| `SKILL.md` body                  | Under 500 lines, ~5,000 tokens | Split into router plus `references/` |
| References                       | Loaded on demand               | Conditional pointers only            |

The description is routing logic, not prose marketing: it answers what the
skill does, when to use it, and when not to use it. Explicit negative
constraints are the strongest fix for trigger misfires.

Conditional pointers beat blanket references - "if the API returns 403, read
`references/auth-errors.md`", never "see `references/` for details".

A deterministic command repeated in prose belongs in `scripts/` - scripts do
precise work, the model does judgment work.

Trigger conflicts resolve by subset detection (one skill contains the other,
merge candidate), mutual exclusion in both descriptions, or consolidation with
a mode selector - never by shortening both descriptions blindly.

## Confidence Matrix

Every finding carries a confidence class that gates its resolution:

| Confidence       | Criteria                                              | Resolution            |
|------------------|-------------------------------------------------------|-----------------------|
| `HIGH`           | Issue confirmed, fix unambiguous, behavior-preserving | May auto-apply        |
| `MEDIUM`         | Issue exists, fix uncertain or behavior-affecting     | Human review required |
| `FALSE_POSITIVE` | Issue does not exist or is intentional                | Skipped and reported  |

### Apply Gates By Change Type

| Change type                             | Auto-applies                 | Human approval               |
|-----------------------------------------|------------------------------|------------------------------|
| Exact-duplicate archival                | Yes, after snapshot          | No                           |
| Frontmatter validation fix              | Yes, at `HIGH` confidence    | No                           |
| Broken reference fix                    | Yes, when target unambiguous | No                           |
| Ownership pointer replacement           | Yes, after snapshot          | No                           |
| Contradiction resolution                | Never                        | Always                       |
| Semantic merge                          | Never                        | Always                       |
| Behavioral change, even framed as a fix | Never                        | Always, plus replay evidence |

## Safety Rules

- Dry-run first, mutate second - no change lands before the report.
- Never delete, always archive - every removed or replaced artifact gets a
  snapshot and a restore path before the mutation.
- Verify every edit - re-read the changed file, a substitution tool can report
  success without matching, multi-line edits belong to structured writers not
  line-oriented blind replacement.
- Re-validate before applying - the file may have changed since the audit.
- A byte-identical file is not a conflict - a restore preserves only files
  whose content actually differs.
- Report divergence rather than repairing it - the owner decides.
- The audit log records actor, timestamp, diff, rationale, and evidence for
  every applied mutation.
- Any promoted change carries a version, a changelog entry with before/after,
  rationale, and evidence, and a one-command rollback.
