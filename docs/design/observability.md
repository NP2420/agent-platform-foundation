# Observability, Audit, and Retention

**Status:** Accepted 2026-11-27. Logs and traces start in M1.2, chained audit records in M1.5, the trace viewer in M2.3. Decisions come from the [decision audit](../research/2026-11-27-decision-audit.md) (A13, A14, A15).

Four separate records, each with its own job:

| Record | Answers | Authoritative? |
|---|---|---|
| Run events and step records | What did this run do, in order? | Yes, for runs ([data model](data-model.md#runs-and-events)) |
| Audit events | Who was allowed or denied what, and can we show it wasn't altered? | Yes, for security facts |
| Traces | Where did the time go, and what did each model and tool call see? | No: diagnostic, sampled later, expires |
| Logs and metrics | What is the process doing, and is it healthy? | No: diagnostic, expires |

Diagnostics can be lost without losing the truth. Nothing that a decision or an audit depends on lives only in a trace or a log.

## What is recorded

**Metadata and digests by default.** Records carry IDs, sizes, counts, timings, outcomes, model and tool names from the registry, and content digests. They never carry raw prompts, model output, tool payloads, file contents, headers, cookies, or secrets.

**Debug capture** of raw payloads is opt-in per run, available only to the owner, and expires after 7 days. It is never enabled for restricted-classification content. Turning it on or off is an audit event.

## Logs

- **structlog**, rendered as one JSON object per line to stdout. The deployment decides where stdout goes.
- **Fields on every line:** timestamp (UTC, ISO 8601), level, event name, logger, and, when present, `run_id`, `step_id`, `correlation_id`, `trace_id`, `span_id`.
- **Trace correlation:** a processor copies `trace_id` and `span_id` from the active OpenTelemetry span into each line, so a log line leads to its trace and back.
- **Redaction** runs as the last processor before rendering. It drops keys on a denylist (`authorization`, `cookie`, `password`, `token`, `api_key`, and others) and masks values that match secret patterns. A unit test feeds it known secrets and asserts that none come out.
- **Event names** are stable identifiers (`model.call.completed`), not sentences, so they can be counted and searched.
- **Levels:** `info` for lifecycle facts, `warning` for handled anomalies (a retry, a budget at 80%), `error` for failures needing attention. Nothing per-token or per-chunk is logged at `info`.

## Traces

- **OpenTelemetry SDK** from M1.2. With no exporter configured, spans go nowhere and cost almost nothing; tests never need a collector.
- **Spans**, one per causal operation: `api.request` → `agent.run` → `context.build`, `model.generate`, `policy.evaluate`, `tool.execute`, `approval.wait`, `input.wait`. New span names are added here first.
- **GenAI semantic conventions** on `model.generate`: the pinned version's attributes for operation, provider, model, token usage, and finish reason. The conventions are still in Development, and in June 2026 they moved to their own repository (`open-telemetry/semantic-conventions-genai`). So the version is pinned in code, and every attribute name lives in one module, making a rename a one-file change.
- **Export:** OTLP over HTTP/protobuf (Langfuse's endpoint doesn't accept gRPC). The app exports straight to the trace viewer; an OpenTelemetry Collector goes in between only when there are two destinations.
- **Content:** spans follow the metadata rule above. With debug capture on, prompts and outputs go on span events, not attributes, so they can be dropped separately.

## Metrics

Run counts and durations, model and tool latency and errors, in-flight work, approval and input waits, retries, and budget exhaustion. Labels stay bounded: never run IDs, prompts, paths, user IDs, or names taken from untrusted input. Metrics are exported over OTLP from M2.3; until then they can be derived from logs.

## Trace viewer (M2.3)

An LLM trace viewer is how runs get read during error analysis, so it arrives in M2, not with the enterprise work. M2.3 runs Langfuse and Phoenix, each as an optional Compose profile, on the same traces, and picks one. The criteria:

- it renders our `gen_ai.*` spans and nested agent steps without custom code;
- a 30-step run is readable: inputs, outputs (with debug capture), timings, and token counts per step;
- it links eval results to the traces behind them;
- its resource cost on this laptop is acceptable, measured. Langfuse's self-hosted stack runs several services; Phoenix can run as one container.

The choice and its measurements go in an ADR. Until M2.3, traces can be printed with the console exporter.

## Audit trail

**Audited actions:** policy decisions (allow and deny), approvals requested and decided, tool invocations with side effects, reads of `restricted` files, content sent to a hosted model (by classification and size), debug capture changes, configuration and grant changes, authentication events (from M3), retention deletions, and administrative corrections.

**Record:** sequence number, timestamp, actor (user or system component), action, target, outcome, run and step IDs where relevant, a payload digest, the previous record's hash, and this record's hash.

**Protections, in order of value** ([audit A13](../research/2026-11-27-decision-audit.md#a13-hash-chained-audit-trail--keep-rescope)):

1. **Append-only.** From M2.1, an `audit_events` table where the application's database role has `INSERT` and `SELECT` only. No code path updates or deletes a record; retention deletion runs under a separate role.
2. **Hash chain.** Each record's hash covers its canonical serialisation (sorted keys, UTF-8 bytes, fixed number and timestamp formats) plus the previous hash. A verifier recomputes the chain and reports the first break. The chain is a pure domain function, tested with Hypothesis: any modification, deletion, insertion, or reordering is detected.
3. **Anchor.** From M2.1, the head hash is written periodically to a location the database admin can't edit, such as a signed commit in a separate private repository. The mechanism is chosen in M2.1.

**Milestone 1:** records are chained and appended to a local JSONL file under the data directory; M2.1 migrates them to the table, chain intact.

**What it claims:** tamper-evident against the application and anyone without database admin rights. With the anchor, changes by an admin are detectable back to the last anchor. It is not tamper-proof, and the docs don't say it is.

## Retention

Defaults; every value is configurable.

| Data | Default | Basis |
|---|---|---|
| Audit events | At least 12 months, the latest 3 months searchable; not deletable by the application role | PCI DSS v4.0.1 10.5.1, a common baseline outside payments too |
| Run events and step records | Kept with the run; deleting a run keeps its audit facts | [Data model](data-model.md#retention) |
| Messages | 90 days | Owner decision, 2026-11-27 |
| Debug payload capture | Off; 7 days when on | Owner decision, 2026-11-27 |
| Traces | 30 days | Owner decision, 2026-11-27 |
| Application logs | 14 days | Owner decision, 2026-11-27 |
| Artifacts | Until deleted by the owner; per-user quota | Owner decision, 2026-11-27 |
| Eval results | Public set in Git indefinitely; private set in `evals/private/` until the owner deletes it | [ADR 0017](../adr/0017-eval-first.md) |

A retention job is itself audited: what it deleted, by count and time range, never by content.

## Testing

- Redaction: known secrets and sensitive keys never reach output.
- Correlation: a log line inside a span carries that span's IDs; one outside carries none.
- Audit chain: Hypothesis stateful tests for append and verify; every tamper kind detected; canonical serialisation stable across runs and platforms.
- Spans: a fake-model run produces the expected span tree with the pinned GenAI attributes.
- Retention: the job deletes only expired records of each type and audits itself.
