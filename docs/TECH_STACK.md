# Technology Stack and Alternatives

**Purpose:** record the proposed technology allocation, why it fits the workload, what alternatives remain credible, and what evidence is required before pinning exact versions.

## 1. Language allocation

| Subsystem | Preferred language | Status | Reason |
|---|---|---|---|
| Agent runtime and orchestration | Python | Accepted direction | AI/model ecosystem, structured data, evaluation tooling, async I/O |
| API/control plane | Python initially | Proposed | Avoid an unnecessary cross-language hop for the first local system; FastAPI is a candidate |
| Node-native tools and future client surfaces | TypeScript | Accepted direction | npm/Node ecosystem, browser/IDE integrations, MCP TypeScript SDK |
| Specialized infrastructure | Go or Rust | Deferred | Use only for measured concurrency, memory, native integration, isolation, or deployment needs |

Polyglot does not mean microservices everywhere. Start with a Python modular monolith. TypeScript, Go, and Rust components should be separate only when a meaningful process/security/deployment boundary exists.

## 2. Python runtime and package management

**Proposed:** Python 3.14.x as the initial compatibility candidate; test Python 3.15.x before selecting. Use `uv` for environment and dependency management.

Python 3.15.2 and 3.14.10 were listed as released on 2026-10-25 in the Python Developer's Guide at the baseline date. The newest interpreter should not be selected blindly: verify support from FastAPI/Starlette, Pydantic, database drivers, MCP SDK, telemetry packages, test/lint/type tools, and any sandbox libraries. If a required dependency lags on 3.15, select 3.14 and record why.

- Project metadata and dependencies: `pyproject.toml`.
- Exact resolver output: commit `uv.lock`.
- Pin the selected interpreter minor and document how to reproduce the environment.
- Keep optional dependencies grouped (dev, model integrations, telemetry, sandbox) where appropriate.

Alternatives: Poetry, PDM, Hatch, pip-tools. `uv` is preferred as a fast unified project/environment/lock workflow, but this is not a fundamental architectural dependency.

## 3. API and application layer

**Proposed:** FastAPI + Pydantic v2 + an ASGI server supported by the selected FastAPI stack.

Why: typed request/response models, OpenAPI generation, async endpoints, and straightforward SSE integration. The API is a transport adapter; use cases and domain logic must not depend on FastAPI request objects.

Alternatives:
- Starlette: thinner ASGI abstraction when less automatic validation/OpenAPI is desired.
- Litestar: another typed ASGI application framework.
- Django: compelling when the platform becomes a conventional database-backed product with a larger admin/content surface.
- TypeScript/Fastify or NestJS: revisit if the product backend is intentionally moved to Node or if a TypeScript client ecosystem becomes central.

## 4. Persistence

**Proposed:** PostgreSQL as application system of record. Compare PostgreSQL 18.7 and 19.0 using `research/POSTGRES_18_VS_19.md` before choosing a major version.

**Proposed Python libraries:** SQLAlchemy 2.x for database access and Alembic for migrations. Compare psycopg 3 async support and asyncpg for compatibility, operational behavior, typing, migration support, and benchmark results. Do not make a driver decision based only on synthetic throughput.

The domain layer should depend on repository/use-case interfaces, not SQLAlchemy sessions. Each concurrent asyncio task should have an appropriate independent `AsyncSession`; SQLAlchemy documents `AsyncSession` as mutable/stateful and not safe to share across concurrent tasks.

Alternatives: SQLModel (built on SQLAlchemy/Pydantic), direct psycopg for explicit SQL, or Kysely/Drizzle if a separate TypeScript service eventually owns a database boundary. Avoid a second database without a specific workload.

## 5. Model serving and provider integration

**Initial inference:** Ollama `0.40.18`, hosted on Windows and reached from Ubuntu/WSL2 at `http://127.0.0.1:11434` using WSL mirrored networking. This topology has been verified with a successful API version request from WSL. Ollama remains bound to `127.0.0.1`; do not widen the listener or add firewall openings for convenience.

The host's initial candidates are `qwen3:4b-q4_K_M` and `nemotron-3-nano:4b`; `qwen3:8b` is a larger reference candidate. At 4K context, both 4B candidates were reported as 100% GPU, with mean warm generation rates of 57.03 and 61.08 tok/s respectively over three exploratory runs. One single-tool smoke test per 4B model returned the correct tool and arguments. These observations do not determine final model roles. See `research/OLLAMA_MODEL_BENCHMARKS_2026-11-25.md`.

