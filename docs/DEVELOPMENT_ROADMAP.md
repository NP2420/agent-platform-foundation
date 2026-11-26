# Development Roadmap

Milestones deliver one capability end to end, measured. Phases are the build steps inside them. A phase ends when its exit gate is met, not when code exists. Milestones are sized by scope, not by time estimates.

## Status

This table is the single place that tracks project status.

| Item | Status | Notes |
|---|---|---|
| Phase 0: host and container environment | Done | [Environment baseline](research/ENVIRONMENT_BASELINE_2026-11-25.md). Revisit if the host changes. |
| Phase 0: inference topology | Done | Windows-hosted Ollama over WSL mirrored networking ([ADR 0010](adr/0010-windows-hosted-ollama-initial-deployment.md)) |
| Phase 0: local model screening | Done for now | T1–T4 pass for both 4B models. To 32K context, Nemotron stays fully on GPU; Qwen3 4B only to 8K. See [benchmarks](research/OLLAMA_MODEL_BENCHMARKS_2026-11-25.md). Quality comparison continues in the milestone 1 eval set. |
| Phase 0: goal and scope | Done | Agreed 2026-11-26: [charter](PROJECT_CHARTER.md), ADRs [0011](adr/0011-file-agent-reference-use-case.md)–[0013](adr/0013-pull-request-workflow.md) |
| Repository setup | Done | Public on GitHub, Apache-2.0, noreply authorship, `master` protected by a ruleset, secret scanning with push protection |
| **Milestone 1** | In progress | Phase 1 done. Phase 2 decisions so far: Pydantic domain types, Pyright, a `CANCELLING` state, timeout as a reason on `FAILED`, Hypothesis. |

**Next steps**

1. Make the CI job `lint, types, tests` a required status check in the `master` ruleset.
2. Review the remaining Phase 2 design questions with the owner, then build the run state machine and domain contracts.

Carried over from model screening, to fold into the milestone 1 eval work: rerun the thinking-on context test with `--num-predict 512`; record Ollama's flash-attention and KV-cache settings; rerun the one stalled Nemotron row.

## Working cycle

For each chunk:

1. **Discover:** the problem, constraints, unknowns.
2. **Research:** relevant chapters, official docs, specs, papers.
3. **Design:** contracts, state transitions, failure semantics, acceptance criteria, alternatives.
4. **Implement** on a branch: one concept or interface at a time.
5. **Verify:** tests and evals run, with actual output recorded in the PR.
6. **Review:** the owner reviews and merges the PR.
7. **Record:** specs, ADRs, research log, and this table updated in the same PR.

## Milestone 1: cited answers from the CLI

**Delivers:** a CLI question → real runtime → read-only search over one approved folder → an answer citing file and section, or "not supported by the documents". Evaluated on local and hosted models.

### Phase 1: Repository and toolchain

Python version (3.14 vs 3.15 compatibility check), `uv` project and lockfile, Ruff, one type checker, pytest, package layout, configuration and secrets conventions, a `.env.example`, and GitHub Actions running lint, types, and tests on every PR. Working copies: owner on WSL ext4, assistant on the Windows-side folder, synced through git (decided 2026-11-26; [environment baseline](research/ENVIRONMENT_BASELINE_2026-11-25.md)).
**Exit:** a fresh clone creates the locked environment and CI passes.

### Phase 2: Domain contracts and run state machine

Typed objects for runs, steps, messages, tool calls, model results, events, errors, and the principal (user identity and scopes). Lifecycle transitions with tests. No model, no database.
**Read:** state machines, layering, Pydantic vs dataclasses, JSON Schema.
**Exit:** deterministic tests cover valid and invalid transitions; contracts are framework-free.

### Phase 3: Model adapters

Provider-neutral contract; Ollama adapter; hosted adapter (Anthropic API, behind configuration and a spend limit); fake adapter. Health and capability checks, timeouts, normalised errors, tool-call parsing, usage and cost accounting per call.
**Exit:** contract tests pass against the fake adapter and both real providers; per-call tokens, cost, and latency are recorded.

### Phase 4: Single-agent loop

Bounded loop, context assembly, stop conditions, budgets (steps, tokens, spend, wall time), run events, cancellation. Several tool calls in one response run concurrently under a fixed cap (a `TaskGroup` and a semaphore, not yet a scheduler).
**Exit:** tests cover completion, multi-turn runs, malformed responses, budget exhaustion, provider timeout, and cancellation.

### Phase 5: Tools, policy, and file search

Tool registry and dispatcher, schema validation, risk tiers, policy checks, audit records. The first real tool: read-only full-text search over an approved folder, with text extraction for Markdown, text, code, and PDF, document version and modification time, and passage-level citations. Path allowlist and the always-blocked list enforced in the tool, with tests for traversal and symlink escape.
**Exit:** the search tool passes contract, permission, path-escape, and malformed-input tests.

