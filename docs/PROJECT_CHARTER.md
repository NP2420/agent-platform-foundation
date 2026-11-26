# Project Charter

## Purpose

Build a reusable, self-hosted, general-purpose agent platform: a controlled runtime where models reason, request tools, run bounded workflows, delegate work, and produce outcomes that can be inspected afterwards.

It is equally a learning project in production software, AI engineering, distributed systems, reliability, and security. The aim is not to clone a commercial product or pile up abstractions. It is a system whose design, tests, security boundaries, and trade-offs hold up to serious review for a clearly stated scope.

## Goals

1. A custom, provider-independent agent loop.
2. A common contract for model calls and model profiles.
3. Local inference through Ollama.
4. Tiered model profiles (primary, fast, summarizer, specialist, evaluator) without needing several models in the first slice.
5. One tool registry and dispatcher for native and MCP tools, behind one policy check.
6. A small in-process orchestrator: sequential and parallel execution, dependencies, bounded resources, explicit failure handling.
7. Runs, messages, steps, and audit events persisted in PostgreSQL.
8. A versioned API and event stream first; human interfaces later.
9. A separate execution broker and sandbox before any powerful filesystem, shell, browser, or code tool.
10. Deterministic tests, agent evaluations, observability, and operational docs developed alongside the runtime.
11. Temporal evaluated only when long-running, recoverable workflows need it.
12. Low running cost: the existing machine and open-source infrastructure.
13. Learn each concept through primary sources, experiments, and small, reviewable changes.

## Non-goals for the first release

- Hosted multi-tenant SaaS.
- A full web dashboard, IDE extension, or polished terminal UI.
- A microservice per module.
- A custom inference engine or model training.
- Building our own database, message broker, workflow engine, container runtime, or telemetry protocol.
- Redis, Kafka, Kubernetes, a vector database, or a graph database without a demonstrated need.
- Multi-agent behaviour as a prerequisite for usefulness.
- Model output authorising its own actions.
- Treating containers alone as safe for arbitrary code.

## Owner-approved direction

| Area | Direction | Status |
|---|---|---|
| Product | General-purpose agent platform | Accepted |
| Deployment | Local, self-hosted, minimal running cost | Accepted |
| Interface | API and SDK first | Accepted |
| Runtime language | Python | Accepted |
| Other languages | TypeScript for Node-native and client work; Go/Rust when justified | Accepted |
| Inference | Ollama first | Accepted |
| Models | Tiered profiles; one model may back all of them initially | Accepted |
| Tools | Native and MCP | Accepted |
| Orchestration | Custom in-process engine first | Accepted |
| Durable workflows | Evaluate Temporal later | Accepted |
| Database | PostgreSQL | Accepted; major version open |
| Execution | Full capabilities long-term, behind a security boundary | Accepted; sandbox open |

## Use cases

1. **Single answer.** A client submits a task; the model answers.
2. **Tool-assisted task.** The model requests a tool; the runtime validates and authorises it; the dispatcher runs it; the model continues with the result.
3. **Multi-step workflow.** The agent proposes several tasks; the orchestrator validates dependencies and limits and runs ready work.
4. **Approval-gated action.** Policy requires a human decision; the run pauses until approval or denial.
5. **Long-running task.** Stays observable and cancellable; durable execution only once there is a need.
6. **Local execution.** Filesystem, shell, browser, or code operations through the broker under a chosen isolation profile.
7. **Evaluation.** A harness runs fixed or model-backed cases and records outcomes and metrics.

No primary use case is chosen yet. The owner is prioritising breadth of learning and will pick a focus later. Until then, evaluation cases cover general tool-use behaviour rather than one domain.

## Quality attributes

| Attribute | How it is verified |
|---|---|
| Correctness | State-machine invariants, schema rejection, tool-call handling tests |
| Reliability | Retry, idempotency, cancellation, and recovery tests |
| Security | Threat-model coverage, privilege boundaries, sandbox negative tests, audit completeness |
| Performance | Model, tool, and end-to-end latency; queue wait; CPU, RAM, and VRAM |
| Operability | A run can be reconstructed from stored records; backup and restore have been exercised |
| Cost | Hardware use; any remote API spend |
| Maintainability | Typed interfaces, migrations, ADRs, tests on critical paths |

There are no numeric targets yet. They get set after measuring real hardware and workload, not before.

## Definition of success

The first milestone is one end-to-end path in which:

- a run is created through the API;
- a model receives a bounded context and requests a registered tool;
- the request is validated and authorised outside the model;
- the tool runs through the dispatcher and returns a structured result;
- the model continues or finishes;
- the run and its events are persisted;
- the whole path is testable deterministically, and failures, limits, and cancellation behave as documented.

Powerful execution, delegation, and durable workflows each need their own security and reliability gates before anyone calls them production-ready.

## Constraints

- Development runs on the owner's laptop. See [the environment baseline](research/ENVIRONMENT_BASELINE_2026-11-25.md).
- Local inference is the baseline. Remote providers are optional adapters and never required.
- Single user for now. Multi-user or tenant isolation is out of scope until there is a real need.
- "Production-grade" always means for a stated threat model, workload, and deployment. It is never a blanket claim.

## Open assumptions

- Expected concurrent runs and run durations.
- Offline operation versus network-dependent tools.
- Browser automation: isolated profile (the default) versus a real user session.
- Retention and cleanup of workspaces, artifacts, and run history.
- Default network egress for code and shell tools (the expected answer is deny).
- Whether the API is ever exposed beyond localhost.
