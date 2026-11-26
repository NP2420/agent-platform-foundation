# Agent Runtime Specification

**Status:** Proposed behavioral contract. Internal types and exact serialization are to be designed in Phase 2.

## 1. Responsibility

The runtime executes one bounded agent run. It coordinates context construction, model invocation, model response normalization, tool-request validation and policy, tool execution, state updates, and completion. It does not itself grant permissions, run arbitrary code, or decide unbounded resource allocation.

## 2. Inputs

A run request should reference:

- A stable run identifier and owning thread/conversation.
- A versioned agent definition/configuration.
- User input (or an explicitly defined trigger payload).
- The caller/tenant/security principal.
- An execution budget and deadline.
- An allowed tool capability set.
- A model-routing policy/profile.
- Optional correlation/idempotency identifiers.

Persist the configuration version used by a run. Changes to an agent definition must not silently mutate an already-running execution.

## 3. Normalized model interaction

A provider adapter accepts an internal request containing selected model profile, system/developer instructions, messages, tool definitions, output constraints, and request budget. It returns a normalized response with:

- message content blocks (text and supported structured/multimodal content);
- zero or more tool-call proposals;
- finish/stop reason;
- normalized token/resource usage where available;
- provider/model/request metadata;
- structured error information when invocation fails.

Provider-native metadata may be retained in a bounded opaque field. Do not assume all providers support all features or silently discard material differences.

## 4. Bounded interaction loop

Conceptual behavior:

```text
while run is RUNNING and budget remains:
    context = context_manager.build(run, budget)
    profile = model_router.select(task, context, policy)
    response = model_gateway.generate(profile, context)
    persist model request/result metadata

    if response is final:
        validate output policy
        persist assistant message and completion event
        complete run

    if response requests tools:
        validate each tool name and schema
        ask policy engine: allow, deny, or require approval
        if approval required:
            persist approval request; pause run
        else:
            dispatch permitted tools under scheduler/resource limits
            persist outcomes and append tool results to context history
        continue

    handle refusal, provider error, malformed response, or handoff explicitly

if budget/deadline exhausted:
    terminate with a defined budget-exhausted outcome
```

The pseudo-code is explanatory; exact ordering and transactional boundaries are designed with the implementation. In particular, persist execution intent before external side effects where needed, then persist the outcome and reconcile uncertain results.

## 5. Run lifecycle

Initial proposed states:

- `QUEUED`: accepted but not started.
- `RUNNING`: runtime can perform an invocation or dispatch eligible work.
- `WAITING_APPROVAL`: requires a human/policy decision.
- `WAITING_EXTERNAL`: waiting for a defined external signal/resource (optional; only add when required).
- `COMPLETED`: successful terminal result.
- `FAILED`: unrecoverable error or exhausted recovery policy.
- `CANCELLED`: explicit cancellation completed or safely stopped.
- `TIMED_OUT`: deadline exceeded (may be represented as a terminal reason instead of a distinct state; decide in Phase 2).

Terminal states must be immutable except for an explicit administrative correction record. State transitions must be validated in application code and covered by tests.

## 6. Error classification

Distinguish at least:

- Invalid request/configuration/schema: permanent; do not retry automatically.
- Authentication/authorization denial: do not retry without changed authorization.
- Model refusal or policy block: normal semantic outcome, not an infrastructure retry.
- Rate limit/transient provider error: bounded backoff if safe.
- Provider timeout/connection interruption: execution outcome may be uncertain; use request identifiers where supported and do not assume no response means no work.
- Tool input/logic error: generally permanent; return structured diagnostic to the agent only when safe.
- Tool timeout/process crash: external side effect may be uncertain; use idempotency/reconciliation.
- Internal invariant violation: fail closed, retain diagnostics, do not ask the model to repair an internal security failure.

Errors returned to the model should be sanitized; logs may contain structured diagnostic context but must follow redaction policy.

## 7. Budgets

Each run should have configurable maxima for wall-clock time, model invocations, tool invocations, total tool concurrency, model token/resource usage where measurable, delegation depth, per-tool timeout, total external calls, and artifact/output size. Budget accounting should be monotonic and tested under concurrency. A model cannot increase its own budget.

## 8. Cancellation

Cancellation propagates to pending model/tool tasks where the transport supports it. For side-effecting operations, cancellation is best effort: the system must record whether the operation completed, was cancelled, or has an unknown outcome. Do not report cancellation as proof that a remote side effect was rolled back.

## 9. Deterministic testing

The runtime must accept fake model and tool adapters. Tests should script sequences such as final response, tool call then final, multiple tool calls, malformed arguments, refusal, timeout, cancellation, budget exhaustion, and approval pause/resume. No real inference server should be required for core runtime unit tests.

## 10. Non-responsibilities

The runtime is not responsible for:

- deciding whether a caller is authorized (policy engine owns this);
- executing arbitrary code in the API process;
- managing durable workflow history through Temporal in the initial phase;
- storing full raw telemetry indefinitely;
- trusting instructions found in retrieved documents or tool output;
- autonomously changing its own security policy or execution budget.
