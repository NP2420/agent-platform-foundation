# API and Event Protocol

**Status:** API-first is accepted. Paths and wire schemas are proposals, refined in M2.2.

## Boundary

The API is the only client boundary. A CLI, web inspector, IDE, or CI job is a thin client of the same commands, queries, and events; none of them reimplements the agent loop, authorisation, or tool execution.

Transport: HTTP/JSON for commands and queries, Server-Sent Events for run events. A Python SDK may wrap it. WebSockets only if a real bidirectional need appears.

## Endpoints

| Method and path | Purpose |
|---|---|
| `POST /v1/runs` | Create a run (agent version, input, idempotency key) |
| `GET /v1/runs/{run_id}` | Current state and summary |
| `GET /v1/runs/{run_id}/events` | Stream and replay events (SSE) |
| `GET /v1/runs/{run_id}/steps` | Execution steps |
| `POST /v1/runs/{run_id}/cancel` | Request cancellation |
| `POST /v1/runs/{run_id}/approvals/{approval_id}` | Approve or deny |
| `GET /v1/threads/{thread_id}` | Thread metadata |
| `GET /v1/threads/{thread_id}/messages` | Paginated messages |
| `GET /v1/agents` | Configured agents and versions |
| `GET /health` | Liveness, with no sensitive detail |
| `GET /ready` | Dependency readiness |

## Creating a run

The client sends an agent version, a thread (or "new"), the input, a small set of allowed options (not arbitrary model overrides), and an idempotency key. The server resolves identity, tool scopes, and budgets from trusted configuration. Nothing in the request or the model output can raise privileges, deadlines, or budgets beyond policy.

## Triggers

Runs can also start from a schedule or an event (for example, a file appearing in a watched folder). A trigger calls the same create-run command, under a configured principal and the same policy checks. It never gets a side door.

## Event envelope

```json
{
  "event_id": "stable-unique-id",
  "schema_version": 1,
  "run_id": "run-id",
  "sequence": 12,
  "type": "tool.completed",
  "occurred_at": "2026-11-26T05:00:00Z",
  "correlation_id": "request-id",
  "causation_id": "optional-prior-event-or-command",
  "data": {}
}
```

Payloads are versioned and bounded. Raw prompts, credentials, file contents, and private tool output are not copied into events.

Initial event types (names are provisional; events describe facts, not UI states):

- `run.accepted|started|paused|resumed|completed|failed|cancelled`
- `model.requested|completed|failed`
- `tool.requested|authorized|denied|started|completed|failed`
- `approval.required|decided`
- `plan.validated|rejected`, `step.started|completed|failed`
- `budget.warning|exhausted`

## SSE delivery

- Event IDs go in the SSE `id` field. Reconnection uses `Last-Event-ID` or a cursor parameter.
- Ordering is guaranteed within a run only, never globally.
- Delivery is at-least-once, so clients must handle duplicates.
- Heartbeat and backpressure behaviour are defined.

## Idempotency and races

A duplicate `POST /v1/runs` with the same key returns the original run. Key scope and expiry are documented. Cancel and approve are idempotent or return a clear conflict. Tests cover two concurrent approvals, approval racing cancellation, and duplicate cancels.

## Exposure

Binds to loopback by default. Localhost is not a trust boundary in itself: consider other local processes and CSRF from browsers. Any non-loopback binding requires authentication, TLS, and explicit configuration. Authentication, tokens, sessions, and CSRF are in the [security spec](SECURITY_SPEC.md#identity-m31).

## Errors

A stable machine-readable code, a safe human message, a correlation ID, a retryable flag, and optional validation details. Never stack traces, absolute paths, secrets, or raw provider errors.

## Versioning

The URL path and the event schema are versioned independently. Prefer additive changes, contract-test them, and document deprecations. If SDK types are generated, generate them from the schemas; the SDK is never the only definition of the contract.
