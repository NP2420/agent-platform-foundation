# ADR 0006: In-Process Orchestrator Before Temporal

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

The project first needs to understand the agent loop, plan validation, dependencies, concurrency, failures, and state transitions. A durable workflow engine adds recovery and long-running execution, but also infrastructure and deterministic-workflow constraints.

## Decision

Build a modest in-process scheduler with explicit orchestration contracts. Keep use cases independent of the scheduler implementation. Evaluate Temporal once concrete needs appear for durable timers, long-running approvals, worker distribution, or replay.

## Consequences

- In-process execution does not survive a crash. Don't claim durability before it is implemented and tested.
- Persist intent and outcome, and design for idempotency, from the start.
- If Temporal arrives, workflow code must be deterministic, with side effects in activities. Activities retry, so external writes still need idempotency.

## Revisit when

Workflow duration, recovery, signalling, or worker topology outgrows what the in-process design can reliably support.
