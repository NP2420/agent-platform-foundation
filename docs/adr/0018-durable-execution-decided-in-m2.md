# ADR 0018: Durable Execution, Decided by Experiment in M2.1

- **Status:** Accepted
- **Date:** 2026-11-27
- **Supersedes:** [ADR 0006](0006-in-process-before-temporal.md)

## Context

ADR 0006 treated durability as a later, Temporal-sized decision. Two things have changed.

- **Our own design.** Runs pause in `WAITING_APPROVAL` and `WAITING_INPUT` until a person answers, which may take hours. A process restart during that wait must not lose the run. That is the main case durable execution exists for.
- **Practice.** Durable execution is now standard infrastructure for production agents. Pydantic AI supports eight engines. DBOS keeps its workflow log in the application's own PostgreSQL, so it needs no new service. Temporal is still the most capable option, and the heaviest to run. ([decision audit, A4](../research/DECISION_AUDIT_2026-11-27.md#a4-durable-execution--change))

## Decision

**Milestone 1** stays in-process and single-process, with no crash-safety claims. From M1.2, each completed step is an immutable record: step ID, run ID, kind, inputs digest, outcome, and timings. The runtime can then persist these records in M2.1 without its shape changing.

**M2.1** chooses the durability mechanism by experiment. The candidates:

1. our own step log in PostgreSQL, written in the same transaction as the step's other rows;
2. DBOS on the same PostgreSQL;
3. Temporal.

**Experiment.** The same agent and eval cases on each candidate. Kill the process at three points: mid model call, mid tool call, and during `WAITING_APPROVAL`. Then restart.

**Criteria, in order:**

- the run resumes from the last completed step;
- no completed side effect runs twice;
- an uncertain outcome is recorded as unknown, not guessed;
- the code added to the runtime, and what it constrains (Temporal's deterministic-workflow rule, for example);
- the services added and their operating cost;
- the fit with the PostgreSQL system of record ([ADR 0007](0007-postgresql-system-of-record.md)).

The use cases depend on a scheduler port (start, execute ready step, record outcome, request approval, resume), never on an engine's API directly.

## Consequences

- Recovery is designed in, not retrofitted. Domain types carry step records from the first phase.
- Whichever engine is chosen, external writes still need idempotency keys. Every engine can re-run a step whose outcome wasn't recorded.
- M2.1 grows by one experiment. In return, the choice rests on measured recovery rather than on a 2024-era default.

## Revisit when

The chosen mechanism fails a recovery test, runs need durable timers or multiple workers it doesn't support, or the step log's own code grows past what a library would cost to adopt.
