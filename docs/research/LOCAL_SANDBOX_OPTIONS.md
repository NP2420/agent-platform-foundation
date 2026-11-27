# Research Note: Execution Sandbox Options

**Decision:** Open; decided in M5.1. No shell or code execution until then.

## Problem

Filesystem, shell, browser, and code tools are far more powerful than ordinary API tools, and their inputs come from an untrusted model. They need a separate broker that validates structured requests and launches restricted workers, never raw model text piped into a shell.

## Mechanisms

| Mechanism | Provides | Limits |
|---|---|---|
| Linux namespaces | Isolated views of processes, mounts, PIDs, IPC, users, network | Complex to configure; not a full security model alone |
| seccomp | Syscall filtering | Profiles take care; doesn't isolate files or network |
| AppArmor / SELinux | Mandatory access control | Host policy and expertise required |
| Landlock | Unprivileged filesystem (and some network) restriction | Depends on kernel ABI; a complementary layer |
| Rootless OCI containers | Containers without a root daemon | Still shares the kernel; configuration matters |
| gVisor | User-space kernel intercepting syscalls | Compatibility and performance overhead |
| Firecracker microVM | VM boundary via KVM | Needs KVM; image lifecycle; overhead |
| Platform-native VM | Host-appropriate isolation on Windows or macOS | A separate design per platform |

These layers combine. A hardened worker might use namespaces, seccomp, Landlock, and cgroups inside a container or VM.

On this host, WSL2 has user namespaces and cgroup v2. `/dev/kvm` exists but the user can't access it yet ([environment baseline](ENVIRONMENT_BASELINE_2026-11-25.md)).

## Broker requirements

- A separate process and non-root identity from the runtime.
- An explicit workspace root and import/export paths.
- No home directory, SSH agent, Docker socket, cloud credentials, or browser profile mounted.
- Filesystem restricted by default, with explicit grants.
- No network egress by default; scoped destinations only when a task needs them.
- Quotas on CPU, memory, PIDs, file size, wall time, output, and disk.
- Per-invocation audit records.
- Cleanup on success, failure, cancellation, and crash.
- Defences against path normalisation, symlink, and archive traversal attacks.
- Defined behaviour for timeouts and ambiguous side effects.

## Negative tests (all must be blocked)

- Reading outside the workspace, directly or through symlinks and archives.
- Inspecting host processes or sensitive mounts.
- Reading environment variables or secrets that weren't granted.
- Reaching localhost services, metadata endpoints, the internet, or LAN hosts.
- Fork bombs and memory, CPU, or disk exhaustion; running past the deadline.
- Writing outside allowed paths.
- Leaving files or processes behind after cleanup.
- Racing cancellation or timeout.

Run these on the selected host and record what is still exposed. Never test malicious payloads outside the isolated boundary.

## Decision rule

Pick the least complex mechanism that meets the threat model. For genuinely untrusted code, a shared kernel may be unacceptable; consider gVisor or a VM. If this host can't support the required model, narrow the feature or run workers on another machine, and don't weaken the security claim.

## References

[Landlock](https://www.kernel.org/doc/html/latest/userspace-api/landlock.html) · [Docker rootless](https://docs.docker.com/engine/security/rootless/) · [gVisor](https://gvisor.dev/docs/) · [Firecracker](https://firecracker-microvm.github.io/)
