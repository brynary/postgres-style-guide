# Aggregation, Window Functions, and Pagination

## Rule

Always pair `LIMIT` with a deterministic `ORDER BY`, paginate application-facing lists by keyset, and use window functions instead of self-joins for ranking and running values.

## Why

`LIMIT` without a total order returns arbitrary rows that shift between requests. `OFFSET` scans and discards everything it skips, so deep pages get slower and drift under concurrent writes. Window functions state analytic intent directly.

## Do

- Write an explicit `ORDER BY` with a deterministic tiebreaker (append `id`) on every query with `LIMIT`.
- Paginate application-facing lists by keyset: `WHERE (created_at, id) < ($1, $2) ORDER BY created_at DESC, id DESC LIMIT $3`; `id` values (uuidv7, time-ordered) make workable cursors.
- Use window functions for ranking, running totals, and neighbors: `row_number()`, `rank()`, `sum() OVER`, `lag()`/`lead()`.
- Name repeated window definitions once with `WINDOW w AS (...)`.
- Group by the natural key columns; keep `HAVING` for conditions on aggregates and `WHERE` for row filters.
- Use `count(*)` for row counts; `count(col)` only when skipping NULLs is the point.
- Use `filter (WHERE ...)` for conditional aggregates instead of `sum(CASE WHEN ... THEN 1 ELSE 0 END)`.

## Avoid

- Do not use `OFFSET` for application-facing pagination; reserve it for small, bounded admin/reporting pages.
- Do not implement top-N-per-group with self-joins; use `row_number()` or `LATERAL` (see [subqueries, EXISTS, and LATERAL](subqueries-exists-and-lateral.md)).
- Do not rely on `DISTINCT` to clean up row multiplication from a wrong join; fix the join.
- Do not use `GROUP BY 1, 2` ordinal references in committed SQL; name the columns.
- Do not compute aggregates the page does not display.

## Example

```sql
-- Keyset pagination: page 2 continues after the last row of page 1.
SELECT o.id, o.created_at, o.total
FROM orders o
WHERE o.user_id = $1
  AND (o.created_at, o.id) < ($2, $3)
ORDER BY o.created_at DESC, o.id DESC
LIMIT 25;

-- Each user's three largest paid orders: window function.
WITH ranked_orders AS (
  SELECT
    o.user_id,
    o.id,
    o.total,
    row_number() OVER (PARTITION BY o.user_id ORDER BY o.total DESC, o.id) AS rank
  FROM orders o
  WHERE o.state = 'paid'
)
SELECT ro.user_id, ro.id, ro.total
FROM ranked_orders ro
WHERE ro.rank <= 3;
```

## Exceptions

- Numbered-page UIs over small bounded sets (admin tables, reports) may use `LIMIT/OFFSET`; keep the deterministic `ORDER BY`.
- Approximate counts for very large tables may read `pg_class.reltuples` instead of `count(*)` when exactness is not required; comment the approximation.
