# Assistant Working Guide

Rules for any AI assistant working in this repository. They are in addition to the specs, never a substitute for reading the current repository.

## Source of truth

- The repository, especially `docs/`, is the durable record. Don't rely on memory of earlier conversations; read the current files first.
- If the docs and the code disagree, say so, work out which is stale, and fix it once the owner agrees.
- Keep decision statuses honest. Don't promote Proposed or Open to Accepted without the owner's confirmation.

## Git

- **The owner commits. Assistants never run `git commit` or `git push`.** Prepare and stage changes, then hand over the commit command.
- Make targeted edits to individual files, not replacement bundles or ZIP drops.
- Check `git status` and `git diff --stat` before staging. Unexpected deletions are a stop signal.
- Keep unrelated changes in separate commits (for example, a restore and a rewrite).

## Research and truthfulness

- Check current or version-sensitive claims against primary sources: specifications, release notes, official docs, source code, papers. Textbooks are for durable concepts; blogs are secondary.
- Separate measured facts, external evidence, interpretation, and decisions.
- Never invent benchmarks, test results, compatibility, or citations. Say what hasn't been verified.
- When hardware or workload determines the answer, propose an experiment instead of asserting a preference.
- Challenge the owner's assumptions with evidence, and your own earlier recommendations too.
- Record material findings in `RESEARCH_LOG.md` or a research note, with dates and versions.

## Teaching

The owner is comfortable with the tools and concepts and wants to refine and apply them. So:

- explain the problem before the abstraction, and the trade-off behind each choice;
- point to the relevant chapter, spec, or paper when it adds something;
- name the failure modes, and what would make the choice wrong;
- skip basics and mechanical syntax explanations, and match depth to the question.

## Implementation

- Small, coherent, reviewable chunks: one concept, interface, or behaviour at a time.
- Before code: the objective, where it fits, the design, and the alternatives considered.
- Name the exact files touched. Avoid unrelated refactors and speculative abstractions.
- Never claim tests, builds, or benchmarks pass unless you ran them and saw the output. Show the commands and the actual results.
- Experiments live in the repository as scripts, not as one-off shell sessions.

## Engineering standards

- Simple, explicit, typed contracts, with dependencies pointing inward.
- Domain logic independent of frameworks, providers, databases, and workflow engines.
- Validate untrusted input at boundaries. Model output never authorises anything.
- Explicit side effects, retries, idempotency, cancellation, and failure states.
- Bounded time, concurrency, memory, processes, output size, and model usage.
- Structured errors; no swallowed exceptions.
- Unit tests for deterministic logic; contract and integration tests at boundaries.
- No new dependency, service, or datastore without a concrete requirement.
- A container is not a sandbox for hostile code.

## Documentation

- Update the affected spec, ADR, research log, and the roadmap status table along with any material change.
- Project status lives only in the roadmap status table. Don't duplicate it elsewhere.
- Write plainly: short declarative sentences, no filler, no repeated disclaimers. State a caveat once, where it applies.

## Session closeout

At the end of a substantial session, report: what changed, the tests run and their results, decisions and their status, open questions, the next chunk, and the commit command for the staged changes.
