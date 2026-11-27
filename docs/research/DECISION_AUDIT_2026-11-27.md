# Decision Audit, 2026-11-27

Decisions 1–91 checked against what production teams, vendors, and research actually do. The question for each one: would a staff engineer building this for a real company make the same call? Where a decision came from our conversation rather than evidence, this note says so, including where the bias was mine.

**Method.** Primary sources where they exist (vendor docs, release notes, papers), practitioner write-ups where they don't. Every claim is linked in [Sources](#sources). Evidence strength is marked **strong** (several independent primary sources), **moderate** (one primary source or consistent practitioner consensus), or **weak** (vendor marketing or a single blog).

**Verdicts.** *Keep*: the evidence supports it. *Amend*: right direction, wrong scope or timing. *Change*: the evidence points elsewhere. *Owner call-out*: a decision you made that I think is wrong.

## Summary

| # | Area | Decision | Verdict | Evidence |
|---|---|---|---|---|
| A1 | Approach | Own agent loop, direct SDKs, framework comparison after M1 | Keep, amend comparison | Strong |
| A2 | Approach | Eval-first; fixed pipeline vs agent loop on one eval set | Keep | Strong |
| A3 | Toolchain | Python 3.15 | Keep | Moderate |
| A4 | Runtime | In-process scheduler, "Temporal later" | Change | Strong |
| A5 | Models | Ollama as the only local server until M7 | Amend (move the vLLM trigger) | Strong |
| A6 | Retrieval | PostgreSQL 18 vs 19 left open until M2.1 | Change (decide 18 now) | Strong |
| A7 | Retrieval | pg_textsearch for BM25 | Keep (maturity concern resolved) | Strong |
| A8 | Retrieval | Hybrid RRF with no reranker | Change (add a reranker arm) | Strong |
| A9 | Eval | Eight categories fixed up front | Amend (revise after error analysis) | Moderate |
| A10 | Eval | ~20 cases per category, per-category comparisons | Amend (state what the data can detect) | Strong (arithmetic) |
| A11 | Eval | Hosted LLM judge calibrated against owner labels | Keep, specify | Moderate |
| A12 | Security | Injection classifier as a defence layer | Change (signal, not control) | Strong |
| A13 | Security | Hash-chained audit trail | Keep, rescope | Moderate |
| A14 | Observability | LLM trace viewer (Langfuse) deferred to M7 | Change (bring to M2) | Moderate |
| A15 | Observability | OTel GenAI semantic conventions | Keep, expect churn | Strong |
| A16 | Product | No requirements doc or SLOs ("it's just me") | Owner call-out | Moderate |
| A17 | Product | Clarification cap of 4 | Keep cap, add an over-asking metric | Moderate |
| A18 | Eval | Trajectory metrics | Amend (diagnostics, not pass/fail) | Moderate |
| A19 | Retrieval | 50-token chunk overlap | Change (0 by default, test 50) | Moderate |
| A20 | Retrieval | Embedding candidates | Amend (name Qwen3-Embedding-0.6B; case caveat) | Moderate |

Everything not listed was checked and holds: uv, Ruff, Pyright strict, SHA-pinned Actions, squash merges, Pydantic strict/frozen domain types, UUIDv7, the run state machine, PostgreSQL as the single store, pgvector with HNSW, passage-ID citations validated while streaming, the licence registry and pinned model digests, bounded retries with no automatic fallback, budgets from measured p99, restricted data never sent to hosted models, policy outside the model, RLS in M3, Argon2id, per-user OAuth, release-please, Dependabot and SBOMs.

## A1. Own agent loop — keep; widen the post-M1 comparison

Anthropic's guidance, from working with dozens of teams, is that the most successful implementations used simple, composable patterns rather than complex frameworks, and that developers should start with the LLM API directly. That matches our choice, and the plan already compares against LangGraph after M1.

