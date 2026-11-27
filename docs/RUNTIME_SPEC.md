# Runtime and Orchestration

**Status:** Proposed. Internal types and serialisation are designed in M1.2. The scheduler and plan schema are finalised in M4.2.

## Runtime responsibility

The runtime executes one bounded run. It builds context, calls the model, normalises the response, validates and authorises tool requests, dispatches them, updates state, and decides when the run is done. It does not grant permissions, run arbitrary code, or allocate unbounded resources.

## Run inputs

- run ID and owning thread;
- agent configuration version (persisted with the run, so later edits never change a run already in progress);
- user input or trigger payload;
- caller identity;
- budget and deadline;
- allowed tool set;
- model profile or routing policy;
- correlation and idempotency IDs.

## The loop

```text
while run is RUNNING and budget remains:
    context  = context_manager.build(run, budget)
    profile  = router.select(task, context, policy)
    response = gateway.generate(profile, context)
    record model call metadata

    if response is final:
        check output policy, persist message, complete run

    elif response has tool calls:
        for each call: validate name and arguments, ask policy
        if any call needs approval: persist request, pause run
        else: dispatch allowed calls under scheduler limits,
              persist outcomes, append results to history

    else: handle refusal, provider error, or malformed response explicitly

on budget or deadline exhaustion: end with a budget-exhausted outcome
```

This is illustrative. The exact ordering and transaction boundaries are designed with the code. The fixed rule: persist intent before any external side effect, then persist the outcome, and reconcile when the outcome is uncertain.

## Normalised model response

The provider adapter returns content blocks, zero or more tool-call proposals, a finish reason, usage (reported, estimated, or unavailable), provider and model metadata, and a structured error on failure. Provider-specific extras go in a bounded opaque field. Capability differences are kept visible, not flattened away.

## Run lifecycle

| State | Meaning |
|---|---|
| `QUEUED` | Accepted, not started |
| `RUNNING` | May call the model or dispatch work |
| `WAITING_APPROVAL` | Blocked on a human or policy decision |
| `WAITING_EXTERNAL` | Blocked on a defined external signal. Add only when needed. |
| `COMPLETED` | Terminal success |
| `FAILED` | Unrecoverable error, or recovery exhausted |
| `CANCELLING` | Cancellation requested; no new work starts, and in-flight model or tool calls are settling |
| `CANCELLED` | Cancellation completed. Each in-flight operation is recorded as completed, cancelled, or unknown. |

A deadline or budget overrun is a **reason on `FAILED`**, not its own state: `FAILED` carries a terminal reason such as `deadline_exceeded`, `budget_exhausted`, or `error` (decided 2026-11-26). New failure kinds add a reason, not a state.

Terminal states never change, apart from an explicit administrative correction record. Transitions are validated in application code and covered by tests.

## Error classes

| Class | Handling |
|---|---|
| Invalid request, configuration, or schema | Permanent. No retry. |
| Authorisation denied | No retry without a changed grant |
| Model refusal or policy block | A normal outcome, not a fault |
| Rate limit or transient provider error | Bounded backoff, where safe |
| Provider timeout or dropped connection | Outcome may be unknown. Don't assume no work was done. |
| Tool input or logic error | Usually permanent. Return a sanitised diagnostic to the model when safe. |
| Tool timeout or crash | Side effect may be unknown. Reconcile using idempotency. |
| Internal invariant violation | Fail closed and keep diagnostics. Never ask the model to repair it. |

Errors shown to the model are sanitised. Logs carry full structured context, subject to redaction.

## Budgets

Per run: wall-clock time, model calls, tool calls, tool concurrency, tokens where measurable, delegation depth, per-tool timeout, external calls, and output size. Accounting is monotonic and correct under concurrency. The model cannot raise its own budget.

## Cancellation

Cancellation propagates to pending model and tool tasks where the transport allows it. For side-effecting operations it is best effort: record whether each operation completed, was cancelled, or has an unknown outcome. Cancellation does not prove that a remote effect was rolled back.

## Orchestration

### Who does what

- **Model / planner:** proposes a decomposition or a sequence of tool calls.
- **Plan validator:** checks structure, operation names, arguments, references, scopes, graph shape, and budgets.
- **Scheduler:** decides which validated nodes are ready and applies concurrency and resource limits.
- **Dispatcher:** runs an authorised operation and returns a normalised result.
- **Run manager:** persists the lifecycle and handles pause, resume, and cancel.

The model is not the scheduler. It never launches tasks, controls concurrency, or bypasses policy.

### Plans are data

A plan node has: a unique ID, a registered operation, validated input (or typed references to upstream results), dependency IDs, risk metadata taken from the registry (never from the model), a timeout within run policy, a retry or failure profile chosen from approved options, and an idempotency key for external side effects.

Validation rejects duplicate IDs, missing or self dependencies, cycles, unknown operations, unauthorised scopes, oversized graphs, and invalid inputs. Values passed between nodes are references to persisted results, never executable expressions.

### Scheduling

A node is ready when all its dependencies have succeeded and the run is still active. The scheduler picks ready nodes within global, per-run, and per-tool concurrency limits, resource quotas, deadlines, and the failure policy.

The first scheduler is single-process and in-memory. It persists enough intent and status to be recoverable, or movable to a durable engine, later. It makes no crash-safety claims until M2.1 implements recovery.

Building blocks to study and compose, using as few as the semantics need:

- `asyncio.TaskGroup`: structured concurrency and coordinated cancellation.
- `asyncio.Semaphore`: a concurrency cap. Not a queue, and not fair.
- A bounded `asyncio.Queue` plus a worker pool: backpressure and reusable workers.
- A DAG readiness layer on top of one of the above.

Never call `create_task` without an owner, and never create tasks without a bound.

### Failure policies

Node outcomes: succeeded, failed, timed out, cancelled, skipped, waiting for approval, unknown. Run-level policy is one of:

- **fail-fast:** cancel pending work when a required node fails;
- **continue-independent:** run unaffected branches and skip dependants;
- **collect-errors:** let an aggregation step receive structured failures.

Retries apply only to retry-safe operations, within bounded policy. Compensation is an explicitly defined action per operation, not a generic rollback. Writes are never retried automatically.

### Idempotency

Local orchestration cannot guarantee exactly-once side effects on external systems. Use a stable operation key, persist intent, use the remote system's idempotency support where it exists, and reconcile uncertain outcomes. State the guarantee per tool, not system-wide.

### Subagents (later, on evidence)

A child agent is a child run with: a parent reference, explicitly scoped tools and permissions, its own budgets, isolated context by default (with explicit handoff of selected content), depth and fan-out limits, propagated cancellation, and a result contract. It never inherits the parent's full authority.

### Temporal boundary (later, on evidence)

The scheduler exposes application-level operations: start plan, execute ready node, record outcome, request approval, resume. Temporal, if adopted, implements that port. Workflow code must be deterministic; side effects go in activities. Activities can retry, so tools still need idempotency.

## Testing

Core runtime and scheduler tests use fake model and tool adapters, with no inference server. Required scenarios:

- **Runtime:** final answer; tool call followed by final answer; multiple tool calls; malformed arguments; refusal; provider timeout; cancellation; budget exhaustion; approval pause and resume.
- **Scheduler:** sequential and parallel DAGs; rejection of cycles, missing dependencies, duplicates, and bad schemas; the concurrency cap is never exceeded; a node never starts before its dependencies; failure propagation follows the policy; cancellation leaves no orphaned tasks; the deadline stops new work; behaviour on duplicate operations is explicit.
