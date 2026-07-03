# Triggers

## Activation

Load this page when creating or reviewing any trigger, or when deciding how audit trails or derived data should be maintained.

## Rule

Use triggers for audit trails and derived-data maintenance, where they guarantee coverage on every write path; never for business workflow logic, and never where a constraint or generated column can express the rule.

## Why

Triggers run no matter which path wrote the row — ORM, psql, script, another service — which is exactly right for bookkeeping that must never be skipped, and exactly wrong for business decisions, which become invisible control flow.

## Do

- Maintain `updated_at` with the shared `set_updated_at()` trigger; the column requirement lives in [standard columns and row lifecycle](standard-columns-and-row-lifecycle.md).
- Write audit trails with `AFTER` row triggers inserting into an append-only audit table.
- Maintain denormalized aggregates (counter columns) with triggers when the source of truth is multiple write paths.
- Prefer, in order: constraint, then generated column, then trigger; a trigger is the tool when the first two cannot express the rule.
- Use `BEFORE` triggers to adjust the row being written (`updated_at`), `AFTER` triggers to record side effects (audit rows, counters).
- Keep each trigger function small and single-purpose; one behavior per trigger.
- Name triggers `{table}_{action}_trigger` per [object naming](object-naming.md), and pin `search_path` in trigger functions per [functions and procedures](functions-and-procedures.md).
- Comment every trigger with what invariant or bookkeeping it maintains.

## Avoid

- Do not put business workflow logic in triggers (state transitions, notifications-with-meaning, cross-service effects).
- Do not maintain values a `STORED` generated column can compute from the same row.
- Do not enforce non-overlap or cross-row uniqueness in triggers; temporal and exclusion constraints own that (see [temporal data and time zones](temporal-data-and-time-zones.md)).
- Do not chain triggers so one trigger's write fires another; that is invisible control flow.
- Do not swallow errors inside trigger functions; a failing trigger must fail the write.
- Do not toggle triggers off during bulk operations without recording why and restoring them in the same migration.

## Example

```sql
-- Shared updated_at maintenance:
CREATE FUNCTION set_updated_at() RETURNS trigger
LANGUAGE plpgsql
SET search_path = public, pg_temp
AS $$
BEGIN
  NEW.updated_at := now();
  RETURN NEW;
END;
$$;

CREATE TRIGGER orders_set_updated_at_trigger
  BEFORE UPDATE ON orders
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Audit: every state change is recorded, no matter who wrote it.
CREATE FUNCTION record_order_state_change() RETURNS trigger
LANGUAGE plpgsql
SET search_path = public, pg_temp
AS $$
BEGIN
  IF NEW.state IS DISTINCT FROM OLD.state THEN
    INSERT INTO order_state_changes (order_id, previous_state, new_state)
    VALUES (NEW.id, OLD.state, NEW.state);
  END IF;
  RETURN NEW;
END;
$$;

CREATE TRIGGER orders_record_state_change_trigger
  AFTER UPDATE ON orders
  FOR EACH ROW EXECUTE FUNCTION record_order_state_change();
```

## Exceptions

- Statement-level triggers with transition tables are the right form for bulk-write auditing when row-level overhead is measured as too high.
- When the application is provably the only write path and needs richer context (actor, request ID), application-level auditing may replace the trigger for that table; document the decision on the audit table.
