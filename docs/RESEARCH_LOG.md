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
| R-001 | Host OS, kernel, hardware, container backend? | Local environment inspection | 0 — initial baseline completed; revisit on host changes |
| R-002 | Python 3.14 vs 3.15? | Dependency support matrix, toolchain tests | 0–1 |
| R-003 | PostgreSQL 18.7 vs 19.0? | Compatibility + representative benchmark | 7 |
| R-004 | psycopg 3 vs asyncpg? | Compatibility, migration, concurrency tests | 7 |
| R-005 | Which Ollama models and quantizations? | Reproducible tool/task benchmark and resource measurements | 0/3 — exploratory benchmark underway; no final selection |
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


## 2026-11-25 — WSL2 environment and Docker integration

- **Question:** Can the existing Windows/WSL2 laptop serve as the local development and inference environment, and what host constraints affect the design?
- **Verified facts:** Windows 11 Home build 26300; Ubuntu 26.04.1 LTS under WSL2; Linux kernel `6.18.58.1-microsoft-standard-WSL2`; Intel Core i7-13700H (14 cores / 20 logical processors); 15.68 GiB physical RAM; NVIDIA RTX 4050 Laptop GPU with 6,141 MiB reported VRAM. WSL showed 7.6 GiB RAM and 2 GiB swap. systemd, cgroup v2, user namespaces, and `/dev/dxg` were present. `/dev/kvm` was present but not readable/writable by the current user. The inspected shell showed `Seccomp=0` and `NoNewPrivs=0`; these values apply only to that process and are not evidence about container restrictions.
- **Docker observation:** Docker Desktop 4.100.1 / Engine 29.9.3 was running with the WSL2 backend. Per-distro WSL integration was enabled for `Ubuntu-26.04`; WSL's Linux Docker CLI then successfully reached the engine, which reported cgroup v2.
- **Filesystem constraint:** Windows C: had 70.27 GiB free in the later measurement. WSL's ext4 reported roughly 1 TB virtual capacity; this must not be interpreted as host physical free space. Keep active repository files on the WSL ext4 filesystem unless a specific Windows integration requires otherwise.
- **Toolchain observation:** WSL had Python 3.14.4 but no pip module or uv; Node.js was absent inside WSL while `npm` resolved to the Windows installation on `/mnt/c`; Go and Rust were absent. No project dependency version is selected yet.
- **Interpretation:** WSL2 is a viable development environment, but local resources are constrained. Avoid concurrent model residency and the full infrastructure stack until measured. KVM sandbox feasibility remains open. Resolve the Windows npm path leak before introducing Node tooling.
- **Decision status:** environment baseline recorded; use Ubuntu/WSL2 as primary development environment; Docker Desktop WSL integration verified. See `research/ENVIRONMENT_BASELINE_2026-11-25.md`.
- **Sources:** [Microsoft WSL networking](https://learn.microsoft.com/en-us/windows/wsl/networking), [Microsoft WSL configuration](https://learn.microsoft.com/en-us/windows/wsl/wsl-config), [Docker WSL best practices](https://docs.docker.com/desktop/features/wsl/best-practices/), [Docker WSL integration](https://docs.docker.com/desktop/features/wsl/).

## 2026-11-25 — Windows-hosted Ollama through WSL mirrored networking

- **Question:** Should initial local inference run in Windows or inside WSL?
- **Verified facts:** Windows-hosted Ollama `0.40.18` was listening on `127.0.0.1:11434`. Under the initial NAT arrangement, WSL could not reach either its localhost endpoint or the Windows host IP. After configuring `[wsl2] networkingMode=mirrored` in `.wslconfig` and restarting WSL, the request `curl http://127.0.0.1:11434/api/version` from Ubuntu succeeded. The configured `OLLAMA_MODELS` path was `C:\Users\<user>\OLLAMA` and its recursive file-size measurement was 27.05 GB. An earlier 3.11 GB measurement used the inactive default `.ollama\models` path and is not the correct storage measurement.
- **Alternatives:** Ollama hosted in WSL (Linux-local service but duplicate model storage and WSL memory use); Windows Ollama with NAT and a wider listener/firewall configuration; containerized inference.
- **Interpretation:** Windows-hosted Ollama is the lowest-friction initial choice for this machine. Mirrored localhost connectivity avoids widening the listener. The provider endpoint must remain configurable so the environment can change later.
- **Decision status:** accepted for initial development environment; not a production deployment commitment. ADR 0010.
- **Sources:** [Microsoft WSL networking](https://learn.microsoft.com/en-us/windows/wsl/networking), [Microsoft WSL configuration](https://learn.microsoft.com/en-us/windows/wsl/wsl-config), [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md).

## 2026-11-25 — Initial local model inference and tool-call smoke tests

- **Question:** Which local models fit the RTX 4050 and can produce usable tool-call proposals?
- **Experiment:** Ollama `0.40.18`; Windows-hosted; RTX 4050 Laptop GPU, 6,141 MiB; Q4_K_M candidates `qwen3:4b-q4_K_M` and `nemotron-3-nano:4b`; 4K context; sequential requests; `think=false`; temperature 0; seed 42. A preliminary `qwen3:8b` observation was also captured.
- **Verified facts:** `ollama ps` reported Qwen3 4B and Nemotron 4B as 100% GPU at 4K context with 3.3 GB and 2.8 GB allocations respectively. Three warm runs averaged 57.03 tok/s for Qwen3 4B and 61.08 tok/s for Nemotron 4B. The Qwen3 requests hit the 128-token output cap; Nemotron generated 54–75 tokens and the saved output did not preserve `done_reason`. Both models passed one simple tool-call smoke test, selecting `get_current_weather` with `city=Boston` and `unit=fahrenheit` from a schema with required fields and an enum, in the presence of a product-search distractor tool. No tool was executed.
- **Qwen3 8B preliminary fact:** one earlier 4K test showed 6.0 GB model allocation and 30% CPU / 70% GPU placement; warm generation was 12.59 tok/s. It was not measured with the same three-run protocol, so do not compare it as a controlled result.
- **Limitations:** tiny sample size; one simple tool prompt per 4B model; no multi-turn round trip, no multi-tool case, no no-tool case, no missing-argument case, no error recovery, no adversarial result, no 8K/16K context, no concurrency, no sustained run, no full model digest capture. Prompt throughput was affected by prompt-cache differences and should not be compared.
- **Interpretation:** both 4B models are viable hardware candidates at 4K context. Nemotron had slightly higher observed generation throughput and lower reported allocation, but model quality and safe tool behavior remain unproven. Qwen3 4B remains the leading primary candidate for further evaluation; Nemotron is an efficiency/secondary candidate. These are provisional descriptions only.
- **Decision status:** no final model-profile assignment. R-005 remains open. Detailed data: `research/OLLAMA_MODEL_BENCHMARKS_2026-11-25.md`.
- **Sources:** [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md), [Ollama API usage fields](https://github.com/ollama/ollama/blob/main/docs/api/usage.mdx), [Qwen3 catalog](https://ollama.com/library/qwen3), [Nemotron 3 Nano catalog](https://ollama.com/library/nemotron-3-nano).
