# Research Log

Dated findings that shaped decisions. Each entry is short and links to the research note or ADR with the detail. Linked pages and APIs change, so recheck them when implementing.

## Open questions

| ID | Question | Evidence needed | Phase |
|---|---|---|---|
| R-003 | PostgreSQL 18 or 19? | Compatibility plus workload benchmark | 7 |
| R-004 | psycopg 3 or asyncpg? | Compatibility, migrations, concurrency | 7 |
| R-005 | Which local models, for which profiles? | Versioned tool-use suite, context scaling, resource use | 0 / 3 |
| R-006 | Which sandbox backend? | Threat model and negative tests on a Linux host | 16 |
| R-007 | Which MCP SDK and protocol revision? | Release notes, migration guide, contract test | 15 |
| R-008 | Is Temporal justified? | Durability requirements, failure-injection comparison | Later |
| R-009 | Do tiered models beat one model? | Same cases and hardware, cost vs quality | Later |
| R-010 | Which observability backend? | Usefulness vs local resource cost | 9 |
| R-011 | Is full-text search enough, or are embeddings needed? | Milestone 1 eval: retrieval misses by cause | 6 |
| R-012 | Which model backs the default profile? | Milestone 1 eval: local vs hosted accuracy, cost, latency | 6 |

Closed: R-001 (host environment), 2026-11-25. R-002 (Python 3.15), 2026-11-26.

## Entries

### 2026-11-25: Initial technology snapshot

