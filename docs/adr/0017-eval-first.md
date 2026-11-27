# ADR 0017: Eval-First Development and Eval Methodology

- **Status:** Accepted
- **Date:** 2026-11-26

## Context

Milestone 1 originally built the whole system and measured it in its last phase. Many AI teams instead build the eval set and scoring first, so each component is measured as it lands and regressions show up immediately. The owner's goal is production practice, where untested quality claims don't ship.

## Decision

**Order.** The eval harness and first cases (M1.3) come right after the domain types (M1.2), before any model or retrieval code. A fixed retrieve-then-answer pipeline (M1.7) is built before the agent loop (M1.8), as the baseline the agent must beat. Both are run with two tool-call methods, native tool calling and schema-constrained JSON, and with local and hosted models.

**Splits.**

- **Dev:** used freely while building and tuning prompts.
- **Held-out test:** run only at milestone reviews and for model or prompt decisions, so results aren't overfitted.
- **Regression:** every fixed bug becomes a permanent case.

**Size.** About 25 test cases per category, starting from about 10 and grown before the milestone 1 review, with new cases also coming from feedback. Every reported rate carries a 95% confidence interval: at 25 cases and ~80% accuracy that's roughly ±16 points, so only large differences count as real.

**Categories.** Answerable, multi-passage, version-specific, no answer, misleading premise, and prompt injection inside a document.

**Grading.** Code checks where the answer is exact: cited passages exist and were retrieved, abstention on no-answer cases, retrieval recall. An LLM judge grades answer correctness against expected facts with a rubric, and is checked against the owner's own labels on a sample before its scores are trusted.

**Format and tooling.** Cases are versioned JSONL files; our own harness runs them. A time-boxed study ports about five cases to Inspect AI and promptfoo, and compares them in a learning note. The exact case schema and interval method are designed in M1.3.

**Public and private.** Committed sets use public documents. Sets built from the owner's files live in git-ignored `evals/private/`, and are reported only as aggregate numbers.

## Consequences

- M1.3 has no real agent to measure, so it is tested against a fake agent with scripted answers.
- The owner verifies roughly 150 test cases plus a dev set over milestone 1.
- The four-way comparison roughly doubles the agent work in milestone 1, in exchange for measured evidence about each choice.

## Revisit when

The test set is large enough to justify statistical tests beyond intervals, or the LLM judge disagrees with the owner's labels too often to be useful.
