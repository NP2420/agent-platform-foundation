# ADR 0004: Provider-Neutral Model Gateway with Ollama First

- **Status:** Accepted direction
- **Date:** 2026-11-25

## Context

The system is local/self-hosted and seeks to minimize recurring cost. It should not become coupled to Ollama or one model, while supporting logical model profiles for different tasks.

## Decision

Define internal model request/response contracts and provider adapters. Implement Ollama first, plus a fake adapter for deterministic tests. Support logical profiles such as primary, fast, summarizer, specialist, and evaluator. Initially, one model may back multiple profiles. The runtime/router chooses invocations; model output cannot spawn work or change policy by itself.

## Consequences

- Capability differences across model/provider/runtime combinations must be represented and tested.
- Do not promise parity for tools, structured output, vision, streaming, or parallel calls.
- Routing is initially explicit/configurable; automated selection follows benchmark evidence.
- Remote fallback must be explicitly permitted by data policy.

## Revisit when

Model count/provider complexity justifies a gateway such as LiteLLM, or evaluation shows another serving runtime better fits the hardware/workload.
