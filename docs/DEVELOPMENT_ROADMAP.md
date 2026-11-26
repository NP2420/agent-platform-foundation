# Development Roadmap

A gated sequence, not a schedule. A phase ends when its exit gate is met, not when code exists.

## Status

This table is the single place that tracks project status.

| Checkpoint | Status | Notes |
|---|---|---|
| 0.1 Host and container environment | Done | [Environment baseline](research/ENVIRONMENT_BASELINE_2026-11-25.md). Revisit if the host changes. |
| 0.2 Inference topology | Done | Windows-hosted Ollama over WSL mirrored networking ([ADR 0010](adr/0010-windows-hosted-ollama-initial-deployment.md)) |
| 0.3 Local model screening | In progress | Throughput measured at 4K. Tool scenarios T1, T3, T4 pass for both 4B models; T2 needs a rerun. See [benchmarks](research/OLLAMA_MODEL_BENCHMARKS_2026-11-25.md). |
| 0.4 Python and toolchain | Open | WSL has Python 3.14.4 but no pip, uv, or Linux-native Node |
| 0.5 Phase 0 review | Open | Confirm Phase 1 scope and close Phase 0 |
| Sandbox host feasibility | Deferred to Phase 10 | `/dev/kvm` exists but the user can't access it. No change until a backend is chosen. |
| PostgreSQL 18 vs 19 | Deferred to Phase 7 | No code depends on the major version before then |

**Next steps**

1. Rerun T2 with the prompt in single quotes, so PowerShell keeps `$100`.
2. Measure both 4B models at 8K, 16K, and 32K context: VRAM, CPU/GPU split, throughput.
3. Repeat the tool scenarios with thinking on.
4. Move the evaluation harness into the repository (`evals/`, Python, run from WSL, raw JSON saved).
5. Full mock-tool round trip: tool call → tool result message → final answer.
6. Select the Python version, then start Phase 1.

## Working cycle

For each phase and each chunk inside it:

1. **Discover:** the concrete problem, constraints, and unknowns.
2. **Research:** relevant chapters, official docs, specifications, papers.
3. **Compare:** credible alternatives for material decisions.
4. **Design:** contracts, state transitions, failure semantics, acceptance criteria.
5. **Implement:** one coherent concept or interface at a time.
6. **Verify:** run the tests and record the actual output.
7. **Reflect:** what differed from expectations, and what should change.
8. **Record:** update the specs, ADRs, research log, and this status table.

## Phases

### Phase 0: Environment and architecture discovery

Characterise the host, inference path, and candidate models. Record the open questions.
**Exit:** no Phase 1–6 decision depends on an unknown host fact. Questions owned by later phases (database version, sandbox) are explicitly deferred to those phases.

### Phase 1: Repository and toolchain

Python version, `uv` project and lockfile, Ruff, type checker, pytest, package layout, configuration and secrets conventions. Decide where the working copy lives (Windows or the WSL ext4 filesystem).
**Exit:** a fresh clone creates the locked environment and passes the lint, type, and test commands.

### Phase 2: Domain contracts and run state machine

Typed objects for agents, versions, messages, runs, steps, tool calls, model results, events, and errors. Lifecycle transitions with tests. No model, no database.
**Read:** state machines, layering, Pydantic vs dataclasses, JSON Schema.
**Exit:** deterministic tests cover valid and invalid transitions; contracts are framework-free.

### Phase 3: Model adapter

Ollama adapter and fake adapter, health and capability checks, normalised responses, timeouts and errors, tool-call parsing.
**Exit:** a baseline model is chosen with its limitations recorded; the adapter is tested against the fake and against real Ollama.

### Phase 4: Single-agent loop

Bounded loop, context assembly interface, mocked tools, stop conditions, budgets, events, cancellation.
**Exit:** tests cover completion, multi-turn runs, malformed responses, step exhaustion, provider timeout, and cancellation.

### Phase 5: Tool registry and dispatcher

Definitions, schema validation, registry, dispatcher, identity, timeouts, concurrency policy, normalisation, audit records.
**Exit:** one read-only tool and one controlled write tool pass the contract, permission, timeout, duplicate, and malformed-input tests.

### Phase 6: Orchestrator

