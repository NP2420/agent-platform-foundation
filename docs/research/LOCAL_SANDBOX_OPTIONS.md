# Research Note: Local Execution Isolation Options

**Decision:** Open. No arbitrary shell/code execution should be enabled until the host and threat model are known and the selected configuration passes negative tests.

## 1. Problem

The platform eventually needs filesystem, shell, browser, and arbitrary-code capabilities. These are significantly more powerful than ordinary API tools. Model instructions and tool inputs are untrusted, so executing them inside the API process or with the user's ambient privileges is unacceptable for a restricted/production mode.

The design needs a separate execution broker and worker boundary. The broker validates a structured operation, selects a workspace and security profile, and launches the worker. It should not simply pass raw model text to an unrestricted shell.

## 2. Candidate mechanisms

| Mechanism | What it contributes | Limits/considerations |
|---|---|---|
| Linux namespaces | Isolate process, mount, PID, IPC, user, and network views | Configuration complexity; host kernel; not a complete security model alone |
| seccomp | Restrict system calls available to a process | Requires careful profiles; does not isolate filesystem/network by itself |
| AppArmor/SELinux | Mandatory access-control policy for process resources | Host policy/configuration and operational expertise required |
| Landlock | Unprivileged filesystem (and supported network) access restriction | Kernel/version support and ABI feature checks; complementary layer |
| Rootless OCI containers | Run container engine/workloads without a root daemon | Reduces some privilege risk; container configuration and kernel boundary still matter |
| gVisor | User-space application kernel that mediates system calls | Compatibility/performance overhead; host/platform requirements |
| Firecracker microVM | Lightweight VM boundary using KVM virtualization | Linux/KVM and operational complexity; resource overhead and image lifecycle |
| Platform-native VM/sandbox | Host-appropriate isolation on Windows/macOS | Need a separate platform-specific design and tested guarantees |

Primary references:
- Linux Landlock: https://www.kernel.org/doc/html/latest/userspace-api/landlock.html
- Docker rootless: https://docs.docker.com/engine/security/rootless/
- gVisor: https://gvisor.dev/docs/
- Firecracker: https://firecracker-microvm.github.io/ and https://github.com/firecracker-microvm/firecracker

These mechanisms are not mutually exclusive. A hardened worker may combine namespaces, seccomp, MAC, Landlock, cgroups/resource controls, and a container/VM boundary.

## 3. Design requirements for the broker

- Separate process and identity from API/runtime.
- Explicit workspace root and artifact import/export paths.
- No ambient home-directory, SSH-agent, Docker socket, cloud credentials, or browser profile mounts.
- Non-root worker identity.
- Restricted filesystem by default; read/write grants are explicit.
- Network egress denied by default for arbitrary code; permit only scoped destinations where a task requires it.
- CPU, memory, process/PID, file size, wall-time, output size, and disk quotas.
- Per-invocation correlation and audit records.
- Cleanup on success, failure, cancellation, and worker crash.
- Safe path normalization and symlink/archive traversal defenses.
- Structured operation API; do not treat a model-provided command string as trusted policy.
- Explicit behavior for ambiguous side effects and timeout.

## 4. Host discovery gate

Before implementation, record locally:

- OS edition/distribution and version;
- kernel version and active virtualization support;
- whether Docker/Podman is available and whether rootless mode works;
- Windows WSL2 configuration if applicable;
- CPU architecture, cores, RAM, GPU/VRAM;
- cgroup version and delegated resource-control availability where applicable;
- ability to create user/network/mount namespaces;
- storage/filesystem behavior and workspace location.

Do not publish sensitive machine identifiers in the repository.

## 5. Required negative tests

A sandbox is not accepted merely because a process launches. Test attempts to:

- read outside assigned workspace;
- follow symlink or archive paths outside workspace;
- inspect host process details and sensitive mounts;
- access environment variables/secrets not granted;
- reach localhost services, metadata endpoints, arbitrary internet destinations, or other LAN hosts;
- create excessive processes/threads, consume memory/CPU/disk, or run past deadline;
- write outside allowed paths;
- retain files/processes after cleanup;
- exploit cancellation/timeout races.

Tests must run on the selected host and record residual limitations. Do not use a malicious payload against a machine/user environment outside the isolated test boundary.

## 6. Decision gate

Select the least-complex mechanism that meets the documented threat model. For untrusted arbitrary code, consider stronger isolation such as gVisor or a VM boundary if container/kernel sharing is outside acceptable risk. If current host OS cannot support the intended threat model, constrain the feature or run the execution worker on a separate host; do not quietly weaken the security claim.
