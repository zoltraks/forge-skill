# Platform Paths

## Purpose

> **Scope:** The skill and rule locations an inventory scans across agent
> platforms, and the per-platform semantics a cleanup must respect
> **Key items:** platform roots table, discovery rules, precedence, portability

This file is the evidence `scripts/audit-skill.py --discover` encodes and the
contract housekeeping respects when it touches copies outside the canonical
project root.

Load it when a housekeeping run performs multi-root discovery, resolves a name
collision, or archives a platform-specific copy.

## Platform Roots

| Platform    | Skill or rule roots                                                      |
|-------------|--------------------------------------------------------------------------|
| Claude Code | `~/.claude/skills/<name>/`, project `.claude/skills/<name>/`             |
| Codex       | `.agents/skills/<name>/`, `~/.agents/skills/<name>/`, `~/.codex/skills/` |
| Cursor      | `.cursor/rules/` - `.mdc` rule files with frontmatter                    |
| Antigravity | `~/.gemini/antigravity/skills/<name>/`, `~/.gemini/config`               |
| Kilo Code   | `.kilocode/rules/` - Markdown rule files                                 |
| Windsurf    | `.windsurf/skills/<name>/`                                               |
| OpenCode    | `.opencode/skills/<name>/`                                               |
| Pi          | Platform-specific - respect first-file-wins semantics                    |

Project-local roots outrank user-level roots for the same skill name.

`~` resolves to the current user's home directory at audit time - the scanner
never writes there.

## Discovery Rules

Per-platform semantics that shape what an inventory may conclude:

- Claude Code reads skill directories one level deep under its roots.
- Codex scans nested skill trees up to several levels and skips a `SKILL.md`
  reached only through a filesystem link.
- Cursor and Kilo Code consume rule files, not skill packages - an `.mdc` or
  Markdown rule file inventories as a rule artifact, not a `SKILL.md` package.
- Antigravity loads a rule only when its frontmatter marks it `always_on` or
  equivalent - a skill present but not marked does not count as active there.
- OpenCode and Kilo Code prefer `~/.agents` before `~/.claude` when both exist.
- Pi applies first-file-wins - the earliest copy in its search order wins, and
  later same-name copies are unreachable, not alternatives.

An inventory that ignores these rules misclassifies reachable copies and can
break a platform's resolution even when the canonical skill is intact.

## Precedence

When the same skill name appears under several roots, precedence resolves in
this order:

1. Project-local roots over user-level roots.
2. The platform's own documented load order, per the rules above.
3. When two roots remain tied, the collision is reported, not resolved - the
   human picks the canonical copy.

A name collision never resolves by silently deleting a copy.

## Portability

The Agent Skills `SKILL.md` format is the canonical source. Platform-specific
artifacts - `.mdc` files, Antigravity metadata fields, tool-specific trigger
frontmatter - are generated or preserved as extensions, and unknown fields are
ignored by other platforms.

Housekeeping preserves harmless platform extension fields verbatim and keeps
the canonical skill fully functional without them.

## Boundaries

- Discovery is read-only. Roots are scanned, never created, and a platform the
  machine does not run is simply absent from the inventory.
- User-home scanning stays inside the listed roots - the audit never sweeps
  the home directory at large.
- A copy the inventory cannot parse is reported `invalid`, not assumed stale.
