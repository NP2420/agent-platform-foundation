# Security and Execution Isolation

**Status:** The security boundary is an accepted requirement. The sandbox backend is open and must be selected and tested on a plain Linux host before any code execution is enabled.

## Stance

The model is an untrusted component that can be steered by user input, retrieved documents, web pages, tool output, MCP servers, memory, or earlier conversation. It may propose actions; only trusted code authorises them. Powerful actions run outside the API and runtime privilege boundary.

Every security claim is scoped to a threat model, host, kernel, runtime configuration, and attacker capability.

## Assets

- User files, repositories, SSH keys, cloud and API credentials, browser sessions, environment variables.
- Conversation history, memory, prompts, private documents, artifacts.
- Model endpoints and provider credentials.
- Database records, run history, approvals, audit events.
- The host itself: processes, network, other users' data.
- Credentials held by tools and MCP servers.

## Threats

OWASP's Top 10 for Agentic Applications (2026) is a useful checklist (goal hijack, tool misuse, privilege abuse, supply chain, unexpected code execution, memory poisoning, inter-agent abuse, cascading failure, false trust, rogue agents), alongside a project-specific model:

- Prompt injection through user input, retrieved text, web pages, or tool output.
- Tool-call spoofing, schema abuse, confused deputy, privilege escalation.
- Secret exfiltration through prompts, logs, artifacts, network, or subprocesses.
- A malicious MCP server or a compromised dependency.
- Path traversal, symlink escape, unsafe archive extraction.
- Shell and code abuse: fork bombs, resource exhaustion, network scanning, lateral movement.
- Data leaking across runs.
- Duplicate side effects after a timeout or recovery.
- Router fallback sending private data to a remote provider.
- Actions taken with a user's ambient browser identity.

## Trust boundaries

1. **Client → API:** authenticate, validate, enforce size and rate limits.
2. **Model → runtime:** output is a proposal, never an instruction or an authorisation.
3. **Tool or MCP → runtime:** metadata and results are untrusted. Validate, bound, label, keep provenance.
4. **Runtime → broker:** only structured, policy-approved requests.
5. **Broker → worker:** restricted identity, explicit filesystem, network, and resource grants.
6. **App → database and secrets:** narrowly scoped credentials.
7. **Local → remote provider:** explicit data classification and configuration before anything leaves the machine.

## Controls

**Authorisation**
- Deny-by-default tool grants and least-privilege capability sets per agent, run, and tool.
- Authorisation comes from policy code, never from model output.
- User, run, worker, and service identities are separate.
- Approvals bind to the exact action, arguments, target, caller, scope, and expiry.

**Execution broker**
- No model-generated code or shell in the API process.
- Structured requests only; never a "run anything" grant.
- A dedicated unprivileged identity and an isolated workspace per invocation.
- Never mount the home directory, SSH agent, credential stores, Docker socket, or host root.
- Limits on filesystem, processes and PIDs, CPU, memory, file size, wall time, and network.
- No network egress by default for arbitrary code.
- Explicit, audited cleanup and artifact export.
- Cancellation is best effort; unknown outcomes are recorded.

**Data and secrets**
- Secrets stay out of prompts and context unless a scoped tool needs them.
- Prefer short-lived scoped credentials over inherited environment secrets.
- Redact tokens and personal data from logs and traces. Never log cookies, auth headers, or private file contents by default.

**Network**
- API, PostgreSQL, Ollama, and telemetry bind to loopback by default.
- Any non-loopback exposure needs authentication.
- Defend against SSRF and DNS rebinding; validate destinations for tools that make requests.
- Sandbox workers cannot reach host services or metadata endpoints.

**Supply chain**
- Lock dependencies and watch advisories.
- Use official SDKs; don't adopt unreviewed MCP servers or tool packages.
- Keep secrets, model weights, and artifacts out of Git. Consider an SBOM for releases.

## File access

- **Allowlist.** A user's tools can reach only folders that user has granted. No grant, no access.
- **Always blocked**, even inside a grant: SSH and GPG keys, cloud credential folders, browser profiles, password-manager data, `.env` files, and anything matching the configured block patterns.
- **Canonicalise, then check.** Resolve `..`, symlinks, junctions, and case before comparing against grants. A symlink that resolves outside a grant is refused.
- **Per-user, enforced by the application.** The agent runs as one OS user, so per-user grants are enforced by the application's authorisation layer. Every tool call carries the caller's identity and is checked against that user's grants.
- **Bounded reads.** Size limits per file and per result; binary files are skipped unless an extractor exists.
- **Contents are untrusted.** A document can contain instructions aimed at the model. They are data, not commands.
- **Writes** (milestone 4) go only to a per-user output folder, or through journalled, approved operations with undo.

Tests: path traversal, symlink and junction escape, case tricks on Windows paths, blocked-pattern matches inside a grant, cross-user access, and injected instructions in documents.

## Sandbox

Candidates and trade-offs are in [research/LOCAL_SANDBOX_OPTIONS.md](research/LOCAL_SANDBOX_OPTIONS.md). A rootless container reduces some risk but proves nothing against hostile code. Selection requires a configuration review and negative tests on the actual host.

## Human approval

Policy defines which actions need approval. The UI is not the boundary: the decision is persisted and enforced at execution time. Changing the arguments, target, or scope invalidates an approval. Denial, expiry, and cancellation have defined semantics.

## Security tests

- Prompt injection in tool output, retrieved documents, web content, and subagent responses.
- Unauthorised tool, argument, and target combinations.
- Approval replay; arguments changed after approval.
- Path traversal, symlink races, archive traversal.
- Network egress and metadata endpoint access.
- Resource exhaustion and process spawning.
- Access to another run's data or artifacts.
- Secret leakage through context, results, errors, logs, and traces.
- Malicious or misbehaving MCP servers.
- Duplicate and ambiguous side effects.

## Gate for powerful execution

Stays disabled until the selected host and sandbox have a documented threat model, a default policy, a configuration review, passing positive and negative tests, cleanup and audit behaviour, and a residual-risk statement. A developer convenience mode, if one exists, is visibly separate and is never called "sandboxed".
