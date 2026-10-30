# Parallel Execution

## Purpose

> **Scope:** Delegation model for splitting large document work across parallel
> scout agents when the host environment supports subagents
> **Key items:** applicability, scout roles, scout contract, merge discipline,
> provenance, sequential fallback

This file defines how Forge splits a large work surface across parallel agents
for wall-clock efficiency.

It applies inside the document workflows - the procedure order and output
contract are unchanged.

## Applicability

Use parallel execution when two conditions hold.

- The work surface is large - a document past roughly two thousand lines, a
  multi-document review, or a repository-wide evidence sweep.
- The host agent supports delegating bounded tasks to subagents or equivalent
  parallel workers.

When either condition fails, the workflow runs sequentially unchanged.

Parallelism never changes what is produced - it changes only who reads or
drafts the evidence.

## Scout Roles

Choose roles from the pool per request shape, merging roles when the surface is
small. State which roles ran and why in the delivery.

| Role            | Focus                                                              |
|-----------------|--------------------------------------------------------------------|
| `source-reader` | Read one authorized source range and return extracted evidence     |
| `inventory`     | Read-only target map: files, layouts, registered resources         |
| `draft`         | Draft one named template region or evidence section to scratch     |

## Scout Contract

Every scout prompt carries the same invariants.

- Scouts never edit the live document or the skill repository - evidence
  scouts are read-only, and drafting scouts write only to their assigned
  scratch path.
- The scout returns findings or drafts as text in its reply, with `file:line`
  or section evidence for every claim.
- The brief scopes the work to named boundaries - a chapter, a checklist
  family, a file set - and names the generated trees to skip.
- The brief carries the context already resolved upstream - document type,
  methodology, conventions - so a scout never re-derives decisions the parent
  already locked.
- A scout that cannot finish reports partial coverage and the gap it hit - the
  parent covers the gap itself.

## Merge Discipline

The parent agent owns synthesis and is the single writer of the deliverable.

Deduplicate overlapping scout output, ranking items more than one scout
surfaced higher.

Keep conflicting readings as both readings with their evidence - never
silently pick one.

Merge regions in document order, and run a global reconciliation pass over the
merged whole - document-wide invariants re-verify after the merge, and this
step is mandatory, not optional.

## Provenance

The delivery records that scouts ran - roles used, scout count, and any gap
the parent filled directly.

A finding never cites "the scout" as evidence - the `file:line` or section
reference is the evidence.

## Sequential Fallback

Without subagent capability the parent performs every scout role itself in the
order the work demands - the role list becomes a reading checklist, not a skip
list.

A partially delegated run that loses a worker mid-flight continues sequentially
for the remaining roles and records the mix in the delivery.
