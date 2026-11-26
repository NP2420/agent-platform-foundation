# Learning Path and Sources

Targeted reading: study what the next design decision needs, then come back when implementation raises a deeper question. Nothing here needs reading cover to cover before coding. Chapter numbers are approximate; check them against your edition.

## Core books

**Designing Data-Intensive Applications, 2nd ed.** (Kleppmann and Riccomini, O'Reilly, 2026). The main reference for storage, transactions, events, and distributed-systems failure. [O'Reilly](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/)

- Ch. 1–2: trade-offs and non-functional requirements
- Ch. 3–4: data models, storage, indexes
- Ch. 5: encoding, schema evolution, durable execution
- Ch. 8: transactions
- Ch. 9–10: distributed failure, consistency, consensus
- Ch. 12–13: stream processing
- Ch. 14: privacy and ethics

**AI Engineering** (Chip Huyen, O'Reilly, 2024). Model selection, evaluation, datasets, inference, and application architecture. [O'Reilly](https://www.oreilly.com/library/view/ai-engineering/9781098166298/)

- Ch. 1–2: foundation-model capabilities
- Ch. 3–4: evaluation methodology and systems
- Ch. 8: dataset engineering
- Ch. 9: inference optimisation
- Ch. 10: application architecture and feedback

**Google SRE books** ([sre.google/books](https://sre.google/books/)). SLIs, SLOs, error budgets, monitoring, incident response. Adapt the large-scale assumptions to a local deployment.

**Building Secure & Reliable Systems** ([free online](https://google.github.io/building-secure-and-reliable-systems/)). Threat modelling, defence in depth, secure defaults.

## Systems references

- [OSTEP](https://pages.cs.wisc.edu/~remzi/OSTEP/): processes, scheduling, concurrency, virtualisation. Read before the sandbox work.
- [The Linux Programming Interface](https://man7.org/tlpi/): processes, file descriptors, permissions, signals, syscalls.
- [CS:APP](https://csapp.cs.cmu.edu/): process, memory, and exception foundations, as needed.
- [Building Microservices, 2nd ed.](https://www.oreilly.com/library/view/building-microservices-2nd/9781492034018/): read selectively when weighing service boundaries.

## Primary online sources

Recheck versions when implementing.

**Agent design:** [Anthropic, Building effective agents](https://www.anthropic.com/engineering/building-effective-agents) · [Anthropic, Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents) · [OpenAI platform docs](https://platform.openai.com/docs/)

**MCP:** [Specification](https://modelcontextprotocol.io/specification/) · [Python SDK](https://github.com/modelcontextprotocol/python-sdk) · [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)

**Model serving:** [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md) · [Ollama tool support](https://ollama.com/blog/tool-support) · [Ollama structured outputs](https://github.com/ollama/ollama/blob/main/docs/capabilities/structured-outputs.mdx) · [vLLM](https://docs.vllm.ai/) · [llama.cpp](https://github.com/ggml-org/llama.cpp)

**Data and workflow:** [PostgreSQL release notes](https://www.postgresql.org/docs/release/) · [PostgreSQL versioning](https://www.postgresql.org/support/versioning/) · [Temporal durable execution](https://docs.temporal.io/durable-execution) · [Temporal Python SDK](https://github.com/temporalio/sdk-python) · [SQLAlchemy asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) · [uv projects](https://docs.astral.sh/uv/guides/projects/)

**Security and observability:** [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/top-10-for-agentic-applications-2026/) · [Landlock](https://www.kernel.org/doc/html/latest/userspace-api/landlock.html) · [Docker rootless](https://docs.docker.com/engine/security/rootless/) · [gVisor](https://gvisor.dev/docs/) · [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/)

## Reading by phase

| Phase | Reading |
|---|---|
| 1 Toolchain | Python and uv docs; GitHub Actions docs |
| 2 Domain contracts | DDIA 1–2, 5, 8; JSON Schema |
| 3–4 Model adapters, loop | AI Engineering 1–4, 9–10; Ollama and Anthropic API docs; Anthropic agent articles |
| 5 Tools and file search | Anthropic tools article; PostgreSQL full-text search chapter; Secure & Reliable Systems |
| 6 Evaluation | AI Engineering 3–4, 8; retrieval evaluation literature |
| 7 Persistence | DDIA 3–5, 8–10; PostgreSQL and SQLAlchemy docs |
| 8–9 API, observability | SSE spec; OpenTelemetry docs; SRE monitoring chapters |
| 10–11 Identity, approvals | OWASP authentication and session cheat sheets; Secure & Reliable Systems |
| 12–14 Writes, orchestrator | DDIA 8–9; OSTEP concurrency; asyncio docs |
| 15 MCP | MCP spec and SDK docs |
| 16 Sandbox | OSTEP virtualisation; TLPI; Landlock, gVisor, Firecracker docs |
| Release review | SRE; Secure & Reliable Systems |
