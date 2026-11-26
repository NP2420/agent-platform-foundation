# Research Note: PostgreSQL 18.7 vs 19.0

**Snapshot date:** 2026-11-25 · **Decision:** Open

## 1. Question

Which PostgreSQL major version should be the local platform's initial system-of-record database? PostgreSQL 18.7 and PostgreSQL 19.0 are both candidates at the research snapshot. The choice should be based on compatibility, operational maturity, and representative workload behavior—not release number alone.

## 2. Verified release facts

- PostgreSQL 18.7 release date: 2026-11-12.
- PostgreSQL 19.0 release date: 2026-11-19.
- PostgreSQL's major-version policy currently provides five years of support for each major release.
- PostgreSQL 19 release notes include a new `INSERT ... ON CONFLICT DO SELECT ... RETURNING` capability, `REPACK`/`REPACK CONCURRENTLY`, `WAIT` for synchronous standby replay/read-after-write behavior, parallel autovacuum improvements, and other query/replication/maintenance changes.

Sources:
- https://www.postgresql.org/docs/19/release-19.html
- https://www.postgresql.org/docs/release/18.7/
- https://www.postgresql.org/support/versioning/

## 3. Potential relevance to this platform

### `INSERT ... ON CONFLICT DO SELECT ... RETURNING`

Potentially useful for idempotent get-or-create/claim workflows where a conflict should return an existing row. It may simplify some transaction patterns, but PostgreSQL 18 can implement equivalent application behavior using other transaction/query strategies. Do not make this one feature the sole reason to use 19.

### `REPACK CONCURRENTLY`

Potentially useful if run/event/invocation tables become large and table/index bloat requires maintenance. This is a future operational concern; the initial local workload may not benefit materially.

### `WAIT` and standby replay

Potentially useful if we later use replication/read replicas and require read-after-write consistency on a standby. The initial local single-instance system likely does not need this feature.

### Parallel autovacuum and other performance changes

Potentially beneficial for larger/high-write workloads. Benchmark only after representative tables/indexes and concurrency patterns exist; small synthetic tests may not represent production behavior.

## 4. Compatibility matrix

Test both candidate versions with:

- selected Python driver (psycopg 3 and/or asyncpg);
- SQLAlchemy 2.x and Alembic selected version;
- migration create/upgrade/downgrade strategy;
- backup and restore tools;
- extensions actually required (avoid adding extensions speculatively);
- connection pooling and prepared statements;
- JSONB, indexes, constraints, transaction isolation, `SKIP LOCKED`/locking patterns as used;
- local Docker/Compose image availability and platform architecture;
- observability/administration tooling used by the project.

## 5. Representative workload benchmark

Build a small schema/benchmark fixture that models actual expected operations:

1. Create run and thread records with idempotency key.
2. Append sequenced run events at model/tool-step cadence.
3. Update run state under competing cancellation/approval/completion requests.
4. Claim an eligible tool invocation with safe concurrency semantics.
5. Query recent events/steps for a run in sequence order.
6. Search/filter recent runs by state and timestamps.
7. Store bounded structured model/tool metadata in JSONB.
8. Run concurrent writers and readers while measuring p50/p95 latency, throughput, lock waits, CPU, memory, WAL/disk growth, and autovacuum behavior.

Use the same schema, hardware, driver, data volume, and concurrency for both versions. Warm up consistently, repeat runs, report sample counts and variability, and avoid drawing conclusions from one run.

## 6. Selection criteria

Select PostgreSQL 19 if:

- required drivers/migrations/tools support it reliably;
- backup/restore and operational workflows are verified;
- there are no blocking extension or platform compatibility issues;
- the new SQL/maintenance capabilities provide practical value or performance is at least acceptable;
- the team accepts the maturity/support implications of adopting a newly released major version.

Select PostgreSQL 18.7 if:

- compatibility or tool ecosystem is materially more mature;
- 19 reveals blockers/regressions;
- 19's new capabilities do not matter to the current workload;
- the conservative baseline better matches project risk tolerance.

Do not assume 18.7 is always safer or 19 is always faster. Record the selected patch version and update policy in an ADR once tests are done.

## 7. Current provisional recommendation

Keep the version open. Prepare a reproducible compatibility/benchmark test during Phase 7, while using 18.7 as a conservative candidate rather than a final decision. Recheck current patch releases when Phase 7 begins; do not hard-code 18.7 if a newer 18.x patch is available then.
