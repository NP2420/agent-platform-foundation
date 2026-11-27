# Security and Execution Isolation

**Status:** The security boundary is an accepted requirement. Prompt-injection, identity, and MCP trust rules accepted 2026-11-27. The sandbox backend is open and must be selected and tested on a plain Linux host before any code execution is enabled.

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
- **Classification.** Every document has a classification (default `internal`, set per folder grant). Policy can keep a class away from a model provider; for example, `restricted` passages are never sent to a hosted model.
- **Writes** (milestone 4) go only to a per-user output folder, or through journalled, approved operations with undo.

Tests: path traversal, symlink and junction escape, case tricks on Windows paths, blocked-pattern matches inside a grant, cross-user access, and injected instructions in documents.

## Sandbox

Candidates and trade-offs are in [research/LOCAL_SANDBOX_OPTIONS.md](research/LOCAL_SANDBOX_OPTIONS.md). A rootless container reduces some risk but proves nothing against hostile code. Selection requires a configuration review and negative tests on the actual host.

## Prompt injection

Any text the model reads can carry instructions: user input, documents, web pages, tool output, MCP metadata. No filter makes that safe. *The Attacker Moves Second* (Nasr, Carlini, Tramèr and others; USENIX Security 2026) took 12 published defences, including detection classifiers, from near-zero attack success in their own papers to over 90% for most under adaptive attacks; human red-teamers beat all of them ([decision audit, A12](research/DECISION_AUDIT_2026-11-27.md#a12-injection-classifier--change-a-signal-not-a-control)).

**What carries the weight** is structure, not detection:

- policy outside the model, risk tiers, and deny-by-default grants, so an injected instruction can only ask for what the run was already allowed to do;
- approvals bound to the exact action for anything beyond `read`;
- untrusted content delimited and labelled with its provenance, and never allowed to change policy, grants, or budgets;
- `restricted` content never leaves the machine, so an injection can't exfiltrate it to a hosted model.

**The classifier is telemetry.** An injection classifier may score retrieved and tool content. A high score is logged and alerted, and the content becomes a candidate eval case. It never blocks, allows, or changes anything, and no document counts it as a control. Which classifier, and whether we train our own, is a learning project after milestone 1.

**Before external-tier tools (M4).** No `external`-tier tool ships until one structural pattern is in place. M4.2 compares two candidates on the injected-content eval cases plus adaptive attacks, and records the choice in an ADR:

- **plan-then-execute:** the tool sequence is fixed as a validated plan before any untrusted content is read, so content can change data but not which actions run;
- **quarantined reader:** a model with no tools reads untrusted content and returns only structured, validated fields to the planning model.

CaMeL-style data-flow capabilities (arXiv 2503.18813) are the reference if neither is enough.

## Identity (M3.1)

- **Passwords:** Argon2id via `argon2-cffi`, at or above OWASP's minimum (19 MiB of memory, 2 iterations, parallelism 1), tuned upward to the latency the login path can afford. The parameters are stored with each hash so they can be raised later.
- **API tokens:** random, shown once, stored only as a hash, with a recognisable prefix for secret scanning, explicit scopes, an expiry, and revocation. A token never grants more than its owner holds.
- **Sessions:** cookies marked `HttpOnly`, `Secure`, and `SameSite`, the ID rotated at login, idle and absolute timeouts. The values are set in M3.1 from the OWASP Session Management Cheat Sheet. Every state-changing request is CSRF-protected.
- **Authorisation, twice.** The application checks every request against the caller's grants. PostgreSQL row-level security on every owned table is a second layer, so a missing check in code still can't return another user's rows.
- **Connector credentials (later):** per-user OAuth with minimal scopes, refresh tokens encrypted at rest, never a shared service account acting for everyone.

## MCP trust (M4.4)

- **Protocol:** pin the revision (2026-07-28 is current; re-check at M4.4) and the SDK version.
- **Tokens:** follow the spec's requirements. Clients send the `resource` parameter; servers accept only tokens issued for them. Tokens are never passed through from one service to another.
- **Third-party servers are supply chain.** Over 30 CVEs against MCP servers were filed in January–February 2026. Each server is pinned by version and digest, reviewed before use, given a per-server tool allowlist, and run with least privilege. Its tool descriptions are untrusted text.
- **Until M5:** only first-party servers and remote servers reached over HTTP with scoped tokens. A third-party server that runs locally is someone else's code with this user's privileges, so it waits until it can run inside the M5 sandbox.

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
