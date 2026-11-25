# Documentation Index

**Document set:** 0.1.0 · **Baseline:** 2026-11-25

This documentation is the durable project reference. Each document distinguishes agreed direction from proposals and unresolved decisions. The implementation must not silently turn an open question into an architectural commitment.

## Read in this order

1. [Project charter](PROJECT_CHARTER.md) — why the platform exists and what is in scope.
2. [System overview](SYSTEM_OVERVIEW.md) — actors, use cases, quality attributes, and assumptions.
3. [Architecture](ARCHITECTURE.md) — logical components, boundaries, and execution paths.
4. [Technology stack](TECH_STACK.md) — proposed technologies, alternatives, and selection gates.
5. [Development roadmap](DEVELOPMENT_ROADMAP.md) — phase sequence, research gates, implementation chunks, and exit criteria.
6. [Assistant working guide](ASSISTANT_WORKING_GUIDE.md) — mandatory collaboration and engineering practices for AI assistants.
7. [Learning path and sources](LEARNING_PATH_AND_SOURCES.md) — books, chapters, standards, papers, and learning objectives.
8. [Project initialization](../PROJECT_INITIALIZATION.md) — put this baseline into a repository and establish the basic workflow.

## Technical specifications

| Document | Responsibility |
|---|---|
| [Runtime specification](RUNTIME_SPEC.md) | Model interaction loop, run lifecycle, stopping, errors, and bounded execution |
| [Orchestration specification](ORCHESTRATION_SPEC.md) | Plans, dependency graphs, scheduling, concurrency, failures, and delegation |
| [Model specification](MODEL_SPEC.md) | Provider abstraction, Ollama baseline, profiles, routing, and model evaluations |
| [Tool specification](TOOL_SPEC.md) | Native tools, MCP, schemas, dispatch, lifecycle, and tool policy |
| [Security specification](SECURITY_SPEC.md) | Threat model, trust boundaries, permissions, and execution isolation |
| [Data model](DATA_MODEL.md) | Relational entities, event history, idempotency, and persistence responsibilities |
| [API specification](API_SPEC.md) | API/SDK boundary, commands, event envelope, and streaming contract |
| [Evaluation specification](EVALUATION_SPEC.md) | Test layers, agent evaluations, datasets, metrics, and release gates |
| [Observability specification](OBSERVABILITY_SPEC.md) | Logs, traces, metrics, correlation, redaction, and local telemetry |
| [Production readiness](PRODUCTION_READINESS.md) | Evidence required before claiming operational readiness |

## Research and decision records

- [Research log](RESEARCH_LOG.md) — dated findings, source links, confidence, and open investigations.
- [File manifest](FILE_MANIFEST.md) — generated inventory and SHA-256 checksums for this document baseline.
- [PostgreSQL 18 vs 19 evaluation](research/POSTGRES_18_VS_19.md).
- [Local execution sandbox options](research/LOCAL_SANDBOX_OPTIONS.md).
- [Local model baseline and benchmark plan](research/LOCAL_MODEL_BASELINE.md).
- [Architecture Decision Records](adr/) — accepted directions, proposals, and decisions deliberately left open.

## Status vocabulary

- **Agreed:** directly confirmed by the project owner.
- **Accepted direction:** an agreed architectural direction whose implementation details still need design and verification.
- **Proposed:** recommended but not yet confirmed or proven.
- **Open:** requires research, environment discovery, experiment, or explicit decision.
- **Deferred:** intentionally postponed until a trigger occurs.
- **Superseded:** replaced by a newer decision; retained for traceability.

## Change control

For a material architecture change:

1. State the problem and evidence.
2. Identify constraints and alternatives.
3. Research authoritative sources and verify their dates/versions.
4. Run an experiment where the answer is workload-dependent.
5. Record the decision in an ADR.
6. Update affected specifications and this index if needed.

A document is not proof that a feature is implemented. Implementation status and evidence belong in the roadmap, test results, and implementation notes.
