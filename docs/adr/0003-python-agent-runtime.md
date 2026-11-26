# ADR 0003: Python as Primary Agent Runtime

- **Status:** Accepted direction; exact interpreter version open
- **Date:** 2026-11-25

## Context

The core runtime requires model integrations, structured data validation, evaluation tooling, asynchronous I/O, and rapid experimentation. Python has a strong ecosystem for these workloads.

## Decision

Implement the first agent runtime, orchestration logic, and API in Python. Prefer a modular monolith with explicit domain/application/infrastructure boundaries. Python 3.14.x is the conservative initial interpreter candidate; test 3.15.x compatibility before pinning.

## Consequences

- Provider/MCP/DB dependencies must be checked against the selected Python minor.
- Use `uv` and commit `uv.lock` for reproducibility.
- Use Pydantic at boundaries where useful; keep domain contracts independent of FastAPI/SQLAlchemy/provider SDKs.
- TypeScript/Go/Rust remain allowed for justified adjacent components.

## Revisit when

A concrete performance, deployment, ecosystem, or security requirement demonstrates that another language is materially better for a subsystem.
