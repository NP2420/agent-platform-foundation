# Development Roadmap

Milestones deliver one capability end to end, measured. Phases are the build steps inside them, numbered per milestone (M1.3 is milestone 1, phase 3), so adding a phase never renumbers another milestone. A phase ends when its exit gate is met, not when code exists. Milestones are sized by scope, not by time estimates.

## Status

This table is the single place that tracks project status.

| Item | Status | Notes |
|---|---|---|
| Phase 0: host and container environment | Done | [Environment baseline](research/ENVIRONMENT_BASELINE_2026-11-25.md). Revisit if the host changes. |
| Phase 0: inference topology | Done | Windows-hosted Ollama over WSL mirrored networking ([ADR 0010](adr/0010-windows-hosted-ollama-initial-deployment.md)) |
| Phase 0: local model screening | Done for now | T1–T4 pass for both 4B models. To 32K context, Nemotron stays fully on GPU; Qwen3 4B only to 8K. See [benchmarks](research/OLLAMA_MODEL_BENCHMARKS_2026-11-25.md). Quality comparison continues in the milestone 1 eval set. |
| Phase 0: goal and scope | Done | Agreed 2026-11-26: [charter](PROJECT_CHARTER.md), ADRs [0011](adr/0011-file-agent-reference-use-case.md)–[0013](adr/0013-pull-request-workflow.md) |
| Repository setup | Done | Public on GitHub, Apache-2.0, noreply authorship, `master` protected by a ruleset requiring `lint, types, tests`, secret scanning with push protection |
| **Milestone 1** | In progress | M1.1 done. Recording the agreed decisions (PRs 1–5) before M1.2. |

**Next steps**

