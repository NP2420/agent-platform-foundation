# Testing and Evaluation

The platform has two kinds of correctness:

1. **Software correctness:** state transitions, schemas, transactions, concurrency, authorisation, errors, APIs. Deterministic, so assert exact results.
2. **Agent quality:** whether the model picks the right tool, supplies correct arguments, respects constraints, and finishes the task. Probabilistic, so measure rates over versioned cases.

A high task score never compensates for a security flaw or a broken invariant.

## Test layers

| Layer | Scope | Dependencies |
|---|---|---|
| Unit | Domain, state machine, schemas, policy, plan validation, budgets | None (fakes) |
| Property | Invariants, graph properties, serialisation, random failure sequences | None |
| Contract | Model adapters, tools, MCP adapter, API and event schemas | Fake servers, fixtures |
| Integration | Runtime with PostgreSQL, Ollama, and an MCP test server | Local services |
| Failure injection | Timeouts, worker crashes, DB loss, duplicate delivery, uncertain side effects | Controlled environment |
| Security | Injection, permission bypass, sandbox escape, data leakage | Isolated environment |
| Agent evaluation | Task success, tool choice and arguments, policy adherence | Real or recorded model output |
| Performance | Latency, throughput, resource use, queueing | Representative local stack |

## Deterministic harness

Core runtime tests use scripted fake model and tool adapters. A test can replay the same sequence of model responses, tool results, clock values, IDs, and failures. Assert exact states, events, and contracts; don't assert exact model prose where semantic criteria are what matter.

## Evaluation cases

Each case records:

- an ID and version;
- the prompt and fixture data;
- the allowed tools and the expected tool behaviour;
- constraints and prohibited actions;
- success criteria and grading method;
- tags and known limitations.

Each result records the model digest, prompt or agent version, tool registry version, runtime version, and settings.

Cases are versioned and reviewed. Keep the examples used during prompt development separate from held-out regression cases.

Model screening cases are listed in [MODEL_SPEC.md](MODEL_SPEC.md#evaluation-plan).

## Metrics

Report per task category, not one overall number:

- task success;
- tool selection precision and recall;
- argument validity and semantic correctness;
- policy compliance and unauthorised attempts;
- hallucinated tool calls or results;
- final-answer faithfulness, where there is a reference;
- recovery after transient failures;
- p50 and p95 latency and time to first token;
- calls per task;
- tokens and resource use;
- completion, failure, cancellation, and timeout rates.

Always include the sample size and failure examples. Never compare models across different prompts, hardware, quantisation, or case sets without saying so.

## Grading

Prefer exact and schema checks, then reference-based graders. Use LLM judges only where they are justified, calibrate them against a human-reviewed sample, and track drift. An LLM judge is never the only evidence for security behaviour.

## Regressions

Prompts, model profiles, tool schemas, the scheduler, and context construction can all change agent quality. Keep a fast smoke suite and a larger manual or scheduled suite. Set thresholds after the first measured baseline, not before. Critical safety regressions block a release whatever the aggregate score.

## Failure-injection scenarios

- Model timeout, server restart, malformed response, unsupported tool-call format.
- MCP disconnect, invalid schema, duplicate response, oversized output.
- Database loss before or after an intent or outcome write.
- Worker crash mid-tool.
- Duplicate run creation, approval, or cancel.
- Budget exhaustion and concurrency saturation.
- Approval argument mutation and expiry.
- Cancellation during a model call and during a side-effecting tool.
- Prompt injection or secret-like content in model or tool output.
