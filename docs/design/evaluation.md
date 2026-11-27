# Testing and Evaluation

**Status:** Accepted ([ADR 0017](../adr/0017-eval-first.md), amended 2026-11-27). The harness and first cases are built in M1.3.

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

Cases are versioned and reviewed by the owner. The case schema and the confidence-interval method are designed in M1.3.

Model screening cases are listed in [models.md](models.md#evaluation-plan).

Cases and results are versioned files under `evals/`, not database tables.

### Public and private sets

- **Public** sets use public documents (public-domain US Army equipment manuals and the PostgreSQL 18 and 19 manuals) and are committed.
- **Private** sets use the owner's personal folders and live in `evals/private/`, which git ignores. Reports from private sets may be summarised in docs as aggregate numbers only, never with questions, answers, or file names.

### Splits and size

Methodology and reasons are in [ADR 0017](../adr/0017-eval-first.md).

- **Dev:** used freely while building and tuning prompts.
- **Held-out test:** run only at milestone reviews and for model or prompt decisions.
- **Regression:** every fixed bug becomes a permanent case.

About 20 test cases per category, about 160 in total, starting from about 10. Every reported rate carries a Wilson 95% confidence interval and its sample size ([ADR 0017 amendment](../adr/0017-eval-first.md#amendment-2026-11-27)).

### File-agent cases

Each milestone 1 case names the question, the expected answer facts, the source passages that support them, and its category. Eight categories in three families:

- **Answer correctly.** *single-source*: a fact stated in one passage. *synthesis*: needs two or more passages combined. *version-sensitive*: the answer differs between document versions (PostgreSQL 18 vs 19, or two revisions of a manual), and the question names the version.
- **Know its limits.** *unanswerable*: in the corpus's domain, but the corpus doesn't say, so the agent must say so. *false premise*: the question assumes something false. *out of scope*: outside the corpus's domain altogether.
- **Robustness.** *underspecified*: needs a clarifying question, or an answer with stated assumptions. *injected content*: a document contains instructions aimed at the model.

Most questions are phrased as a service technician would ask them; synthesis and version-sensitive cases lean toward an engineer's. The categories are revised after an error-analysis pass on the M1.7 baseline.

Across types, some cases hinge on exact identifiers (part numbers, model numbers, error codes), because embedding models can lose case and punctuation.

## Metrics

Report per category, with intervals, and for the whole set. Per-category numbers are directional; only whole-set paired comparisons gate anything.

- task success;
- answer accuracy against the expected facts;
- citation correctness: cited passages exist and actually support the claim;
- abstention: says "not supported" on no-answer cases, and doesn't on answerable ones;
- retrieval recall: whether the supporting passage was among those retrieved (separates search failures from reasoning failures);
- retrieval quality per arm, measured without generation in M1.6: recall@k, MRR, and latency per query, plus index size, build time, VRAM for embedding and reranker models, and hosted cost for contextual retrieval ([ADR 0019](../adr/0019-search-architecture.md));
- clarification: unnecessary-clarification rate outside `underspecified` (target near zero), and resolution rate on `underspecified`;
- tool selection precision and recall (a diagnostic: a different valid path never fails a case);
- argument validity and semantic correctness;
- policy compliance and unauthorised attempts (any violation fails the case, whatever the answer);
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

For milestone 1: code checks score citations (exist, and were retrieved), abstention, and retrieval recall. An LLM judge scores answer correctness against the expected facts with a written rubric, as pass or fail per dimension. Its scores count only after calibration against the owner's labels, reported as true-positive and true-negative rates with every run. Model, prompt, and decoding are pinned; unparseable verdicts are judge errors. The owner re-labels a blind sample a week later, and that self-consistency is reported too. The hosted judge follows the hosted-data rules: never `restricted` content, `internal` only where the folder's policy allows.

### Tooling

Our own harness, with cases as versioned JSONL. A time-boxed study in M1.3 ports about five cases to [Inspect AI](https://inspect.aisi.org.uk/) and [promptfoo](https://www.promptfoo.dev/) and compares them in a learning note.

## Regressions

Prompts, model profiles, tool schemas, the scheduler, and context construction can all change agent quality. Keep a fast smoke suite and a larger manual or scheduled suite. Set thresholds after the first measured baseline, not before. From M2.3 the CI gate compares each change with the baseline on the whole public set, paired case by case (exact McNemar test). On about 160 cases it reliably detects a change of about 10 points, not 5. Critical safety regressions block a release whatever the aggregate score.

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
