# Agent Skills Specification Summary

## Purpose

> **Scope:** The portable Agent Skills format a generated skill conforms to
> **Key items:** canonical source, frontmatter fields, naming limits, progressive
> disclosure, file references, validation

The canonical specification lives at `https://agentskills.io/specification` - it
is the authority this file condenses, and it wins any disagreement.

When network access is approved, verify against the upstream specification, this
file is the local working contract.

This file is also the `spec` profile contract - the minimal layout a generated
skill must satisfy outside the astra member conventions recorded in
`references/astra-conventions.md`.

## Package Layout

A skill is a directory whose name matches its `name` field, containing a
`SKILL.md` at its root.

Optional resource directories sit beside it, and any additional files or
directories are legal:

- `scripts/` - executable code the agent runs, self-contained or with documented
  dependencies.
- `references/` - documentation the agent reads on demand, kept small and
  focused.
- `assets/` - static resources: templates, images, schemas, data files.

## Frontmatter

`SKILL.md` opens with a YAML frontmatter block followed by the Markdown body:

| Field           | Required | Constraint                                                       |
|-----------------|----------|------------------------------------------------------------------|
| `name`          | yes      | Lowercase alphanumeric characters and hyphens, 1-64 characters   |
| `description`   | yes      | 1-1024 characters, states what the skill does and when to use it |
| `license`       | no       | License name or reference to a bundled license file              |
| `compatibility` | no       | 1-500 characters, environment requirements                       |
| `metadata`      | no       | Map of string keys to string values, reasonably unique key names |
| `allowed-tools` | no       | Space-separated list of pre-approved tools, experimental         |

The `name` field additionally must not start or end with a hyphen, must not
contain consecutive hyphens, and must match the parent directory name.

The specification allows unicode lowercase alphanumerics in `name` - Forge
generates ASCII-only slugs as a deliberate stricter convention.

Forge additionally rejects angle brackets in `description`, a portability
precaution the specification's ecosystem recommends against injection into the
system prompt.

Unrecognized top-level fields are rejected by strict validators.

## Body

The Markdown body is the skill instructions the agent loads whole on activation -
the specification places no format restriction on it.

Recommended sections are step-by-step instructions, input and output examples,
and common edge cases.

Keep the router lean - route to resource files rather than inlining them. The
specification recommends under 500 lines and under 5000 tokens. The astra
convention enforces the same 500-line ceiling.

## Progressive Disclosure

Three levels:

1. Metadata - `name` and `description` are always visible (~100 tokens per
   skill) and drive selection.
2. The `SKILL.md` body - loaded on activation (under 5000 tokens recommended).
3. Resource files - read on demand when the task reaches them, at zero token
   cost while idle.

Write `description` as the routing surface: what the skill does plus explicit
trigger scope. Keep deep detail in resource files, and tell the agent when to
load each one - a gated reference beats a generic pointer.

## File References

Reference other files with relative paths from the skill root, and keep the
reference chain one level deep from `SKILL.md` - a reference file may point at
siblings, avoid deeper nesting.

## Validation

The reference validator is `skills-ref`
(`https://github.com/agentskills/agentskills/tree/main/skills-ref`):

```bash
skills-ref validate ./my-skill
```

It checks the frontmatter and naming conventions. Forge's own
`scripts/validate-skill.py` covers the same surface locally - pass `--profile
spec` for a spec-layout tree.

## Validation Points

A conforming skill: frontmatter parses, `name` matches the directory and the
naming pattern, `description` and `compatibility` respect their limits, and every
referenced resource path resolves inside the skill directory.
