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

Phase 0 and M1.1 (toolchain and CI) are done. Milestone 1 (cited answers from the CLI) continues with M1.2, the domain types and run state machine. See the status table in [`docs/project/roadmap.md`](docs/project/roadmap.md).

## Documentation

Start with the charter, architecture, and roadmap. Read the specifications when working on the relevant phase.

| Document | Covers |
|---|---|
| [Project charter](docs/project/charter.md) | Purpose, scope, non-goals, use cases, quality attributes |
| [Architecture](docs/design/architecture.md) | Components, trust boundaries, request flow, source layout |
| [Tech stack](docs/design/tech-stack.md) | Technology choices, alternatives, and when to revisit them |
| [Development roadmap](docs/project/roadmap.md) | Current status, phases, and exit gates |
| [Contributing](CONTRIBUTING.md) | Workflow, branches, commits, PRs, local checks |
| [Assistant working guide](AGENTS.md) | How AI assistants should work in this repository |
| [Learning path](docs/learning/learning-path.md) | Books and primary sources, mapped to phases |

**Specifications:** [runtime and orchestration](docs/design/runtime.md) · [models](docs/design/models.md) · [tools](docs/design/tools.md) · [security](docs/design/security.md) · [data model](docs/design/data-model.md) · [observability and audit](docs/design/observability.md) · [API](docs/design/api.md) · [testing and evaluation](docs/design/evaluation.md)

Observability lives in the architecture doc. The release checklist is the last section of the roadmap.

**Decisions and research:** [ADRs](docs/adr/README.md) · [research log](docs/research/research-log.md) · [environment baseline](docs/research/2026-11-25-environment-baseline.md) · [Ollama benchmarks](docs/research/2026-11-25-ollama-model-benchmarks.md) · [sandbox options](docs/research/local-sandbox-options.md) · [PostgreSQL 18 vs 19](docs/research/postgres-18-vs-19.md) · [enterprise gap](docs/research/enterprise-gap.md)

## Development

Requires [uv](https://docs.astral.sh/uv/) 0.13.x. From WSL, in a clone on the Linux filesystem (not `/mnt/c`; see the [environment baseline](docs/research/2026-11-25-environment-baseline.md)):

```bash
uv sync                      # Python 3.15 and dev tools, exactly as locked
uv run pre-commit install    # once per clone: Ruff on every commit
uv run ruff format --check . # formatting
uv run ruff check .          # lint
uv run pyright               # types (strict)
uv run pytest                # tests
```

CI runs the same commands on every pull request. Copy `.env.example` to `.env` for local configuration; `.env` is git-ignored.

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
- Changes arrive as pull requests; see [CONTRIBUTING.md](CONTRIBUTING.md) and [ADR 0013](docs/adr/0013-pull-request-workflow.md).

- Never commit database volumes or generated artifacts other than eval results.
- Version-sensitive facts (releases, SDK behaviour, model capabilities) are dated. Recheck them when implementing and record changes in the research log.

## Licence

[Apache-2.0](LICENSE).
