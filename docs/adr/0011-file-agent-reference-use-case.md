# ADR 0011: File Agent as the Reference Use Case

- **Status:** Accepted
- **Date:** 2026-11-26

## Context

The platform was general-purpose with no first use case, which left the evaluation suite and the model choice with nothing concrete to measure. Companies that ship agents start with one narrow job and widen from there. The owner wants an agent that can eventually do anything with files that a user could, securely.

## Decision

The reference use case is an agent that works with files, grown in gated steps:

1. read-only search and answers with file-and-section citations, abstaining when the documents don't support an answer;
2. writing summaries and reports into an output folder;
3. organising files, with preview, approval, and undo;
4. running code on files, inside the sandbox.

File access is deny-by-default: only folders the user approves, with a built-in always-blocked list (credentials, keys, browser profiles, password-manager exports).

Two corpora:

- **Public:** this repository's docs and the PostgreSQL manual. These evaluation sets are committed. PostgreSQL ships separate 18 and 19 manuals, which tests version-aware answers.
- **Private:** the owner's personal folders. These evaluation sets live in `evals/private/` and are never committed.

Retrieval starts as full-text search. Embeddings are added only if the milestone 1 evaluation shows full-text search measurably failing.

## Consequences

- Phase 5's first real tool is file search, with path-scope tests from the start.
- The evaluation spec gains citation-correctness and abstention metrics.
- Documents carry a path, a modification time, and, where known, a version.
- Write and execute capabilities each need their own milestone and security gate.

## Revisit when

A different use case would teach more, or milestone 1 shows this one doesn't exercise the runtime enough.
