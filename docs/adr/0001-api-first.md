# ADR 0001: API and SDK as the Product Boundary

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

The platform may eventually be driven from a CLI, web inspector, IDE, CI job, or other automation. Building those surfaces first would scatter orchestration, permission, and state logic across clients.

## Decision

A versioned API and event protocol is the only client boundary. Every human-facing interface is a client of it. A minimal SDK or reference client gets built only when it is needed to exercise the API end to end. No UI is needed for the first vertical slice.

## Consequences

- Commands, queries, event schemas, and idempotency need deliberate design.
- Clients contain no agent-loop or authorisation logic.
- SSE is the initial event transport, and its reconnect and replay behaviour must be specified.
- A UI can be added later without changing runtime semantics.

## Revisit when

An interaction needs a different transport, or a minimal visual inspector would materially speed up debugging.
