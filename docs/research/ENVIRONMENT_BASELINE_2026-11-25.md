# Local Development Environment Baseline

**Observed:** 2026-11-25 (America/Indiana/Indianapolis)  
**Purpose:** record the actual development host used for Phase 0. This is a developer-environment observation, not a production deployment specification.

## 1. Executive summary

The primary environment is Windows 11 Home with Ubuntu 26.04.1 LTS under WSL2. Docker Desktop's WSL integration is enabled and verified. Ollama runs natively on Windows and is reachable from Ubuntu over `127.0.0.1` after enabling WSL mirrored networking.

**Current topology:**

```text
Windows 11 host
├── Ollama 0.40.18
│   ├── HTTP API: 127.0.0.1:11434
│   └── NVIDIA GeForce RTX 4050 Laptop GPU (6,141 MiB)
│
└── WSL2 VM
    └── Ubuntu 26.04.1 LTS
        ├── Python 3.14.4 (system interpreter)
        ├── Docker CLI → Docker Desktop Linux engine
        └── Future agent runtime / project repository
```

## 2. Hardware and host

| Item | Observed value |
|---|---|
| Host OS | Windows 11 Home, version `10.0.26300`, build `26300` |
| CPU | 13th Gen Intel Core i7-13700H |
| Physical CPU topology | 14 cores / 20 logical processors |
| Physical RAM | 15.68 GiB (approximately 16 GB installed) |
| Discrete GPU | NVIDIA GeForce RTX 4050 Laptop GPU |
| Dedicated GPU memory reported by `nvidia-smi` | 6,141 MiB |
| Integrated GPU | Intel Iris Xe |
| Windows NVIDIA driver reported by WMI | `32.0.16.1074` |
| WSL NVIDIA driver reported by `nvidia-smi` | `610.74` KMD; `610.53` utility version in captured output |

The laptop is resource-constrained for running several model servers and infrastructure components simultaneously. Model concurrency, context allocation, and Docker memory usage must be measured rather than assumed.

## 3. WSL distribution and kernel

| Item | Observed value |
|---|---|
| Distribution | `Ubuntu-26.04` |
| OS release | Ubuntu `26.04.1 LTS`, codename `resolute` |
| WSL version | `3.0.5.0` |
| Kernel | `6.18.58.1-microsoft-standard-WSL2` |
| Architecture | `x86_64` |
| CPUs visible inside WSL | 20 logical CPUs |
| RAM visible inside WSL at inspection | 7.6 GiB total; 6.8 GiB available |
| Swap visible inside WSL | 2.0 GiB |
| Init | `systemd` |
| Cgroups | cgroup v2 (`cgroup2fs`) |
| User namespaces | `unshare --user --map-root-user true` succeeded |
| `/dev/dxg` | Present |
| `/dev/kvm` | Present, but current user cannot read or write it |
| Current shell `Seccomp` | `0` |
| Current shell `NoNewPrivs` | `0` |

The seccomp and `NoNewPrivs` values above describe the inspected shell process only. They do **not** establish which restrictions Docker or a future execution sandbox will apply. Likewise, the presence of `/dev/kvm` does not prove that a KVM-based microVM runtime can operate for this user.

The KVM device is owned by `root:kvm`, while the inspected user is not a member of the `kvm` group. Do not change group membership or device permissions until a specific KVM-based design is selected and its security implications are understood.

## 4. WSL memory and filesystem observations

At the time of inspection, WSL reported approximately 7.6 GiB total memory and 2 GiB swap. No custom `.wslconfig` was present during the initial inventory. Mirrored networking was subsequently added to `%USERPROFILE%\.wslconfig`:

```ini
[wsl2]
networkingMode=mirrored
```

After `wsl --shutdown` and restarting Ubuntu, a request from WSL to `http://127.0.0.1:11434/api/version` successfully reached the Windows Ollama service.

Filesystem observations:

- WSL root filesystem: ext4 on `/dev/sdd`, approximately 1,007 GiB virtual filesystem capacity at inspection.
- Windows C: mounted at `/mnt/c` as `9p`.
- Windows C: volume: 928.33 GiB total; 70.27 GiB free in the later storage measurement.
- The WSL ext4 capacity is the virtual filesystem capacity; it must not be interpreted as physical free capacity on the Windows disk.

**Repository placement recommendation:** keep the repository in the Ubuntu ext4 filesystem (for example, `~/src/agent-platform`) rather than `/mnt/c`, unless a Windows-native tool requires a Windows-side working copy. This follows Docker's WSL filesystem performance guidance.

## 5. Docker environment

Docker Desktop is installed on Windows and uses the WSL2 backend.

| Item | Observed value |
|---|---|
| Docker Desktop | `4.100.1` (`247138`) |
| Docker Engine | `29.9.3` |
| containerd | `v2.4.2` |
| Docker Compose CLI plugin | `v5.7.1` |
| Engine OS/architecture | `linux/amd64` |
| Cgroup version reported by engine | `2` |
| WSL integration | Enabled and verified for `Ubuntu-26.04` |
| Docker executable in WSL | `/usr/bin/docker` (also `/bin/docker`) |

