# Tools

**Status:** Native and MCP tools are accepted. Contracts are finalised before Phase 5.

## Responsibilities

The tool platform registers approved tools; shows the model a scoped set of definitions; validates proposed arguments; checks policy outside the model; executes with controlled identity, timeout, cancellation, and concurrency; normalises output and errors; and records intent and outcome.

## Tool definition

Illustrative only. The real version uses enums and immutable value objects.

```python
class ToolDefinition:
    name: str
    description: str
    input_schema: dict
    output_schema: dict | None
    required_scopes: set[str]
    risk_class: str
    side_effects: str
    timeout_seconds: float
    retry_profile: str
    idempotency_mode: str
    concurrency_group: str | None
    execution_backend: str
```

Risk, scopes, side effects, and backend come from trusted registration, never from the model or an MCP server.

Each invocation carries an invocation ID, run and step IDs, caller identity, tool version, validated arguments, the policy decision, a deadline, an idempotency key where relevant, and correlation metadata.

## Tool kinds

**Native tools.** In-process functions for trusted, bounded capabilities. Small, typed, with explicit side effects. Native does not mean safe: a function can still read secrets or reach the network.

**MCP tools.** Discovered and called through an MCP client adapter. MCP is an interoperability protocol, not our scheduler, database, authorisation system, or isolation boundary. Server metadata and outputs are untrusted. A server's own description of a tool grants it nothing.

**File tools.** The first real tools, for the reference use case ([ADR 0011](adr/0011-file-agent-reference-use-case.md)). `search_files` runs full-text search over the caller's approved folders and returns passages with path, section, line range, modification time, and document version where known. `read_file` returns a bounded passage. Both resolve every path against the caller's grants after canonicalisation, refuse symlinks that leave a grant, and refuse the always-blocked list ([security spec](SECURITY_SPEC.md#file-access)). File contents are untrusted input to the model.

**Execution tools** (later). Filesystem, shell, browser, and code go through the execution broker. There is never a generic `shell` tool inside the API or runtime process.

## Risk tiers

| Tier | Meaning | Examples | Default policy |
|---|---|---|---|
| `read` | No side effects | `search_files`, `read_file` | Allowed within grants |
| `write_reversible` | Changes that can be undone from a journal | Writing a report to the output folder; rename or move with undo | Allowed in the output folder; approval elsewhere |
| `external` | Effects outside the platform's control, or irreversible | Sending a message, deleting a file, network calls, running code | Approval required, or denied by default |

The tier comes from trusted registration, never from the model or an MCP server. The list is extensible: a new tier gets added with a new kind of effect, not in advance.

## Invocation lifecycle

1. The model proposes a name and arguments.
2. Check the tool exists in the run's allowed registry snapshot.
3. Validate the arguments against the schema. Reject extra fields.
4. Look up risk, scopes, side effects, and backend from trusted configuration.
5. Policy decides: allow, deny, or require approval.
6. The dispatcher checks deadline, concurrency, resources, and idempotency.
7. Persist intent before any external side effect that needs recovery.
8. Execute through the native, MCP, or broker adapter.
9. Normalise and size-limit the output, and label it as untrusted.
10. Persist the result, or record an uncertain outcome, and emit events.
11. Return the sanitised result to the model.

A database transaction cannot atomically include a remote side effect. Model that gap explicitly.

## Errors

Distinguish: schema invalid, unknown or unavailable tool, not authorised, approval required, rate limited, timed out, cancelled, remote error, protocol error, output invalid or too large, and outcome unknown. Never return secrets or raw stack traces to the model. Retry behaviour comes from the tool's retry profile and idempotency mode.

## MCP requirements

- Use the official Python SDK first; the TypeScript SDK is for Node-native servers.
- Pin the SDK version and protocol revision, and check migration notes when implementing.
- Write protocol contract tests.
- Keep the server session lifecycle separate from the run lifecycle.
- Scope server connections and allowed tools to the requesting identity and run.
- Handle disconnects and stale capability lists.
- Never import executable code supplied by an MCP server.

## Policy

- Deny by default; each agent and run gets the least privilege it needs.
- An approval binds to the exact operation, an argument digest, the identity, and an expiry. Changed arguments need a new approval.
- Write and sensitive tools must have an explicit risk classification.
- Tool output can carry prompt injection. Delimit it as untrusted and never let it override policy.
- Bound output size, execution time, and concurrency.
- Audit the tool version, identity, input digest, policy result, and outcome, subject to redaction.

## Tests

Native and MCP produce the same envelope; schema rejection; unknown tool; unauthorised tool; arguments changed after approval; timeout; cancellation; oversized output; malformed protocol response; server disconnect; duplicate invocation; uncertain side-effect outcome; prompt injection in tool output.
