# API and Event Protocol Specification

**Status:** API/SDK-first is agreed. Endpoint paths and exact wire schemas are proposed contracts to refine during Phase 8.

## 1. Boundary principle

The API is the platform's client boundary. CLI, web inspector, IDE, CI, and other automation should be thin clients of the same commands, queries, and event protocol. No client should implement agent-loop logic, authorization policy, or tool execution independently.

Initial transport: HTTP/JSON for commands and queries; Server-Sent Events (SSE) for server-to-client run events. A Python SDK may wrap the API. WebSockets are not required unless bidirectional streaming requirements emerge.

## 2. Proposed endpoints

| Method/path | Purpose |
|---|---|
| `POST /v1/runs` | Create a run with agent/version, input, and policy-bounded options |
| `GET /v1/runs/{run_id}` | Fetch current run state/summary |
| `GET /v1/runs/{run_id}/events` | Subscribe/replay events using SSE |
| `GET /v1/runs/{run_id}/steps` | Inspect execution steps |
| `POST /v1/runs/{run_id}/cancel` | Request cancellation |
| `POST /v1/runs/{run_id}/approvals/{approval_id}` | Submit approve/deny decision |
| `GET /v1/threads/{thread_id}` | Fetch thread metadata |
| `GET /v1/threads/{thread_id}/messages` | Fetch paginated messages |
| `GET /v1/agents` | List configured agent definitions/versions (local administrative scope initially) |
| `GET /health` | Liveness/health endpoint with no sensitive details |
| `GET /ready` | Readiness for required dependencies (policy-dependent) |

Do not expose arbitrary internal repository/database operations as public endpoints.

## 3. Run creation contract

Run creation should accept an agent/version reference, thread or new-thread choice, user input, optional explicitly allowed options (not arbitrary model overrides), and client idempotency key. The server resolves caller identity, authorized agent/tool scopes, and run budgets from trusted configuration. The model cannot choose a higher privilege, deadline, or token budget than policy permits.

## 4. Event envelope

Proposed event fields:

```json
{
  "event_id": "stable-unique-id",
  "schema_version": 1,
  "run_id": "run-id",
  "sequence": 12,
  "type": "tool.completed",
  "occurred_at": "RFC3339 timestamp",
  "correlation_id": "request-or-workflow-id",
  "causation_id": "optional-prior-event-or-command-id",
  "data": {}
}
```

Exact IDs and timestamp representation will be selected during implementation. Payloads must be versioned and bounded. Sensitive raw prompts, credentials, full file contents, and private tool outputs should not be copied into every event.

Initial event types may include:

- `run.accepted`, `run.started`, `run.paused`, `run.resumed`, `run.completed`, `run.failed`, `run.cancelled`;
- `model.requested`, `model.completed`, `model.failed`;
- `tool.requested`, `tool.authorized`, `tool.denied`, `tool.started`, `tool.completed`, `tool.failed`;
- `approval.required`, `approval.decided`;
- `plan.validated`, `plan.rejected`, `step.started`, `step.completed`, `step.failed`;
- `budget.warning`, `budget.exhausted`.

Treat names as proposed; define a stable catalog and state that they describe facts rather than UI animations.

## 5. SSE delivery

- Events should have stable IDs suitable for SSE `id` fields.
- Support reconnect/replay using `Last-Event-ID` or a documented cursor query.
- Document ordering scope (for example, monotonically ordered within a run).
- Clients must handle duplicate delivery and reconnect; event handling should be idempotent.
- Do not claim global ordering across independent runs.
- Heartbeats and backpressure behavior must be defined.

## 6. Idempotency and concurrency

Run creation should accept an idempotency key; server stores the mapping and returns the original logical run for a valid duplicate. Define key scope and expiry. Cancellation and approval commands must be idempotent or return clear conflict semantics. Race handling (two approvals, approval while cancellation occurs, duplicate cancel) must be tested.

## 7. Authentication and exposure

Initial local API should bind to loopback by default. Even on localhost, consider other local processes/users and CSRF/SSRF risks based on client type. Any non-loopback binding needs authentication, authorization, transport protection, and an explicit deployment configuration. Do not treat “local” as a universal trust boundary.

## 8. Error envelope

Use stable machine-readable error codes, human-readable safe messages, correlation/request identifiers, retryability classification, and optional validation details. Do not return stack traces, local absolute paths, secrets, or raw provider exception dumps to clients.

## 9. Contract versioning

Version the public API path and event schema independently where necessary. Use additive changes where possible. Maintain contract tests and document deprecation. Keep Python SDK types generated/derived from authoritative schemas where practical, but do not make the SDK the only definition of the API contract.