**Internal abstraction:** provider-neutral model request/response contracts plus provider adapters. Preserve capability metadata and provider-specific options rather than flattening all providers into a lowest-common-denominator API. Configure the endpoint (for example, `OLLAMA_BASE_URL`) instead of hard-coding Windows/WSL networking into application code. The initial host placement can change without changing the provider-neutral runtime contract.

Alternatives and future options:
- llama.cpp: local quantized GGUF inference and fine-grained local control.
- vLLM: higher-throughput serving and batching for compatible GPU workloads; requires configuration and hardware fit.
- Remote hosted providers: optional adapters for capability or quality comparison, not a mandatory dependency.
- LiteLLM: optional later gateway if unified routing, provider fallbacks, or centralized usage policies become operational requirements.

Do not introduce a gateway proxy before there is enough complexity to justify it. Start with one Ollama adapter and a fake adapter; add a second real provider to validate abstraction quality when useful.

## 6. Tool integration

- Native Python tools use the internal tool contract and dispatcher.
- MCP tools use the official MCP Python SDK initially; TypeScript MCP SDK is available for Node-native servers/integrations.
- Pin SDK version and protocol revision used; check migration notes and examples when implementing.
- MCP is interoperability, not the scheduler, run store, authorization engine, or trust boundary.

## 7. Orchestration and durability

**Initial:** custom in-process scheduler using asyncio primitives, bounded concurrency, and explicit plan/state contracts.

Evaluate `asyncio.TaskGroup`, semaphores, bounded queues/worker pools, and graph scheduling as separate patterns. Use task groups where structured concurrency fits; don't treat TaskGroup as a full workflow engine.

**Later:** Temporal Python SDK if long-running, resumable, multi-worker workflows justify durable workflow infrastructure. Workflow code must be deterministic; network/model/tool/database/process side effects belong in activities. Activity execution can be retried and therefore external operations need idempotency/reconciliation.

Alternatives: a queue such as Redis-backed BullMQ/Celery/RQ for independent background jobs; LangGraph for graph/state-driven agent workflows; Prefect/Dagster for data-oriented workflow use cases. Compare the actual durability and control requirements before selection.

## 8. Validation, testing, observability

- Contracts: Pydantic for Python models; JSON Schema at cross-process/tool boundaries.
- Testing: pytest; add Hypothesis for state/property testing if beneficial; contract tests for providers and MCP; failure injection.
- Quality: Ruff for lint/format; select mypy or Pyright and make one authoritative type-check command.
- Observability: OpenTelemetry API/SDK with structured logs; collector/backends optional and profile-driven.
- Evaluation: custom evaluation runner, deterministic fixtures, versioned datasets, explicit graders and metrics.

Avoid coupling the domain layer to an observability vendor. Redact or omit sensitive prompt/tool payload attributes by default.

## 9. Packaging and local infrastructure

- Docker Compose for reproducible optional services where host support is suitable.
- Do not assume Docker is a sufficient hostile-code sandbox.
- Keep PostgreSQL/Ollama/telemetry ports bound to localhost or private networks unless there is an explicit access design.
- Keep model weights, DB data, generated artifacts, and credentials out of Git.
- Enable infrastructure by profile; unit tests should not require the entire stack.

## 10. Explicitly deferred technologies

| Technology | Trigger for reconsideration |
|---|---|
| Temporal | Need durable timers, long-running approval waits, workflow replay, multi-worker execution |
| Redis | Measured need for cache, ephemeral coordination, or a queue not handled by current design |
| Kafka/NATS | Independent event consumers, throughput, retention, or fan-out requirements exceed PostgreSQL/event delivery design |
| Kubernetes | Multiple services/replicas and operational team justify orchestration overhead |
| Vector DB | Retrieval workload/scale/latency requires a specialized index beyond PostgreSQL options |
| Go/Rust | Profiled bottleneck, native OS integration, distribution, or sandbox requirement |
| LangGraph | Demonstrated need for graph primitives that outweigh adopting a framework as an execution owner |
| LiteLLM | Multi-provider fleet/routing policy becomes difficult to maintain in our adapters |

## 11. Decision rule

Choose the simplest technology that meets functional, security, reliability, and operational requirements. For a material decision, record: workload, alternatives, operational cost, security posture, compatibility, benchmark evidence, reversibility, and a trigger for revisiting it.
