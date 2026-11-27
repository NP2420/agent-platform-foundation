# ADR 0014: Python 3.15 and the Toolchain

- **Status:** Accepted; the type-checker choice is superseded by [ADR 0015](0015-pyright.md)
- **Date:** 2026-11-26

## Context

[ADR 0003](0003-python-agent-runtime.md) left the interpreter version open: pick the newest version that the full dependency set supports. M1.1 needs the version, the environment manager, and one lint, format, type, and test setup that CI enforces.

## Evidence

On 2026-11-26, both CPython 3.14.10 and 3.15.2 installed every planned dependency from prebuilt wheels, with source builds disabled: pydantic, httpx, anthropic, pypdf, pytest, anyio, ruff, mypy, pyright, fastapi, uvicorn, sqlalchemy, alembic, psycopg (binary), asyncpg, opentelemetry-sdk, and mcp. Later candidates temporalio and pgvector also had 3.15 wheels. Ruff 0.17.6 and mypy 2.4.1 both accept 3.15 as a target.

## Decision

- **Python 3.15** (`requires-python = ">=3.15,<3.16"`, `.python-version` = `3.15`).
- **uv** for environments and locking; `uv.lock` is committed, and CI installs with `uv sync --locked`. Required uv: `>=0.13.8,<0.14`.
- **Ruff** for formatting and linting, including bugbear, pyupgrade, and bandit security rules.
- **mypy in strict mode** as the one authoritative type checker. Pyright was the alternative; it was rejected because its PyPI package downloads a Node runtime on first use, an extra moving part in CI.
- **pytest** with strict markers and config, and importlib import mode.
- **GitHub Actions** run format, lint, types, and tests on every PR and on `master`. Actions are pinned to commit SHAs, with the tag in a comment.

## Consequences

- If a future dependency lacks 3.15 wheels, the fallback is 3.14, recorded in a superseding ADR.
- Bumping uv, Ruff, mypy, or an action is a deliberate PR, not drift.
- The CI job name, `lint, types, tests`, becomes a required status check on `master`.

## Revisit when

Python 3.16 ships and the dependency set supports it, or a required library drops 3.15.
