# Project Status — Phase 0

**Updated:** 2026-11-25  
**Document set:** 0.2.0

## Current position

We are still in Phase 0: architecture and environment discovery. No application runtime code has been started. The purpose of this phase is to validate the development environment, research unresolved infrastructure choices, and make the architecture consistent with measured constraints before building.

## Completed observations

- Primary development environment: Windows 11 Home + Ubuntu 26.04.1 under WSL2.
- Hardware: Intel Core i7-13700H, 15.68 GiB physical RAM, NVIDIA RTX 4050 Laptop GPU with 6,141 MiB reported VRAM.
- Docker Desktop WSL integration works from Ubuntu; Docker Engine is 29.9.3 and reports cgroup v2.
- WSL mirrored networking allows Ubuntu to reach Windows-hosted Ollama at `127.0.0.1:11434`.
- Ollama 0.40.18 remains bound to loopback on Windows.
- Actual configured Ollama model directory measured at 27.05 GB; C: had 70.27 GiB free during inspection.
- Qwen3 4B and Nemotron 3 Nano 4B both ran fully on GPU at 4K context in the recorded tests.
- Both models passed one simple tool-call selection/argument smoke test.

## Decisions currently accepted for initial development

- Ubuntu/WSL2 is the primary development environment.
- Docker Desktop's WSL integration is the container engine path; no separate Docker daemon is required inside Ubuntu.
- Windows-hosted Ollama is the initial inference service, reached using mirrored-network localhost.
- Keep Ollama bound to loopback; do not expose the unauthenticated API on all interfaces.
- The model endpoint is configuration, not a hard-coded platform assumption.

## Still open

- Final model/profile assignments and practical context length.
- Multi-step tool-use quality, multi-tool calling, abstention, malformed calls, and recovery.
- Python project minor version and dependency set.
- PostgreSQL 18 vs 19 and database driver.
- Sandbox backend and threat model, including KVM feasibility.
- Whether inference should move to Linux/containers for another deployment target.

## Immediate next work

Continue the model behavior evaluation with:

1. Tool selection with distractors and varied wording.
2. Missing-information behavior (ask instead of inventing arguments).
3. No-tool behavior.
4. Two independent calls in one response.
5. Complete mock-tool round trip: assistant tool-call message → tool result message → assistant final response.
6. Tool error and untrusted tool-result cases.

These are evaluation experiments only. The models' proposed tools are not executed; authorization and execution remain future runtime responsibilities.

## Related records

- `research/ENVIRONMENT_BASELINE_2026-11-25.md`
- `research/LOCAL_MODEL_BASELINE.md`
- `research/OLLAMA_MODEL_BENCHMARKS_2026-11-25.md`
- `RESEARCH_LOG.md`
- `DEVELOPMENT_ROADMAP.md`
- `adr/0010-windows-hosted-ollama-initial-deployment.md`
