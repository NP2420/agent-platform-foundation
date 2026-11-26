# ADR 0009: Local-First and Self-Hosted

- **Status:** Accepted
- **Date:** 2026-11-25

## Context

The project prioritises learning and near-zero running cost, and runs on the owner's existing laptop.

## Decision

Local inference through Ollama. The database and optional infrastructure are self-hosted. External model APIs are optional. Use Docker Compose profiles and run only the services the current phase needs.

## Consequences

- Model choice is bounded by local RAM and VRAM (6 GB on the current GPU).
- Local services bind to loopback by default.
- Model weights and database volumes stay out of Git.
- Any cloud provider needs explicit configuration and a data policy.
- The stack's resource overhead gets measured; the full future infrastructure never needs to run at once.

## Revisit when

A workload needs remote inference, a dedicated inference host, or services beyond this machine.
