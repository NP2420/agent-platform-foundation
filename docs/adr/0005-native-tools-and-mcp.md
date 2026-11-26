# ADR 0005: One Tool Contract for Native and MCP Tools

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

The platform needs both direct in-process tools and standardised external ones. MCP provides interoperability, but it shouldn't dictate internal orchestration or authorisation.

## Decision

Native Python tools and MCP-backed tools share one registry, dispatcher, and policy contract. The official MCP SDKs act as adapters. Schemas, permissions, risk, side effects, timeouts, retries, and idempotency are part of trusted local registration.

## Consequences

- MCP is not the authorisation engine, scheduler, database, or sandbox.
- MCP server metadata and output are untrusted.
- Every invocation is validated and authorised locally before dispatch.
- SDK and protocol versions are pinned and contract-tested.

## Revisit when

A tool category needs a different protocol or execution backend. Even then, the common policy and audit envelope stays.
