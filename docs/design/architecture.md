# Architecture

**Status:** The principles and boundaries are accepted ([ADRs 0001–0009](../adr/README.md), [0012](../adr/0012-portable-deployment.md)). Each component is built in the milestone the [roadmap](../project/roadmap.md) gives it; until then this describes the plan.

A Python modular monolith with explicit adapter boundaries. The boxes below are logical components, not services. Everything runs in one process until a concrete need (isolation, scaling, independent deployment) justifies splitting something out.

## Principles

1. The model proposes; deterministic code validates, authorises, schedules, and executes.
2. The runtime owns the agent loop. Clients submit commands and render events; they hold no agent or authorisation logic.
3. The orchestrator is our own code, framework-independent, and in-process to start.
4. Model providers and tool transports sit behind internal interfaces (ports and adapters).
5. Model output, MCP servers, web content, documents, and tool results are untrusted input.
6. Model-generated code and shell commands never run in the API process.
7. Application state (PostgreSQL) and telemetry (traces, logs, metrics) are separate records with different retention rules.
8. Every external side effect has defined retry and idempotency behaviour.
9. New services and infrastructure need evidence, not anticipation.

## Components

**CLI.** The first client. In milestone 1 it calls the runtime directly; from milestone 2 it is an API client like any other.

**API / control plane.** Request validation, run creation and queries, approval and cancellation commands, event streaming over SSE, quotas. FastAPI. No reasoning logic, no user code. See [api.md](api.md).

**Run manager.** Creates runs, binds each to an agent configuration version, enforces lifecycle transitions, and coordinates persistence. A thread (conversation) can contain many runs.

**Agent runtime.** The bounded model ↔ tool loop. See [runtime.md](runtime.md).

**Context manager.** Builds each model request from stored history under a token budget: selects, summarises, retrieves, or drops messages. It is not the store of record. Compaction keeps provenance and never silently drops hard constraints.

**Model gateway.** Maps a logical profile to a provider adapter. Owns capability checks, timeouts, safe retries, and usage accounting. No automatic fallback between models or providers. See [models.md](models.md).

