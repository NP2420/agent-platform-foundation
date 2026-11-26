# Learning Path and Sources

**Purpose:** connect each development phase to reliable technical literature. Reading is targeted: study the relevant concepts before design decisions, then return to the source when implementation reveals new questions. This is not a requirement to finish every book cover to cover before coding.

## 1. Core books

### Designing Data-Intensive Applications, 2nd Edition

Martin Kleppmann and Chris Riccomini, O'Reilly, February 2026.

Official page: https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/

Use as the primary reference for database, event, transaction, distributed-systems, and data architecture decisions.

Suggested reading map (confirm chapter titles/order against the copy in use):

- Ch. 1–2: trade-offs, nonfunctional requirements, and data-intensive system design — project framing and architecture reviews.
- Ch. 3–4: data models and storage/retrieval — relational schema, indexes, query patterns.
- Ch. 5: encoding/evolution and durable execution/event-driven architecture — schema evolution and durable workflows.
- Ch. 8: transactions — run creation, idempotency records, state updates, concurrency.
- Ch. 9–10: distributed systems, failures, consistency, and consensus — failure boundaries and recovery semantics.
- Ch. 12–13: stream processing and streaming philosophy — event consumers and telemetry where relevant.
- Ch. 14: doing the right thing — privacy, ethics, legal, and operational considerations.

### AI Engineering: Building Applications with Foundation Models

Chip Huyen, O'Reilly, 2024.

Official page: https://www.oreilly.com/library/view/ai-engineering/9781098166298/

Use for model selection, evaluations, data, inference optimization, application architectures, feedback, and operational trade-offs.

Suggested map:

- Ch. 1–2: foundation model capability and application design — model/runtime context.
- Ch. 3–4: evaluation methodology and evaluation systems — our evaluation harness.
- Ch. 8: dataset engineering — versioned evaluation cases and data quality.
- Ch. 9: inference optimization — local model serving, batching, quantization, latency/resources.
- Ch. 10: AI application architecture and user feedback — model routing, system behavior, and product boundary.

Check the exact chapter mapping in the current edition before assigning reading; use the concepts relevant to the phase.

### Site Reliability Engineering (Google), 2nd Edition and online SRE books

Official library: https://sre.google/books/

Use selected chapters/concepts for service-level indicators/objectives, error budgets, monitoring, incident response, capacity, automation, and operational readiness. Do not apply large-scale service assumptions uncritically to a local deployment; adapt the principles to the scope.

### Building Secure & Reliable Systems

Google, free online book: https://google.github.io/building-secure-and-reliable-systems/

Use for threat modeling, defense in depth, secure defaults, resilient design, and security/reliability collaboration.

## 2. Systems foundations and references

- **Operating Systems: Three Easy Pieces (OSTEP):** https://pages.cs.wisc.edu/~remzi/OSTEP/ — processes, scheduling, concurrency, memory, persistence, virtualization. Relevant before sandbox/process execution.
- **The Linux Programming Interface:** https://man7.org/tlpi/ — processes, file descriptors, permissions, namespaces-adjacent OS mechanisms, signals, and system calls. Consult sections relevant to the selected host.
- **Computer Systems: A Programmer's Perspective (CS:APP):** https://csapp.cs.cmu.edu/ — process/memory/exception foundations where needed.
- **Building Microservices, 2nd Edition:** https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/ — use selectively when considering service boundaries; the initial architecture is deliberately a modular monolith.

## 3. Primary online sources

Always recheck version/date when implementing; these links are entry points, not timeless proof of current behavior.

### Agent design and tool quality

- Anthropic, *Building effective agents*: https://www.anthropic.com/engineering/building-effective-agents
- Anthropic, *Writing effective tools for agents*: https://www.anthropic.com/engineering/writing-tools-for-agents
- OpenAI platform documentation: https://platform.openai.com/docs/ and API references as needed.

Use to study agent loops, workflow-vs-agent trade-offs, tool definitions, and operational patterns. Treat vendor recommendations as useful engineering evidence, not universal law.

### MCP

