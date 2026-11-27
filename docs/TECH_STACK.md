# Tech Stack

What we plan to use, why, the credible alternatives, and what would make us reconsider. Exact versions are pinned when each phase starts.

## Languages

| Subsystem | Language | Status | Why |
|---|---|---|---|
| Agent runtime and orchestration | Python | Accepted | Model ecosystem, async I/O, evaluation tooling |
| API / control plane | Python | Proposed | No cross-language hop for a local system |
| Node-native tools, future clients | TypeScript | Accepted | npm ecosystem, browser and IDE integrations, MCP TS SDK |
| Specialised infrastructure | Go or Rust | Deferred | Only for a measured concurrency, memory, native-integration, or isolation need |

Polyglot does not mean microservices. Another language becomes a separate component only where a real process, security, or deployment boundary already exists.

## Python and packaging

- **Interpreter:** Python 3.15. Every planned dependency installed from prebuilt wheels on 3.15.2 ([ADR 0014](adr/0014-python-toolchain.md)). If one ever lags, fall back to 3.14 in a superseding ADR.
- **Environment:** `uv`. Metadata in `pyproject.toml`; `uv.lock` committed and never hand-edited. Dependency groups for dev, telemetry, and so on.
- **Alternatives:** Poetry, PDM, Hatch, pip-tools. `uv` is a convenience, not an architectural dependency.

## API layer

**Proposed:** FastAPI, Pydantic v2, and the ASGI server the FastAPI stack supports. It gives typed models, OpenAPI, async endpoints, and simple SSE. The API is a transport adapter; use cases never touch FastAPI request objects.

**Alternatives:** Starlette (thinner), Litestar, Django (if this becomes a conventional CRUD product), Fastify or NestJS (if the backend moves to Node).

## Persistence

**Proposed:** PostgreSQL with SQLAlchemy 2.x and Alembic. The major version (18 or 19) is decided in M2.1 ([research note](research/POSTGRES_18_VS_19.md)). Driver: psycopg 3 or asyncpg, chosen on compatibility, migrations, typing, and a realistic benchmark rather than synthetic throughput.

**Alternatives:** SQLModel, raw psycopg, or Kysely/Drizzle if a TypeScript service ever owns a database. No second database without a specific workload.

## Inference

Ollama 0.40.18 on Windows, reached from WSL at `127.0.0.1:11434` over mirrored networking, still bound to loopback. See [ADR 0010](adr/0010-windows-hosted-ollama-initial-deployment.md). Candidate models and measurements are in [MODEL_SPEC.md](MODEL_SPEC.md).

Adapters in milestone 1: Ollama, Anthropic API (optional, prepaid Console balance with a hard limit), and a fake adapter for tests. Use the official Anthropic Python SDK. Two real providers from the start keep the abstraction honest. No gateway proxy until the complexity calls for one.

**Later options:** vLLM when there are concurrent users (load-tested in M3), llama.cpp, other hosted providers, LiteLLM. Models are pinned by digest and listed in a licence registry ([model spec](MODEL_SPEC.md#model-registry-licences-and-pinning)).

## Tools

Native Python tools go through our dispatcher. MCP uses the official Python SDK, or the TypeScript SDK for Node servers. Pin the SDK and protocol revision. MCP is interoperability, not scheduling, storage, or authorisation.

## Orchestration

**Initial:** our own in-process scheduler on asyncio (TaskGroup, semaphores, bounded queues), with explicit plan and state contracts. TaskGroup is a structured-concurrency primitive, not a workflow engine.

**Durability:** chosen in M2.1 by a failure-injection experiment between our own PostgreSQL step log, DBOS, and Temporal ([ADR 0018](adr/0018-durable-execution-decided-in-m2.md)).

**Alternatives:** Celery, RQ, or BullMQ for independent background jobs; LangGraph or Pydantic AI for agent state and loops (both compared after milestone 1); Prefect or Dagster for data workflows.

## CLI

Typer, as a thin client: it parses arguments, calls the runtime (an API client from milestone 2), and renders events. No agent or policy logic lives in the CLI.

## Testing and quality

- Contracts: Pydantic v2 for domain and boundary types, in strict, frozen, extra-forbidding mode ([ADR 0016](adr/0016-pydantic-domain-types.md)); JSON Schema across process and tool boundaries.
- Tests: pytest; Hypothesis for property and stateful tests, starting with the run state machine; contract tests for providers and MCP.
- Lint and format: Ruff. Type checking: Pyright in strict mode, the one authoritative checker ([ADR 0015](adr/0015-pyright.md)).
- Telemetry: OpenTelemetry SDK and structured logs. Collectors and backends are optional.
- Evaluation: our own harness and versioned cases in `evals/`.

## CI and repository

- GitHub, public, Apache-2.0. Feature branches and pull requests; `master` is protected ([ADR 0013](adr/0013-pull-request-workflow.md)).
- GitHub Actions on Linux: Ruff, type check, and pytest on every PR; the public eval set once it can run in CI (M2.3). Hosted-model evals run only when a key is configured and never on PRs from forks.

## Local infrastructure

- Run only the services the current phase needs. Unit tests need none of them.
- Docker Compose (through Docker Desktop's WSL integration) for PostgreSQL and optional services, enabled by profile.
- Bind PostgreSQL, Ollama, and telemetry to localhost. Never enable Docker's unauthenticated TCP socket.
- Model weights, database volumes, artifacts, and secrets stay out of Git.
- Docker is a packaging tool, not a hostile-code sandbox.

## Deferred technologies

| Technology | Reconsider when |
|---|---|
| Temporal, DBOS | Compared in M2.1 ([ADR 0018](adr/0018-durable-execution-decided-in-m2.md)); adopted only if one wins the recovery experiment |
| Redis | A measured need for caching, ephemeral coordination, or a queue |
| Kafka / NATS | Independent consumers or fan-out outgrow PostgreSQL-backed events |
| Kubernetes | Several services and replicas justify the operational overhead |
| Vector DB | Retrieval scale or latency outgrows PostgreSQL (full-text, pgvector) |
| Go / Rust | A profiled bottleneck, native integration, or sandbox requirement |
| LangGraph, Pydantic AI | The post-milestone-1 comparison shows one beats our own loop on the same evals by enough to justify the dependency |
| LiteLLM | Multi-provider routing becomes painful in our own adapters |

## Decision rule

Choose the simplest technology that meets the functional, security, and operational requirements. For a material choice, record the workload, alternatives, operational cost, security posture, compatibility, evidence, reversibility, and a trigger to revisit it.
