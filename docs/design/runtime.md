# Runtime and Orchestration

**Status:** Proposed. Internal types and serialisation are designed in M1.2. The durability mechanism is chosen in M2.1 ([ADR 0018](../adr/0018-durable-execution-decided-in-m2.md)). The scheduler and plan schema are finalised in M4.2.

## Runtime responsibility

The runtime executes one bounded run. It builds context, calls the model, normalises the response, validates and authorises tool requests, dispatches them, updates state, and decides when the run is done. It does not grant permissions, run arbitrary code, or allocate unbounded resources.

## Synchronous domain, asynchronous runtime

The domain layer (types, the run state machine, policy decisions, budget accounting) is synchronous and does no I/O, so it can be tested exhaustively without an event loop. The runtime around it is asynchronous: model calls, tool calls, timers, and cancellation run on `asyncio` under a `TaskGroup` that owns every task it starts. The runtime calls into the domain to decide; the domain never awaits.

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

The loop is ReAct-style: the model reasons, proposes an action (a tool call, a question to the user, or a final answer), the runtime carries it out under policy, and the observation goes back into context. Tool calls arrive either as native tool calls or as schema-constrained JSON, depending on the profile ([model spec](models.md#tool-call-methods)); the loop is the same for both.

```text
while run is RUNNING and budget remains:
    context  = context_manager.build(run, budget)
    profile  = router.select(task, context, policy)
    response = gateway.generate(profile, context)
    record model call metadata

    if response is final:
        check output policy, persist message, complete run

    elif response asks the user a question:
        if clarification cap not reached: persist question, move to WAITING_INPUT
        else: tell the model to answer with stated assumptions, or abstain

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
| `WAITING_INPUT` | Blocked on the user's answer to a clarifying question |
| `WAITING_EXTERNAL` | Blocked on a defined external signal. Add only when needed. |
| `COMPLETED` | Terminal success |
| `FAILED` | Unrecoverable error, or recovery exhausted |
| `CANCELLING` | Cancellation requested; no new work starts, and in-flight model or tool calls are settling |
| `CANCELLED` | Cancellation completed. Each in-flight operation is recorded as completed, cancelled, or unknown. |

A deadline or budget overrun is a **reason on `FAILED`**, not its own state: `FAILED` carries a terminal reason such as `deadline_exceeded`, `budget_exhausted`, or `error` (decided 2026-11-26). New failure kinds add a reason, not a state.

Terminal states never change, apart from an explicit administrative correction record. Transitions are validated in application code and covered by tests.

## Clarification

The model asks the user a question through a reserved `ask_user` action, never as free text that the runtime has to guess at. Questions are limited per run by a configurable cap, default 4. Once the cap is reached, the model has to answer with its assumptions stated, or abstain. The question count goes on the run's trace, and the eval reports how often the agent asks when it didn't need to ([decision audit, A17](../research/2026-11-27-decision-audit.md#a17-clarification-cap--keep-the-cap-measure-over-asking)). A cancelled or expired `WAITING_INPUT` run ends `CANCELLED` or `FAILED` with a reason, like any other wait.

## Step records

Every completed model call, tool call, approval decision, and user answer becomes an immutable step record: step ID (UUIDv7), run ID, kind, a digest of its inputs, outcome (succeeded, failed, cancelled, or unknown), timings, and usage where measured. Step records are the unit of recovery: after a restart, a run resumes from its last recorded step, and an operation that started without a recorded outcome is treated as unknown, never as not done. Milestone 1 keeps them in memory; M2.1 persists them using the mechanism [ADR 0018](../adr/0018-durable-execution-decided-in-m2.md) selects.

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

## Retries

Only the transient classes above are retried: rate limits, transient provider errors, and timeouts on calls known to be safe to repeat. Retries use exponential backoff with full jitter, a bounded number of attempts, and a total time cap inside the run's deadline. A `Retry-After` from the provider is honoured when it falls within that cap; otherwise the call fails. Each attempt is recorded. There is no automatic fallback: a failed call never moves to another model or provider on its own ([model spec](models.md#routing)). Writes are never retried automatically.

## Budgets

Per run: wall-clock time, model calls, tool calls, tool concurrency, tokens where measurable, clarifying questions, delegation depth, per-tool timeout, external calls, and output size. Accounting is monotonic and correct under concurrency. The model cannot raise its own budget.

**Defaults.** Until the M1.7 baseline exists, defaults are provisional and generous, and reaching one is logged as a finding. After the baseline, each default is set to about twice the measured p99 for the eval set, and revisited when the workload changes. A budget that real runs never approach catches nothing; one set at the median fails healthy runs.

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

### Durability boundary

The scheduler exposes application-level operations: start plan, execute ready node, record outcome, request approval, resume. The durability mechanism chosen in M2.1 implements that port ([ADR 0018](../adr/0018-durable-execution-decided-in-m2.md)). If it is Temporal, workflow code must be deterministic and side effects go in activities. Whatever it is, a step can run again if its outcome wasn't recorded, so tools still need idempotency.

## Testing

Core runtime and scheduler tests use fake model and tool adapters, with no inference server. Required scenarios:

- **Runtime:** final answer; tool call followed by final answer; multiple tool calls; malformed arguments; refusal; provider timeout; cancellation; budget exhaustion; approval pause and resume; clarification pause and resume, and the cap; retries stay within attempt and time bounds and honour `Retry-After`; no retry on permanent errors; every completed step leaves exactly one step record.
- **Scheduler:** sequential and parallel DAGs; rejection of cycles, missing dependencies, duplicates, and bad schemas; the concurrency cap is never exceeded; a node never starts before its dependencies; failure propagation follows the policy; cancellation leaves no orphaned tasks; the deadline stops new work; behaviour on duplicate operations is explicit.
