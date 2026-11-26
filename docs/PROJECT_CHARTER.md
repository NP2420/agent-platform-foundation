# Project Charter

**Status:** Agreed scope and direction; detailed implementation choices remain subject to the status labels in the rest of this package.

## 1. Purpose

Design and build a reusable, self-hosted, general-purpose AI agent platform. The platform should provide a controlled runtime in which models can reason, request tools, execute bounded workflows, delegate work, and produce inspectable outcomes. The project is also a structured learning effort in production software, AI engineering, distributed systems, reliability, and security.

The goal is not to reproduce a named commercial product or maximize the number of abstractions. The goal is a system whose architecture, behavior, tests, security boundaries, operational model, and trade-offs can withstand a serious engineering review for a clearly stated deployment scope.

## 2. Goals

1. Build a custom, provider-independent agent execution loop.
2. Establish a common contract for model invocations and model profiles.
3. Support local inference through Ollama as the initial baseline.
4. Design for tiered model roles (primary, fast, summarizer, specialist, evaluator) without requiring multiple models in the first vertical slice.
5. Provide a tool registry and dispatcher that support native tools and MCP servers through a common policy boundary.
6. Build a small in-process orchestration engine with sequential execution, concurrency, dependencies, bounded resource use, and explicit failure handling.
7. Persist application state, runs, messages, execution steps, and audit-relevant events in PostgreSQL, after evaluating version compatibility.
8. Expose an API/SDK-first interface with a versioned event stream. Human-facing interfaces are later clients.
9. Provide a separate execution broker and isolation boundary before enabling powerful filesystem, shell, browser, or arbitrary-code tools.
10. Develop deterministic tests, agent evaluations, observability, and operational documentation alongside the runtime.
11. Evaluate Temporal when long-running workflows, durable timers, worker recovery, and workflow signaling justify it.
12. Keep development self-hosted and low-cost, using the existing development machine and open-source infrastructure where practical.
13. Teach the engineering concepts through primary sources, textbooks, experiments, and small, reviewable implementation changes.

## 3. Non-goals for the initial release

- A hosted multi-tenant SaaS service.
- A complete web dashboard, IDE extension, or polished terminal UI.
- A microservice for every logical module.
- A custom LLM inference engine or model training platform.
- Building a new database, message broker, workflow engine, container runtime, or telemetry protocol.
- Introducing Redis, Kafka, Kubernetes, a vector database, or a graph database without a demonstrated requirement.
- Treating multi-agent behavior as a prerequisite for a useful first release.
- Allowing model-generated instructions to authorize their own actions.
- Claiming that containers alone make arbitrary code execution safe.

## 4. User-approved project direction

| Area | Direction | Status |
|---|---|---|
| Product | General-purpose agent platform | Agreed |
| Deployment | Local/self-hosted, minimal ongoing cost | Agreed |
| Interface | API and SDK first; interfaces later | Agreed |
| Runtime language | Python primary | Accepted direction |
| Additional languages | TypeScript for Node-native/client surfaces; Go/Rust when justified | Accepted direction |
| Inference | Ollama first | Agreed direction |
| Model strategy | Tiered profiles, initially may use one model | Agreed direction |
| Tools | Native and MCP | Agreed direction |
| Orchestration | Custom in-process engine first | Agreed direction |
| Durable workflows | Evaluate Temporal later | Agreed direction |
| Database | PostgreSQL; compare 18.7 and 19.0 | Agreed direction; version open |
| Execution | Full capabilities are a long-term requirement behind a security boundary | Agreed scope; sandbox open |

## 5. Quality objectives

The platform should be engineered around:

- **Correctness:** explicit state transitions, schema validation, defined failure semantics, deterministic core tests.
- **Reliability:** bounded retries, cancellation, idempotency, recoverable state, controlled concurrency.
- **Security:** least privilege, deny-by-default policies, separation of model decisions from authorization, isolated execution, auditable approvals.
- **Observability:** correlated run histories, traces, metrics, and structured logs with sensitive-data controls.
- **Evaluability:** repeatable datasets, regression tests, model comparisons, and clearly defined success metrics.
- **Maintainability:** explicit module boundaries, typed contracts, migrations, ADRs, and dependency discipline.
- **Resource efficiency:** local-first operation, measurable CPU/RAM/VRAM/disk usage, and optional infrastructure profiles.

Numeric SLOs, concurrency targets, supported operating systems, and resource ceilings are intentionally open until the host environment and intended workload have been characterized.

## 6. Definition of success

A successful initial platform is not defined by the presence of all planned features. It must demonstrate at least one end-to-end use case in which:

- a run is created through the API;
- a configured model receives a bounded context;
- the model can request a registered tool;
- the tool request is validated and authorized outside the model;
- the tool executes through the dispatcher and returns a structured result;
- the model continues or returns a final response;
- the run and relevant events are persisted;
- the execution can be inspected and tested deterministically;
- failures, limits, and cancellation behave according to documented semantics.

Powerful local execution, multi-agent delegation, and durable workflow execution require their own security and reliability gates before being called production-ready.

## 7. Constraints and assumptions

- Initial development uses the owner's existing machine; its OS, kernel, CPU, RAM, GPU/VRAM, and container capabilities must be discovered before pinning runtime and sandbox choices.
- Local inference is the baseline; remote providers may be optional adapters, not required infrastructure.
- Minimal recurring cost is preferred over hosted dependencies.
- Current versions and compatibility must be rechecked at implementation time.
- A “production-grade” claim is always scoped to a concrete threat model, workload, deployment model, SLO, operational owner, and validated release process.
