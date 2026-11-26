# ADR 0015: Pyright as the Type Checker

- **Status:** Accepted; supersedes the type-checker choice in [ADR 0014](0014-python-toolchain.md)
- **Date:** 2026-11-26

## Context

ADR 0014 chose mypy, mainly because the Pyright PyPI package downloads a Node runtime on first use. That turned out to be a weak reason: the `pyright[nodejs]` extra installs Node as an ordinary Python wheel (`nodejs-wheel-binaries`), so nothing downloads at run time. The owner reviewed the options and chose Pyright.

## Options considered

| | mypy | Pyright | ty | Pyrefly |
|---|---|---|---|---|
| Maturity | Mature, community reference | Mature; engine behind VS Code's Pylance | Beta, 0.0.x, no stable API | 1.0 (May 2026) |
| Typing-spec conformance | Lower | High | Lowest of these | High |
| Pydantic | Plugin | Via `dataclass_transform` | Built in | Built in |
| Speed | Fast (mypyc-compiled) | Slower than current mypy | Fastest | Very fast |

Sources: [pydevtools comparison](https://pydevtools.com/handbook/explanation/how-do-mypy-pyright-and-ty-compare/), [ty on PyPI](https://pypi.org/project/ty/), [Pyrefly comparison](https://pyrefly.org/en/docs/compare/).

## Decision

Pyright in strict mode, installed as `pyright[nodejs]`, checking `src` and `tests`. Chosen for stricter, specification-conformant checking, and because the same engine powers the editor (Pylance), so editor and CI agree.

## Consequences

- CI runs `uv run pyright` in place of `uv run mypy`.
- Pydantic typing relies on `dataclass_transform`, not a plugin. If that misses a case, the fix is an explicit annotation, not a second checker.
- ty is the likely future candidate once it has a stable release; revisit then.

## Revisit when

ty or Pyrefly is stable and measurably better on this codebase, or Pyright's Pydantic support causes repeated false results.
