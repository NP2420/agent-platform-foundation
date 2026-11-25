# Agent Platform — Architecture Baseline

**Document set:** 0.1.0 · **Baseline date:** 2026-11-25  
**Status:** Project direction approved; detailed decisions retain the status shown in the documents and ADRs.

This repository is the durable project reference for designing and implementing a self-hosted, general-purpose AI agent platform. The project is educational as well as technical: implementations must be accompanied by explanations, primary-source research, experiments, tests, and reflection.

## Start here

1. Read [`docs/INDEX.md`](docs/INDEX.md).
2. Read [`docs/PROJECT_CHARTER.md`](docs/PROJECT_CHARTER.md) and [`docs/SYSTEM_OVERVIEW.md`](docs/SYSTEM_OVERVIEW.md).
3. Read [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) and [`docs/TECH_STACK.md`](docs/TECH_STACK.md).
4. Read [`docs/DEVELOPMENT_ROADMAP.md`](docs/DEVELOPMENT_ROADMAP.md) before implementation.
5. Read [`docs/ASSISTANT_WORKING_GUIDE.md`](docs/ASSISTANT_WORKING_GUIDE.md) whenever an AI assistant helps with the repository.
6. Follow [`PROJECT_INITIALIZATION.md`](PROJECT_INITIALIZATION.md) for Git/repository setup.

## Agreed direction

- General-purpose agent platform, initially local and self-hosted.
- API/SDK-first product boundary; CLI, web inspector, and IDE integrations are later clients.
- Python is the primary agent-runtime/orchestration language.
- TypeScript is available for Node-native integrations and future client/harness surfaces.
- Go or Rust may be used for specialized infrastructure only when a measured requirement justifies them.
- Ollama is the initial local inference baseline.
- Model routing supports multiple profiles/tiers, but the first vertical slice may use one model.
- Native tools and MCP tools are both first-class integration types.
- Full execution capability (filesystem, shell, browser, code) is a long-term goal behind a separate security boundary.
- Build a modest in-process scheduler first; evaluate Temporal when durable workflow requirements justify it.
- PostgreSQL is the proposed system-of-record database. PostgreSQL 18.7 versus 19.0 remains an explicit evaluation decision.
- Self-hosted, low-cost development is a design constraint.

## Status vocabulary

- **Agreed:** directly confirmed by the project owner.
- **Proposed:** recommended baseline, pending evidence or explicit confirmation.
- **Open:** requires research, environment discovery, or a decision.
- **Deferred:** intentionally postponed until a stated trigger occurs.
- **Superseded:** replaced by a later decision; retained for history.

Do not silently convert Proposed or Open decisions into Agreed decisions.

## Source freshness

The baseline is dated 2026-11-25. Vendor APIs, SDKs, MCP revisions, model capabilities, security tooling, and database releases change. Re-check official documentation and release notes when a decision is implemented, and record material changes in `docs/RESEARCH_LOG.md` and an ADR.
