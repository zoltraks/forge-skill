# Layout Profiles

## Purpose

> **Scope:** The generation layouts Forge can emit and the hosts that consume
> each
> **Key items:** astra, spec, and plugin profiles, selection rules, harness
> discovery, portability

A layout profile is the combination of a template set, a file contract, and a
validation profile.

Phase 0 resolves and records the profile, phase 2 designs against its file
contract, phase 3 renders its template set, and phase 4 validates with the
matching `--profile` of `scripts/validate-skill.py`.

## Profiles

| Profile  | Package                                                       | Consumed by                        |
|----------|---------------------------------------------------------------|------------------------------------|
| `astra`  | Full member contract per `references/astra-conventions.md`    | astra-skills collection members    |
| `spec`   | Minimal spec package per `references/skills-specification.md` | Any spec-conformant agent host     |
| `plugin` | A `spec` skill inside Claude Code plugin packaging            | Claude Code plugin and marketplace |

The `astra` profile is the default - every existing generation rule assumes it
unless the request says otherwise.

The `spec` profile applies when the request asks for a portable or minimal
skill, names a non-astra host, or names the specification layout directly.

The `plugin` profile applies when the request names a Claude Code plugin or a
marketplace package - it wraps a `spec` skill, never an `astra` tree.

An ambiguous profile ask resolves per the active interaction mode.

## Profile Contents

| File or directory                                                                                                         | `astra`      | `spec`       | `plugin`                |
|---------------------------------------------------------------------------------------------------------------------------|--------------|--------------|-------------------------|
| `SKILL.md`                                                                                                                | router       | router       | inside `skills/<name>/` |
| Domain dirs (`process/`, `references/`, `scripts/`, `assets/`)                                                            | as evidenced | as evidenced | inside `skills/<name>/` |
| `evals/evals.json`                                                                                                        | astra schema | spec schema  | inside `skills/<name>/` |
| `README.md`, `LICENSE`, `.gitignore`                                                                                      | yes          | optional     | plugin root             |
| `AGENTS.md`, `CHANGELOG.md`, `docs/`, shared `process/` contracts, `scripts/check-update.py`, `scripts/validate-skill.py` | yes          | no           | no                      |
| `.claude-plugin/plugin.json`                                                                                              | no           | no           | plugin root             |
| `.claude-plugin/marketplace.json`                                                                                         | no           | no           | marketplace root        |

A `spec` tree may legally carry any additional directories the evidence
justifies - the profile drops only the astra member contract, not the domain
payload.

The `plugin` profile renders in two passes: the `spec` set into
`<plugin-root>/skills/<skill-name>/`, then the `plugin` set into the plugin
root. A marketplace request adds a third pass rendering the `marketplace` set
into the marketplace root.

## Harness Discovery

The spec package is the portable unit - hosts differ only in where they look
for it:

| Host           | Project-scope path         | Notes                                                         |
|----------------|----------------------------|---------------------------------------------------------------|
| Claude Code    | `.claude/skills/<name>/`   | User scope `~/.claude/skills/`, plugins via `.claude-plugin/` |
| GitHub Copilot | `.github/skills/<name>/`   | Also reads `.claude/skills/`                                  |
| Codex CLI      | `.agents/skills/<name>/`   |                                                               |
| Gemini CLI     | `.gemini/skills/<name>/`   |                                                               |
| Cursor         | `.cursor/skills/<name>/`   |                                                               |
| OpenCode       | `.opencode/skills/<name>/` | Also reads `.claude/skills/` and `.agents/skills/`            |
| Devin          | `.devin/skills/<name>/`    |                                                               |

These paths come from the 2026-10 source survey - treat them as evidence, not
law. When the placement matters, verify against the host's current
documentation, and record the checked source in the run ledger.

Hosts not in the table follow the same pattern under their own dot-directory -
check `https://agentskills.io/clients` for the supported-product list.

Host-specific behavior belongs in `metadata` keys, never in custom top-level
frontmatter fields - OpenCode's `opencode/slash` and `opencode/autoinvoke`
entries are the pattern.

## Install Methods

| Method             | Mechanism                                                        |
|--------------------|------------------------------------------------------------------|
| Direct placement   | Copy the package into the host's discovery path                  |
| Plugin marketplace | `.claude-plugin/marketplace.json` registry, install by name      |
| Registry CLI       | skills.sh and similar one-command installers                     |
| Git submodule      | Pinned external repository, the astra collection's own mechanism |

## Portability Rule

Keep domain logic in scripts and rule files, keep harness glue thin and
generated.

Hardcode sequential steps inside the skill rather than relying on a host's
orchestration behavior - the same package performs differently across runtimes,
and decoupled logic survives the variance.

A skill that only works when force-loaded is a design bug - its `description`
must stand alone in every host.