- **PostgreSQL:** 18.7 (Nov 12) and 19.0 (Nov 19) are both current. 19 adds features with modest relevance here. Version choice deferred to Phase 7. → [note](research/POSTGRES_18_VS_19.md)
- **Python:** 3.15.2 and 3.14.10 were both released 2026-10-25. Start from 3.14 and test 3.15. `uv` gives `pyproject.toml` plus a committed `uv.lock`. → [devguide](https://devguide.python.org/versions/), [uv](https://docs.astral.sh/uv/guides/projects/)
- **MCP:** use the official Python and TypeScript SDKs. The v2 SDK line was described as targeting the 2026-07-28 protocol revision; confirm in Phase 15. → [spec](https://modelcontextprotocol.io/specification/)
- **Ollama:** supports chat tool calls and JSON-schema structured output; reliability depends on the model. → [API](https://github.com/ollama/ollama/blob/main/docs/api.md)
- **Temporal:** workflow state is rebuilt by replay, so side effects go in activities, which may run more than once. Build in-process first ([ADR 0006](adr/0006-in-process-before-temporal.md)). → [durable execution](https://docs.temporal.io/durable-execution)
- **Agent security:** OWASP's 2026 agentic Top 10 used as a checklist. Landlock, rootless Docker, and gVisor have different boundaries; a container alone is no argument. → [note](research/LOCAL_SANDBOX_OPTIONS.md)

### 2026-11-25: Host environment

Windows 11 + Ubuntu 26.04.1 on WSL2; i7-13700H, 15.68 GiB RAM, RTX 4050 6 GB. WSL sees 7.6 GiB. Docker Desktop's WSL integration works (cgroup v2). `/dev/kvm` is present but not accessible. No uv or Linux Node; Windows npm leaks onto the PATH. → [environment baseline](research/ENVIRONMENT_BASELINE_2026-11-25.md)

### 2026-11-25: Inference placement

Windows Ollama on loopback was unreachable from WSL in NAT mode and reachable after enabling mirrored networking. Chose Windows-hosted Ollama over Ollama-in-WSL (duplicate weights, WSL memory pressure) and over NAT with a widened listener. The active model directory holds 27.05 GB. → [ADR 0010](adr/0010-windows-hosted-ollama-initial-deployment.md)

### 2026-11-25: First model screen

At 4K both 4B candidates run fully on the GPU: Qwen3 4B 57.0 tok/s (3.3 GB), Nemotron 4B 61.1 tok/s (2.8 GB). Qwen3 8B partly offloads to CPU (12.6 tok/s). All four tool scenarios pass for both 4B models: T1 (selection), T2 (product search, rerun 2026-11-26 after a PowerShell `$100` interpolation bug), T3 (two parallel calls), T4 (asks for the missing city). Nemotron's tool prompt is about twice as many tokens. No model selected. → [benchmarks](research/OLLAMA_MODEL_BENCHMARKS_2026-11-25.md)

**Lesson:** run experiments from a versioned harness, not interactive shells.

### 2026-11-26: Context scaling

With `num_ctx` raised from 4K to 32K, Qwen3 4B grows from 3.3 GB to 8.0 GB and spills to CPU from 16K (77% GPU, then 51%), falling to 1.3 tok/s at 32K. Nemotron 4B grows from 2.8 GB to 3.5 GB, stays on the GPU, and holds about 47–50 tok/s. With thinking off, both recalled a planted code word at every size. With thinking on, Qwen3 used its whole 64-token budget on reasoning. One Nemotron request stalled at 16K and is treated as an outlier. Resource fit favours Nemotron; quality is still untested, so no model is selected. R-005 stays open. Caveats: one run per configuration, an easy needle, and Ollama's flash-attention and KV-cache settings weren't recorded. → [benchmarks](research/OLLAMA_MODEL_BENCHMARKS_2026-11-25.md#context-scaling-2026-11-26)

### 2026-11-26: Goal and scope agreed

Through a question-and-answer session with the owner: the purpose is practising production-grade AI engineering; the reference use case is a file agent, read-only first ([ADR 0011](adr/0011-file-agent-reference-use-case.md)); the deployment is portable and cloud-ready ([ADR 0012](adr/0012-portable-deployment.md)); and the workflow is branches, PRs, and CI ([ADR 0013](adr/0013-pull-request-workflow.md)). The repository goes public under Apache-2.0.

**Finding:** a Claude Pro subscription does not include API access; API usage needs a separately funded Console account. Monthly API credits come only with Max, Ultra, and Team plans. The hosted adapter therefore uses a small prepaid Console balance with a hard limit. → [Pro plan](https://support.claude.com/en/articles/8325606-what-is-the-pro-plan), [API credits](https://support.claude.com/en/articles/17154008-monthly-api-credits-for-max-ultra-and-team-plans)

### 2026-11-26: Enterprise gap

Mapped what would change if this ran as a production application at a large manufacturer, with Komatsu as the example: SSO, source-system connectors, multilingual search (PostgreSQL full-text can't segment Japanese), a model gateway with data residency, Kubernetes and IaC, compliance including export control. Planned as milestone 6 with free local stand-ins. Taken now: `language` and `classification` fields on documents, with policy able to keep a class away from hosted models. → [note](research/ENTERPRISE_GAP.md)

### 2026-11-26: Where the working copy lives

Benchmarked the dev loop on `/mnt/c` vs WSL ext4: 82.8 s vs 1.5 s in total, 19.2 s vs 0.8 s for 1,000 tests. Moving only the venv to ext4 still left tests at 13.9 s, because the cost is per file opened across the Windows boundary. Decision: the owner works in a WSL ext4 clone; the assistant keeps the Windows-side folder and syncs through git. → [environment baseline](research/ENVIRONMENT_BASELINE_2026-11-25.md), [ADR 0013](adr/0013-pull-request-workflow.md)

### 2026-11-26: Python version and toolchain

CPython 3.14.10 and 3.15.2 both installed the full planned dependency set from prebuilt wheels with source builds disabled, including later candidates temporalio and pgvector; Ruff and mypy accept 3.15 as a target. Chose 3.15, uv, Ruff, strict mypy, pytest, and GitHub Actions pinned to commit SHAs. → [ADR 0014](adr/0014-python-toolchain.md)

### 2026-11-26: Type checker and domain types

Compared mypy, Pyright, ty, and Pyrefly. Pyright has much higher typing-spec conformance than mypy; current mypy is faster than Pyright; ty is still 0.0.x with no stable API. The earlier objection to Pyright, a Node download at first run, disappears with the `pyright[nodejs]` extra. Owner chose Pyright ([ADR 0015](adr/0015-pyright.md)). For domain types the owner chose Pydantic over dataclasses or attrs; Pydantic is already required by the Anthropic SDK, the MCP SDK, and FastAPI ([ADR 0016](adr/0016-pydantic-domain-types.md)). → [pydevtools comparison](https://pydevtools.com/handbook/explanation/how-do-mypy-pyright-and-ty-compare/)

## Entry template

```markdown
### YYYY-MM-DD: Topic
Question, sources (with dates and versions), facts, experiment and results,
interpretation, decision or status, revisit trigger. Link the note or ADR.
```