**Orchestrator.** Validates plans (as data), schedules ready nodes under concurrency and budget limits, and handles failure and cancellation. Executes registered operations only. See [runtime.md](runtime.md#orchestration).

**Tool registry and dispatcher.** The registry holds trusted definitions; the dispatcher validates arguments, checks policy, executes with timeouts, normalises output, and records the invocation. Native and MCP tools share this path. See [tools.md](tools.md).

**Policy engine.** Decides allow, deny, or require-approval from identity, granted scopes, tool risk, and resource limits. A model's claim that something is safe counts for nothing.

**Execution broker.** A separate process boundary for filesystem, shell, browser, and code. Accepts structured, policy-checked requests and runs them in restricted workers. The sandbox backend is open. See [security.md](security.md).

**Persistence.** PostgreSQL holds agent versions, threads, messages, runs, steps, tool invocations, approvals, and an append-only run event history. That history supports audit and replay to clients; it does not make the system event-sourced. See [data-model.md](data-model.md).

**Observability.** See [below](#observability).

```mermaid
flowchart TB
    Client[API / SDK clients] --> API[FastAPI control plane]
    API --> RM[Run manager]
    RM --> Runtime[Agent runtime]
    Runtime --> Context[Context manager]
    Runtime --> Router[Model gateway]
    Router --> Ollama[Ollama]
    Router --> Providers[Optional remote providers]
    Runtime --> Policy[Policy engine]
    Runtime --> Orchestrator[Orchestrator]
    Orchestrator --> Dispatcher[Tool dispatcher]
    Dispatcher --> Native[Native tools]
    Dispatcher --> MCP[MCP client adapter]
    Dispatcher --> Broker[Execution broker]
    MCP --> MCPServers[External MCP servers]
    Broker --> Sandbox[Sandboxed worker]
    RM --> DB[(PostgreSQL)]
    Runtime --> DB
    Dispatcher --> DB
    DB --> Events[SSE event stream]
    API --> Events
```

## Trust boundaries

| Actor | Role | Trust |
|---|---|---|
| API client | Creates runs, streams events, approves, cancels | Authenticated; request content untrusted |
| Agent runtime | Builds context, calls models, interprets results | Trusted code |
| Model | Produces text, structured output, tool-call proposals | Untrusted; never an authority |
| Native tool | In-process application function | Trusted only for its declared capability |
| MCP server | External tool provider | Separate trust domain; metadata and output untrusted |
| Execution worker | Runs powerful operations | Separate boundary, least privilege |
| PostgreSQL | Application state | Trusted, access-controlled |
| Ollama | Local inference | Local service; keep it on loopback |

## One tool-assisted run

```mermaid
sequenceDiagram
    participant C as Client
    participant R as Runtime
    participant M as Model adapter
    participant P as Policy
    participant D as Dispatcher
    participant DB as PostgreSQL

    C->>R: POST /v1/runs (input, idempotency key)
    R->>DB: run + run.accepted
    R->>M: generate(context, tools)
    M-->>R: tool-call proposal
    R->>P: authorise(tool, args, scope)
    alt allowed
        R->>D: execute
        D->>DB: invocation intent
        D-->>R: normalised result
        D->>DB: invocation outcome
        R->>M: generate(context + result)
        M-->>R: final answer
        R->>DB: message + run.completed
    else needs approval
        R->>DB: approval request, run paused
        R-->>C: approval.required
    else denied
        R->>DB: denial, run outcome
    end
```

## Dependency rules

- `domain` imports only the standard library and Pydantic ([ADR 0016](../adr/0016-pydantic-domain-types.md)): no web framework, ORM, provider SDK, MCP SDK, or Temporal code.
- `application` defines use cases and ports; infrastructure implements the ports.
- `runtime` reaches models through model ports and tools through the dispatcher port.
- `orchestration` is deterministic for a given plan, state, and input. Plan validation never calls a model.
- Infrastructure (API, database, providers, MCP, telemetry, execution) lives in adapters.

## Source layout

The target shape. Create directories as their phase starts, not all at once.

```text
pyproject.toml, uv.lock, .python-version   # M1.1
src/agent_platform/
    domain/  application/  runtime/  orchestration/  models/
    tools/  security/  persistence/  api/  observability/
tests/{unit,integration,contract,evaluation,security}/
evals/        # versioned evaluation cases and harness
infra/compose/
scripts/
docs/
```

Directories are modules in one package, not separate services or distributions.

## Deployment

Portable by design ([ADR 0012](../adr/0012-portable-deployment.md)): containers, configuration from the environment, no state in app processes, health and readiness endpoints, logs to stdout. The same stack runs on the laptop or any Linux host; only configuration differs.

- **Milestone 1:** the CLI calls the runtime in-process. Ollama, or an optional hosted API, is reached at a configured endpoint.
- **Milestone 2 onward:** one Python service (API and runtime), PostgreSQL, and an optional telemetry profile, started with Docker Compose. The CLI becomes an API client.
- **Later, if justified:** separate API and worker processes, restricted execution workers, Temporal, TypeScript MCP servers.

## Observability

Four separate records: run events and step records (the truth about runs), audit events (hash-chained security facts), traces (OpenTelemetry, with GenAI conventions), and structured logs and metrics. Metadata and digests by default, never raw content. An LLM trace viewer arrives in M2.3. Details, including retention, are in [observability.md](observability.md).

## Open choices

| Choice | Decided |
|---|---|
| Durable execution: our own step log, DBOS, or Temporal | M2.1, by experiment ([ADR 0018](../adr/0018-durable-execution-decided-in-m2.md)) |
| Async database driver: psycopg 3 or asyncpg | M2.1, by workload benchmark ([tech stack](tech-stack.md#persistence)) |
| ASGI server and worker topology | Not yet scheduled; needed by the API in M2.2 ([API spec](api.md)) |
| Model routing policy | Only on evidence ([roadmap](../project/roadmap.md#later-only-on-evidence)); no automatic fallback meanwhile ([models](models.md)) |
| Sandbox backend | M5.1 ([sandbox options](../research/local-sandbox-options.md)) |
| Artifact storage beyond local disk | When artifacts outgrow local disk ([data model](data-model.md#artifacts)) |

Already decided: Python 3.15 ([ADR 0014](../adr/0014-python-toolchain.md)); PostgreSQL 18 with psycopg 3 ([ADR 0019](../adr/0019-search-architecture.md)).
