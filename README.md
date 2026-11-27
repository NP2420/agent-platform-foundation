# Agent Platform

A self-hosted agent platform, built from first principles to practise production-grade AI engineering: evaluated, secure, observable, and budgeted. The reference use case is an agent that works with files. It starts read-only, answering questions with cited sources, and gains write and code-execution abilities one security gate at a time.

Models are configuration (Ollama by default, hosted APIs optional), model output never authorises anything, and every run carries a user identity. The stack is Python, PostgreSQL, and OpenTelemetry, packaged to run on a laptop or any Linux host.

## Status

Status is kept in one place: the [roadmap status table](docs/project/roadmap.md#status).

## Documentation

Start at the [docs index](docs/README.md). It gives a reading order and a one-line summary of every document.

## Development

Requires [uv](https://docs.astral.sh/uv/) 0.13.x. Work in a clone on the WSL Linux filesystem, not `/mnt/c` ([why](docs/research/2026-11-25-environment-baseline.md)).

```bash
uv sync
uv run pytest
```

The full local checks, branch and commit rules, and what never gets committed are in [CONTRIBUTING.md](CONTRIBUTING.md). AI assistants follow [AGENTS.md](AGENTS.md). Report vulnerabilities as described in [SECURITY.md](SECURITY.md).

## Licence

[Apache-2.0](LICENSE).