1. Finish recording the agreed decisions: this plan and the eval methodology; runtime and model decisions; the observability spec; CI hardening.
2. M1.2: design the domain types and run state machine for approval, after the [phase reading](LEARNING_PATH_AND_SOURCES.md#reading-by-phase).

Carried over from model screening, for M1.3 and M1.4: rerun the thinking-on context test with `--num-predict 512`; record Ollama's flash-attention and KV-cache settings; rerun the one stalled Nemotron row.

## Working cycle

For each chunk ([CONTRIBUTING.md](../CONTRIBUTING.md)):

1. **Read:** the phase reading, before the phase starts.
2. **Design:** types, signatures, failure semantics, and planned tests, with options. The owner approves before code.
3. **Implement** on a branch: one concept per PR, about 300 lines at most.
4. **Verify:** tests and evals run; actual output recorded.
5. **Explain back:** the owner explains the design; gaps get discussed.
6. **Merge:** the owner squash-merges once CI passes.
7. **Record:** specs, ADRs, research log, and this table updated in the same PR; a learning note at the end of each phase.

## Milestone 1: cited answers from the CLI

**Delivers:** a CLI question → real runtime → search over approved folders → an answer citing file and section, or "not supported by the documents". Built eval-first ([ADR 0017](adr/0017-eval-first.md)): a fixed pipeline and an agent loop, each with two tool-call methods, compared on the same eval set with local and hosted models.

### M1.1: Repository and toolchain — done

Python 3.15, uv, Ruff, Pyright, pytest, CI, pre-commit ([ADR 0014](adr/0014-python-toolchain.md), [ADR 0015](adr/0015-pyright.md)).

### M1.2: Domain types and run state machine

Pydantic domain types ([ADR 0016](adr/0016-pydantic-domain-types.md)) for runs, steps, messages, tool calls, model results, events, errors, and the principal. The run state machine with `QUEUED`, `RUNNING`, `WAITING_APPROVAL`, `CANCELLING`, `CANCELLED`, `COMPLETED`, and `FAILED` with reasons. UUIDv7 IDs. Structured logs carrying run and trace IDs. No model, no database.
**Exit:** example and Hypothesis stateful tests cover every legal and illegal transition; terminal states never change.

### M1.3: Eval harness and first cases

Case format, dev / held-out test / regression splits, code-based scoring (citations exist, abstention, retrieval recall), confidence intervals, and a runner tested against a fake agent. The first ~10 cases per category, verified by the owner. Time-boxed study: port ~5 cases to Inspect AI and promptfoo and compare them in a learning note.
**Exit:** one command runs the eval against the fake agent and writes a reproducible report.

### M1.4: Model adapters

Provider-neutral contract; Ollama, Anthropic API, and fake adapters; both tool-call methods (native tool calling and schema-constrained JSON); timeouts, normalised errors, per-call tokens, cost, and latency. Recorded responses in CI; a live suite run in WSL. Prompts as versioned files. Choose the hosted model and spend limit.
**Exit:** contract tests pass on recordings and live against both real providers.

### M1.5: Threat model, tools, policy, and file search

First the threat model (OWASP LLM Top 10 and STRIDE). Then the tool registry, policy checks, risk tiers, classification, and audit records, and the file-search and file-read tools: extraction for Markdown, text, code, and PDF; passages with citations; path allowlist and the always-blocked list. Build the public corpus: equipment manuals and the PostgreSQL 18 and 19 manuals.
**Exit:** contract, permission, path-escape, classification, and malformed-input tests pass.

### M1.6: Fixed pipeline baseline

Always search, then answer from the retrieved passages. Rejects answers that cite unretrieved passages. Measured on the eval set.
**Exit:** a baseline eval report for each model and tool-call method.

### M1.7: Agent loop

The model decides when and what to search. Bounded loop, context assembly, hard budget caps on by default, run events, cancellation through `CANCELLING`, and concurrent tool calls under a fixed cap.
**Exit:** tests cover completion, multi-turn runs, malformed responses, budget exhaustion, timeouts, and cancellation; an agent eval report.

### M1.8: CLI, feedback, comparison, and review

CLI client; per-answer feedback with a script that turns bad answers into draft cases; the LLM judge, checked against the owner's labels; the four-way comparison (pipeline vs agent × two tool-call methods); cases grown to ~25 per category; a private eval set over a personal folder in `evals/private/`; the system card.
**Exit:** comparison report, system card, milestone review, and release `v0.1.0`.

### After milestone 1: LangGraph comparison

Rebuild the milestone 1 agent on LangGraph, time-boxed, and compare it on the same eval set. Written up as a learning note.

## Milestone 2: persisted runs, API, and observability

**Delivers:** runs persisted in PostgreSQL and served through a versioned API with streamed events; the tracing backend; evals gating CI.

### M2.1: PostgreSQL persistence

Schema, migrations, repositories, transaction boundaries, run and event persistence, idempotency records, document index tables. Review the API and data-model specs first.
**Decide:** PostgreSQL 18 vs 19 ([research note](research/POSTGRES_18_VS_19.md)); psycopg 3 vs asyncpg.
**Exit:** tests cover conflicts, restart recovery, uniqueness, and concurrent access.

### M2.2: API and event streaming

Versioned REST API, SSE events, idempotency keys, error envelope, scheduled and event-triggered runs through the same create-run path, and a feedback endpoint. The CLI becomes an API client.
**Exit:** a client can run a task and reconstruct its progress from events alone.

### M2.3: Tracing backend and CI eval gate

OpenTelemetry Collector and dashboards as an optional Compose profile. The public eval set runs in CI and fails the PR on a regression past a threshold set from the milestone 1 baseline.
**Exit:** a bad run can be diagnosed from its trace and records alone; a deliberate quality regression fails CI.

## Milestone 3: multiple users

**Delivers:** local accounts, authentication, per-user folder permissions, approvals, a web run inspector.

### M3.1: Identity and authorisation

Local accounts, password or token authentication, sessions, per-user folder grants, admin role. File permissions are enforced by the application's authorisation layer, because the agent runs as one OS user.
**Exit:** tests show one user's runs, files, and results are invisible to another.

### M3.2: Approvals and web inspector

Approval requests bound to exact actions, with expiry. A minimal local web page to ask questions, browse runs, give feedback, and approve or deny.
**Exit:** approval replay, argument mutation, and expiry tests pass.

## Milestone 4: write actions and MCP

**Delivers:** the agent writes summaries and reports, plans and carries out multi-step file changes with approval and undo, and uses MCP tools.

### M4.1: Output writing

Summaries and reports written to a per-user output folder only.
**Exit:** writes outside the output folder are impossible, and tests prove it.

### M4.2: Orchestrator

Plans as data, DAG validation, dependency resolution, bounded concurrency, failure policies, cancellation ([runtime spec](RUNTIME_SPEC.md#orchestration)). A bulk file reorganisation is the first real plan.
**Exit:** tests prove validation, dependency order, bounded parallelism, the failure policy, and clean cancellation.

### M4.3: File organisation

Rename, move, and tag, run as orchestrated plans with a preview, approval, an undo journal, and idempotent operations.
**Exit:** every change can be previewed, approved, and undone; partial failures leave a recoverable state.

### M4.4: MCP

MCP client adapter, server lifecycle, trust policy. MCP tools go through the same registry, policy, and dispatcher path.
**Exit:** a test MCP server's tool runs under the same policy and audit as a native tool.

## Milestone 5: sandboxed code execution

### M5.1: Execution broker and sandbox

Structured execution requests, per-run workspaces, worker identity, resource and network limits, artifact handling, cleanup, audit.
**Decide:** the sandbox backend ([research note](research/LOCAL_SANDBOX_OPTIONS.md)), including KVM feasibility. It must run on a plain Linux host, not only WSL.
**Exit:** negative tests show filesystem, network, process, and resource access outside the grant is blocked. No arbitrary execution before this.

## Milestone 6: enterprise profile

**Delivers:** the same system in the shape a large company would run it, using free local stand-ins. Candidate tools: Keycloak (SSO), OpenSearch or PGroonga (Japanese search), vLLM behind a model gateway, kind or k3d with Terraform, Langfuse; classification and export-control policy; Japanese eval cases. Tools are chosen when the milestone starts. Scope is in the [enterprise gap note](research/ENTERPRISE_GAP.md).

## Every milestone ends with

- a release: semantic version tag, changelog, release notes, and a software bill of materials;
- the release review below, scoped to that milestone;
- a learning note.

## Later, only on evidence

Each needs a measured reason before it starts.

- **Context compaction and memory:** when runs exceed the usable context in measured cases.
- **Tiered model routing:** when one model per profile measurably costs too much or fails a task category.
- **Subagents:** when delegation measurably improves success on chosen evals.
- **Temporal:** when durable timers, long approvals, or multi-worker recovery are needed and a failure-injection test shows the gap.

## Release review

Before calling any milestone production-ready for a stated scope:

- **Scope:** supported users, workload, hosts, threat model, residual risks.
- **Correctness:** state-machine and contract tests; invalid plans, tools, and paths fail closed.
- **Reliability:** bounded retries; idempotency or an explicit unknown-outcome policy per side-effecting tool; backup and restore actually exercised.
- **Security:** model output is never authorisation; deny-by-default scopes; bound approvals; redaction; no unintended network exposure.
- **Quality:** reproducible eval results with thresholds from measured baselines.
- **Operations:** runs reconstructable from records; correlated telemetry; cost within budget.

A failed high-severity security or data-integrity check is never offset by a good average eval score.
