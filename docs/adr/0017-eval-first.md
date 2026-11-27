# ADR 0017: Eval-First Development and Eval Methodology

- **Status:** Accepted; amended 2026-11-27 (see the end)
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

## Amendment, 2026-11-27

Agreed with the owner after the [decision audit](../research/DECISION_AUDIT_2026-11-27.md) (A9, A10, A11, A16, A17, A18). Where this section and the text above disagree, this section wins.

**Categories.** Eight, in three families, replacing the six above:

| Family | Category | What the case tests |
|---|---|---|
| Answer correctly | single-source | a fact stated in one passage |
| | synthesis | combining two or more passages |
| | version-sensitive | the answer differs by document version, and the question names the version |
| Know its limits | unanswerable | in the corpus's domain, but the corpus doesn't say |
| | false premise | the question assumes something false |
| | out of scope | outside the corpus's domain altogether |
| Robustness | underspecified | needs a clarifying question, or an answer with stated assumptions |
| | injected content | a document contains instructions aimed at the model |

**Size.** About 20 cases per category, about 160 in total, starting from about 10 per category in M1.3. Most questions are phrased as a service technician would ask them (procedures, specs, part numbers, troubleshooting); synthesis and version-sensitive cases lean toward an engineer's questions.

**Categories are a hypothesis.** After the M1.7 baseline, an error-analysis pass reads the failing traces, groups the failures actually seen, and may split, merge, or add categories (A9).

**Statistics.** Wilson 95% intervals on every rate. With about 20 cases, a per-category result is directional only (16 of 20 is 58–92%), so per-category numbers are shown with their intervals and never gate anything. The CI gate from M2.3 compares a change with the baseline on the whole set, paired case by case, with an exact McNemar test. On 160 cases that reliably catches a change of about 10 points and usually misses 5, and reports say so (A10).

**Judge.** Binary pass or fail per rubric dimension, never a 1–5 scale. Calibrated against the owner's labels and reported as true-positive and true-negative rates (or Cohen's kappa), not raw agreement. Model, prompt, examples, and decoding are pinned; unparseable verdicts count as judge errors. With one labeller there's no human–human baseline, so a blind sample of the owner's labels is re-labelled a week later and the self-consistency is reported. A fresh sample is labelled at each milestone review (A11). The judge is a hosted model and follows the same data rules as any hosted call: never `restricted` content, and `internal` content only where that folder's policy allows hosted models. Otherwise private sets are scored by code checks only, or by a local judge reported separately.

**Clarification.** Two rates: unnecessary clarification on every case outside `underspecified` (target near zero), and resolution on `underspecified` cases (A17).

**Trajectories.** Tool choice, call counts, and loops are diagnostics and budgets, not pass or fail. A case never fails only because the agent took a different valid path. A forbidden tool call or a policy violation fails the case whatever the answer (A18).

**Service objectives.** After the M1.7 baseline, `docs/SERVICE_OBJECTIVES.md` sets measured targets: a correctness floor, abstention rate, p95 latency and time to first token, cost per question on the hosted model, and later availability (A16).