Verification succeeded from Ubuntu after enabling the distribution under Docker Desktop **Settings → Resources → WSL Integration**, applying the change, running `wsl --shutdown`, and reopening Ubuntu. `docker version` returned both client and server information.

Do not enable the unauthenticated Docker TCP listener (`tcp://localhost:2375`) for this project. It is not required for the WSL integration and would expand the control surface.

## 6. Development tools observed in WSL

| Tool | Observed state |
|---|---|
| `python3` | `/usr/bin/python3`, version `3.14.4` |
| `pip` for system Python | Not installed (`No module named pip`) |
| `uv` | Not installed |
| `node` | Not installed inside Ubuntu |
| `npm` | Resolves to Windows installation under `/mnt/c/Program Files/nodejs/npm` |
| `go` | Not installed |
| `rustc` | Not installed |
| `git` | `/usr/bin/git` |
| `docker` | Linux CLI available and connected to Docker Desktop |

The Windows `npm` path leaking into Ubuntu is an environment hygiene issue to address before Node-native development. Install a Linux-native Node toolchain if/when a TypeScript component is introduced; do not use the Windows `npm` executable to manage a Linux project tree.

Python `3.14.4` is the observed system interpreter, not yet the selected project interpreter. The project must use `uv` and a repository-local environment after the dependency compatibility review. Do not install application dependencies into Ubuntu's system Python.

## 7. Ollama host and network integration

| Item | Observed value |
|---|---|
| Host OS | Windows |
| Ollama version | `0.40.18` |
| API listener | `127.0.0.1:11434` |
| API health check on Windows | Successful |
| API health check from WSL NAT mode | Failed against both WSL localhost and host IP |
| API health check from WSL mirrored mode | Successful using `127.0.0.1:11434` |
| `OLLAMA_MODELS` | `C:\Users\<user>\OLLAMA` (Windows path; username intentionally omitted) |
| Actual model-directory size measured | 27.05 GB |

The measured directory was the configured `OLLAMA_MODELS` path. An earlier measurement of `%USERPROFILE%\.ollama\models` returned 3.11 GB but was not the active model directory and must not be used as the installed-model storage figure.

Ollama remains bound to loopback. Do not change it to `0.0.0.0` or add firewall exceptions as a shortcut. The mirrored-network localhost path has already been demonstrated to work.

### Models listed before the new benchmark candidates were added

The Windows `ollama list` output included:

- `qwen3:14b` — 9.3 GB
- `qwen2.5-coder:7b` — 4.7 GB
- `nomic-embed-text:latest` — 274 MB
- `llama3.1:8b` / `llama3.1:latest` — same reported model ID
- `qwen3:8b` / `qwen3:latest` — same reported model ID
- `llama3.2:1b` — 1.3 GB
- `gemma3:latest` — 3.3 GB

The user subsequently downloaded `qwen3:4b-q4_K_M` and `nemotron-3-nano:4b`; their measured metadata and benchmark results are recorded in `OLLAMA_MODEL_BENCHMARKS_2026-11-25.md`.

## 8. Decisions and open constraints

### Accepted initial environment choices

- Use Windows-hosted Ollama initially.
- Keep Ollama bound to Windows loopback and access it from Ubuntu through WSL mirrored networking.
- Use Ubuntu/WSL as the primary development environment.
- Use Docker Desktop's WSL integration rather than installing a second independent Docker daemon inside Ubuntu.

### Still open

- Project Python minor version and exact dependency set.
- Whether the eventual sandbox can use a container-only design, gVisor, a microVM, or another backend.
- Whether KVM access is needed; no KVM access change is authorized by this baseline.
- Whether PostgreSQL 18 or 19 is selected.
- Whether Windows-hosted inference remains the best deployment once the platform is containerized or moved to a Linux server.
- Model/profile selection and practical context sizes.

## 9. Primary references

- [Microsoft: Accessing network applications with WSL](https://learn.microsoft.com/en-us/windows/wsl/networking) — mirrored networking and localhost behavior.
- [Microsoft: WSL advanced settings](https://learn.microsoft.com/en-us/windows/wsl/wsl-config) — `.wslconfig` options.
- [Docker: WSL 2 best practices](https://docs.docker.com/desktop/features/wsl/best-practices/) — filesystem placement and WSL integration.
- [Docker: WSL integration](https://docs.docker.com/desktop/features/wsl/) — enabling the integration for a distribution.
- [Ollama API](https://github.com/ollama/ollama/blob/main/docs/api.md) — API endpoint and response details.

## 10. Revisit triggers

Revisit this profile when the host OS, WSL version, GPU, RAM, disk, Docker backend, inference host, or sandbox design changes. Re-run the relevant diagnostic commands and update the observation date; do not silently carry these values forward.
