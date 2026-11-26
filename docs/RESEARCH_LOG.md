# Research Log

Dated findings that shaped decisions. Each entry is short and links to the research note or ADR with the detail. Linked pages and APIs change, so recheck them when implementing.

## Open questions

| ID | Question | Evidence needed | Phase |
|---|---|---|---|
| R-002 | Python 3.14 or 3.15? | Dependency support matrix, toolchain run | 1 |
| R-003 | PostgreSQL 18 or 19? | Compatibility plus workload benchmark | 7 |
| R-004 | psycopg 3 or asyncpg? | Compatibility, migrations, concurrency | 7 |
| R-005 | Which local models, for which profiles? | Versioned tool-use suite, context scaling, resource use | 0 / 3 |
| R-006 | Which sandbox backend? | Threat model and negative tests on the host | 10 |
| R-007 | Which MCP SDK and protocol revision? | Release notes, migration guide, contract test | 9 |
| R-008 | Is Temporal justified? | Durability requirements, failure-injection comparison | 15 |
| R-009 | Do tiered models beat one model? | Same cases and hardware, cost vs quality | 13 |
| R-010 | Which observability backend? | Usefulness vs local resource cost | 12 |

Closed: R-001 (host environment), 2026-11-25.

## Entries

### 2026-11-25: Initial technology snapshot

- **PostgreSQL:** 18.7 (Nov 12) and 19.0 (Nov 19) are both current. 19 adds features with modest relevance here. Version choice deferred to Phase 7. → [note](research/POSTGRES_18_VS_19.md)
- **Python:** 3.15.2 and 3.14.10 were both released 2026-10-25. Start from 3.14 and test 3.15. `uv` gives `pyproject.toml` plus a committed `uv.lock`. → [devguide](https://devguide.python.org/versions/), [uv](https://docs.astral.sh/uv/guides/projects/)
- **MCP:** use the official Python and TypeScript SDKs. The v2 SDK line was described as targeting the 2026-07-28 protocol revision; confirm in Phase 9. → [spec](https://modelcontextprotocol.io/specification/)
- **Ollama:** supports chat tool calls and JSON-schema structured output; reliability depends on the model. → [API](https://github.com/ollama/ollama/blob/main/docs/api.md)
- **Temporal:** workflow state is rebuilt by replay, so side effects go in activities, which may run more than once. Build in-process first ([ADR 0006](adr/0006-in-process-before-temporal.md)). → [durable execution](https://docs.temporal.io/durable-execution)
- **Agent security:** OWASP's 2026 agentic Top 10 used as a checklist. Landlock, rootless Docker, and gVisor have different boundaries; a container alone is no argument. → [note](research/LOCAL_SANDBOX_OPTIONS.md)

### 2026-11-25: Host environment

Windows 11 + Ubuntu 26.04.1 on WSL2; i7-13700H, 15.68 GiB RAM, RTX 4050 6 GB. WSL sees 7.6 GiB. Docker Desktop's WSL integration works (cgroup v2). `/dev/kvm` is present but not accessible. No uv or Linux Node; Windows npm leaks onto the PATH. → [environment baseline](research/ENVIRONMENT_BASELINE_2026-11-25.md)

### 2026-11-25: Inference placement

Windows Ollama on loopback was unreachable from WSL in NAT mode and reachable after enabling mirrored networking. Chose Windows-hosted Ollama over Ollama-in-WSL (duplicate weights, WSL memory pressure) and over NAT with a widened listener. The active model directory holds 27.05 GB. → [ADR 0010](adr/0010-windows-hosted-ollama-initial-deployment.md)

### 2026-11-25: First model screen

At 4K both 4B candidates run fully on the GPU: Qwen3 4B 57.0 tok/s (3.3 GB), Nemotron 4B 61.1 tok/s (2.8 GB). Qwen3 8B partly offloads to CPU (12.6 tok/s). Tool scenarios T1 (selection), T3 (two parallel calls), and T4 (asks for missing city) pass for both 4B models. T2 is invalid because of a PowerShell `$100` interpolation bug. Nemotron's tool prompt is about twice as many tokens. No model selected. → [benchmarks](research/OLLAMA_MODEL_BENCHMARKS_2026-11-25.md)

**Lesson:** run experiments from a versioned harness, not interactive shells.

## Entry template

```markdown
### YYYY-MM-DD: Topic
Question, sources (with dates and versions), facts, experiment and results,
interpretation, decision or status, revisit trigger. Link the note or ADR.
```
