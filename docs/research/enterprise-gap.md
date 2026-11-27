# Research Note: Enterprise Gap

**Snapshot:** 2026-11-26 · **Status:** Reference for milestone 7; nothing here is being built yet.

## Question

If this platform were a production application inside a large industrial manufacturer, what would have to change? Komatsu is the worked example: it runs a technical-document service bot for mechanics and dealers across several regions, and it organises AI through a central enablement function, about 500 AI Transformation Leads, and a Japan-first rollout ([Komatsu, 2026-06-09](https://www.komatsu.jp/en/newsroom/2026/20260619)). Komatsu has not published its AI stack. It has worked with Microsoft on data platforms before ([International Mining](https://im-mining.com/?p=57266)), so Azure services are used below as the likely enterprise defaults. Any major cloud provider maps the same way.

## What carries over unchanged

The runtime and run state machine, policy outside the model, provider adapters, risk tiers, identity on every run, evaluation discipline, containers, and configuration from the environment. These were chosen to map onto a company setting.

## What changes

| Area | This project | Enterprise production | Local stand-in for milestone 7 |
|---|---|---|---|
| Identity | Local accounts | SSO through Entra ID (OIDC/SAML), automatic provisioning (SCIM), roles separating employees, dealers, and customers; document permissions mirrored from source systems | Keycloak |
| Data sources | Approved local folders | Connectors to SharePoint and document management, telematics APIs (Komtrax), PLM and dealer systems; continuous ingestion; documents versioned per machine model and serial range | A connector interface with a mock document-management service |
| Search | PostgreSQL full-text | Multilingual search. PostgreSQL's built-in parser can't segment Japanese, so a search engine with a Japanese analyser (OpenSearch/Elasticsearch, Azure AI Search, or PGroonga), plus multilingual embeddings | OpenSearch with the kuromoji analyser, or PGroonga |
| Models | Ollama, plus an optional hosted API under a spend cap | Cloud-hosted models behind an internal gateway (rate limits, cost attribution, PII filtering, logging); Japan-region residency and no-training terms; vLLM for on-machine models | vLLM behind the model adapter, with a small gateway in front |
| Deployment | Docker Compose | Kubernetes (AKS) or managed containers, Terraform or Bicep, dev/staging/prod with automated releases, Key Vault, private networking | kind or k3d, Terraform, two environments |
| Database | Local PostgreSQL | Managed PostgreSQL with high availability, point-in-time recovery, and tested disaster recovery | Restore drills against a backup |
| Observability | OpenTelemetry, optional dashboards | The company monitoring platform, LLM tracing, SLOs, on-call, incident runbooks | Langfuse (self-hosted) alongside the OpenTelemetry Collector |
| Long-running work | In-process scheduler | Temporal or a managed queue with multiple workers | Temporal development server |
| Compliance | Threat model and negative tests | Formal security review and pen test, audit-log retention, APPI and GDPR, EU AI Act transparency, and export control of technical data (restricting who, including which model provider, may see it) | Classification and export-control fields enforced by the policy engine |
| Evaluation | Offline versioned sets | Offline plus live monitoring and user feedback; gold sets per language, verified by service engineers; a regression gate on every model upgrade | Japanese and English cases; a feedback endpoint |
| Interface | CLI, then a web inspector | Embedded in existing portals and chat tools, a mobile app for mechanics, offline mode on jobsites | — |
| Organisation | Owner and assistant | Product owner, central AI standards, security sign-off, support, training, phased regional rollout | — |

## Decisions taken now

Two cheap choices keep this path open:

- **Documents carry `language` and `classification` fields from milestone 1** ([data model](../design/data-model.md)). Adding them later would mean re-indexing and rewriting policy.
- **Policy may deny a tool result by classification** ([security spec](../design/security.md#file-access)), for example keeping `restricted` documents away from a hosted model.

Everything else waits for milestone 7.
