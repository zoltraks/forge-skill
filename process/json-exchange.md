# JSON Parameter Exchange

## Purpose

> **Scope:** Emit and consume machine-readable parameter documents in place of, or
> alongside, the question surfaces of the generation and maintenance workflows.
> **Key items:** emission trigger, diagnostic output, emitted document, parameter
> catalog, returned document, authority

This file defines how Forge exposes its intake questions as JSON and how it consumes
JSON answers.

## When To Emit

When the request asks for the questions, settings, or parameters "in JSON", "as JSON",
or another machine-readable format, emit a parameter document instead of the question
prompts.

Detection and default resolution still run first: the document contains only the
questions that are actually pending in this session.

Emit the document where the request directs - inline in the response by default, inside
a fenced `json` block.

## Diagnostic Output

When the request names a debugging mode, a diagnostic mode, or asks for detailed or
verbose information, emit the parameter document for information purposes only.

The document covers only surfaces that are actually pending - diagnostics expose the
intake state and never create a question.

When no surface is pending, nothing emits - no parameter document, no
pending-decisions note, and no question prompts.

The emission order is fixed: the JSON document first, then a text description of the
pending decisions, then the question prompts.

The question prompts still run. The emitted document does not replace the question
flow.

## Emitted Document

The document carries a `description`, context fields (`target`, `task`, `date`,
`time`), and an `intake` array.

- `target` - the skill directory, collection directory, or source the task centers on.
- `task` - the classified task: `create-skill`, `create-collection`,
  `analyze-source`, `generate-from-analysis`, `update-skill`, or `maintain`.
- `date` - the current day in `YYYY-MM-DD` format.
- `time` - the local time in `hh:mm:ss` followed by the timezone offset.

`task` emits as an empty string when no task is classified yet - enable mode has none.

Each parameter object keeps a fixed key order: `id`, `question`, `answer`,
`description`, `type`, `menu`, `default` - the `default` key is always the last key of
the object.

- `id` - a stable kebab-case identifier for the parameter.
- `question` - the literal question wording presented to the answering side.
- `answer` - emitted as an empty string, or an empty array for `selection`, to be
  filled by the answering side.
- `description` - what the parameter controls and the detection evidence behind its
  default.
- `type` - `choice` for a single-option answer taken from `menu`, `selection` when
  multiple options may be chosen, or `text` for free input.
- `menu` - required for `choice` and `selection` types and omitted for `text`,
  letter-keyed (`A`, `B`, `C`, ...), and the recommended option label carries
  "(recommended)". A menu lists at most three candidate options plus a trailing
  `Cancel - abort the operation` entry, and `Cancel` is never the `default`.
- `default` - the option letter or suggested text applied when the answer stays empty.

```json
{
    "description": "Intake parameters for <target>",
    "target": "<skill-or-collection-directory>",
    "task": "create-skill",
    "date": "2026-10-19",
    "time": "13:45:21 GMT+2",
    "intake": [
        {
            "id": "research-depth",
            "question": "How deep should the gathering run go?",
            "answer": "",
            "description": "Sets the gathering bound - the supplied sources already cover the requested scope.",
            "type": "choice",
            "menu": {
                "A": "Focused - the supplied sources only (recommended)",
                "B": "Extended - supplied sources plus approved additions",
                "C": "Cancel - abort the operation"
            },
            "default": "A"
        }
    ]
}
```

## Parameter Catalog

Every pending question surface emits with a stable kebab-case `id`:

| Parameter                 | Type        | Surface                                                              |
|---------------------------|-------------|----------------------------------------------------------------------|
| `skill-selection`         | `choice`    | Generic activation phrase with several candidate skills              |
| `mode-selection`          | `choice`    | Request mixes conflicting enable, operation, and maintenance signals |
| `operation-selection`     | `choice`    | Target-scoped activation pending the operation to run on the target  |
| `skill-name`              | `text`      | The generated skill's slug when no safe default exists               |
| `skill-purpose`           | `text`      | One-line purpose and scope for the generated skill                   |
| `target-location`         | `text`      | Output directory for the generated skill or collection               |
| `research-depth`          | `choice`    | Gathering bound: focused, extended, or exhaustive                    |
| `source-selection`        | `selection` | Which inventoried sources enter the gathering plan                   |
| `collection-members`      | `selection` | Which proposed member skills the collection generates                |
| `checkpoint-confirmation` | `choice`    | Material phase checkpoint: proceed, adjust, or cancel                |
| `permission-request`      | `choice`    | A separately gated action: network, install, overwrite, publish      |
| `session-review-approval` | `choice`    | Approve the session-review findings report before applying changes   |

Parameters that mirror `process/forge-workflow.md` decision points follow that
document's question wording and option order. This file describes the envelope, not
the questions.

## Returned Document

The answering side may return the document with `answer` fields filled.

Answers arriving as prompt selections or natural-language responses are equivalent.

A returned document that resolves every pending surface is applied without re-asking.

Validation failures - an `answer` letter outside `menu`, a `selection` carrying no
entry, a `choice` answer that ignores `Cancel` - re-emit the document in diagnostic
mode with the failure named, then continue the question flow.

## Autonomous Surfaces

A procedure that defines an autonomous mode - the session review's flag in
`process/session-review.md`, and every operation gate under the interaction modes of
`process/decision-modes.md` - resolves each of its pending surfaces to the recommended
option without waiting.

The document emits with the resolved value in `answer` instead of the empty string, and
the resolution is reported in the reply like an answered question.

A verbose flag additionally reports the full `menu` and the rationale behind each
resolved default.

Under `fully autonomous` no question surface emits at all - surfaces that cannot be
resolved safely are recorded as skipped decisions, never as empty prompts.

## Authority

The emitted document describes pending decisions. It never performs the operation.

A filled document returned with answers is user input of the same rank as an
interactive answer - the permission boundaries of `process/decision-modes.md` still
govern what may run without asking.
