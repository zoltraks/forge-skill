# Agent Skills Specification Summary

## Purpose

> **Scope:** The portable Agent Skills format a generated skill conforms to
> **Key items:** frontmatter fields, naming limits, progressive disclosure, layout

This summary condenses the Agent Skills specification for generation and
validation. When network access is approved, verify against the upstream
specification, this file is the local working contract.

## Package Layout

A skill is a directory whose name matches its `name` field, containing a
`SKILL.md` at its root. Optional resource directories sit beside it - common
conventions are `scripts/`, `references/`, `assets/`, and domain directories such
as `process/` or `templates/`.

## Frontmatter

`SKILL.md` opens with a YAML frontmatter block:

| Field           | Required | Constraint                                                                                       |
|-----------------|----------|--------------------------------------------------------------------------------------------------|
| `name`          | yes      | Lowercase letters, digits, single hyphens, max 64 characters, matches the directory name         |
| `description`   | yes      | Non-empty, max 1024 characters, states what the skill does and when to use it, no angle brackets |
| `license`       | no       | License identifier or name                                                                       |
| `compatibility` | no       | Environment requirements, max 500 characters                                                     |
| `metadata`      | no       | Key-value map, `version` is conventional                                                         |
| `allowed-tools` | no       | Space-delimited tool permission list                                                             |

Unrecognized top-level fields are rejected by strict validators.

## Body

The body is Markdown instructions the agent reads when the skill is active. Keep
the router lean - route to resource files rather than inlining them. A 500-line
ceiling is the astra convention, the specification expects concise always-loaded
content.

## Progressive Disclosure

Three levels:

1. Metadata - `name` and `description` are always visible and drive selection.
2. The `SKILL.md` body - loaded on activation.
3. Resource files - read on demand when the task reaches them.

Write `description` as the routing surface: what the skill does plus explicit
trigger scope. Keep deep detail in resource files.

## Validation Points

A conforming skill: frontmatter parses, `name` matches the directory and the
naming pattern, `description` and `compatibility` respect their limits, and every
referenced resource path resolves inside the skill directory.