### Phase 6: Evaluation and CLI

A CLI client over the runtime. A 25–40 question set over the public corpus (assistant drafts, owner verifies), including no-answer and misleading-question cases. Report answer accuracy, citation correctness, abstention, tokens, cost, and latency, for a local and a hosted model. A small private set over a personal folder, kept in `evals/private/`.
**Exit:** the eval runs from one command, reproducibly, and its report is in the PR.

**Milestone 1 review:** is full-text search good enough, or is there measured evidence for embeddings? Which model goes in the default profile? What did the failures have in common?

## Milestone 2: persisted runs, API, and observability

**Delivers:** runs persisted in PostgreSQL and served through a versioned API with streamed events; tracing; evals gating CI.

### Phase 7: PostgreSQL persistence

Schema, migrations, repositories, transaction boundaries, run and event persistence, idempotency records, document index tables.
**Decide:** PostgreSQL 18 vs 19 ([research note](research/POSTGRES_18_VS_19.md)); psycopg 3 vs asyncpg.
**Exit:** tests cover conflicts, restart recovery, uniqueness, and concurrent access.

### Phase 8: API and event streaming

Versioned REST API, SSE events, idempotency keys, error envelope, scheduled and event-triggered runs through the same create-run path. The CLI becomes an API client.
**Exit:** a client can run a task and reconstruct its progress from events alone.

### Phase 9: Observability and CI eval gate

OpenTelemetry tracing across API, runtime, model, and tool calls; structured logs; cost and latency dashboards as an optional Compose profile. The public eval set runs in CI and fails the PR on a regression past a threshold set from the milestone 1 baseline.
**Exit:** a bad run can be diagnosed from its trace and records alone; a deliberate quality regression fails CI.

## Milestone 3: multiple users

**Delivers:** local accounts, authentication, per-user folder permissions, approvals, a web run inspector.

### Phase 10: Identity and authorisation

Local accounts, password or token authentication, sessions, per-user folder grants, admin role. File permissions are enforced by the application's authorisation layer, because the agent runs as one OS user.
**Exit:** tests show one user's runs, files, and results are invisible to another.

### Phase 11: Approvals and web inspector

Approval requests bound to exact actions, with expiry. A minimal local web page to ask questions, browse runs, and approve or deny.
**Exit:** approval replay, argument mutation, and expiry tests pass.

## Milestone 4: write actions and MCP

**Delivers:** the agent writes summaries and reports, plans and carries out multi-step file changes with approval and undo, and uses MCP tools.

### Phase 12: Output writing

Summaries and reports written to a per-user output folder only.
**Exit:** writes outside the output folder are impossible, and tests prove it.

### Phase 13: Orchestrator

Plans as data, DAG validation, dependency resolution, bounded concurrency, failure policies, cancellation ([runtime spec](RUNTIME_SPEC.md#orchestration)). A bulk file reorganisation is the first real plan.
**Read:** asyncio structured concurrency, queues, backpressure. Compare with LangGraph without adopting it.
**Exit:** tests prove validation, dependency order, bounded parallelism, the failure policy, and clean cancellation.

### Phase 14: File organisation

Rename, move, and tag, run as orchestrated plans with a preview, approval, an undo journal, and idempotent operations.
**Exit:** every change can be previewed, approved, and undone; partial failures leave a recoverable state.

### Phase 15: MCP

MCP client adapter, server lifecycle, trust policy. MCP tools go through the same registry, policy, and dispatcher path.
**Exit:** a test MCP server's tool runs under the same policy and audit as a native tool.

## Milestone 5: sandboxed code execution

### Phase 16: Execution broker and sandbox

Structured execution requests, per-run workspaces, worker identity, resource and network limits, artifact handling, cleanup, audit.
**Decide:** the sandbox backend ([research note](research/LOCAL_SANDBOX_OPTIONS.md)), including KVM feasibility. It must run on a plain Linux host, not only WSL.
**Exit:** negative tests show filesystem, network, process, and resource access outside the grant is blocked. No arbitrary execution before this.

## Milestone 6: enterprise profile

**Delivers:** the same system in the shape a large company would run it, using free local stand-ins: SSO (Keycloak), multilingual search with Japanese support, vLLM behind a model gateway, Kubernetes and Terraform with two environments, LLM tracing, classification and export-control policy, and Japanese eval cases. Scope and the stand-ins are in the [enterprise gap note](research/ENTERPRISE_GAP.md). Phases are planned when milestone 5 is done.

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

## Scope control

Each PR delivers one concept, interface, or tested behaviour. If research invalidates a decision, update the ADR and this plan before continuing.
