# ADR 0005: Unified Internal Tool Contract for Native Tools and MCP

- **Status:** Accepted direction
- **Date:** 2026-11-25

## Context

The platform needs direct local application tools and standardized external tools. MCP provides interoperability but should not define all internal orchestration behavior.

## Decision

Use one internal registry/dispatcher/policy contract for native Python tools and MCP-backed tools. Use official MCP SDKs as adapters. Tool schemas, permissions, risk, side effects, timeout, retry, and idempotency metadata are part of trusted tool registration/configuration.

## Consequences

- MCP is not the authorization engine, scheduler, database, or sandbox.
- MCP server metadata/tool output is untrusted.
- Every invocation is validated and authorized locally before dispatch.
- SDK/protocol versions must be pinned and contract-tested.

## Revisit when

A tool category requires a different protocol or isolated execution backend, while preserving the common policy/audit envelope.