**Amend:** add **Pydantic AI** to that comparison. We already standardise on Pydantic, and it has become the framework most aligned with our stack: it runs agents durably on Temporal, DBOS, Prefect, Restate and others. Comparing against LangGraph alone tests one design philosophy; comparing against both tells us whether the hand-written loop still earns its maintenance cost.

## A2. Eval-first — keep

This is the strongest decision in the plan. Anthropic's advice is to start with simple prompts, optimise them with comprehensive evaluation, and add multi-step agents only when simpler solutions fall short. Our fixed-pipeline-vs-agent-loop comparison on one eval set is exactly that test.

## A3. Python 3.15 — keep

My earlier concern was that 3.15 is too new. The evidence doesn't support changing it. 3.15.0 shipped on 9 October 2026. PyTorch 2.15 supports Python 3.11 through 3.15, with torch.compile on 3.15, which matters if a local reranker or embedding model runs in-process. Compiled database drivers (psycopg-binary, asyncpg) had 3.15 wheels before final release. The real risk is a transitive compiled dependency three levels down; the existing rule (fall back to 3.14 in a superseding ADR if a wheel lags) covers that. A company would pin whatever its base images ship, so the Dockerfile in M2 should name the base image and its Python explicitly.

## A4. Durable execution — change

ADR 0006 treats durability as a later, Temporal-sized decision. Since we wrote it, durable execution has become standard infrastructure for agents. Pydantic AI's own docs say to use it in production whenever a run must survive a deploy, crash or transient API failure, **or when a workflow waits hours or days for a person**. We already have `WAITING_APPROVAL` and `WAITING_INPUT`. Those states are exactly the case durable execution exists for.

Temporal is no longer the only serious option. DBOS keeps the workflow log in the Postgres you already run, and each step's output commits in the same transaction as the rows it wrote. Recovery reads that output back instead of re-running the step. That fits ADR 0007 (PostgreSQL as system of record) with no new service.

**Proposed change:** keep M1 in-process. Rewrite ADR 0006 so M2.1 decides between three options, using a failure-injection test (kill the process mid-run, then mid-approval):

1. our own step log in Postgres, about the size of the existing persistence work;
2. DBOS on the same Postgres;
3. Temporal.

The M1.2 state machine should be designed so each step's result is a persistable record. That is cheap now and expensive to retrofit.

## A5. Ollama until M7 — amend

Practitioner and vendor sources agree: Ollama is the local development tool, and vLLM is the production serving engine. Red Hat's benchmark on one A100 found vLLM peaking at 793 tokens/s against Ollama's 41, even with Ollama tuned for parallelism. One fair counterpoint from the same data: Ollama's per-token latency stayed stable under load, while vLLM's rose, so for one user Ollama is fine.

The plan puts vLLM in M7 (enterprise). The trigger is wrong. vLLM becomes necessary when there is **more than one concurrent user**, which is M3. **Proposed change:** in M3, run the same load test against Ollama and vLLM behind the adapter, and adopt vLLM if Ollama's throughput is the bottleneck. Check vLLM's GPU and quantisation support on your card first; production vLLM favours AWQ/GPTQ over GGUF, so the model artefacts differ.

## A6. PostgreSQL 18 vs 19 — change: decide 18 now

pg_textsearch supports **PostgreSQL 17 and 18**. Choosing pg_textsearch (decision approved) already decides the major version, unless we want to wait for 19 support. Leaving R-003 open until M2.1 means M1.5 builds the search on a version we haven't committed to. **Proposed change:** PostgreSQL 18 now, recorded in the retrieval ADR; revisit 19 when pg_textsearch lists it. The PostgreSQL 18 and 19 manuals stay in the corpus. That is document content, not the server version.

## A7. pg_textsearch — keep; maturity concern resolved

