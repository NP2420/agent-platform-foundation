# ADR 0003: Python for the Agent Runtime

- **Status:** Accepted; interpreter version open
- **Date:** 2026-11-25

## Context

The runtime needs model integrations, structured validation, evaluation tooling, async I/O, and fast iteration. Python's ecosystem covers all of these.

## Decision

The first runtime, orchestrator, and API are written in Python as a modular monolith with domain, application, and infrastructure layers. Python 3.14.x is the starting interpreter candidate; 3.15.x gets tested before the version is pinned.

## Consequences

- The provider, MCP, and database dependencies must all support the chosen minor version.
- `uv` manages the environment, and `uv.lock` is committed.
- Pydantic is used at boundaries; domain contracts stay free of FastAPI, SQLAlchemy, and provider SDKs.
- TypeScript, Go, and Rust remain available for justified adjacent components (ADR 0002).

## Revisit when

A concrete performance, deployment, ecosystem, or security requirement shows another language is materially better for a subsystem.
