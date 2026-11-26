# Agent Platform

A self-hosted agent platform, built from first principles to practise production-grade AI engineering. The repository holds the design (architecture, specs, decision records), Phase 0 research, and an evaluation harness. Application code starts with milestone 1.

## Direction

- **Purpose:** practise building production-grade AI the way a company would: evaluated, secure, observable, and budgeted.
- **Reference use case:** an agent that works with files. It starts read-only with cited answers, then writes reports, organises files with approval and undo, and finally runs code in a sandbox.
- **Models are configuration:** Ollama by default; hosted APIs are optional adapters with spend limits.
- **Security:** model output never authorises anything; file access is deny-by-default through approved folders; every run carries a user identity.
- **Portable:** containers and environment configuration; runs on a laptop or any Linux host.
- **Stack:** Python runtime, PostgreSQL, OpenTelemetry. Native and MCP tools share one registry and policy check.
- **Workflow:** feature branches, pull requests, CI. Licensed Apache-2.0.

## Where things stand

Phase 0 is done: the host is characterised, local models are screened, and the goal is agreed. Milestone 1 (cited answers from the CLI) starts with the Phase 1 toolchain. See the status table in [`docs/DEVELOPMENT_ROADMAP.md`](docs/DEVELOPMENT_ROADMAP.md).

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

Observability lives in the architecture doc. The release checklist is the last section of the roadmap.

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

- The repository is public. Personal files, private eval sets (`evals/private/`), secrets, and model weights never enter it.
- Changes arrive as pull requests; see [ADR 0013](docs/adr/0013-pull-request-workflow.md).

- Never commit database volumes or generated artifacts other than eval results.
- Version-sensitive facts (releases, SDK behaviour, model capabilities) are dated. Recheck them when implementing and record changes in the research log.

## Licence

[Apache-2.0](LICENSE).
