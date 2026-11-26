# Evaluation and Testing Specification

## 1. Purpose

The platform has two different correctness problems:

1. Conventional software correctness: state transitions, schemas, transactions, concurrency, authorization, error handling, and APIs.
2. Probabilistic agent quality: whether a model selects appropriate tools, supplies correct arguments, follows constraints, and completes tasks.

These require related but distinct test strategies. A high task score does not compensate for a security flaw or a broken state invariant.

## 2. Test layers

| Layer | Scope | External dependencies |
|---|---|---|
| Unit | Domain, state machine, schemas, policy, graph validator, budget accounting | None; use fakes |
| Property/state | State invariants, graph properties, serialization, randomized failure sequences | Usually none |
| Contract | Model adapters, native tools, MCP adapter, API/event schemas | Fake servers or provider fixtures |
| Integration | Runtime + database + Ollama + selected MCP test server | Local services |
| Failure injection | Timeouts, worker crash, DB interruption, duplicate delivery, uncertain side effect | Controlled test environment |
| Security | Prompt injection, permission bypass, sandbox escape attempts, data leakage | Dedicated isolated environment |
| Agent evaluation | Task completion, tool choice/arguments, output criteria, policy adherence | Real or recorded model responses |
| Performance/load | Throughput, latency, resource use, queueing, concurrency | Representative local stack |

## 3. Deterministic test harness

Core runtime tests must run with fake model and fake tool adapters. Fakes should allow scripted responses and errors. A test should be able to reproduce the same sequence of model responses, tool results, clocks, IDs, and failures. Use deterministic seeds where randomness is relevant.

Avoid brittle tests that assert an LLM's exact prose when semantic criteria are intended. For deterministic software paths, assert exact state/events/output contracts.

## 4. Versioned evaluation cases

A case should record:

- stable ID and version;
- task prompt/input and relevant fixture data;
- expected capabilities/allowed tools;
- expected constraints and prohibited actions;
- success criteria and grading method;
- difficulty/tags and known limitations;
- model, model digest/version, prompt/agent version, tool registry version, and runtime version used for results.

Evaluation dataset changes should be reviewed and versioned. Keep training/prompt-development examples distinct from hidden regression cases where practical to reduce overfitting.

## 5. Metrics

Measure per-task category, not only one overall number:

- task success/criteria satisfaction;
- correct tool selection and tool-call precision/recall where labeled;
- argument validity and semantic correctness;
- policy compliance and unauthorized-action attempts;
- hallucinated tool/result claims;
- final answer factuality/faithfulness for tasks with references;
- recovery success after transient failures;
- p50/p95 latency and time-to-first-token;
- model/tool invocations per task;
- token/resource usage (mark provider estimates/unknowns);
- peak RAM/VRAM and throughput under concurrency;
- run completion, failure, cancellation, and timeout rates.

Report sample size, confidence/uncertainty, and failure examples. Do not compare models using dissimilar prompts, hardware, quantization, or evaluation sets without noting the differences.

## 6. Grading

Use deterministic exact/schema checks when possible, reference-based graders where reliable, and rubric/LLM judges only when justified. Calibrate automated judges against a human-reviewed sample; track disagreements and judge drift. Never use an LLM judge as the sole evidence for security-critical behavior.

## 7. Regression policy

A change to prompts, model profile, tool schema, scheduler, or context construction can alter agent quality. Maintain a small fast smoke evaluation and a larger scheduled/manual suite. Define regression thresholds after the first measured baseline; avoid arbitrary pass percentages before data exists. Critical safety regressions should block release regardless of aggregate task score.

## 8. Failure-injection scenarios

- model timeout, server restart, malformed response, unsupported tool-call format;
- MCP disconnect, invalid schema, duplicate tool response, oversized output;
- database disconnect before/after side effect intent/outcome persistence;
- worker crash during tool execution;
- duplicate run creation, retry, approval, or cancellation command;
- resource budget exhaustion and concurrency saturation;
- approval argument mutation and expiry;
- cancellation during model request and during side-effecting tool execution;
- model/tool output carrying prompt injection or secret-like content.

## 9. Release gate

A release must have reproducible test/evaluation results for the supported environment, known limitations, resolved critical security failures, and explicit review of any quality regression. See `PRODUCTION_READINESS.md`.