I flagged pg_textsearch as young. It reached 1.0 general availability in March 2026, and v1.1.0 is marked production-ready on Tiger Cloud. In September 2026, Google Cloud added it to AlloyDB and Cloud SQL. Two managed providers shipping it is strong evidence. One caveat: it needs `shared_preload_libraries`, which limits availability on managed Postgres such as RDS and Supabase until those providers add it. For a Komatsu-style deployment, that means checking the target platform's extension list before committing.

## A8. Reranker — change: add it as an eval arm

Our retrieval plan stops at hybrid search with RRF. The common production shape in 2026 is two stages: hybrid retrieval fetches about 50 candidates, then a cross-encoder narrows them to the top few. A cross-encoder reads the query and passage together rather than comparing separate embeddings. That is why it handles things like negation that embeddings miss: on the NevIR negation benchmark, most bi-encoders score 5–12% pairwise accuracy, while a cross-encoder reranker reaches 65.2%. Reported gains are roughly 5–7 NDCG points (moderate evidence; numbers vary by dataset).

The primary research agrees. BEIR (NeurIPS 2021) found BM25 a robust zero-shot baseline, with re-ranking and late-interaction models achieving the best zero-shot results, at a high compute cost. A follow-up on BEIR found that once a reranker is used, retrieving candidates with a dense model gave no nDCG@10 advantage over plain BM25. So keyword search plus a reranker may match hybrid search plus a reranker on our corpus, without the embedding pipeline.

Self-hostable options with clear licences: `BAAI/bge-reranker-v2-m3` (Apache 2.0, multilingual, which matters for the Japanese work in M7) and Qwen3-Reranker (Apache 2.0, sizes from 0.6B). **Proposed change:** M1.5/M1.6 compares four arms on the same eval set: keyword-only, keyword plus reranker, hybrid, and hybrid plus reranker. Measure latency and VRAM, since the reranker competes with the generation model for GPU memory.

## A9. Eval categories — amend: revise after error analysis

The eight categories were designed up front. Practitioner consensus (Hamel Husain and others) is that error analysis comes first: read real traces, group the failures you actually see, then build evaluators for those. Code checks handle deterministic failures and an LLM judge the subjective ones. Our categories are a reasonable starting hypothesis, and several (false premise, injected content) are hard to discover from traces alone. Anthropic's agent-eval guidance supports both halves: evals are especially useful early, to encode expected behaviour, and the task set should then come from real failures. **Proposed change:** keep the eight for M1.3, then add an error-analysis pass after the M1.6 baseline that may split, merge, or add categories. Record the result in ADR 0017's amendment.

## A10. Sample size — amend: state what the data can detect

This is arithmetic, not opinion (Wilson intervals and exact McNemar tests, computed for this note):

| Data | Observed | 95% interval |
|---|---|---|
| One category, 16/20 correct | 80% | 58%–92% |
| Whole set, 128/160 correct | 80% | 73%–86% |

| Paired comparison on 160 cases (fixed / broke) | Net change | p |
|---|---|---|
| 22 / 6 | +10 pts | 0.004 |
| 26 / 10 | +10 pts | 0.011 |
| 12 / 4 | +5 pts | 0.077 |
| 18 / 10 | +5 pts | 0.185 |

So: per-category results with 20 cases are directional only; a 20-point swing can be noise. On the whole set, a paired gate reliably catches about a 10-point change and usually misses 5. That is acceptable for M1, but the report and the CI gate must say so. **Proposed change:** the gate runs on the whole set with the paired test; per-category numbers are shown with intervals and never gate. Grow the categories where decisions depend on them.

## A11. LLM judge — keep; specify the calibration

Calibration against human labels is standard practice. The specifics that make it credible:

