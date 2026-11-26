# Development Environment Baseline

**Observed:** 2026-11-25. Rerun the checks and update this file if the host changes.

## Topology

```text
Windows 11 host
├── Ollama 0.40.18  (127.0.0.1:11434, RTX 4050 Laptop GPU 6,141 MiB)
└── WSL2 VM
    └── Ubuntu 26.04.1 LTS
        ├── Python 3.14.4 (system)
        ├── Docker CLI → Docker Desktop engine
        └── project runtime (future)
```

## Hardware and host

| Item | Value |
|---|---|
| OS | Windows 11 Home, 10.0.26300 |
| CPU | Intel Core i7-13700H, 14 cores / 20 threads |
| RAM | 15.68 GiB |
| dGPU | NVIDIA RTX 4050 Laptop, 6,141 MiB, 45 W limit |
| iGPU | Intel Iris Xe |
| NVIDIA driver | Windows 32.0.16.1074; WSL `nvidia-smi` 610.74 (KMD) / 610.53 |
| C: drive | 928.33 GiB total, 70.27 GiB free |

This laptop can't keep several models and the full infrastructure stack resident at once. Measure memory use before adding services.

## WSL

| Item | Value |
|---|---|
| Distro | Ubuntu 26.04.1 LTS (`resolute`), WSL 3.0.5.0 |
| Kernel | 6.18.58.1-microsoft-standard-WSL2, x86_64 |
| CPUs / RAM / swap | 20 / 7.6 GiB / 2 GiB |
| Init, cgroups | systemd, cgroup v2 |
| User namespaces | `unshare --user --map-root-user true` works |
| `/dev/dxg` | Present |
| `/dev/kvm` | Present, owned by `root:kvm`; user not in the `kvm` group |
| Shell `Seccomp` / `NoNewPrivs` | 0 / 0 (this shell only; says nothing about containers) |

Don't change KVM group membership until a KVM-based sandbox is actually chosen (Phase 10).

`.wslconfig` (added for Ollama access; there was none before):

```ini
[wsl2]
networkingMode=mirrored
```

The WSL ext4 root reports about 1 TB of capacity. That is a virtual disk size, not free space on C:.

Docker recommends keeping repositories on the WSL ext4 filesystem rather than `/mnt/c` for performance. The current working copy is on the Windows side, so decide in Phase 1 whether to move it.

## Docker

| Item | Value |
|---|---|
| Docker Desktop | 4.100.1 (247138), WSL2 backend |
| Engine / containerd / Compose | 29.9.3 / v2.4.2 / v5.7.1 |
| Engine platform, cgroup | linux/amd64, v2 |
| WSL integration | Enabled for `Ubuntu-26.04`; verified with `docker version` |

Enabling the integration took: Settings → Resources → WSL Integration, then `wsl --shutdown`. Don't enable the unauthenticated `tcp://localhost:2375` socket.

## Tools in WSL

| Tool | State |
|---|---|
| `python3` | 3.14.4, no pip module |
| `uv` | Not installed |
| `node` | Not installed |
| `npm` | Resolves to the Windows install under `/mnt/c`. Fix before any Node work: install a Linux Node and don't drive a Linux tree with Windows npm. |
| `go`, `rustc` | Not installed |
| `git`, `docker` | Present |

Project dependencies never go into the system Python; use `uv`.

## Ollama

| Item | Value |
|---|---|
| Version | 0.40.18 on Windows |
| Listener | `127.0.0.1:11434` |
| From WSL, NAT mode | Failed (both localhost and the host IP) |
| From WSL, mirrored mode | Works at `127.0.0.1:11434` |
| `OLLAMA_MODELS` | `C:\Users\<user>\OLLAMA`, 27.05 GB |

An earlier measurement of 3.11 GB was taken from the default `.ollama\models` path, which is not the active directory. Ignore it.

Models already installed before screening: `qwen3:14b` (9.3 GB), `qwen2.5-coder:7b` (4.7 GB), `nomic-embed-text` (274 MB), `llama3.1:8b`, `qwen3:8b`, `llama3.2:1b` (1.3 GB), `gemma3` (3.3 GB). Added for screening: `qwen3:4b-q4_K_M`, `nemotron-3-nano:4b`.

## References

[WSL networking](https://learn.microsoft.com/en-us/windows/wsl/networking) · [WSL configuration](https://learn.microsoft.com/en-us/windows/wsl/wsl-config) · [Docker WSL best practices](https://docs.docker.com/desktop/features/wsl/best-practices/) · [Docker WSL integration](https://docs.docker.com/desktop/features/wsl/) · [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md)
