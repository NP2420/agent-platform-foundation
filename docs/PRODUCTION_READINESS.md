# Production Readiness and Release Review

A “production-grade” claim must always identify the supported deployment, threat model, workload, operational owner, and known exclusions. Passing this checklist for a local developer deployment does not imply the platform is ready for an internet-facing multi-tenant service.

## 1. Requirements and scope

- [ ] Intended users, use cases, workload, supported OS/hardware, and deployment topology are documented.
- [ ] Trust boundaries and threat model have been reviewed.
- [ ] Numeric SLOs, availability expectations, concurrency, retention, and resource budgets are defined for the target deployment.
- [ ] Unsupported configurations and residual risks are explicit.

## 2. Correctness

- [ ] Domain contracts and state transitions have unit/property tests.
- [ ] Public API/event schemas are versioned and contract-tested.
- [ ] Invalid plans, cycles, unknown tools, and invalid arguments fail closed.
- [ ] Database constraints and transactions protect invariants.
- [ ] Concurrency tests cover races in run creation, approvals, cancellation, and invocation claims.

## 3. Reliability and recovery

- [ ] Every retry policy is bounded and tied to error class/operation semantics.
- [ ] Side-effecting tools have idempotency/reconciliation behavior or an explicit unknown-outcome policy.
- [ ] Cancellation and timeout semantics are documented and tested.
- [ ] Restart/failure-injection tests cover run and tool execution boundaries.
- [ ] Database backup and restore have been exercised.
- [ ] Migrations and rollback/forward-recovery procedures are documented.
- [ ] Resource exhaustion cannot create uncontrolled tasks/processes or unbounded queues.

## 4. Security

- [ ] Model output is never treated as authorization.
- [ ] Least-privilege tool scopes and deny-by-default policy are active.
- [ ] Approval binds to specific action, target, arguments, identity, and expiry.
- [ ] Sensitive data is redacted from prompts/logs/traces where appropriate.
- [ ] Local services are not unintentionally exposed to the network.
- [ ] Powerful code/shell/filesystem execution uses the reviewed broker and sandbox backend.
- [ ] Sandbox negative tests demonstrate restricted filesystem/network/process/resource access.
- [ ] Dependency and MCP server trust/supply-chain controls are documented.
- [ ] Secret handling and credential rotation/revocation are documented.

## 5. Model and agent quality

- [ ] Model/profile selection is recorded and reproducible.
- [ ] Evaluation suite covers representative task categories and adversarial cases.
- [ ] Tool selection/argument correctness and task success are measured separately.
- [ ] Automated judges are calibrated; security tests do not rely solely on LLM judging.
- [ ] Regression thresholds are justified by measured baseline and intended use.
- [ ] Model fallback does not violate local-data/remote-provider policy.

## 6. Observability and operations

- [ ] A run can be reconstructed from persisted application records.
- [ ] Logs, traces, and metrics have correlation IDs and bounded cardinality.
- [ ] Sensitive telemetry capture is disabled/redacted by default.
- [ ] Operator knows how to inspect failures, recover service, and handle stuck runs.
- [ ] Resource use, disk growth, model storage, and artifact retention are monitored.
- [ ] Health/readiness semantics are defined.

## 7. Performance and cost

- [ ] Representative local workload has been benchmarked.
- [ ] p50/p95 latency, throughput, peak memory/VRAM, queue wait, and resource limits are recorded.
- [ ] Backpressure and saturation behavior are tested.
- [ ] Optional services can be disabled when not needed.
- [ ] Remote provider spend (if enabled) has explicit budgets/limits.

## 8. Release decision

Record:

- build/version and source revision;
- supported deployment configuration;
- test/evaluation evidence and date;
- unresolved defects and residual risks;
- migration/backup/restore result;
- security review result;
- rollback/recovery approach;
- explicit go/no-go owner decision.

A failed high-severity security or data-integrity control must not be offset by a high average agent-evaluation score.
