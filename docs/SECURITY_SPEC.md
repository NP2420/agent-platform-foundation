# Security and Execution Isolation Specification

**Status:** Security boundary is an agreed requirement. Exact host-specific sandbox implementation is open and must be researched before enabling arbitrary execution.

## 1. Security objective

Treat the model as an untrusted decision-making component that can be manipulated by user content, retrieved documents, web pages, tool outputs, MCP servers, memory, or prior conversation. The model may propose an action; only trusted application code can authorize it. Powerful actions execute outside the API/runtime privilege boundary.

A security claim must be scoped to a threat model, host OS, kernel, container/runtime configuration, attacker capability, and supported deployment mode.

## 2. Assets

- User files, source repositories, SSH keys, cloud/API credentials, browser sessions, and environment variables.
- Conversation history, memory, model prompts, private documents, and artifacts.
- Model-serving endpoints and provider credentials.
- Database records, run history, approvals, and audit events.
- Host OS, processes, network, and other local users' data.
- Tool/MCP server credentials and external resources.

## 3. Threats to model

Use OWASP Top 10 for Agentic Applications (2026) as one taxonomy, including goal hijack, tool misuse, identity/privilege abuse, supply-chain risks, unexpected code execution, memory poisoning, inter-agent communication abuse, cascading failures, false trust, and rogue agents. It supplements rather than replaces a project-specific threat model.

Concrete threats:

- Prompt injection in user input, retrieved text, websites, or tool output.
- Tool-call spoofing, schema abuse, confused deputy, or privilege escalation.
- Secret exfiltration through prompts, logs, artifacts, network access, or subprocesses.
- Malicious MCP server or compromised dependency.
- Path traversal, symlink escape, workspace escape, and unsafe archive extraction.
- Shell/code execution abuse, fork bombs, resource exhaustion, network scanning, and lateral movement.
- Cross-run or cross-user data leakage.
- Replayed/duplicate side effects after timeout/recovery.
- Model/router fallback sending private data to an unintended remote provider.
- Browser profile/session theft or actions performed with a user's ambient identity.

## 4. Trust boundaries

1. **Client → API:** authenticate requests, validate inputs, enforce size/rate quotas.
2. **Model → runtime:** model outputs are proposals, not trusted instructions or authorization.
3. **Tool/MCP → runtime:** metadata/results are untrusted; validate, bound, sanitize, and preserve provenance.
4. **Runtime → execution broker:** structured, policy-approved requests only.
5. **Broker → sandbox worker:** restricted identity and explicit filesystem/network/resource permissions.
6. **Application → database/secrets:** narrowly scoped credentials and transactional repository access.
7. **Local host → any remote provider:** explicit data classification and consent/configuration before remote transmission.

## 5. Required controls

### Identity and authorization

- Deny-by-default tool grants.
- Least-privilege capability sets at agent/run/tool level.
- Authorization performed by trusted policy code, not inferred from model output.
- Separate user identity, run identity, worker identity, and external service credentials.
- Approval is bound to exact action/arguments/target, caller, scope, and expiry.

### Execution broker

- Do not execute model-generated shell/code in the API process.
- Broker accepts a structured request, not an arbitrary free-form “run anything” grant.
- Use a dedicated unprivileged identity and isolated workspace.
- Do not mount the user's full home directory, SSH agent, credential store, Docker socket, or host root into a worker.
- Apply filesystem, process, CPU, memory, PID, file-size, wall-time, and network controls.
- Default to no network egress for arbitrary code unless explicitly needed and approved.
- Ensure workspace cleanup and artifact export are explicit and audited.
- Treat cancellation and worker termination as best-effort for external side effects; record unknown outcomes.

### Data and secrets

- Keep secrets out of system prompts and ordinary context unless a narrowly scoped tool requires them.
- Prefer credential broker/short-lived scoped credentials over environment-wide secret inheritance.
- Redact tokens, personal data, and sensitive prompt/tool payload fields from logs/traces.
- Do not log raw browser cookies, authorization headers, or private file contents by default.
- Use explicit data policy for optional remote model providers.

### Network and local services

- Bind API, PostgreSQL, Ollama, and telemetry endpoints to loopback/private interfaces by default.
- Authenticate any non-loopback API exposure.
- Protect local services from DNS rebinding/SSRF and validate destinations where tools make requests.
- Restrict access to internal metadata endpoints and host services from sandbox workers.

### Dependencies and supply chain

- Pin and lock dependencies, review security advisories, and minimize permissions.
- Verify official SDKs/protocol revisions; avoid copying unreviewed MCP servers or arbitrary tool packages.
- Keep secrets/model weights/runtime artifacts out of source control.
- Record dependency versions and consider an SBOM for release artifacts.

## 6. Sandbox options to evaluate

See `research/LOCAL_SANDBOX_OPTIONS.md`. Candidate layers include Linux namespaces, seccomp, AppArmor/SELinux, Landlock, rootless OCI containers, gVisor, and Firecracker microVMs. These are not interchangeable; they differ in compatibility, host requirements, isolation boundary, operational complexity, and resource overhead. On Windows/macOS, suitable VM/container backends and host filesystem semantics must be examined separately.

A rootless container reduces some risks but is not proof of isolation against hostile code. A sandbox selection requires configuration review and negative tests on the actual target host.

## 7. Human approval

Approval should be required by policy for defined classes of sensitive actions. The UI is not the security boundary; the approval decision must be persisted and enforced at execution time. Any change to approved arguments/target/scope invalidates the approval. Provide denial, expiry, and cancellation semantics.

## 8. Security testing

- Prompt injection in tool outputs, retrieved documents, web content, and delegated-agent responses.
- Unauthorized tool/argument/target combinations.
- Approval replay or argument mutation after approval.
- Path traversal, symlink race, archive traversal, workspace boundary tests.
- Network egress and local metadata access tests.
- Resource exhaustion and process spawning limits.
- Cross-run data and artifact access.
- Secret leakage through model context, tool result, errors, logs, and traces.
- Malicious or misbehaving MCP server tests.
- Duplicate and ambiguous external side-effect execution.

## 9. Go-live gate

Powerful local execution remains disabled until the selected host/sandbox has a documented threat model, default policy, configuration review, positive and negative tests, cleanup/audit behavior, and explicit residual-risk statement. A developer convenience mode must be visibly separate from a restricted mode; never label an unrestricted mode “sandboxed.”
