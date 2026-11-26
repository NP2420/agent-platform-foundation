# ADR 0008: Separate Execution Broker for Powerful Capabilities

- **Status:** Accepted; sandbox backend open (decided in Phase 16)
- **Date:** 2026-11-25

## Context

Long-term scope includes local files, shell, browser, and arbitrary code. Model output, web content, documents, and tool results are all untrusted. Running these operations in the API or runtime process with the user's ambient privileges is an unacceptable boundary.

## Decision

Introduce a separate execution broker and isolated workers before enabling any powerful capability. The runtime sends structured, policy-approved requests. Workers get an explicit identity, workspace, filesystem and network grants, resource quotas, a timeout, and an audit trail. Model-generated code never runs in the control-plane process.

## Consequences

- The sandbox choice depends on the host and the threat model.
- A plain Docker container proves nothing about isolation.
- Execution features stay disabled until negative tests pass.
- A worker might be written in Go or Rust if needed, but the language itself provides no isolation.

## Revisit when

Research selects a concrete backend, or the supported execution scope changes.
