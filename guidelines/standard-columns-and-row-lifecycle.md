# Standard Columns and Row Lifecycle

## Rule

Give every durable business table trigger-maintained `created_at`/`updated_at` columns, hard-delete rows by default, and derive computed columns with generated columns (virtual unless indexed or hot).

## Why

Uniform lifecycle columns make debugging, syncing, and auditing possible everywhere. Trigger maintenance keeps `updated_at` honest on every write path. Hard deletes keep uniqueness, queries, and FKs simple; soft delete is real complexity that must be bought deliberately.

## Do

- Add to every durable business table:
  - `created_at timestamptz NOT NULL DEFAULT now()`
  - `updated_at timestamptz NOT NULL DEFAULT now()`
- Maintain `updated_at` with the shared `set_updated_at()` trigger on every such table; the trigger pattern lives in [triggers](triggers.md).
- Hard-delete rows with `DELETE`; rely on `ON DELETE RESTRICT` (see [foreign keys and relationships](foreign-keys-and-relationships.md)) to surface dependents.
- Where the product genuinely needs recovery or audit history, use `deleted_at timestamptz` soft delete on that table, and then always:
  - enforce active-row uniqueness with partial indexes, per [index basics](index-basics.md);
  - define the child-row policy, because soft deletion does not activate FK delete actions;
  - scope application queries to `deleted_at IS NULL`;
  - include the active-row predicate in upserts, per [DML, upserts, and RETURNING](dml-upserts-and-returning.md);
  - define a purge/retention job.
- Use generated columns for values derived from the same row; virtual by default, `STORED` when the column is indexed, hot on the read path, expensive to compute, or must flow through logical replication.
- Give business defaults with `DEFAULT` at the column (`state text NOT NULL DEFAULT 'pending'`).

## Avoid

- Do not maintain `updated_at` from application code; any write path outside the ORM silently leaves it stale.
- Do not add `deleted_at` to tables "just in case"; unpaired with partial unique indexes and query scoping it is a latent bug, and history without a consumer is dead weight.
- Do not mix soft- and hard-delete semantics for the same table.
- Do not reach for a derivation trigger or application writes when a generated column can express the rule; the constraint -> generated column -> trigger escalation lives in [triggers](triggers.md).
- Do not index a virtual generated column; PostgreSQL requires `STORED` for that.

## Example

```sql
CREATE TABLE documents (
  id uuid DEFAULT uuidv7() PRIMARY KEY,
  title text NOT NULL,
  body text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER documents_set_updated_at_trigger
  BEFORE UPDATE ON documents
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();
```

## Version Notes

- Virtual generated columns are the PG18 default; on PG17 and older, all generated columns are `STORED`.

## Exceptions

- Immutable append-only tables (events, audit logs) need `created_at` only; skip `updated_at` and its trigger.
- Regulatory retention requirements may mandate soft delete or archival regardless of product needs; document the driver on the table's migration.
