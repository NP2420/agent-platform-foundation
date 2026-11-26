# ADR 0010: Windows-Hosted Ollama for Initial Local Inference

- **Status:** Accepted for the initial development environment; deployment remains replaceable
- **Date:** 2026-11-25

## Context

The primary development environment is Ubuntu 26.04.1 under WSL2 on a Windows 11 Home host. The host has an NVIDIA RTX 4050 Laptop GPU with 6,141 MiB reported VRAM and 15.68 GiB physical RAM. Ollama `0.40.18` is already installed on Windows, with approximately 27.05 GB of model storage under the configured `OLLAMA_MODELS` directory. WSL has a 7.6 GiB memory limit in the captured environment. A Windows-hosted inference server therefore avoids duplicating weights in the WSL virtual disk and avoids placing the inference server's process memory inside the WSL VM allocation.

Initially, Ollama listened only on Windows `127.0.0.1:11434`. WSL NAT mode could not connect through either its own localhost or the Windows host IP because the service was bound to Windows loopback. After setting `networkingMode=mirrored` under `[wsl2]` in `%USERPROFILE%\.wslconfig`, shutting WSL down, and restarting Ubuntu, `curl http://127.0.0.1:11434/api/version` succeeded from WSL.

## Decision

Use Windows-hosted Ollama as the initial local inference server. The Python runtime in Ubuntu/WSL2 will connect to `http://127.0.0.1:11434` through mirrored networking. Keep the Ollama listener on loopback; do not expose it on `0.0.0.0` or enable unauthenticated remote access as a workaround.

The endpoint must be configurable (for example, `OLLAMA_BASE_URL`) so Linux-hosted Ollama, a dedicated inference host, llama.cpp, vLLM, or another provider can be evaluated later without changing the agent-runtime contract.

## Alternatives considered

1. **Ollama inside WSL2:** cleaner Linux-local service and localhost topology, but would duplicate model storage and consume the WSL VM's memory allocation. Reconsider if Linux-native deployment or container co-location becomes more important.
2. **Windows Ollama with NAT host-IP access:** would require a Windows listener address and firewall configuration that exposes a wider interface. Rejected for the initial setup because mirrored localhost access worked without widening the listener.
3. **Containerized inference:** potentially useful for a reproducible Linux deployment, but introduces GPU passthrough, image/runtime, storage, and resource questions that are not needed for the first local baseline.

## Consequences

- WSL mirrored networking becomes part of the local development environment configuration.
- The inference service remains a Windows-hosted dependency; the agent runtime should implement health checks, connection errors, and configurable endpoint behavior.
- The project is not yet proven portable to a Linux-only deployment; that will require a separate deployment profile and test.
- Model weights remain in the Windows-configured Ollama directory and should not be copied into Git or Docker build contexts.
- This decision does not imply that Windows-hosted Ollama is the production deployment choice.

## Evidence

- WSL-to-Windows API version request succeeded at `http://127.0.0.1:11434/api/version` after mirrored networking was enabled.
- Ollama reported version `0.40.18` and a loopback listener on port `11434`.
- See `docs/research/ENVIRONMENT_BASELINE_2026-11-25.md` and `docs/research/OLLAMA_MODEL_BENCHMARKS_2026-11-25.md`.

## Revisit when

- The platform is moved to a Linux-only host or server.
- The inference service is containerized or distributed independently.
- Mirrored networking becomes unreliable or conflicts with required VPN/network policy.
- Windows memory/GPU scheduling, security posture, or operational overhead becomes a measured bottleneck.