Plan representation, DAG validation, dependency resolution, bounded concurrency, failure propagation, cancellation.
**Read:** asyncio structured concurrency, TaskGroup, semaphores, queues, backpressure. Compare with LangGraph without adopting it.
**Exit:** tests prove validation, dependency order, bounded parallelism, the failure policy, clean cancellation, and no unbounded task creation.

### Phase 7: PostgreSQL persistence

Schema, migrations, repositories, transaction boundaries, run and event persistence, idempotency records, recovery.
**Decide:** PostgreSQL 18 vs 19 ([research note](research/POSTGRES_18_VS_19.md)); psycopg 3 vs asyncpg.
**Exit:** the version, driver, and migration process are recorded; tests cover conflicts, restart recovery, uniqueness, and concurrent access.

### Phase 8: API and event streaming

Versioned REST API, run create, get, list, and cancel, approvals, SSE stream, idempotency keys, error envelope, minimal SDK.
**Exit:** contract tests pass; a client can run a task and reconstruct its progress from events alone.

### Phase 9: MCP

Client adapter, connection lifecycle, capability discovery, metadata mapping, protocol errors, timeouts, server trust policy.
**Exit:** a test MCP server's tool runs through the same registry, policy, and dispatcher path as a native tool.

### Phase 10: Execution broker and sandbox

Structured execution requests, workspaces, worker identity, limits, artifact handling, cleanup, audit.
**Decide:** the sandbox backend ([research note](research/LOCAL_SANDBOX_OPTIONS.md)), including KVM feasibility on this host.
**Exit:** the threat model and backend are reviewed, and negative tests show filesystem, network, process, and resource access is blocked. No arbitrary execution before this.

### Phase 11: Context and memory

History selection, token budgets, compaction, summaries with provenance, an optional retrieval interface. Vector or graph storage only for a real retrieval case.
**Exit:** tests show relevance, provenance, budget adherence, and resistance to instructions in retrieved content.

### Phase 12: Evaluation and observability hardening

Versioned case suite, graders, trace correlation, metrics, redaction, failure-injection harness.
**Exit:** baseline reports can be regenerated; regressions can fail a check.

### Phase 13: Tiered routing

A model registry with profiles, routing rules, capability checks, fallbacks, budget controls.
**Exit:** routing measurably beats one model on cost or success, and is reproducible and tested.

### Phase 14: Subagents

Child-run contract, scoped permissions, context policy, budgets, depth limits, cancellation propagation.
**Exit:** delegation measurably helps on chosen evaluations and cannot exceed its scopes or budgets.

### Phase 15: Temporal (only if justified)

Reassess whether durable timers, long approvals, worker distribution, or replay are actually needed. If they are, define workflow and activity boundaries and keep our contracts Temporal-independent.
**Exit:** a failure-injection test demonstrates durability worth the infrastructure cost.

### Phase 16: Release hardening

Configuration and secrets, access control, backup and restore, upgrades, quotas, runbook, dependency review, load and security tests.
**Exit:** a release review covering:

- **Scope:** supported users, workload, OS and hardware, threat model, residual risks, unsupported configurations.
- **Correctness:** state-machine and contract tests; invalid plans and tools fail closed; database constraints protect invariants; concurrency races are tested.
- **Reliability:** bounded retries; idempotency or an explicit unknown-outcome policy per side-effecting tool; restart tests; backup and restore actually exercised; migration procedure.
- **Security:** model output is never authorisation; deny-by-default scopes; bound approvals; redaction; no unintended network exposure; sandbox negative tests; secret handling.
- **Agent quality:** reproducible model selection; representative and adversarial cases; calibrated judges; thresholds based on measured baselines.
- **Operations:** runs can be reconstructed from records; telemetry is correlated with bounded cardinality; resource and disk growth is monitored.
- **Decision:** version and commit, evidence and date, open defects, and an explicit go or no-go.

A failed high-severity security or data-integrity check is never offset by a good average evaluation score.

## Review points

End of Phase 0 (architecture) · end of Phase 3 (model baseline) · end of Phase 6 (orchestrator and concurrency) · end of Phase 7 (database) · end of Phase 9 (MCP trust) · before Phase 10 (sandbox threat model) · end of Phase 12 (reliability baseline) · before Phase 14 (evidence for delegation) · before Phase 15 (evidence for Temporal) · before any release claim.

## Scope control

Split a phase into chunks that each deliver one concept, interface, or tested behaviour. Don't bundle unrelated subsystems to go faster. If research invalidates a decision, update the ADR and this plan before continuing.
