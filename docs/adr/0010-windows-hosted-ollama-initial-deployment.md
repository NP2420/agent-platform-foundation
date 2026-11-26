# ADR 0010: Windows-Hosted Ollama via WSL Mirrored Networking

- **Status:** Accepted for the development environment
- **Date:** 2026-11-25

## Context

Development happens in Ubuntu 26.04.1 under WSL2 on Windows 11 Home, with an RTX 4050 Laptop GPU (6,141 MiB) and 15.68 GiB RAM. Ollama 0.40.18 was already installed on Windows with about 27 GB of models. WSL is capped at 7.6 GiB of RAM, so running Ollama inside WSL would duplicate the weights and eat that allocation.

Ollama listened only on Windows `127.0.0.1:11434`. In WSL's default NAT mode, neither WSL's localhost nor the Windows host IP could reach it. After setting `networkingMode=mirrored` under `[wsl2]` in `%USERPROFILE%\.wslconfig` and restarting WSL, `curl http://127.0.0.1:11434/api/version` succeeded from Ubuntu.

## Decision

Use Windows-hosted Ollama. The Python runtime in WSL connects to `http://127.0.0.1:11434` over mirrored networking. Ollama stays bound to loopback: no `0.0.0.0`, no firewall openings.

The endpoint is configuration (`OLLAMA_BASE_URL`), so Ollama in Linux, a dedicated host, llama.cpp, vLLM, or another provider can be swapped in without changing the runtime contract.

## Alternatives

1. **Ollama inside WSL.** A cleaner Linux topology, but duplicate storage and WSL memory pressure. Reconsider for Linux-native or containerised deployment.
2. **Windows Ollama via NAT and the host IP.** Requires widening the listener and opening the firewall. Rejected because mirrored mode works without either.
3. **Containerised inference.** GPU passthrough, image, and storage questions that aren't needed yet.

## Consequences

- Mirrored networking becomes part of the documented development setup.
- The runtime needs health checks and clear connection errors, because inference is an external dependency.
- Portability to a Linux-only host is unproven and needs its own deployment profile and test.
- Model weights stay in the Windows Ollama directory, out of Git and Docker build contexts.
- This is not a production deployment decision.

## Revisit when

The platform moves to a Linux host or server; inference is containerised or moved to another machine; mirrored networking conflicts with VPN or network policy; or Windows GPU or memory scheduling becomes a measured bottleneck.