- Official specification: https://modelcontextprotocol.io/specification/
- Official Python SDK: https://github.com/modelcontextprotocol/python-sdk
- Official TypeScript SDK: https://github.com/modelcontextprotocol/typescript-sdk

Check current protocol revision, SDK version, migration notes, transport, authorization, and security guidance. The baseline research indicates the v2 SDK line targets the 2026-07-28 protocol revision; verify when implementation begins.

### Ollama and model serving

- Ollama API: https://github.com/ollama/ollama/blob/main/docs/api.md
- Ollama tool support: https://ollama.com/blog/tool-support
- Ollama structured outputs: https://github.com/ollama/ollama/blob/main/docs/capabilities/structured-outputs.mdx
- vLLM documentation: https://docs.vllm.ai/
- llama.cpp: https://github.com/ggml-org/llama.cpp

### Database and workflow

- PostgreSQL release notes: https://www.postgresql.org/docs/release/
- PostgreSQL versioning policy: https://www.postgresql.org/support/versioning/
- Temporal durable execution: https://docs.temporal.io/durable-execution
- Temporal Python SDK: https://github.com/temporalio/sdk-python
- SQLAlchemy asyncio: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- uv project guide: https://docs.astral.sh/uv/guides/projects/

### Security and observability

- OWASP Top 10 for Agentic Applications 2026: https://genai.owasp.org/top-10-for-agentic-applications-2026/
- Linux Landlock documentation: https://www.kernel.org/doc/html/latest/userspace-api/landlock.html
- Docker rootless mode: https://docs.docker.com/engine/security/rootless/
- gVisor documentation: https://gvisor.dev/docs/
- OpenTelemetry Collector: https://opentelemetry.io/docs/collector/

## 4. Reading-to-development map

| Phase | Primary reading |
|---|---|
| 0–1: architecture and setup | DDIA Ch. 1–2; Python/uv official docs; project charter |
| 2: domain/state contracts | DDIA Ch. 2, 5, 8; API/schema docs |
| 3–4: model baseline/runtime | AI Engineering Ch. 1–4, 9–10; Ollama docs; agent-design articles |
| 5: tools and policies | Tool/MCP specs; Anthropic effective-tools article; secure systems book |
| 6: scheduler/concurrency | OSTEP process/concurrency chapters; DDIA Ch. 9; Python asyncio docs |
| 7: persistence | DDIA Ch. 3–5, 8–10; PostgreSQL docs; SQLAlchemy docs |
| 8–9: API/events/MCP | API specs, MCP protocol/SDK docs, OpenTelemetry docs |
| 10: sandbox | OSTEP virtualization/security; TLPI; Landlock, Docker, gVisor/VM docs; secure systems book |
| 11: context/retrieval | AI Engineering data/evaluation chapters; retrieval research and current system docs |
| 12: evaluations/operations | AI Engineering Ch. 3–4; SRE; OpenTelemetry |
| 13–14: routing/delegation | AI Engineering Ch. 1–4, 9–10; current multi-agent research and evaluations |
| 15–16: durability/release | DDIA Ch. 5, 8–10; Temporal docs; SRE; secure systems book |

## 5. How sources are used

For each important design topic:

1. Identify the question and the kind of evidence needed.
2. Prefer current official specifications/docs for API/protocol behavior.
3. Use textbooks for durable concepts and systems reasoning.
4. Use papers/benchmarks for new model/agent techniques; inspect methodology and limitations.
5. Use blogs/tutorials as secondary explanation, not sole support for security or correctness claims.
6. Run a project-specific experiment when the result depends on our model, data, hardware, or concurrency pattern.
7. Record date, version, evidence, confidence, and decision impact in `RESEARCH_LOG.md` or a focused research note.

## 6. Avoid cargo-cult learning

Do not read a whole textbook chapter merely to tick a box. Identify the concepts needed for the next design decision, work through meaningful examples, and revisit the material when implementation reveals a deeper issue. The goal is conceptual transfer: understand why a mechanism exists and when it is or is not appropriate.
