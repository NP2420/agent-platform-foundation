# Research Note: PostgreSQL 18 vs 19

**Snapshot:** 2026-11-25 · **Decision:** Open; decided in M2.1.

## Facts

- 18.7 was released on 2026-11-12. 19.0 was released on 2026-11-19.
- Each major version is supported for five years.
- New in 19: `INSERT ... ON CONFLICT DO SELECT ... RETURNING`, `REPACK` / `REPACK CONCURRENTLY`, `WAIT` for standby replay (read-after-write on replicas), and parallel autovacuum improvements.

Sources: [19 release notes](https://www.postgresql.org/docs/19/release-19.html) · [18.7 release notes](https://www.postgresql.org/docs/release/18.7/) · [versioning policy](https://www.postgresql.org/support/versioning/)

## Relevance here

| Feature | Value to this project |
|---|---|
| `ON CONFLICT DO SELECT ... RETURNING` | Simplifies idempotent get-or-create and claims. 18 can do the same with other patterns, so it's not decisive on its own. |
| `REPACK CONCURRENTLY` | Helps if the event and invocation tables bloat. Not a concern initially. |
| `WAIT` / standby replay | Only matters with replicas. Not planned. |
| Parallel autovacuum | Helps write-heavy workloads at scale. Benchmark with real tables before judging. |

## Compatibility checks (both versions)

The chosen driver (psycopg 3 and/or asyncpg); SQLAlchemy 2.x and Alembic; migration up and down; backup and restore; any extensions we actually use; pooling and prepared statements; JSONB, indexes, constraints, isolation levels, and `SKIP LOCKED` where used; Docker image availability; admin tooling.

## Workload benchmark

Same schema, hardware, driver, data volume, and concurrency for both versions:

1. Create a thread and run with an idempotency key.
2. Append sequenced run events at a realistic model and tool cadence.
3. Update run state under competing cancel, approve, and complete requests.
4. Claim a tool invocation safely under concurrency.
5. Read a run's events in sequence order.
6. Filter recent runs by state and time.
7. Store bounded JSONB metadata.
8. Run concurrent readers and writers while measuring p50/p95 latency, throughput, lock waits, CPU and memory, WAL and disk growth, and autovacuum.

Warm up consistently, repeat, and report variance.

## Selection

Choose **19** if drivers, migrations, backup, and extensions all work, there are no regressions, and either the new features help or performance is at least on par.

Choose **18.x** if the ecosystem is materially more mature there, 19 shows blockers, or the new features don't matter yet.

Default until tested: 18.x as the conservative candidate. Use the latest 18 patch available when M2.1 starts.
