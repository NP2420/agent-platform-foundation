# ADR 0004: Provider-Neutral Model Gateway, Ollama First

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

The system is local and low-cost, but should not be tied to Ollama or to any one model. It also needs logical roles for different kinds of work.

## Decision

Define internal model request and response contracts, with provider adapters behind them. Implement Ollama first, plus a fake adapter for deterministic tests. Support logical profiles (primary, fast, summarizer, specialist, evaluator); one model may back several at first. The runtime and router decide which model calls happen; model output cannot spawn work or change policy.

## Consequences

- Capability differences between models, providers, and runtimes are represented and tested, not hidden.
- No promise of parity for tools, structured output, vision, streaming, or parallel calls.
- Routing starts as explicit configuration; automatic selection follows benchmark evidence.
- Remote fallback requires an explicit data policy.

## Revisit when

The number of providers justifies a gateway such as LiteLLM, or evaluation shows another serving runtime fits the hardware better.
