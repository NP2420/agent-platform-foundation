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

Read before the phase starts. Chapter numbers are approximate; check them against your edition.

| Phase | Reading |
|---|---|
| M1.1 Toolchain | Python and uv docs; GitHub Actions docs |
| M1.2 Domain types, state machine | [*Architecture Patterns with Python*, ch. 1: Domain Modeling](https://www.cosmicpython.com/book/chapter_01_domain_model.html); Pydantic [strict mode](https://pydantic.dev/docs/validation/latest/concepts/strict_mode/) and [models](https://pydantic.dev/docs/validation/latest/concepts/models/) (frozen models); Hypothesis [stateful testing](https://hypothesis.readthedocs.io/en/latest/stateful.html) |
| M1.3 Evals | AI Engineering 3–4; Inspect AI and promptfoo docs; confidence intervals for proportions |
| M1.4 Model adapters | AI Engineering 5, 9; Ollama and Anthropic API docs on tool use and structured output |
| M1.5 Threat model, tools, policy | OWASP Top 10 for LLM Applications; STRIDE threat modelling; Anthropic tools article |
| M1.6 Corpus and search | BEIR paper (Thakur et al., 2021); pg_textsearch and pgvector docs; *A Systematic Analysis of Chunking Strategies* (arXiv 2601.14123) |
| M1.7–M1.8 Pipeline, agent loop | AI Engineering 6; Anthropic *Building effective agents* |
| M1.9 Comparison, feedback | AI Engineering 8, 10; published model and system cards |
| M2.1 Persistence | DDIA 3–5, 8–10; PostgreSQL and SQLAlchemy docs |
| M2.2–M2.3 API, tracing | SSE spec; OpenTelemetry docs; SRE monitoring chapters |
| M3.1–M3.2 Identity, approvals | OWASP authentication and session cheat sheets; Secure & Reliable Systems |
| M4.1–M4.3 Writes, orchestrator | DDIA 8–9; OSTEP concurrency; asyncio docs |
| M4.4 MCP | MCP spec and SDK docs |
| M5.1 Sandbox | OSTEP virtualisation; TLPI; Landlock, gVisor, Firecracker docs |
| Release review | SRE; Secure & Reliable Systems |
