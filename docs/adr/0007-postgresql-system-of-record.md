# ADR 0007: PostgreSQL as System of Record

- **Status:** Accepted. Version: PostgreSQL 18, from M1.6 ([ADR 0019](0019-search-architecture.md)). Driver: psycopg 3 from M1.6, rechecked against asyncpg in M2.1.
- **Date:** 2026-11-25

## Context

The platform stores relational entities (agents, versions, threads, messages, runs, steps, invocations, approvals) and bounded semi-structured metadata. Transactional consistency and relational queries matter.

## Decision

PostgreSQL is the primary store. Choose between 18.x and 19.x using compatibility checks and a representative workload test. Choose psycopg 3 or asyncpg after checking SQLAlchemy and Alembic support and concurrency behaviour. SQLAlchemy 2.x and Alembic are the proposed tooling.

## Consequences

- No second database without a demonstrated need.
- Event history plus queryable state, which is not event sourcing.
- Short transactions, never held open across model or tool calls.
- One `AsyncSession` per concurrent unit of work.

## Revisit when

Profiling or requirements justify another store, or compatibility testing rules out both candidate versions.
