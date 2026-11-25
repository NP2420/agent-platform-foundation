# Project Initialization — Basics

This package establishes the documentation baseline and initial repository conventions. It deliberately does **not** generate the application runtime or lock dependency versions; those are the first development tasks after the architecture review.

## 1. Put the documentation in the repository

The ZIP is arranged so its contents can be extracted into the root of an empty Git repository. It contains `README.md`, `PROJECT_INITIALIZATION.md`, `.editorconfig`, `.gitignore`, and `docs/`.

If the repository already exists, extract into its root and review any existing `README.md`, `.gitignore`, or `.editorconfig` before overwriting them. Merge intentionally; do not blindly replace existing project configuration. Suggested repository name: `agent-platform` (placeholder).

## 2. Initialize Git

From the repository root:

```bash
git init
git status
git add README.md PROJECT_INITIALIZATION.md .editorconfig .gitignore docs
git commit -m "docs: establish agent platform architecture baseline"
```

Configure `user.name` and `user.email` if required. Never commit secrets, model weights, database volumes, generated artifacts, or private data.

## 3. Proposed initial source tree

Do not create all these files immediately. This is the target shape for the first Python modular monolith; add directories as their roadmap phases begin.

```text
agent-platform/
├── README.md
├── PROJECT_INITIALIZATION.md
├── pyproject.toml              # created in Phase 1 with uv
├── uv.lock                     # generated and committed by uv
├── .python-version             # selected after compatibility check
├── .env.example                # placeholders only; no real credentials
├── .gitignore
├── .editorconfig
├── docs/
│   ├── INDEX.md
│   ├── ...
│   ├── adr/
│   └── research/
├── src/agent_platform/
│   ├── domain/
│   ├── application/
│   ├── runtime/
│   ├── orchestration/
│   ├── models/
│   ├── tools/
│   ├── security/
│   ├── persistence/
│   ├── api/
│   └── observability/
├── tests/{unit,integration,contract,evaluation,security}/
├── infra/compose/
├── scripts/
└── artifacts/                  # local runtime output; ignored by Git
```

This is a **modular monolith**, not a mandate to split each directory into a service or Python distribution. The initial API and runtime may run in one process. Worker processes and separate services are introduced only when required.

## 4. Toolchain initialization (Phase 1, after Phase 0 review)

The proposed Python environment manager is [`uv`](https://docs.astral.sh/uv/guides/projects/). Its project guide describes `pyproject.toml` as the project definition and `uv.lock` as the exact, cross-platform resolved dependency lockfile that should be committed.

After Phase 0 confirms the interpreter and dependency compatibility matrix, initialize from the repository root:

```bash
uv init --package --name agent-platform
```

Review generated `pyproject.toml`; do not accept defaults blindly. Set the selected Python constraint and package layout, then run:

```bash
uv sync
uv run python --version
```

Commit `pyproject.toml` and `uv.lock`. Do not hand-edit `uv.lock`.

The Python minor version is intentionally not frozen here. Python 3.15.2 and 3.14.10 are both listed as released on 2026-10-25, but the project should choose the newest version whose complete dependency/toolchain matrix is supported and tested. See [Python version status](https://devguide.python.org/versions/).

## 5. Local infrastructure policy

- Start with only the services needed for the current milestone.
- Use Docker Compose for reproducible supporting services where compatible with the host.
- Do not run the entire eventual stack for every unit test.
- Do not mount the user's full home directory into an agent execution container.
- Do not expose Ollama, PostgreSQL, or internal service ports publicly by default.
- Store local volumes, model weights, database data, and artifacts outside Git.
- Never put API keys or tokens in tracked files.

The final sandbox choice depends on host OS, kernel capabilities, and threat model. Docker is a development packaging tool; an ordinary container configuration must not be assumed sufficient for hostile-code isolation.

## 6. First initialization checkpoint

- [ ] Documentation committed.
- [ ] Python version selected using dependency compatibility checks.
- [ ] `uv` creates a reproducible environment and lockfile.
- [ ] Lint, type-check, and unit-test commands documented.
- [ ] No secret, model weight, database volume, or private artifact is tracked.
- [ ] Host OS, CPU, RAM, GPU/VRAM, storage, and container capabilities recorded in a local environment note (do not publish sensitive machine details).
- [ ] Initial ADRs reviewed.

Only then begin the first runtime implementation chunk.
