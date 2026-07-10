# DML, Upserts, and RETURNING

## Rule

Every `UPDATE` and `DELETE` carries a `WHERE` clause, post-write reads use `RETURNING`, and upserts use `INSERT ... ON CONFLICT` (reserving `MERGE` for multi-action bulk synchronization).

## Why

An unqualified `UPDATE` or `DELETE` is the most destructive statement an agent can emit. `RETURNING` removes the write-then-read round trip and its race. `ON CONFLICT` is the atomic, idiomatic upsert; `MERGE` earns its weight only when one pass must insert, update, and delete.

## Do

- Spell an intentional full-table write as `WHERE true` with an explicit marker comment.
- Use `RETURNING old.col, new.col` (PG18) when the delta matters: audit records, cache invalidation, change notifications.
- Reference incoming upsert values as `excluded.col`.
- Target `ON CONFLICT` at the specific constraint's columns, not `DO NOTHING` without a conflict target.
- When the arbiter is a partial unique index (soft-delete tables), repeat its predicate in the conflict target: `ON CONFLICT (email) WHERE deleted_at IS NULL DO UPDATE ...`; a bare column list matches only full constraints and fails at runtime against a partial index.
- Use `MERGE` only when synchronizing a table against a source set with insert, update, and delete actions in one pass.
- Batch bulk changes with data-modifying CTEs or multi-row `VALUES`/`UNNEST` statements, not row-at-a-time loops.
- Batch very large updates/deletes in chunks (by key range) to bound lock time and WAL spikes; the batching procedure lives in the safe schema migration workflow.

## Avoid

- Do not check-then-write for uniqueness in application code; concurrent writers race; `ON CONFLICT` exists for this.
- Do not follow an `INSERT` with a `SELECT` to learn what was written.
- Do not interleave chatty single-row DML in a loop when one set-based statement does the work.

## Example

```sql
-- Upsert a setting, keeping track of what changed (PG18 RETURNING OLD/NEW):
INSERT INTO user_settings (user_id, key, value)
VALUES ($1, $2, $3)
ON CONFLICT (user_id, key) DO UPDATE
  SET value = excluded.value
RETURNING old.value AS previous_value, new.value AS current_value;

-- Multi-step write as one statement: cancel stale orders, log each one.
WITH canceled AS (
  UPDATE orders o
  SET state = 'canceled'
  WHERE o.state = 'pending'
    AND o.created_at < now() - interval '30 days'
  RETURNING o.id, o.user_id
)
INSERT INTO order_events (order_id, user_id, event_type)
SELECT c.id, c.user_id, 'auto_canceled'
FROM canceled c;
```

## Version Notes

- `RETURNING old.*/new.*` requires PostgreSQL 18; on older targets, return the new row and fetch prior state inside the same data-modifying CTE if needed.
- `MERGE` requires PG15+; `MERGE ... RETURNING` requires PG17+.

## Exceptions

- Framework-generated DML (ORM writes) follows the framework; these rules govern hand-written and agent-written SQL.
- Truncating a table is `TRUNCATE`, not an unqualified `DELETE`; it is DDL-adjacent and belongs in migrations or documented maintenance scripts.
