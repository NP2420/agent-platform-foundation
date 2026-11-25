# Observability Specification

## 1. Objectives

An operator/developer should be able to answer:

- What happened during a run, in what order, and which component performed each step?
- Which model/provider/version and prompt/agent version were used?
- Which tools were proposed, authorized, denied, executed, and with what outcome?
- Where did time, tokens, and local resources go?
- Why did a run fail, pause, or exhaust a budget?
- Can the issue be reproduced safely without exposing private data?

## 2. Three distinct data products

### Application event history

Durable run facts/state transitions in PostgreSQL. Used for run inspection, audit, recovery semantics, and event replay to clients. It is not a replacement for distributed tracing.

### Traces

OpenTelemetry spans represent causal operations such as API request, run, model call, tool dispatch, policy check, database operation, and execution-worker call. Use W3C trace context/correlation as supported by instrumentation. Keep high-cardinality/sensitive fields out of metric labels.

### Logs and metrics

Structured logs capture diagnostic events with run/step/correlation IDs. Metrics aggregate latency, counts, errors, queue depth, concurrency, resource use, budget exhaustion, and model/tool outcomes.

## 3. Initial spans

Proposed hierarchy:

```text
api.request
└── agent.run
    ├── context.build
    ├── model.generate
    ├── policy.evaluate
    ├── orchestration.plan_validate
    ├── tool.execute
    │   ├── tool.schema_validate
    │   ├── tool.authorize
    │   └── tool.backend_call
    ├── approval.wait
    └── run.persist
```

Span names and attributes should be mapped to current OpenTelemetry conventions where stable. GenAI semantic conventions evolve; pin the convention version/attributes adopted and avoid depending on experimental fields without a local compatibility layer.

## 4. Metrics

Candidate metrics:

- `agent_runs_started_total`, `agent_runs_completed_total`, `agent_runs_failed_total`, `agent_runs_cancelled_total`;
- run duration and queue wait histograms;
- model request count/error/latency and reported token usage;
- tool invocation count/error/latency by safe tool class (not arbitrary tool input);
- in-flight runs and tool calls;
- approval wait duration and pending approvals;
- budget exhaustion counts;
- worker CPU/memory/PID and sandbox resource usage when available;
- event stream reconnect/lag metrics.

Metric labels must be bounded; do not label metrics with run IDs, prompts, file paths, arbitrary tool names from untrusted sources, or user identifiers.

## 5. Sensitive data and redaction

Default to recording metadata/digests rather than raw prompts, complete tool arguments/results, file contents, environment variables, authorization headers, cookies, or secrets. When payload capture is explicitly enabled for debugging, apply access controls, encryption, retention limits, and redaction. Never emit credentials into telemetry.

A trace is not automatically safe because it is local. Local observability endpoints and dashboards also require access control if the host is shared or network-exposed.

## 6. Initial local stack

Start with application structured logs and OpenTelemetry SDK instrumentation. A local Collector and Grafana/Tempo/Prometheus stack can be an optional profile once traces/metrics are useful. Avoid making the full telemetry stack a prerequisite for unit tests or basic local runtime development.

Collector documentation: https://opentelemetry.io/docs/collector/.

## 7. Diagnostics and correlation

Every API request, run, step, tool invocation, and approval should have stable identifiers and a documented relationship. Carry trace context across MCP/worker boundaries when supported, but do not trust external trace baggage for authorization. The run event store remains authoritative for application execution facts.
