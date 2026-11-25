# Orchestration Specification

**Status:** Proposed in-process design. Scheduler behavior and plan schema will be finalized in Phases 2 and 6.

## 1. Responsibility split

- **Agent/planner:** proposes a task decomposition or tool-call sequence.
- **Plan validator:** validates structure, registered operation names, arguments, references, scopes, graph properties, and budgets.
- **Scheduler:** determines which validated tasks are eligible to run and applies concurrency/resource limits.
- **Executor/dispatcher:** performs an authorized operation and returns a normalized result.
- **Run manager:** persists lifecycle and coordinates pause/resume/cancel.

The model is not the scheduler. It does not launch arbitrary tasks, bypass policy, or directly control process concurrency.

## 2. Plan representation

A plan is data, not executable code. A node should include:

- stable node ID unique within the plan;
- registered operation/tool reference;
- validated structured input or references to upstream results;
- explicit dependency IDs;
- operation class/risk metadata derived from the registry, not trusted from the model;
- deadline/timeout bounded by run policy;
- retry and failure behavior selected from policy-approved profiles;
- optional idempotency key for external side effects.

The plan validator verifies unique IDs, existing dependency references, no self-edge, no cycles, no unsupported operation, no unauthorized scope, bounded node count/depth, and valid input schemas. Values passed between nodes should be typed references to persisted results, not arbitrary executable expressions.

## 3. Scheduling semantics

A node is eligible when all required dependencies have successful results and the run remains active. The scheduler selects ready nodes while respecting:

- global and per-run concurrency limits;
- per-tool/per-server limits;
- resource quotas (CPU, memory, process count, network, file size) where relevant;
- deadlines and cancellation;
- fairness between runs if multiple runs are supported;
- dependency ordering and declared failure policy.

The initial scheduler can be single-process/in-memory. Persist enough intent, status, and result information that the design can later be recovered or moved to a durable engine. Do not promise crash-safe in-flight state until the persistence/recovery phase implements it.

## 4. Concurrency choices to study

- `asyncio.TaskGroup`: structured concurrency and coordinated cancellation for a bounded group of tasks.
- `asyncio.Semaphore`: simple concurrency limit, but not a queue, fairness guarantee, or full scheduler.
- Bounded `asyncio.Queue` + worker pool: explicit backpressure and reusable workers.
- DAG scheduler: dependency readiness and graph execution layered above a task execution mechanism.

These are complementary rather than mutually exclusive. The implementation should use the least complex composition that satisfies required semantics. Avoid `create_task` without ownership/lifecycle tracking; avoid unbounded task creation.

## 5. Failure policies

Possible node outcomes: succeeded, failed, timed out, cancelled, skipped, waiting approval, unknown external outcome. Run-level behavior must be explicit:

- fail-fast: cancel downstream/pending work when a required node fails;
- continue-independent: execute independent branches but mark dependent nodes skipped;
- collect-errors: complete a designated aggregation step with structured failures;
- retry: only for errors and operations declared retry-safe, within bounded policy;
- compensation: separate explicitly defined compensating action for operations that support it; not a generic rollback claim.

A scheduler should not automatically retry arbitrary writes. Network failure after a remote side effect can leave the outcome uncertain.

## 6. Idempotency and exactly-once caveat

Exactly-once execution of arbitrary external side effects cannot be guaranteed by local orchestration alone. Use a stable operation/idempotency key, persist operation intent, use remote idempotency support where available, and implement status reconciliation for uncertain results. State the guarantee per tool, not globally.

## 7. Subagents (deferred)

A child agent should be represented as a child run with:

- parent run and task reference;
- explicit scoped permissions and tools;
- bounded model/token/tool/time budgets;
- context-sharing policy (isolated by default; explicit handoff of selected content);
- maximum delegation depth and fan-out;
- cancellation propagation and result contract.

A child agent must not inherit all parent authority automatically. Delegation is a potential privilege-escalation and cascading-failure boundary.

## 8. Temporal migration boundary

The in-process scheduler should expose application-level operations such as start plan, execute eligible node, record outcome, request approval, and resume. Temporal integration can later implement the durable orchestration port. Temporal workflow code must be deterministic; side-effecting operations belong in activities. Activities may retry, so tool operations still require idempotency/reconciliation.

## 9. Required tests

- DAG with sequential and parallel branches.
- Cycle, missing dependency, duplicate node, and invalid schema rejection.
- Maximum concurrency never exceeded.
- A node starts only after dependencies succeed.
- Failure propagation matches policy.
- Cancellation does not leave unowned tasks.
- Deadline/budget stops scheduling new work.
- Duplicate operation idempotency behavior is explicit.
- Independent runs cannot exceed global resource quotas or starve indefinitely (when multi-run scheduling is implemented).
