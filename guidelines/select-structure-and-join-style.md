# SELECT Structure and Join Style

## Rule

Write explicit `JOIN ... ON` joins, qualify every column in multi-table queries, and never use `SELECT *` in application SQL.

## Why

Explicit joins keep the relationship between tables visible where it happens. Qualified columns and explicit select lists mean schema changes cannot silently change a query's meaning or widen its results.

## Do

- Join with explicit ANSI syntax: `JOIN ... ON`, `LEFT JOIN ... ON`.
- Prefer `ON` over `USING`; it survives column renames and stays unambiguous with three or more tables.
- Qualify every column with its table alias in any query that references more than one table.
- List selected columns explicitly in application queries, views, and functions.
- Put join conditions in `ON` and row filters in `WHERE`; for `LEFT JOIN`, conditions on the right table belong in `ON` (in `WHERE` they silently convert the join to inner).
- Order `FROM` items so the driving table comes first, then joins in the order the data flows.
- Alias per [sql formatting and comments](sql-formatting-and-comments.md).

## Avoid

- Do not use comma joins (`FROM a, b WHERE ...`).
- Do not use `NATURAL JOIN`; it silently re-matches when columns are added.
- Do not use `SELECT *` in committed application SQL; it is acceptable only for ad hoc exploration. Use `SELECT 1` inside `EXISTS`, and `count(*)` for row counts.
- Do not use `RIGHT JOIN`; reorder the tables and use `LEFT JOIN`.
- Do not leave columns unqualified in multi-table queries; an added column in another table can make them ambiguous or, worse, silently re-bind.

## Example

```sql
-- Users and their paid order count, including users with none:
SELECT
  u.id,
  u.email,
  count(o.id) AS paid_order_count
FROM users u
LEFT JOIN orders o
  ON o.user_id = u.id
  AND o.state = 'paid'      -- filter on the right table stays in ON
WHERE u.created_at >= now() - interval '90 days'
GROUP BY u.id, u.email;
```

## Exceptions

- `CROSS JOIN` is allowed when a cartesian product is the intent (generating combinations); say so with the explicit keyword.
- `USING` is tolerated in ad hoc psql exploration, not in committed SQL.
