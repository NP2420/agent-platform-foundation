# ADR 0008: Separate Execution Broker for Powerful Local Capabilities

- **Status:** Accepted architectural requirement; sandbox backend open
- **Date:** 2026-11-25

## Context

The long-term platform scope includes local files, shell commands, browser access, and arbitrary code. Model output, web content, retrieved documents, and tool results are untrusted. Executing these operations in the API/runtime process with ambient user privileges creates an unacceptable privilege boundary.

## Decision

Introduce a separate execution broker and worker isolation boundary before enabling powerful local execution. The API/runtime sends structured, policy-approved operation requests. Workers use an explicit identity, workspace, filesystem/network grants, resource quotas, timeout, and audit trail. Do not execute model-generated code directly inside the control-plane process.

## Consequences

- Host OS, kernel, and threat model must be discovered before selecting a sandbox.
- Docker containers alone are not a sufficient security proof.
- Local execution features remain disabled until negative tests pass.
- Go/Rust may be used for a worker only if a concrete requirement warrants it; language choice does not itself create isolation.

## Revisit when

Threat model/host research selects a concrete backend or the supported execution scope is narrowed/expanded.
