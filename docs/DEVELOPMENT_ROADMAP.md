# Development Roadmap

**This is a gated sequence, not a calendar promise.** Each phase is completed in small implementation chunks. A phase does not advance merely because code exists; its research, design, verification, and reflection gates must be satisfied.

## 1. Working cycle for every phase

1. **Discover:** identify the concrete problem, constraints, and unknowns.
2. **Research:** read relevant textbooks/chapters, official documentation, specifications, papers, and recent issue/release notes.
3. **Compare:** evaluate at least the credible alternatives for material decisions.
4. **Discuss:** separate facts, interpretations, assumptions, and recommendations; resolve questions with the project owner.
5. **Design:** write contracts, state transitions, failure semantics, and acceptance criteria before substantial code.
6. **Implement in chunks:** one coherent concept or interface at a time; explain the change and how it fits.
7. **Verify:** unit, contract, integration, security, and failure tests as relevant; run commands and report actual outcomes.
8. **Reflect:** compare expected behavior with observed behavior; revise assumptions/design if evidence requires it.
9. **Record:** update docs, ADRs, research log, roadmap status, and known limitations.

Every coding chunk should have: objective, context, chosen design, alternatives considered, files touched, explanation, tests, observed output, and next step.

## 2. Phases and gates

### Phase 0 — Architecture and environment discovery

**Research/discussion:** inspect host OS/kernel, CPU, memory, GPU/VRAM, storage, container support, user privilege model, and network constraints. Recheck current Python, PostgreSQL, Ollama, and MCP versions. Establish an initial threat model and expected workload. Review all documents with the owner.

**Deliverables:** confirmed environment profile (kept local if sensitive), open-question list, prioritized threat model, initial SLO/usage assumptions, reviewed ADRs.

**Exit gate:** no critical architectural choice depends on unknown host facts without an explicit experiment/decision plan.

### Phase 1 — Repository/toolchain foundation

**Build:** Git conventions, `uv` project, Python version and lockfile, formatting/lint/type/test commands, package structure, configuration/secrets conventions, CI-ready test command.

**Research checkpoint:** compare Python 3.14 and 3.15 dependency compatibility; understand Python packaging, import/package layout, configuration, and reproducible builds.

**Exit gate:** fresh clone can create a locked environment and run a passing minimal test/lint/type-check set.

### Phase 2 — Domain contracts and run state machine

**Build:** typed domain objects for agent definitions/versions, messages, runs, steps, tool calls, model results, events, and errors. Define lifecycle invariants and transition tests without a real model or database.

**Research checkpoint:** state machines, domain/application/infrastructure boundaries, event records vs event sourcing, Pydantic vs dataclasses, JSON Schema.

**Exit gate:** deterministic tests prove valid/invalid transitions and core contracts are independent of frameworks.

### Phase 3 — Local model baseline and provider adapter

**Build:** Ollama connectivity, health/capability checks, one model adapter, fake model adapter, normalized responses, timeout/error handling, structured output/tool-call parsing.

**Research/experiment:** select local model candidates on actual hardware; compare tool selection, arguments, structured output, latency, context use, resource use, and task completion.

**Exit gate:** chosen baseline and limitations recorded; adapter contract tested against fake and real local model.

### Phase 4 — Single-agent runtime loop

**Build:** bounded loop, context assembly interface, model invocation, normalized tool-call response handling (initially mocked), stopping conditions, budgets, run events, cancellation behavior.

**Research checkpoint:** tool-calling loop patterns, context-window management, structured outputs, prompt injection boundaries, retry taxonomy.

**Exit gate:** deterministic tests cover normal completion, multiple model turns, malformed responses, max-step exhaustion, provider timeout, and cancellation.

### Phase 5 — Tool registry and native tool dispatcher

**Build:** tool definitions, JSON Schema validation, registry, dispatcher, context/identity, timeouts, concurrency policy, result normalization, audit recording.

**Research checkpoint:** API design, input/output validation, side-effect classification, idempotency, capability security, error semantics.

**Exit gate:** native read-only tool and controlled write tool pass contract, permission, timeout, duplicate, and malformed-input tests.

### Phase 6 — In-process orchestration and dependency scheduler

**Build:** plan representation, DAG validation, dependency resolution, bounded concurrency, sequential/parallel execution, failure propagation, cancellation, deterministic scheduler tests.

**Research checkpoint:** asyncio structured concurrency, TaskGroup, semaphores, bounded queues, worker pools, graph execution, fairness, backpressure. Compare with a reference framework such as LangGraph without surrendering our runtime semantics.

**Exit gate:** tests prove acyclic plan validation, dependency correctness, bounded parallelism, failure policy, cancellation, and no unbounded task creation.

### Phase 7 — PostgreSQL persistence and recovery semantics

**Build:** schema/migrations, repositories, transaction boundaries, run/event persistence, message/step records, idempotency records, recovery tests.

**Research checkpoint:** DDIA transactions, indexes, isolation, write amplification, event history; compare PostgreSQL 18.7 and 19.0 using `research/POSTGRES_18_VS_19.md`; compare psycopg 3 and asyncpg for compatibility and workload fit.

**Exit gate:** selected version/driver and migration process recorded; tests cover transaction conflicts, restart recovery, uniqueness/idempotency, and concurrent access.

