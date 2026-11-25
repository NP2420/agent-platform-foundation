# ADR 0006: Build an In-Process Orchestrator Before Considering Temporal

- **Status:** Accepted direction
- **Date:** 2026-11-25

## Context

The project is educational and must first understand the agent loop, plan validation, dependencies, concurrency, failures, and state transitions. A durable workflow engine can add recovery and long-running execution but introduces operational infrastructure and deterministic-workflow constraints.

## Decision

Build a modest in-process scheduler and explicit orchestration contracts first. Keep application use cases independent of the scheduler implementation. Evaluate Temporal after concrete requirements emerge for durable timers, long-running approvals, worker distribution, and recovery/replay.

## Consequences

- Initial in-process execution does not automatically survive process crashes; do not claim durable recovery before implementing and testing it.
- Persist intent/outcome and design idempotency from the beginning where useful.
- If Temporal is introduced, workflow code must be deterministic and side effects belong in activities.
- Activities may retry; external writes still need idempotency/reconciliation.

## Revisit when

Required workflow duration, recovery, signaling, or worker topology exceeds what a modest in-process design can reliably support.
