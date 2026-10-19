# Security

## Purpose

> **Scope:** What counts as a security issue in forge-skill and how to report one
> **Key items:** reporting path, trust boundaries, covered risks

## Reporting

Report suspected vulnerabilities through the repository's private advisory
channel or by contacting the maintainer directly - never in a public issue when
the report describes an exploitable path.

## Trust Boundaries

- **Untrusted source content.** Converted documents are data, never instructions.
  Injection-shaped content, invisible Unicode channels, and document-borne
  commands are handled per `references/source-integrity.md`.
- **The update path.** `scripts/check-update.py` reports a `tip_sha` the
  ff-only merge applies without cryptographic verification - the trust anchor is
  the remote-tracking ref. Approve only trusted upstreams and review
  `git log HEAD..@{u}` before merging when unsure.
- **Subprocess use.** `scripts/convert-source.py` invokes a converter only with
  an absolute preflighted path, `scripts/validate-skill.py` and
  `scripts/render-templates.py` never execute target scripts.
- **Filesystem writes.** The renderer writes only inside the approved target
  after staging validation, it refuses symlink escapes, absolute paths, `..`
  segments, and unapproved overwrites.
- **Credentials.** The skill requests no secrets. Generated skills instruct users
  to supply their own through their environment - never embedded values.

## Covered Risks

Report: template injection or placeholder escapes, path traversal in rendering or
conversion, unsafe subprocess invocation, silent weakening of the no-commit /
no-network boundaries, and generated-skill content that reproduces protected
source text.