### Phase 8 — API/SDK and event streaming

**Build:** versioned REST API, run create/get/list/cancel, approval command shape, event stream, idempotency key handling, error envelope, minimal Python SDK/client.

**Research checkpoint:** API versioning, SSE semantics/reconnect, authentication boundary, request idempotency, event delivery ordering and replay cursor.

**Exit gate:** API contract tests pass; a client can run a task and reconstruct its progress from the event interface.

### Phase 9 — MCP integration

**Build:** MCP client adapter, server connection lifecycle, capability discovery, tool metadata mapping, protocol errors, timeouts, server trust policy.

**Research checkpoint:** current MCP specification revision, official Python SDK and TypeScript SDK versions, transports, authorization, capability negotiation, protocol security, compatibility tests.

**Exit gate:** compatible MCP test server exposes a tool that runs through the same registry/policy/dispatcher path as a native tool.

### Phase 10 — Execution broker and sandbox

**Build:** only after host/threat-model review; structured execution requests, workspace model, worker identity, time/resource/network restrictions, output/artifact handling, cleanup and audit trail.

**Research checkpoint:** compare namespaces/seccomp/AppArmor/Landlock, rootless containers, gVisor, microVM options, and platform-specific facilities. Read `research/LOCAL_SANDBOX_OPTIONS.md`.

**Exit gate:** threat model and selected isolation backend reviewed; negative tests show disallowed filesystem/network/process/resource access is blocked. Do not enable arbitrary execution before this gate.

### Phase 11 — Context manager and memory/retrieval foundations

**Build:** durable conversation history selection, token budgeting, truncation/compaction strategy, summaries with provenance, optional retrieval interface. Add vector/graph infrastructure only if a real retrieval case warrants it.

**Research checkpoint:** AI Engineering evaluation/data engineering, context management, retrieval quality, memory poisoning, privacy/retention, retrieval alternatives (PostgreSQL full-text/pgvector, external vector stores, graph stores).

**Exit gate:** context construction tests demonstrate relevance, provenance, budget adherence, and resistance to untrusted retrieved instructions.

### Phase 12 — Evaluation and observability hardening

**Build:** versioned evaluation cases, deterministic runner, model-backed evaluation suite, graders, trace correlation, metrics, structured logs, redaction, failure-injection harness.

**Research checkpoint:** AI Engineering evaluation chapters, SRE service indicators, OpenTelemetry semantic conventions and stability, LLM-as-judge limitations and calibration.

**Exit gate:** baseline quality/performance reports can be regenerated; critical paths are traceable; evaluation regressions can fail CI or release checks.

### Phase 13 — Tiered model routing

**Build:** model registry and profiles for primary, fast, summarizer, specialist, evaluator; task routing rules; capability checks; measured fallbacks; budget controls.

**Research/experiment:** compare quality, success rate, cost/resource/latency of one-model versus routed approaches. Ensure delegation/routing reduces total task cost or improves success rather than merely adding complexity.

**Exit gate:** policy is explicit, reproducible, benchmarked, and has fallback/limit tests.

### Phase 14 — Subagents and delegation

**Build:** child-run contract, scoped tools/permissions, isolated or shared context policy, budgets, result handoff, recursion/depth limits, cancellation propagation.

**Research checkpoint:** multi-agent communication, shared-state hazards, task decomposition quality, agentic security and cascading failures.

**Exit gate:** delegation provides measurable benefit on selected evaluations and cannot exceed configured budgets/scopes.

### Phase 15 — Temporal evaluation/integration

**Decision gate:** do not integrate Temporal just because it is on the roadmap. Reassess whether workflows now require durable timers, long-running approvals, worker distribution, replay, or recovery guarantees that our current design cannot maintain economically.

If justified, define workflow/activity boundaries, deterministic workflow code, activity idempotency, migration/operations, and local cost/resource implications. Keep our runtime and use-case contracts independent of Temporal.

**Exit gate:** a failure-injection test demonstrates a meaningful durability capability that justifies the infrastructure cost.

### Phase 16 — Release and operational hardening

**Build:** configuration and secret handling, access controls, backup/restore, upgrades/migrations, resource quotas, operational runbook, dependency/SBOM review, security tests, load tests, release procedure.

**Research checkpoint:** SRE error budgets/SLOs, secure/reliable systems, deployment hardening for selected host environment.

**Exit gate:** scoped release review against `PRODUCTION_READINESS.md`; explicitly list residual risks and unsupported deployment scenarios.

## 3. Review checkpoints

Require a deliberate review at:

- End of Phase 0: architecture alignment.
- End of Phase 3: model baseline selection.
- End of Phase 6: orchestrator design and concurrency correctness.
- End of Phase 7: database/version/transaction decision.
- End of Phase 9: MCP boundary and trust model.
- Before Phase 10 is enabled: sandbox threat-model approval.
- End of Phase 12: reliability/evaluation baseline.
- Before Phase 14: evidence that multi-agent delegation helps.
- Before Phase 15: evidence that Temporal is needed.
- Before any release claim: production-readiness review.

## 4. Scope-control rule

A milestone may be split into smaller chunks. Each chunk should deliver one understandable concept, one cohesive interface, or one tested behavior. Do not combine unrelated subsystems just to move faster. If research invalidates a decision, revise the plan and ADR before continuing.
