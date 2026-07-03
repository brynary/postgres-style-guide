# Subqueries, EXISTS, and LATERAL

## Rule

Use `EXISTS (SELECT 1 ...)` for semi-joins, always `NOT EXISTS` instead of `NOT IN` against subqueries, `= ANY` for parameterized lists, and `LATERAL` for per-row derived rows.

## Why

`NOT IN` returns zero rows when its subquery yields a single NULL, a silent wrong answer. `EXISTS` states membership intent directly and the planner treats it as a semi-join. `LATERAL` expresses per-row top-N without correlated-subquery contortions.

## Do

- Test membership with `EXISTS (SELECT 1 FROM ... WHERE ...)`.
- Test non-membership with `NOT EXISTS`, never `NOT IN (subquery)`.
- Pass parameterized value lists as `column = ANY($1)` with an array parameter; one bind parameter regardless of list length.
- Use `IN (...)` only for short literal lists written in place.
- Use `LATERAL` joins for per-row derived rows: latest N children per parent, per-row computations reused across the select list.
- Use a scalar subquery only when it returns at most one row by construction; otherwise it is a runtime error waiting for data.

## Avoid

- Do not use `NOT IN` against any subquery or nullable column; the NULL trap is silent.
- Do not rewrite semi-joins as `JOIN` + `DISTINCT`; the deduplication hides intent and multiplies rows before removing them.
- Do not nest subqueries more than one level; decompose per [CTEs and query decomposition](ctes-and-query-decomposition.md).
- Do not use correlated subqueries in the select list for values a join or `LATERAL` can produce once.

## Example

```sql
-- Users with at least one paid order, none of them refunded:
SELECT u.id, u.email
FROM users u
WHERE EXISTS (
  SELECT 1 FROM orders o
  WHERE o.user_id = u.id AND o.state = 'paid'
)
AND NOT EXISTS (
  SELECT 1 FROM orders o
  WHERE o.user_id = u.id AND o.state = 'refunded'
);

-- Latest two orders per user: LATERAL.
SELECT u.id, recent.id AS order_id, recent.created_at
FROM users u
CROSS JOIN LATERAL (
  SELECT o.id, o.created_at
  FROM orders o
  WHERE o.user_id = u.id
  ORDER BY o.created_at DESC, o.id
  LIMIT 2
) AS recent;
```

## Exceptions

- `NOT IN` against a short literal list of non-null values (`state NOT IN ('draft', 'archived')`) is safe and readable.
- Use `LEFT JOIN LATERAL ... ON true` instead of `CROSS JOIN LATERAL` when parents without matches must be kept.
