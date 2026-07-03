# Query Performance Investigation

Use this workflow when a query is slow, a page or job has a database bottleneck, or an index is proposed as a performance fix.

## Required Guidelines

Load [guidelines.md](../guidelines.md), then load these guideline pages as needed:

- [Index basics](../guidelines/index-basics.md)
- [Advanced indexes](../guidelines/advanced-indexes.md)
- [CTEs and query decomposition](../guidelines/ctes-and-query-decomposition.md)
- [Aggregation, window functions, and pagination](../guidelines/aggregation-window-functions-and-pagination.md)
- [JSONB, arrays, and normalization](../guidelines/jsonb-arrays-and-normalization.md)

## Workflow

1. Capture the actual slow query with its real bind values (from logs, `pg_stat_statements`, or application telemetry), not a paraphrase of it.
2. Record a baseline: `EXPLAIN (ANALYZE, BUFFERS)` on a production-representative dataset. Development databases with 100 rows prove nothing.
3. Read the plan from the innermost expensive node outward. Classify the bottleneck:
   - Sequential scan on a large table with a selective filter: missing or unusable index.
   - Index exists but unused: expression mismatch, type mismatch, low selectivity, or operators the index cannot serve (GIN vs `=`).
   - Misestimated row counts (estimated vs actual off by orders of magnitude): stale statistics (`ANALYZE` the table) or correlated predicates.
   - Nested loop over many rows: join order/estimate problem.
   - Sort or hash spilling to disk: memory-bound aggregation or missing supporting index for the sort order.
   - Fast query, slow endpoint: N+1 statements at the application layer; fix the call pattern, not the query.
4. Fix in this order: rewrite the query to match existing access paths, refresh statistics, then add or adjust an index under the [advanced indexes](../guidelines/advanced-indexes.md) gating rule (stated query pattern, `CREATE INDEX CONCURRENTLY` per the safe schema migration workflow).
5. Change one thing at a time and rerun the same `EXPLAIN (ANALYZE, BUFFERS)`; keep the change only on a material, repeatable win.
6. Check the write side of any new index: hot-path insert/update tables pay for every index they carry.
7. Record the outcome where the change lives (migration comment or commit): the query pattern, the before/after timings, and the plan node that changed.

## Measurement Commands

```sql
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;

-- Statement-level view of what is actually slow:
SELECT query, calls, mean_exec_time, rows
FROM pg_stat_statements
ORDER BY mean_exec_time * calls DESC
LIMIT 20;

-- Are existing indexes used? Candidates for removal:
SELECT relname, indexrelname, idx_scan
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

ANALYZE orders;  -- refresh statistics for one table
```

## Avoid

- Do not add an index as the first move; most slow queries are shape problems (missing filter, N+1, offset pagination) the index would only mask.
- Do not tune against `EXPLAIN` without `ANALYZE`; estimates are the thing being debugged.
- Do not test on unrepresentative data sizes.
- Do not add planner hints via `MATERIALIZED`/`NOT MATERIALIZED` or `enable_*` settings as a fix; they are diagnostics, and any kept fence needs a comment and evidence.
- Do not keep a "faster" query that violates the query-style guidelines without recording the measured justification.
- Do not touch server-wide settings (`work_mem`, `shared_buffers`) to fix one query.
