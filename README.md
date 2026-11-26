# Agent Platform

A self-hosted, general-purpose AI agent platform, built from first principles as a learning project. The repository currently holds the design: architecture, specifications, decision records, and Phase 0 research. No application code exists yet.

## Direction

- General-purpose agent platform, local and self-hosted, with minimal running cost.
- API/SDK first. CLI, web inspector, and IDE integrations come later as clients of the same API.
- Python for the agent runtime and orchestration. TypeScript for Node-native integrations and future clients. Go or Rust only where a measured need justifies them.
- Ollama for local inference. The runtime talks to models through a provider-neutral adapter.
- Model profiles (primary, fast, summarizer, specialist, evaluator) are designed in from the start, but one model can serve all of them at first.
- Native tools and MCP tools share one registry, policy check, and dispatcher.
- Shell, filesystem, browser, and code execution are long-term goals, behind a separate execution broker and sandbox.
- A small in-process scheduler first. Temporal only if durable-workflow requirements show up.
- PostgreSQL as the system of record. The major version (18 or 19) is still open.

## Where things stand

Phase 0 (environment and architecture discovery). The Windows 11 + WSL2 host is characterised, Docker works from WSL, and Windows-hosted Ollama is reachable from WSL over mirrored networking. Two 4B models are under evaluation. See the status table at the top of [`docs/DEVELOPMENT_ROADMAP.md`](docs/DEVELOPMENT_ROADMAP.md).

## Documentation

Start with the charter, architecture, and roadmap. Read the specifications when working on the relevant phase.

| Document | Covers |
|---|---|
| [Project charter](docs/PROJECT_CHARTER.md) | Purpose, scope, non-goals, use cases, quality attributes |
| [Architecture](docs/ARCHITECTURE.md) | Components, trust boundaries, request flow, source layout |
| [Tech stack](docs/TECH_STACK.md) | Technology choices, alternatives, and when to revisit them |
| [Development roadmap](docs/DEVELOPMENT_ROADMAP.md) | Current status, phases, and exit gates |
| [Assistant working guide](docs/ASSISTANT_WORKING_GUIDE.md) | How AI assistants should work in this repository |
| [Learning path](docs/LEARNING_PATH_AND_SOURCES.md) | Books and primary sources, mapped to phases |

**Specifications:** [runtime and orchestration](docs/RUNTIME_SPEC.md) · [models](docs/MODEL_SPEC.md) · [tools](docs/TOOL_SPEC.md) · [security](docs/SECURITY_SPEC.md) · [data model](docs/DATA_MODEL.md) · [API](docs/API_SPEC.md) · [testing and evaluation](docs/EVALUATION_SPEC.md)

Observability lives in the architecture doc. The release checklist is Phase 16 of the roadmap.

**Decisions and research:** [ADRs](docs/adr/README.md) · [research log](docs/RESEARCH_LOG.md) · [environment baseline](docs/research/ENVIRONMENT_BASELINE_2026-11-25.md) · [Ollama benchmarks](docs/research/OLLAMA_MODEL_BENCHMARKS_2026-11-25.md) · [sandbox options](docs/research/LOCAL_SANDBOX_OPTIONS.md) · [PostgreSQL 18 vs 19](docs/research/POSTGRES_18_VS_19.md)

## Decision status labels

| Label | Meaning |
|---|---|
| Accepted | Confirmed by the project owner. Implementation details may still be open. |
| Proposed | Recommended, not yet confirmed or proven. |
| Open | Needs research, an experiment, or a decision. |
| Deferred | Postponed until a stated trigger. |
| Superseded | Replaced by a later decision; kept for history. |

A proposal does not become accepted by being written down. Change a status only when the owner confirms it.

## Repository rules

- Never commit secrets, model weights, database volumes, or generated artifacts.
- Version-sensitive facts (releases, SDK behaviour, model capabilities) are dated. Recheck them when implementing and record changes in the research log.
