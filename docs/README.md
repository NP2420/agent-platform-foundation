# Documentation

Start here. Read the first three in order; the rest when the phase you're working on needs them.

1. [Charter](project/charter.md): why the project exists, its scope, and what success looks like.
2. [Architecture](design/architecture.md): components, trust boundaries, and how a run flows.
3. [Roadmap](project/roadmap.md): current status, then each milestone's phases and exit gates.

## Folders

| Folder | Holds | Read it for |
| --- | --- | --- |
| [`project/`](project/charter.md) | Charter and roadmap | What we're building and when |
| [`design/`](design/architecture.md) | Specs | How the system works, or will work |
| [`adr/`](adr/README.md) | Architecture decision records | What was decided, and why |
| [`research/`](research/research-log.md) | Benchmarks, audits, comparisons, the research log | The evidence behind decisions |
| [`learning/`](learning/README.md) | Learning path and phase notes | What to read, and what was learned |

## Specs

| Spec | Covers |
| --- | --- |
| [Architecture](design/architecture.md) | Components, trust boundaries, dependency rules, source layout, deployment |
| [Runtime](design/runtime.md) | Run lifecycle, agent loop, clarification, retries, budgets, cancellation, orchestration |
| [Models](design/models.md) | Profiles, model registry and licences, tool-call methods, routing, providers |
| [Tools](design/tools.md) | Tool contract, risk tiers, invocation lifecycle, MCP requirements, policy |
| [Security](design/security.md) | Threats, file access, policy, prompt injection, identity, sandboxing |
| [Data model](design/data-model.md) | Entities, run events, idempotency, artifacts, retention |
| [Observability](design/observability.md) | Logs, traces, metrics, audit chain, retention |
| [API](design/api.md) | Endpoints, the event envelope, SSE delivery, idempotency, versioning |
| [Evaluation](design/evaluation.md) | Test layers, eval cases, metrics, grading, regression gates |
| [Tech stack](design/tech-stack.md) | Every technology choice, its alternatives, and when to revisit it |

## Research

| Note | Covers |
| --- | --- |
| [Research log](research/research-log.md) | Dated findings, each linked to its note or ADR |
| [Environment baseline](research/2026-11-25-environment-baseline.md) | The development host, WSL, Docker, and GPU, as measured |
| [Ollama model benchmarks](research/2026-11-25-ollama-model-benchmarks.md) | First screen of local models: tool calls, context, speed |
| [Decision audit](research/2026-11-27-decision-audit.md) | Every decision so far checked against production practice |
| [PostgreSQL 18 vs 19](research/postgres-18-vs-19.md) | Why 18, and when to revisit 19 |
| [Sandbox options](research/local-sandbox-options.md) | Candidate sandboxes for code execution (decided in M5.1) |
| [Enterprise gap](research/enterprise-gap.md) | What a company deployment would add (milestone 7) |

## Conventions

**One home per fact.** Status lives in the roadmap's status table. Decisions and their reasons live in ADRs; specs describe the design and link to the ADRs rather than restating them. Repository rules live in [CONTRIBUTING.md](../CONTRIBUTING.md).

**Specs are designs until built.** A spec describes the intended system. A part of it is current only once its milestone ships; each spec's Status line says what is accepted and what is still open.

**Decision status labels**, used in ADRs and specs:

| Label | Meaning |
| --- | --- |
| Accepted | Confirmed by the owner. Implementation details may still be open. |
| Proposed | Recommended, not yet confirmed or proven. |
| Open | Needs research, an experiment, or a decision. |
| Deferred | Postponed until a stated trigger. |
| Superseded | Replaced by a later decision; kept for history. |

A proposal doesn't become accepted by being written down. Only the owner changes a status.

**Dated facts.** Version-sensitive facts (releases, SDK behaviour, model capabilities) carry the date they were checked. Recheck them when implementing, and record changes in the research log.

**Names and layout** follow [ADR 0023](adr/0023-docs-layout-and-link-checks.md): lower-case kebab-case, with dated notes starting with the date. Links are checked on every PR.
