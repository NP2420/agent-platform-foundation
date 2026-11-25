# Research Log

**Baseline research snapshot:** 2026-11-25

This log records material findings that inform the architecture. It is not a permanent guarantee that a linked page or API remains unchanged. Recheck source and version when implementing.

## 2026-11-25 — Initial architecture baseline

### PostgreSQL 18.7 and 19.0

- PostgreSQL 19.0 was released on 2026-11-19. Its release notes include `INSERT ... ON CONFLICT DO SELECT ... RETURNING`, concurrent repacking, read-after-write `WAIT` behavior for standby replay, and parallel autovacuum improvements among other changes.
- PostgreSQL 18.7 was released on 2026-11-12.
- PostgreSQL major releases are supported for five years under the current versioning policy.
- **Interpretation:** PostgreSQL 19 has potentially useful features, but release age/driver/extension/back-up compatibility deserves scrutiny. The database major version is an explicit evaluation rather than an automatic “latest wins” decision.
- **Decision status:** PostgreSQL accepted as proposed system of record; 18.7 vs 19.0 open.
- Sources: [PostgreSQL 19 release notes](https://www.postgresql.org/docs/19/release-19.html), [PostgreSQL 18.7 release notes](https://www.postgresql.org/docs/release/18.7/), [versioning policy](https://www.postgresql.org/support/versioning/).

### Python runtime and tooling

- The Python Developer's Guide listed Python 3.15.2 and 3.14.10 as released on 2026-10-25 at this snapshot.
- **Interpretation:** Python 3.15 should be tested, but dependency compatibility and ecosystem maturity determine the selected runtime. Python 3.14.x is the initial conservative candidate, not a final version decision.
- `uv` supports project metadata in `pyproject.toml` and a reproducible `uv.lock` intended for source control.
- Sources: [Python version status](https://devguide.python.org/versions/), [uv project guide](https://docs.astral.sh/uv/guides/projects/).

### MCP SDKs and protocol

- Official Python and TypeScript MCP SDK repositories provide the supported SDK implementations. The v2 SDK line was described as targeting the 2026-07-28 protocol revision at the research snapshot; confirm current release/migration state before implementation.
- **Interpretation:** use the official SDK rather than implementing MCP wire behavior manually. Pin SDK/protocol compatibility and write contract tests. MCP is not our scheduler, database, authorization system, or execution sandbox.
- Sources: [MCP specification](https://modelcontextprotocol.io/specification/), [Python SDK](https://github.com/modelcontextprotocol/python-sdk), [TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk).

### Ollama and local inference

- Current Ollama docs describe chat/tool calling and structured outputs via a JSON schema format. Support and reliability depend on the exact model and runtime.
- **Interpretation:** Ollama is a viable baseline, but tool-use and structured-output capability must be tested against exact model tags/digests on the actual hardware.
- Sources: [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md), [tool support](https://ollama.com/blog/tool-support), [structured outputs](https://github.com/ollama/ollama/blob/main/docs/capabilities/structured-outputs.mdx).

### Temporal and retry semantics

- Temporal's durable execution model persists workflow history and reconstructs workflow state by replay. Side effects belong in activities, not nondeterministic workflow code.
- Activities may execute more than once when completion is not durably reported; external side effects need idempotency or reconciliation.
- **Interpretation:** first implement and understand the in-process runtime/scheduler; maintain a clean adapter boundary so Temporal can be evaluated later.
- Sources: [Temporal durable execution](https://docs.temporal.io/durable-execution), [Temporal Python SDK](https://github.com/temporalio/sdk-python), [Temporal Python error handling](https://github.com/temporalio/documentation/blob/main/docs/develop/python/best-practices/error-handling.mdx).

### Agent security

- OWASP's 2026 Agentic Applications taxonomy includes risks such as goal hijacking, tool misuse, identity/privilege abuse, supply-chain compromise, unexpected code execution, memory poisoning, inter-agent communication abuse, cascading failures, false trust, and rogue agents.
- Linux Landlock is a userspace access-control mechanism; Docker rootless mode reduces risk associated with daemon/container privileges; gVisor provides an application-kernel isolation layer. These technologies have different threat boundaries and host requirements.
- **Interpretation:** a distinct execution broker and host-specific sandbox decision must precede arbitrary code/shell capability. A container alone is not a complete security argument.
- Sources: [OWASP Top 10 for Agentic Applications 2026](https://genai.owasp.org/top-10-for-agentic-applications-2026/), [Landlock](https://www.kernel.org/doc/html/latest/userspace-api/landlock.html), [Docker rootless](https://docs.docker.com/engine/security/rootless/), [gVisor](https://gvisor.dev/docs/).

### Learning sources

- DDIA 2nd edition (Kleppmann and Riccomini, 2026) is the principal reference for data systems, transactions, distributed systems, and durability.
- Chip Huyen's *AI Engineering* (2024) is the principal reference for model selection, evaluation, datasets, inference, and AI application architecture.
- Google's SRE books and *Building Secure & Reliable Systems* provide operational and security/reliability foundations.
- Sources: [DDIA 2e](https://www.oreilly.com/library/view/designing-data-intensive-applications/9781098119058/), [AI Engineering](https://www.oreilly.com/library/view/ai-engineering/9781098166298/), [Google SRE books](https://sre.google/books/), [Building Secure & Reliable Systems](https://google.github.io/building-secure-and-reliable-systems/).

## Open investigations

| ID | Question | Required evidence | Planned phase |
|---|---|---|---|
| R-001 | Host OS, kernel, hardware, container backend? | Local environment inspection | 0 |
| R-002 | Python 3.14 vs 3.15? | Dependency support matrix, toolchain tests | 0–1 |
| R-003 | PostgreSQL 18.7 vs 19.0? | Compatibility + representative benchmark | 7 |
| R-004 | psycopg 3 vs asyncpg? | Compatibility, migration, concurrency tests | 7 |
| R-005 | Which Ollama models and quantizations? | Reproducible model benchmark | 3 |
| R-006 | Which sandbox backend? | Host-specific threat model and negative tests | 10 |
| R-007 | MCP SDK/protocol version? | Current release notes, migration guide, compatibility test | 9 |
| R-008 | When is Temporal justified? | Workflow durability requirements and failure-injection comparison | 15 |
| R-009 | Do tiered models improve outcomes? | Same dataset/hardware, cost-quality comparison | 13 |
| R-010 | Which observability backend? | Operational value, resource cost, local workflow needs | 12 |

## Research entry template

```markdown
## YYYY-MM-DD — Topic
- Question:
- Context/workload:
- Sources (title, publisher, date/version, URL):
- Verified facts:
- Interpretations:
- Experiment and environment:
- Results:
- Limitations/unknowns:
- Recommendation:
- Decision status / ADR:
- Revisit trigger:
```