- binary pass/fail per dimension, not 1–5 scales;
- report true-positive and true-negative rates (or Cohen's kappa), not raw agreement;
- pin the judge model, prompt, and decoding settings, and record parse failures as explicit errors;
- re-label a fresh sample periodically.

One practitioner target is 75–90% judge-to-human agreement. Above 90% may mean the rubric is too coarse. Since you are the only labeller, there is no human–human agreement baseline. The honest substitute is re-labelling a blind sample of your own labels a week later and reporting your self-consistency.

## A12. Injection classifier — change: a signal, not a control

The primary source is *The Attacker Moves Second* (Nasr, Carlini, Tramèr and others from OpenAI, Anthropic and Google DeepMind; USENIX Security 2026). It tested 12 published defences across four technique families, including filtering classifiers such as the ProtectAI DeBERTa detector. Most went from near-zero attack success in their original papers to over 90% under adaptive attacks, and human red-teamers beat all of them. The defences that hold are architectural, not detection-based:

- plan-then-execute: the tool sequence is fixed before untrusted content is read;
- a quarantined model that reads untrusted text but cannot call tools;
- capability tracking on data flow, as in CaMeL.

Our plan already has the most important piece: policy outside the model, risk tiers, and approvals for writes. **Proposed change:** the classifier stays as telemetry (log and alert on likely injections, feed eval cases), and SECURITY_SPEC stops counting it as a layer that prevents anything. M4 (writes) adopts one of the architectural patterns before external-tier tools ship. Plan-then-execute fits the orchestrator we already planned.

## A13. Hash-chained audit trail — keep, rescope

Hash chains are the standard tamper-evidence technique: each row stores the previous row's hash, so a change, deletion, or insertion breaks verification for everything after it. The limits matter. A chain stored in the same database can be rewritten wholesale by someone with write access, and application-level read-only settings don't stop direct database tampering. Real systems pair it with storage-level controls. NIST SP 800-92 lists integrity checking as a function of log storage. Its 2023 revision (still a draft) drops implementation detail, so it gives no specific technique. **Proposed scope, in order of value:**

1. an append-only table: the application's role has `INSERT` and `SELECT` only, never `UPDATE` or `DELETE`;
2. the hash chain, with canonical serialisation (UTF-8 bytes, fixed number formatting);
3. a periodic anchor: write the head hash somewhere the database admin can't edit, such as a signed Git commit or a separate file.

Without item 3, call it tamper-evident against the application, not against an admin.

## A14. LLM trace viewer at M7 — change: bring it to M2

Error analysis (A9) means reading traces, and a JSONL file is a poor way to read a 30-step agent run. Langfuse and Phoenix both ingest OpenTelemetry, both self-host, and Phoenix recommends Postgres for production. The M1.8 HTML report covers eval results, not individual traces. **Proposed change:** M2 adds a self-hosted trace viewer as an optional Compose profile fed by the OTel spans we already emit. Pick Langfuse or Phoenix in M2 by trying both on the same traces. M7 keeps the enterprise integration work.

## A15. OTel GenAI conventions — keep, expect churn

These conventions are still in Development status. In June 2026 (semantic-conventions v1.42.0), the GenAI conventions moved out of the main repository into `open-telemetry/semantic-conventions-genai`, so the import path and version source change too. Adopting them is still right, because every tracing backend we'd consider reads them. Langfuse turns spans carrying `gen_ai.*` attributes into generations with model, token and cost data, while noting that the conventions are still evolving. Pin the convention version in code, keep the attribute names in one module, and expect a rename or two. One practical detail for M2: Langfuse's OTLP endpoint accepts HTTP/protobuf, not gRPC.

## A16. Owner call-out: no requirements or SLOs

You declined a PRD because "it's just me". For a PRD written to win stakeholder approval, that's right. But you asked for a result that looks like a staff engineer built it, and staff engineers write down measurable targets before they tune anything. Without targets, "the agent is good" has no definition, and none of the budget, latency or eval numbers have anything to be compared against. The charter defines production-grade as evaluated, secure, observable and budgeted, but sets no numbers for any of them.

**Proposed change:** one page, not a PRD. Service objectives set **after** the M1.6 baseline, from measured data:

- answer correctness floor;
- correct-abstention rate;
- p95 end-to-end latency and time to first token;
- cost per question on the hosted model;
- for M2+, availability and error budget.

Plus a short "who uses this and for what" paragraph, so the eval set has a user to represent. The SRE books are already in the reading list; this is where they get applied. Google's own SRE guidance recommends writing an SLO design document before opening any monitoring console. It also warns that too many indicators dilute attention while too few leave behaviour unexamined, so keep the list short.

## A17. Clarification cap — keep the cap, measure over-asking

Research frames clarification as two problems: deciding *when* to ask, and *what* to ask, while minimising interaction cost. Models tend to assume one interpretation instead of asking, and the hard part is avoiding unnecessary questions. A configurable cap of 4 is harmless as a ceiling. What's missing is a penalty for asking when it wasn't needed. **Proposed change:** the eval reports an *unnecessary-clarification rate* on every non-underspecified case (target near zero), next to the resolution rate on underspecified ones. Questions per run go on the trace.

## A18. Trajectory metrics — amend: diagnose, don't gate (added in the second source pass)

Anthropic's agent-eval guidance argues for grading outcomes rather than prescribing a fixed sequence of steps or tool calls. Agents often find valid solutions the test didn't anticipate, and rigid evals push optimisation the wrong way. Our trajectory metrics (tool selection, calls per task, loops) remain useful for finding *why* a case failed. **Proposed change:** they are reported as diagnostics and budgets (calls, tokens, cost), and no case fails only because the agent took a different valid path. The exception is the safety checks: a forbidden tool call or a policy violation fails the case regardless of the answer.

## A19. Chunk overlap — change: default to none, test it (third source pass)

The plan says structure-aware chunks of about 500 tokens with 50 tokens of overlap. The structure-aware part is supported. A 2026 study of 36 chunking methods, across six domains and five embedding models, found grouping by paragraph the best overall, while fixed-size character chunks did poorly. The overlap is not supported. An industry study run to set production defaults (arXiv 2601.14123) found overlap gave no measurable benefit and raised indexing cost, and that sentence chunking was the most cost-effective method. **Proposed change:** overlap defaults to 0; the M1.5/M1.6 retrieval comparison includes 0 vs 50 tokens, so we measure the choice rather than inherit it.

## A20. Embedding candidates — amend (third source pass)

The plan compares nomic-embed-text with "one multilingual model". Two findings name that model and add a caveat:

- **Qwen3-Embedding-0.6B** is the usual pick for quality per VRAM among local models: Apache 2.0, about 1.5 GB, available in Ollama, with a 32K context. It pairs with the Qwen3-Reranker in A8. BGE-M3 is the alternative for breadth across languages. The specific multilingual candidate should be Qwen3-Embedding-0.6B.
- **Since Ollama v0.30.0, all input to nomic-embed-text is lowercased**, as its model card specifies. Our Ollama (0.40.18) does this. Equipment manuals are full of model and part numbers where case can matter, so the eval needs a few cases that depend on exact identifiers. BM25 covers exact matches either way, which is one more reason to keep the keyword arm.

## Also checked in the third pass (keep)

- **UUIDv7:** PostgreSQL 18 adds `uuidv7()`, generating timestamp-ordered UUIDs for better index locality. That confirms the ID choice. IDs are still generated in the domain layer, because M1.2 has no database; the database default is a backstop.
- **Argon2id:** OWASP's minimum is 19 MiB of memory, 2 iterations and parallelism 1. Record those as the floor in SECURITY_SPEC.
- **MCP:** the current spec is 2026-07-28, the largest revision since launch. It removes sessions at the protocol layer. More than 30 CVEs against MCP servers were filed in January–February 2026. The plan already pins the protocol revision; M4 also treats every third-party MCP server as untrusted code from the supply chain: pinned, reviewed, and run with least privilege.

## Where the bias was mine

- **The injection classifier** was my suggestion and sounded rigorous. The evidence says it isn't a control.
- **Python 3.15** was something I kept questioning on instinct. The evidence supports keeping it.
- **pg_textsearch** I called young without checking. It is GA and on two hyperscalers.
- **Langfuse at M7** came from treating tracing as an enterprise feature rather than a debugging tool.
- **ADR 0006** reflected 2024-era practice, when durable execution meant Temporal and a cluster.

## Questions put to the owner

1. **A4:** rewrite ADR 0006 so M2.1 chooses between our own step log, DBOS and Temporal, by failure-injection test?
2. **A6:** commit to PostgreSQL 18 now?
3. **A8:** add a reranker arm to M1.5/M1.6?
4. **A12:** demote the classifier to telemetry, and require an architectural pattern before M4's external tools?
5. **A14:** trace viewer in M2 instead of M7?
6. **A16:** one-page service objectives after the M1.6 baseline?
7. **A5, A9, A10, A11, A13, A17:** accept the amendments as written?
8. **A1:** add Pydantic AI to the post-M1 framework comparison?

## Outcome (owner, 2026-11-27)

All proposed changes were accepted as written:

- **A1:** LangGraph and Pydantic AI in the post-M1 comparison.
- **A4:** ADR 0006 is rewritten for a bake-off in M2.1.
- **A5:** vLLM trigger moves to M3.
- **A6:** PostgreSQL 18 now.
- **A8:** reranker added as an eval arm in M1.5/M1.6.
- **A9–A11:** eval amendments.
- **A12:** classifier becomes telemetry; an architectural pattern is required before M4's external tools.
- **A13:** audit scope as listed.
- **A14:** trace viewer in M2.
- **A16:** one page of service objectives after M1.6.
- **A17:** unnecessary-clarification rate.

These are recorded in PRs 3–7 with the decisions they amend. A18 came from a second source pass and was approved by the owner. A19 and A20 came from a third pass and were approved: overlap 0 by default with 50 tested, and nomic-embed-text compared with Qwen3-Embedding-0.6B plus eval cases that depend on exact identifiers. For A16, the primary user is **mixed, technician first**: mostly service-technician questions about procedures, specs, part numbers and troubleshooting, with some engineer-style synthesis and version questions.

## Sources

- Anthropic, [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- Pydantic AI, [Durable execution](https://pydantic.dev/docs/ai/durable-execution/overview/); HackerNoon, [Durable execution for AI agents compared](https://hackernoon.com/durable-execution-for-ai-agents-langgraph-dbos-inngest-and-temporal-compared)
- Python, [What's new in 3.15](https://docs.python.org/3/whatsnew/3.15.html); PyTorch, [2.15 release](https://pytorch.org/blog/pytorch-2-15-release-blog/); [3.15 wheel readiness survey](https://python.plainenglish.io/93-6-of-the-top-1-000-pypi-packages-are-python-3-15-ready-64-of-the-140-that-compile-are-not-3a54d8ae0534)
- Red Hat, [Ollama vs vLLM benchmark](https://developers.redhat.com/articles/2025/08/08/ollama-vs-vllm-deep-dive-performance-benchmarking); Vercel, [Ollama vs vLLM](https://vercel.com/i/ollama-vs-vllm); SitePoint, [Ollama to vLLM migration](https://www.sitepoint.com/ollama-vs-vllm-a-migration-guide-for-scaling-teams/)
- Tiger Data, [pg_textsearch docs](https://www.tigerdata.com/docs/deploy/tiger-cloud/tiger-cloud-extensions/pg-textsearch) and [1.0 announcement](https://www.postgresql.org/about/news/pg_textsearch-v10-3264); [Google Cloud adds pg_textsearch](https://www.tigerdata.com/newsroom/google-cloud-brings-native-bm25-full-text-search-to-alloydb-and-cloud-sql-via-tiger-datas-pg_textsearch); [awesome-search operational note](https://frutik.github.io/awesome-search/Tools/pg_textsearch)
- Rerankers: [Splunk](https://www.splunk.com/en_us/blog/artificial-intelligence/reranker-models.html), [BigData Boutique](https://bigdataboutique.com/blog/rag-reranking-improving-retrieval-quality-with-cross-encoders), [Local AI Master](https://localaimaster.com/blog/reranking-cross-encoders-guide), [Klu](https://klu.ai/glossary/cross-encoder-reranking)
- Evals: [Pragmatic Engineer with Hamel Husain](https://newsletter.pragmaticengineer.com/p/evals); [Label Studio judge calibration](https://labelstud.io/learningcenter/how-to-use-llm-as-judge-for-agent-evaluation); [Arize judge alignment](https://arize.com/blog/measuring-human-llm-judge-alignment/); [OneUptime, Cohen's kappa](https://oneuptime.com/blog/post/2026-08-31-calibrate-llm-judge-cohens-kappa)
- Primary sources added in the second pass: Nasr et al., [The Attacker Moves Second (arXiv 2510.09023, USENIX Security 2026)](https://arxiv.org/abs/2510.09023); Thakur et al., [BEIR (arXiv 2104.08663)](https://arxiv.org/abs/2104.08663); [In Defense of Cross-Encoders for Zero-Shot Retrieval (arXiv 2212.06121)](https://arxiv.org/abs/2212.06121); Anthropic, [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents); Google SRE, [Service Level Objectives](https://sre.google/sre-book/service-level-objectives/), [Implementing SLOs](https://sre.google/workbook/implementing-slos/) and [How to design good SLOs](https://cloud.google.com/blog/products/devops-sre/how-to-design-good-slos-according-to-google-sres/); NIST, [SP 800-92](https://csrc.nist.gov/pubs/sp/800/92/final) and [its Rev. 1 draft](https://csrc.nist.gov/Projects/log-management); Langfuse, [OpenTelemetry integration](https://langfuse.com/integrations/native/opentelemetry); [GenAI semconv repository move](https://dev.to/azena-ai/opentelemetrys-genai-semantic-conventions-are-not-stable-yet-heres-what-actually-shipped-in-2026-3mke)
- Third pass: [A Systematic Analysis of Chunking Strategies (arXiv 2601.14123)](https://arxiv.org/abs/2601.14123); [A Systematic Investigation of Document Chunking Strategies (arXiv 2603.06976)](https://arxiv.org/html/2603.06976); [Qwen3 Embedding (arXiv 2506.05176)](https://arxiv.org/abs/2506.05176); [D-Central local embedding comparison](https://d-central.tech/local-embedding-models/); [InsiderLLM embedding guide](https://insiderllm.com/guides/embedding-models-rag/); PostgreSQL, [18 release announcement](https://postgresql.org/about/news/postgresql-18-released-3142/); OWASP, [Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html); MCP, [2026-07-28 security considerations](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization/security-considerations); WorkOS, [MCP 2026 spec](https://workos.com/blog/mcp-2026-spec-agent-authentication); CSA, [Agentic MCP security best practices](https://labs.cloudsecurityalliance.org/agentic/agentic-mcp-security-best-practices/)
- Injection: [Design patterns for securing LLM agents (arXiv 2506.08837)](https://arxiv.org/abs/2506.08837); [CaMeL (arXiv 2503.18813)](https://arxiv.org/abs/2503.18813)
- Audit: [Tamper-evident audit logs](https://dev.to/robertatkinson3570/the-architecture-behind-tamper-proof-audit-logs-56ek); [Activepieces, hash-chained audit trail](https://www.activepieces.com/blog/what-a-hash-chained-audit-trail-actually-means); [Vendure, tamper-proof storage](https://docs.vendure.io/current/platform/audit-trail/tamper-proof-storage)
- Clarification: [Clarify When Necessary (arXiv 2311.09469)](https://arxiv.org/abs/2311.09469); [Modeling future turns (arXiv 2410.13788)](https://arxiv.org/abs/2410.13788)
