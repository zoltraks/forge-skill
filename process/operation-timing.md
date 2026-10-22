# Operation Timing

## Purpose

> **Scope:** Elapsed-time reporting for named operations under a verbose,
> informational, or diagnostic request mode.
> **Key items:** mode trigger, clock capture, closing report, coverage

This file defines how Forge reports the time a named operation took.

## Trigger

Timing arms when the request names a verbose, informational, or diagnostic
mode.

The three mode names share the diagnostic surface defined in
`process/json-exchange.md` - that file owns the parameter-document emission,
this file owns only the timing report.

The mode is request-scoped - it is named in the request text and is never
resolved from environment variables.

## Timing

When timing is armed and the request names an operation, the agent notes the
system clock before starting the work.

## Report

The response ends with a separate paragraph whose single sentence is the last
sentence of the response: `<description> operation took <m:ss>`, where
`<description>` is a short phrase naming the operation the last user query
asked for and `<m:ss>` is the elapsed time in minutes:seconds.

## Coverage

The timing covers task requests - the activation standby and the enablement
response carry no timing line.
