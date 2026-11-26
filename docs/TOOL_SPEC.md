# Tool Platform Specification

**Status:** Native tools and MCP tools are agreed directions. Exact contracts are to be finalized before implementation.

## 1. Tool platform responsibilities

- discover/register approved tools;
- provide the model with an appropriately scoped tool description/schema;
- validate proposed arguments at runtime;
- check authorization and policy outside the model;
- execute with controlled identity, timeout, cancellation, concurrency, and resource policy;
- normalize outputs/errors;
- persist invocation intent/outcome and emit events;
- enforce data redaction and trust boundaries.

## 2. Unified internal tool contract

A conceptual definition:

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

This is illustrative, not final code. Prefer explicit enums/value objects and immutable definitions in implementation. Do not trust risk, permission, or execution-backend fields supplied by the model; derive these from registered configuration.

Each invocation should include a stable invocation ID, run/step ID, caller identity, tool version, validated arguments, policy decision, deadline, idempotency key when relevant, and correlation metadata.

## 3. Tool categories

### Native tools

Direct in-process functions for trusted, bounded application capabilities. Keep them small, typed, and side-effect explicit. Native does not mean automatically safe: a function can still read secrets, access files, or make network requests.

### MCP tools

External capabilities discovered and invoked through an MCP client adapter. MCP provides interoperability for tools/resources/prompts; it is not our scheduler, database, application authorization system, or isolation boundary.

MCP server metadata and tool outputs are untrusted. Enforce local allowlists, scopes, timeouts, response-size limits, and output handling. The MCP server's own tool definition does not grant it permission to act on behalf of the local user.

### Future execution tools

Filesystem, shell, browser automation, and arbitrary code should use an execution broker and isolated worker. Do not expose a generic unrestricted `shell` function inside the main API/runtime process.

## 4. Invocation lifecycle

1. Model proposes tool name and arguments.
2. Runtime verifies the tool exists in the run's allowed registry snapshot.
3. Validate the arguments against the schema and reject additional/ambiguous fields according to policy.
4. Derive risk, required scopes, side-effect class, and backend from trusted tool configuration.
5. Policy engine authorizes, denies, or creates an approval request.
6. Dispatcher checks deadlines, concurrency, resource, and idempotency rules.
7. Persist invocation intent before performing an external side effect when required by the operation's recovery contract.
8. Execute through native/MCP/broker adapter.
9. Normalize and size-limit output; treat returned content as untrusted data.
10. Persist result or uncertain outcome and emit lifecycle events.
11. Return sanitized result to the agent context.

Exact database transaction behavior depends on whether the operation is local, database-backed, or remote. A transaction cannot atomically include an arbitrary remote API side effect.

## 5. Error model

Distinguish schema invalid, tool unavailable, not authorized, approval required, rate-limited, timed out, cancelled, remote error, protocol error, output invalid/too large, and outcome unknown. Do not return raw secrets or unrestricted stack traces to the model. Retry decisions derive from an explicit retry profile and side-effect/idempotency behavior.

## 6. MCP implementation requirements

- Use the official Python SDK for the initial Python MCP client/server work; TypeScript SDK is available for Node-native integrations.
- Verify SDK version, current MCP protocol revision, transport, authentication, and migration guidance when implementing; the MCP SDK major versions and examples can change.
- Pin SDK versions and add protocol contract tests.
- Distinguish server transport/session lifecycle from application run lifecycle.
- Scope server connections and allowed tools to the requesting identity/run.
- Handle server disconnects and stale capability definitions.
- Do not permit untrusted MCP servers to supply executable code to be imported into the trusted application.

## 7. Security policy

- Deny by default.
- Least-privilege tool exposure per agent/run.
- Approval tied to a specific operation, arguments or argument digest, identity, and expiry; changed arguments require a new decision.
- Sensitive/write tools require explicit policy classification.
- Tool output can contain prompt injection; delimit/label it as untrusted and never let it override system policy.
- Bound output size, execution time, response count, and concurrency.
- Audit tool version, identity, input digest, policy result, and outcome while applying privacy/redaction rules.

## 8. Tests

Native/MCP parity on the common envelope; schema rejection; unknown tool; unauthorized tool; changed arguments after approval; timeout; cancellation; oversized output; malformed protocol response; server disconnect; duplicate invocation; uncertain side-effect outcome; and prompt-injection content returned by a tool.
