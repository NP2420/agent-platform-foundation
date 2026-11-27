# Project Charter

## Purpose

Practise building production-grade AI the way a company would, so the hard parts and the mistakes happen here, not on the job. The vehicle is a self-hosted agent platform. The model reasons and proposes actions; trusted code validates, authorises, executes, records, and measures them.

Production-grade means four things. The system is **evaluated** (versioned test sets, regression gates), **secure** (least privilege, policy outside the model, injection-aware), **observable** (every run can be traced and explained afterwards), and **budgeted** (cost and latency measured on every model call).

## Reference use case

**An agent that works with files.** It starts read-only: answering questions over approved folders, citing the file and section, and saying so when the documents don't support an answer. It then grows step by step toward anything a user could do with their files, each step behind its own security gate:

1. Read and answer with citations.
2. Write summaries and reports into an output folder.
3. Organise files (rename, move, tag), with approval and undo.
4. Run code on files, in a sandbox.

The use case was chosen because it is useful, safe to start, and exercises retrieval, provenance, abstention, and permissions. Running it locally also has a real benefit: private files never leave the machine. See [ADR 0011](../adr/0011-file-agent-reference-use-case.md).

Two corpora: public documents (this repository's docs and the PostgreSQL manual) for committed evaluation sets, and the owner's personal folders for private evaluation that is never committed.

## Goals

1. A custom, provider-independent agent loop with an explicit run state machine.
2. Models as configuration: Ollama by default, hosted providers as optional adapters, chosen per profile.
3. One tool registry, policy check, and dispatcher for native and MCP tools.
4. Deny-by-default file access through explicitly approved folders.
5. Identity on every run from day one; local multi-user accounts soon after the API.
6. Versioned evaluation sets with citation and abstention metrics, run in CI.
7. Tracing, structured logs, and per-run cost and latency accounting.
8. Portable, container-based deployment that runs on the laptop or any Linux host.
9. A separate execution broker and sandbox before any code execution.
10. A company-style workflow: branches, pull requests, CI, and review.

## Non-goals

- Hosted multi-tenant SaaS.
- A microservice per module.
- Custom inference engines or model training.
- Building our own database, broker, workflow engine, container runtime, or telemetry protocol.
- Redis, Kafka, Kubernetes, vector or graph databases without a measured need.
- Model output authorising its own actions.
- Treating containers alone as safe for arbitrary code.

## Owner-approved direction

| Area | Direction | Status |
|---|---|---|
| Purpose | Practise production-grade AI engineering | Accepted |
| Use case | File agent, read-only first ([ADR 0011](../adr/0011-file-agent-reference-use-case.md)) | Accepted |
| Deployment | Self-hosted, portable, cloud-ready shape ([ADR 0012](../adr/0012-portable-deployment.md)) | Accepted |
| Models | Ollama default; hosted API optional, with a hard spend limit | Accepted |
| Users | Identity on every run now; local accounts in milestone 3 | Accepted |
| File access | Allowlist; sensitive paths always blocked | Accepted |
| Interface | CLI, then API; web UI after multi-user | Accepted |
| Runtime language | Python | Accepted |
| Database | PostgreSQL 18 ([ADR 0019](../adr/0019-search-architecture.md)) | Accepted |
| Workflow | Branches, PRs, CI; assistant writes, owner reviews and merges ([ADR 0013](../adr/0013-pull-request-workflow.md)) | Accepted |
| Licence | Apache-2.0 | Accepted |

## Definition of success: milestone 1

One narrow path, end to end, measured:

- a question is asked from a CLI;
- it runs through the real runtime: run state machine, model adapter, tool registry, policy check;
- a read-only search tool scoped to one approved folder finds the relevant passages;
- the answer cites file and section, or says the documents don't support an answer;
- an evaluation set of about 160 cases in eight categories (drafted by the assistant, verified by the owner) reports answer accuracy, citation correctness, abstention, and clarification behaviour ([ADR 0017](../adr/0017-eval-first.md#amendment-2026-11-27));
- the same set is run on a local model and a hosted model, with cost and latency for each;
- all of it is deterministic-testable with fake adapters.

Later milestones are in the [roadmap](roadmap.md).

## Quality attributes

| Attribute | How it is verified |
|---|---|
| Correctness | State-machine invariants, schema rejection, tool-call handling tests |
| Answer quality | Accuracy, citation correctness, abstention on versioned eval sets |
| Security | Path-scope tests, injection tests, permission tests, sandbox negative tests |
| Observability | A run can be reconstructed from its records and trace |
| Cost and latency | Tokens, spend, and time per run, against stated budgets |
| Reliability | Retry, idempotency, cancellation, and recovery tests |
| Portability | The stack starts from a clean Linux host with only configuration changes |

Numeric targets are set after the first measured baseline, in `docs/SERVICE_OBJECTIVES.md`, written at the end of M1.7.

## Constraints

- Development hardware is a laptop with a 6 GB GPU ([environment baseline](../research/2026-11-25-environment-baseline.md)). Local models are small; hosted models fill the quality gap where allowed.
- Hosted API use is paid separately from any Claude chat subscription, through a prepaid Console balance with a hard limit.
- The repository is public. Personal files, personal evaluation cases, secrets, and model weights never enter it.
