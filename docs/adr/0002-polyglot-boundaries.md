# ADR 0002: Languages per Subsystem, Not Microservices by Default

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

Python is strongest for model, data, and evaluation work. TypeScript fits Node-native tools and client surfaces. Go or Rust may suit specialised infrastructure. A single-language rule would be needlessly restrictive, but every extra service boundary adds operational cost.

## Decision

Python is the primary language for the runtime and orchestration. TypeScript is for Node-native integrations and future clients. Go or Rust only when a measured workload, native interface, deployment need, or security boundary justifies a separate component. Start as a Python modular monolith.

## Consequences

- Cross-language boundaries need explicit schemas and transport contracts (HTTP, gRPC, or MCP).
- No language gets chosen for prestige or assumed speed.
- A separate process needs a reason beyond code organisation.

## Revisit when

A subsystem has requirements that another language or a separate deployment lifecycle demonstrably meets better.
