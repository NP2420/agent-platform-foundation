# ADR 0016: Pydantic for Domain Types

- **Status:** Accepted
- **Date:** 2026-11-26

## Context

M1.2 defines the core types: runs, steps, messages, tool calls, model results, events. The architecture said the domain imports no frameworks. The owner's goal is learning production AI engineering; dependencies are acceptable, and building something by hand is worthwhile only where it teaches something.

## Options considered

1. **Frozen dataclasses in the domain, Pydantic at the edges.** No dependency in the core, but hand-written validation, hand-written JSON conversion, and mapping code wherever objects cross the API or the database.
2. **Pydantic everywhere.** Validation, JSON, and JSON Schema built in; one shape from the API to storage.
3. **attrs.** Declarative validation, but a dependency without Pydantic's schema and JSON support, and less common in AI codebases.

## Decision

Pydantic v2 for domain types, configured strictly:

- `strict=True`: no silent type coercion (`"5"` stays an error).
- `extra="forbid"`: unknown fields are rejected.
- `frozen=True`: immutable; a state transition returns a new object.
- `pydantic>=2,<3`.

API request and response models stay separate from domain models wherever their shapes differ, so transport concerns don't leak into the domain.

## Why

- Pydantic is already in the dependency tree: the Anthropic SDK, the MCP SDK, and FastAPI all require it, so a dependency-free core would not remove it.
- The platform is schema-heavy: tool definitions are JSON Schema; tool calls, structured outputs, events, and API bodies are JSON in both directions.
- Validation runs whenever an object is built, including when it's rebuilt from storage or events.
- It is the standard in AI Python codebases, so the skill transfers.
- The learning in M1.2 is the state machine, which is the same with any of the three; hand-written validators would add boilerplate, not understanding.

## Consequences

- The architecture's dependency rule changes: the domain may import the standard library and Pydantic only.
- A Pydantic major-version upgrade would touch the domain. The version pin and strict tests contain that risk.

## Revisit when

A component needs zero dependencies, or profiling shows model construction on a hot path.
