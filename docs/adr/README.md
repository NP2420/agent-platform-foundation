# Architecture Decision Records

One file per material decision. An ADR is never edited to reverse a decision: write a new one and mark the old one Superseded.

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-api-first.md) | API and SDK are the product boundary | Accepted |
| [0002](0002-polyglot-boundaries.md) | Languages chosen per subsystem, not microservices by default | Accepted |
| [0003](0003-python-agent-runtime.md) | Python for the agent runtime | Accepted; version set by 0014 |
| [0004](0004-model-provider-abstraction.md) | Provider-neutral model gateway, Ollama first | Accepted |
| [0005](0005-native-tools-and-mcp.md) | One tool contract for native and MCP tools | Accepted |
| [0006](0006-in-process-before-temporal.md) | In-process orchestrator before Temporal | Superseded by 0018 |
| [0007](0007-postgresql-system-of-record.md) | PostgreSQL as system of record | Accepted; version and driver set by 0019 |
| [0008](0008-execution-isolation-boundary.md) | Separate execution broker for powerful capabilities | Accepted; sandbox open |
| [0009](0009-local-first-self-hosted.md) | Local-first, self-hosted | Accepted |
| [0010](0010-windows-hosted-ollama-initial-deployment.md) | Windows-hosted Ollama via WSL mirrored networking | Accepted for development |
| [0011](0011-file-agent-reference-use-case.md) | File agent as the reference use case | Accepted; corpus superseded by 0020, retrieval by 0019 |
| [0012](0012-portable-deployment.md) | Portable, cloud-ready deployment shape | Accepted |
| [0013](0013-pull-request-workflow.md) | Branches, pull requests, and CI | Accepted |
| [0014](0014-python-toolchain.md) | Python 3.15, uv, Ruff, pytest, CI | Accepted; type checker superseded by 0015 |
| [0015](0015-pyright.md) | Pyright as the type checker | Accepted |
| [0016](0016-pydantic-domain-types.md) | Pydantic for domain types | Accepted |
| [0017](0017-eval-first.md) | Eval-first development and eval methodology | Accepted |
| [0018](0018-durable-execution-decided-in-m2.md) | Durable execution, decided by experiment in M2.1 | Accepted |
| [0019](0019-search-architecture.md) | Search architecture: PostgreSQL 18, staged retrieval arms | Accepted |
| [0020](0020-data-and-model-governance.md) | Data and model governance | Accepted |
| [0021](0021-supply-chain-and-releases.md) | Supply chain and releases: Dependabot, cooldown, audit, zizmor, release-please | Accepted; required checks extended by 0022 |
| [0022](0022-licences-code-scanning-coverage.md) | Dependency licences, CodeQL, and coverage | Accepted |

## Writing one

Use the existing files as the template: Status, Date, Context, Decision, Consequences, Revisit when. Before writing, state the problem and the evidence, list the alternatives, check sources and versions, and run an experiment if the answer depends on the workload. Afterwards, update any spec the decision affects.
