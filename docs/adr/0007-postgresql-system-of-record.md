# ADR 0007: PostgreSQL as Proposed Application System of Record

- **Status:** Accepted direction; major version and driver open
- **Date:** 2026-11-25

## Context

The platform stores relational entities (agents, versions, threads, messages, runs, steps, invocations, approvals) plus bounded semi-structured provider/tool metadata. Transactional consistency and queryable relationships are important.

## Decision

Use PostgreSQL as the primary application store. Evaluate 18.7 and 19.0 with compatibility and representative workload tests. Select Python DB driver (psycopg 3 or asyncpg) after checking SQLAlchemy/Alembic support and concurrency behavior. Use SQLAlchemy 2.x/Alembic as proposed tools, subject to Phase 7 validation.

## Consequences

- No second database without a demonstrated requirement.
- Store event history and queryable state; do not call the system event-sourced unless it meets that definition.
- Keep transactions short; never hold DB transactions open across LLM or external tool calls.
- One async session per concurrent unit of work/task where using SQLAlchemy AsyncSession.

## Revisit when

Workload profiling or product requirements demonstrate that another database/store is justified, or compatibility/operational testing rejects PostgreSQL candidates.
