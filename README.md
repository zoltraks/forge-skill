# Forge Skill

Forge is an Agent Skills package that creates **new** Agent Skills - from scratch,
from research on a topic, or from external sources such as PDF books, EPUB files,
Word documents, and HTML pages.

It is a member of the [Astra Skills](https://github.com/Astra-Professional/astra-skills)
collection, and its default `astra` layout follows the same conventions: a routed
`SKILL.md`, shared activation / JSON-exchange / session-review procedures, a
once-per-session update check, governance documents, behavioral evals, and the
dual-mode autonomy contract (interactive, autonomous, fully autonomous, verbose).

Two further layouts are supported: the `spec` profile emits a minimal package
conformant to the [Agent Skills specification](https://agentskills.io/specification),
and the `plugin` profile wraps a spec skill in Claude Code plugin packaging.
Existing skills migrate between layouts in both directions.

## What It Does

| Operation              | What it covers                                                 |
|------------------------|----------------------------------------------------------------|
| Create a skill         | Research a topic and generate a complete skill document set    |
| Create a spec skill    | Generate a minimal spec-conformant package for any host        |
| Package a plugin       | Wrap a skill in Claude Code plugin or marketplace packaging    |
| Create a collection    | Generate an index plus independently owned member skills       |
| Migrate a layout       | Adopt a foreign skill into astra or export a member to spec    |
| Analyze a source       | Convert and survey a PDF/book/document into an evidence report |
| Generate from analysis | Render a skill from a recorded analysis or resumed run state   |
| Update a skill         | Propose folding a new source into an existing skill            |
| Maintain Forge         | Changes and session reviews of this repository                 |

## How It Works

A creation request runs a five-phase pipeline:

1. **Initialization** - classify the operation and interaction mode, open a dated
   gitignored run workspace, and start the run-state ledger.
2. **Research foundation** - define the question, plan bounded gathering, extract
   and cite evidence, and note conflicts and gaps.
3. **Architecture design** - map the distilled knowledge onto the skill router:
   triggers, operations, resource files, and the resolved profile's
   compatibility matrix.
4. **Generation** - render the template set with the approved context into a
   scratch staging area, validate, then write the target.
5. **Finalization** - run the validation suite and deliver the summary report.

External documents convert through an approved local converter - MarkItDown when
installed or previously approved - with provenance, injection screening, and
extraction-quality reporting. Raw source text stays in scratch, only derived,
attributed knowledge lands in the generated skill.

## Directory Tree

```
forge-skill/
├── SKILL.md          # Runtime router - modes, update check, operations, boundaries
├── AGENTS.md         # Agent entry point for maintaining this repository
├── README.md         # This file
├── CHANGELOG.md      # Release history
├── LICENSE           # MIT
├── process/          # Pipeline, conversion, research, and shared contracts
├── references/       # Specifications, conventions, and methodology evidence
├── templates/        # Generation skeletons and the output-path map
├── scripts/          # Mechanical tools: validation, rendering, conversion
├── docs/             # Governance: STYLE, VERSIONING, MAINTENANCE, CONTRIBUTING, SECURITY
├── evals/            # Behavioral regression prompts
└── tests/            # Deterministic unit tests and synthetic fixtures
```

## Requirements

- An agent environment with file access and Python 3.10+.
- No network access for local sources. Remote fetching, cloning, and package
  installation always require explicit approval - including in fully autonomous
  mode, which skips them instead.
- MarkItDown is optional: needed only to convert binary documents such as PDF or
  DOCX. Plain text and Markdown sources work without it.

## Usage

Activate through your agent environment's skill mechanism, then name the task:

```
use forge
forge a skill for municipal permit workflows from this handbook.pdf
create a portable spec-layout skill for release notes
package the release-notes skill as a Claude Code plugin
adopt this external skill into astra
create a skill collection for our support tooling, autonomously
analyze this EPUB for a new skill, verbose
generate the skill from the recorded analysis
```

Every operation accepts `autonomous`, `fully autonomous`, and `verbose` flags -
see `process/decision-modes.md` for the authoritative matrix.

## Limitations

- Forge generates document sets, it does not invent domain expertise. A blocked
  essential phase produces a partial run, not an ungrounded skill.
- Automatic fold-in of new sources into an existing skill is deferred - the
  Update operation reports a proposed fold only.
- Conversion quality is best effort: scanned PDFs need a separate OCR path, and
  extraction loss is reported, never hidden.
- Self-healing routing and live model benchmarking are deferred enhancements.

## License

MIT - see `LICENSE`.
