# ADR 0001: API/SDK-First Product Boundary

- **Status:** Accepted direction
- **Date:** 2026-11-25

## Context

The platform may later be used through a CLI, web inspector, IDE extension, CI job, or automation client. Building each surface first risks duplicating orchestration, permission, and state logic in user interfaces.

## Decision

Treat a versioned API and event protocol as the primary client boundary. Human-facing interfaces are clients of this boundary. Build a minimal SDK/reference client only when needed to validate the API end-to-end. No full UI is required for the first runtime vertical slice.

## Consequences

- API commands, queries, event schemas, and idempotency must be designed deliberately.
- Clients do not contain agent-loop or authorization logic.
- SSE is the initial event-stream candidate; reconnect/replay behavior must be specified.
- A UI can be added later without changing runtime semantics.

## Revisit when

A concrete interaction requirement needs a different transport or a minimal visual inspector materially improves debugging.
