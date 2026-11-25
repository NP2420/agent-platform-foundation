# System Overview

## 1. System context

The platform accepts requests from clients, executes runs using one or more model invocations, and mediates access to tools and local capabilities. It stores application state and execution history, publishes events, and provides enough evidence to inspect, test, and evaluate behavior.

The first deliverable is a local API/SDK-backed modular application. The design should permit a later CLI, web run inspector, IDE client, or automation client without moving orchestration or authorization into those interfaces.

## 2. Actors and external systems

| Actor/system | Role | Trust posture |
|---|---|---|
| API/SDK client | Creates runs, reads state, streams events, submits approvals/cancellation | Authenticated client; request content is untrusted input |
| Agent runtime | Constructs context, invokes models, interprets results | Trusted application code; model output is untrusted |
| Model server | Generates text, structured output, and candidate tool calls | Untrusted decision source; never an authorization authority |
| Native tool | Application function exposed through the registry | Trusted only to its declared capability; implementation still requires review |
| MCP server | External tool/resource/prompt provider | Separate trust domain; outputs and metadata are untrusted |
| Execution worker | Runs potentially powerful actions in a restricted environment | Separate security boundary; least privilege |
| PostgreSQL | Stores platform application state and records | Trusted persistence boundary; access-controlled |
| Ollama | Initial local inference server | Local service; network exposure must be constrained |
| Future Temporal service | Durable workflow coordination, if adopted | Infrastructure dependency; not part of initial minimum stack |

## 3. Main use cases

1. **Single-agent interaction:** client submits a task; runtime invokes a model; model returns a final answer.
2. **Tool-assisted task:** model requests a tool; runtime validates and authorizes it; dispatcher executes it; result is returned to the model.
3. **Multi-step workflow:** agent proposes multiple tasks; scheduler validates dependencies and limits; ready work executes; results feed subsequent steps.
4. **Approval-gated action:** a policy requires human authorization; the run pauses; client submits approval/denial; the run resumes or terminates.
5. **Long-running task:** execution remains observable and cancellable; durable workflow support may be added after need is demonstrated.
6. **Local execution:** tool broker runs filesystem, shell, browser, or code operations within an explicitly selected isolation profile.
7. **Evaluation:** a test harness runs deterministic fixtures or model-backed cases and records outcomes, metrics, and artifacts.

## 4. Logical system boundary

Inside the platform: run management, agent loop, context assembly, model abstraction, orchestration, tool registry/dispatcher, policy checks, application persistence, API/event protocol, evaluation, and telemetry instrumentation.

Outside the platform: model inference process (initially Ollama), MCP servers, external websites/APIs, host OS/container runtime, and future workflow infrastructure. These are integrated through explicit adapters and should not be trusted implicitly.

## 5. Quality attributes and provisional measures

| Attribute | What to measure or verify | Target status |
|---|---|---|
| Correctness | State-machine invariants, schema rejection, tool selection and result handling | Define testable invariants in Phase 0/1 |
| Reliability | Recovery tests, retry behavior, idempotency tests, cancellation latency | Numeric SLO open |
| Security | Threat-model coverage, privilege boundaries, sandbox escape assumptions, audit completeness | Threat model before powerful tools |
| Performance | End-to-end latency, model latency, queue wait, tool latency, CPU/RAM/VRAM | Benchmark local workload first |
| Scalability | Maximum concurrent runs and tool invocations without starvation/resource exhaustion | Workload target open |
| Operability | Reconstruct a run from persisted records and traces; backup/restore exercise | Required before release |
| Cost | Hardware utilization and optional remote API spend | Local-first; numeric budget open |
| Maintainability | Typed interfaces, migration discipline, ADRs, test coverage of critical paths | Quality gates defined per phase |

Do not assign arbitrary numeric targets before measuring the actual hardware, model, and expected workload. The first benchmark establishes a baseline; later targets should be justified by usage requirements.

## 6. Assumptions requiring confirmation during Phase 0

- Host OS and kernel version; whether Linux, Windows/WSL2, and/or macOS are involved.
- Whether the runtime is single-user indefinitely or should support multiple local users/tenants later.
- Expected concurrent runs, average and maximum run duration, and acceptable queueing.
- Whether runs must work offline or may use network APIs.
- Whether browser automation uses a clean isolated browser profile or an existing user session (the default should be isolated; user-profile reuse is not assumed).
- Workspace/artifact retention and cleanup rules.
- Backup and restore expectations for run history and local artifacts.
- Whether external network egress is denied by default for code/shell tools.
- Whether the platform will ever expose an API beyond localhost.
- Hardware budget for primary and fast local model profiles.

## 7. Design principle

Prefer the smallest architecture that satisfies the documented workload and threat model. Keep module boundaries explicit. Split deployable services only when a requirement such as isolation, scaling, independent availability, or operational ownership justifies the extra distributed-systems complexity.
