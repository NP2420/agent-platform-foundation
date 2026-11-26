# ADR 0002: Polyglot by Subsystem, Not by Default Microservices

- **Status:** Accepted direction
- **Date:** 2026-11-25

## Context

Different workloads benefit from different language ecosystems. Python has strong model/data/evaluation integration; TypeScript fits Node-native tools and future client surfaces; Go and Rust may fit specialized infrastructure or native execution. A single-language mandate can be unnecessarily restrictive, but unnecessary service boundaries add operational complexity.

## Decision

Use Python as the primary agent runtime/orchestration language. Use TypeScript for Node-native integrations and future client/harness surfaces. Consider Go/Rust only when a measured workload, native interface, deployment requirement, or security boundary justifies a separate component. Start as a Python modular monolith.

## Consequences

- Cross-language boundaries require explicit schemas and transport contracts.
- No language is chosen merely for prestige or presumed speed.
- Separate processes/services need a reason beyond code organization.
- MCP and HTTP/gRPC can be considered as integration boundaries where appropriate.

## Revisit when

A real subsystem has requirements that are demonstrably better met by another language or a separate deployment lifecycle.
