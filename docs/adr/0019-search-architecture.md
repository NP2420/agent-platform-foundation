# ADR 0019: Search Architecture

- **Status:** Accepted
- **Date:** 2026-11-27
- **Supersedes:** the retrieval line of [ADR 0011](0011-file-agent-reference-use-case.md) ("full-text first, embeddings only if it fails")

## Context

Answers are only as good as the passages behind them. ADR 0011 planned full-text search alone, adding embeddings only after a failure. Since then, three findings changed that ([decision audit](../research/DECISION_AUDIT_2026-11-27.md) A6–A8, A19, A20):

- **Two stages is the common production shape:** retrieve about 50 candidates, then rerank them with a cross-encoder. On BEIR, re-ranking gave the best zero-shot results, and BM25 candidates served a reranker as well as dense ones did.
- **pg_textsearch** brings BM25 to PostgreSQL (1.0 in March 2026, now in Cloud SQL and AlloyDB). It supports PostgreSQL 17 and 18.
- **Chunk overlap** gave no measurable benefit in a 2026 industry study, while chunking along document structure did well.

The question is no longer "full-text or embeddings" but which arm wins on our corpus. That is measured, not assumed.

## Decision

**Store.** PostgreSQL 18, in Docker Compose, from M1.6: pg_textsearch for BM25 and pgvector with HNSW for vectors. psycopg 3, sync for indexing scripts and async in the runtime; the M2.1 workload benchmark can overturn it (R-004). One database; no separate vector store ([ADR 0007](0007-postgresql-system-of-record.md)).

**Extraction.** Markdown, text, and code as-is. PDFs: text-based only, with pypdf and pdfplumber compared on the corpus; scanned PDFs are skipped and reported, not OCR'd. The PostgreSQL manuals are extracted from their HTML, keeping section structure.

**Chunking.** Along document structure (headings, sections, paragraphs), about 500 tokens, with no overlap by default. Each passage records its document version, section path, page where known, and line range.

**Arms.** Evaluated on retrieval metrics alone in M1.6, before any generation, in stages:

1. keyword (BM25): overlap 0 vs 50 tokens;
2. keyword plus reranker;
3. hybrid (BM25 plus vectors, fused with reciprocal rank fusion): nomic-embed-text vs Qwen3-Embedding-0.6B;
4. hybrid plus reranker, with the winners of stages 1 and 3;
5. contextual retrieval on the best arm so far: before indexing, a model writes a 50–100-token note placing each chunk in its whole document, prepended to the chunk for both BM25 and embedding. Public corpus only, written by the hosted model because a whole manual doesn't fit a local model's context. Anthropic reports 49% fewer failed retrievals, or 67% with reranking; that is a vendor claim, and this stage tests it on our corpus.

Reranker candidates: `bge-reranker-v2-m3` and Qwen3-Reranker-0.6B. Each stage carries only its winner forward. M1.7 onwards uses the best arm; the others stay runnable for later comparisons.

**Passages to the model.** Packed into a token budget set per profile, highest-ranked first, whole passages only. Each passage has an ID; the model cites passage IDs, and citations are checked against the retrieved set as the answer streams. A citation to anything not retrieved fails the answer.

**Citations shown to people:** file, then page or section, then line range.

**Freshness.** Per folder: `on_search` (default; changed files are re-indexed before the query runs) or `manual`. A file that is about to be cited is always re-checked by hash, so a citation never points at stale text.

## Consequences

- PostgreSQL moves into milestone 1, so M1.6 adds Docker Compose and a migration tool earlier than planned.
- The staged comparison costs several index builds. Retrieval-only metrics keep each one cheap: no model generates an answer.
- Contextual retrieval spends hosted tokens at index time, under the hosted spend limit. Each note is stored with its passage, along with the model and prompt version that wrote it, so lineage covers it ([ADR 0020](0020-data-and-model-governance.md)). Private and restricted files never get hosted notes.
- Embedding models and rerankers become registry entries with licences and digests ([model spec](../MODEL_SPEC.md#model-registry-licences-and-pinning)).
- Ollama lowercases nomic-embed-text input, so the eval includes cases that depend on exact part and model numbers. BM25 still matches those exactly.
- pg_textsearch needs `shared_preload_libraries`, so a managed target must offer it. Cloud SQL and AlloyDB do; others need checking.

## Revisit when

The corpus or languages change (Japanese in M7 needs a different analyser), latency or VRAM rule out the winning arm, or PostgreSQL search measurably limits quality.
