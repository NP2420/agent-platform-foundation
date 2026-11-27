# ADR 0020: Data and Model Governance

- **Status:** Accepted
- **Date:** 2026-11-27
- **Supersedes:** the corpus list in [ADR 0011](0011-file-agent-reference-use-case.md), which predates the shift to equipment manuals

## Context

A production system has to answer, for any answer it gives: which document version it came from, whether we were allowed to use that document and model, and whether the data went anywhere it shouldn't. The repository is public, so the corpus and eval data also need rules about what may be committed.

## Decision

**Classification.** Every document is `public`, `internal`, or `restricted`. The default is `internal`, set per folder grant. `restricted` content is never sent to a hosted model, never captured in debug payloads, and its reads are audited ([security spec](../SECURITY_SPEC.md#file-access), [observability spec](../OBSERVABILITY_SPEC.md#audit-trail)).

**Public corpus.** Equipment manuals and the PostgreSQL 18 and 19 manuals.

- **Manuals:** only US Army technical manuals marked Distribution Statement A (approved for public release). US government works are in the public domain, but the distribution statement is what confirms release.
- **PostgreSQL manuals:** under the PostgreSQL License.

The corpus is not committed. `corpus/manifest.toml` lists each document's URL, licence, distribution statement where relevant, SHA-256, and retrieval date. A fetch script downloads it and refuses any file whose hash doesn't match.

**Applicability.** Each document records what it applies to: equipment model, manual revision, and publication date for manuals; major version for the PostgreSQL manuals. Version-specific eval cases depend on it.

**Lineage.** Every passage traces to a document ID, document version, and content hash. Every answer traces to its passages, and every run records the model digest, prompt version, and retrieval arm. Given a run ID, the exact inputs behind an answer can be named.

**Models.** The licence registry and digest pinning are in the [model spec](../MODEL_SPEC.md#model-registry-licences-and-pinning). A model with no recorded licence can't be used. Python dependencies are covered by [ADR 0022](0022-licences-code-scanning-coverage.md).

**Private data.** Sets built from the owner's files live in git-ignored `evals/private/` and are reported only as aggregates ([ADR 0017](0017-eval-first.md)). Nothing derived from private files (passages, embeddings, traces) is committed.

## Consequences

- Corpus setup is one script, with no binary files in Git.
- Each corpus document needs a manifest entry with its licence before it can be used.
- A wrong manifest entry is a licence risk, so manifest changes are reviewed like code.

## Revisit when

A source with different licence terms is added, documents come from systems other than local folders (M7), or classification needs more than three levels.
