# ADR 0009: Local-First, Self-Hosted Development Baseline

- **Status:** Agreed
- **Date:** 2026-11-25

## Context

The project prioritizes learning and low/no recurring costs and will initially run on the owner's existing machine.

## Decision

Use local inference through Ollama as the baseline; self-host the database and optional infrastructure; make external provider APIs optional. Use Docker Compose profiles where practical and start only the services needed for the current development phase.

## Consequences

- Model/hardware selection is constrained by actual local RAM/VRAM and performance.
- Local services should bind to loopback/private interfaces by default.
- Model weights and database volumes are not committed to Git.
- Optional cloud providers require explicit configuration/data policy.
- Resource overhead of the stack must be measured; the entire future infrastructure need not run simultaneously.

## Revisit when

A concrete workload requires remote inference, a dedicated inference host, or a self-hosted service beyond the local machine.
