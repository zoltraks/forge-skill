# Operation Timing

## Purpose

> **Scope:** Elapsed-time reporting for operations, armed by default on every
> operation the skill answers.
> **Key items:** default arming, opt-out, clock capture, closing report, coverage

This file defines how Forge reports the time an operation took.

## Trigger

Timing is armed by default on every operation the skill answers - the bare
activation's once-per-session update check and every task request alike.

Naming `no timing`, `without timing`, or an equivalent opt-out on the request
disarms it for that request only - the default re-arms on the next request.

The verbose, diagnostic, and timing modes additionally emit the parameter document
of `process/json-exchange.md` - that file owns the parameter-document emission,
this file owns only the timing report.

The informational mode adds nothing beyond the timing paragraph - no parameter
document emits and no option lists expand.

A named mode is request-scoped - it is named in the request text and is never
resolved from environment variables.

## Timing

The agent notes the system clock before starting the operation's work.

## Report

The response ends with a separate paragraph whose single sentence is the last
sentence of the response: `<description> operation took <m:ss>`, where
`<description>` is a short phrase naming the operation the last user query asked
for and `<m:ss>` is the elapsed time in minutes:seconds.

## Performance Analysis

An operation that runs longer than three minutes closes with a breakdown table
placed immediately before the timing sentence.

| Stage    | Elapsed  | Share  | Note                            |
|----------|----------|--------|---------------------------------|
| `<name>` | `<m:ss>` | `<n>%` | what consumed or saved the time |

The rule binds every long operation the session runs, not only the skill's own
procedures. Stage times come from command-reported elapsed values, recorded clock
captures, or output timestamps - when none exists, the note says so instead of
guessing.

## Progress Heartbeat

While a backgrounded command runs past about a minute, the agent reports progress
roughly every 60 seconds - the output printed since the last note aggregated into
one short line carrying the current stage, items done of the total, and warnings
seen. A poll that finds no new output still earns a brief "still in <stage>" line.

## Agent Identity

A verbose, diagnostic, or timing report names the driving agent and model ahead of
the stage table. Detection follows a ladder - an explicit value named in the
request, then the tool's own namespace variables, then known environment markers
(`AI_AGENT` carrying `devin` proves Devin, `CLAUDECODE` and `CLAUDE_CODE_*` prove
Claude Code, `CODEX_*` proves Codex, `CURSOR_TRACE_ID` proves Cursor,
`ANTIGRAVITY_*` proves AntiGravity, `GEMINI_CLI` proves Gemini, `QWEN_CODE` proves
Qwen, a `windsurf` `ACP_BACKEND` proves a Windsurf-family host), then configured
settings keys, then agent self-declaration for what stays unresolved. The markers
identify the host product best-effort - an unresolved value reports `unset`, an
honest answer rather than a failure.

## Coverage

The timing covers every operation the skill answers - a bare activation times its
once-per-session update check, and task requests time the task work.
