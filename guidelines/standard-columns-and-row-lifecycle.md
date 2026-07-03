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
  - convert unique constraints to partial unique indexes: `CREATE UNIQUE INDEX ... WHERE deleted_at IS NULL` — noting that partial unique indexes cannot be foreign-key targets, so restructure any FK that referenced the constraint first;
  - decide and document the child-row policy: soft delete never issues `DELETE`, so `ON DELETE RESTRICT` will not surface dependents — either cascade the soft delete in the application, block it while dependents exist, or restrict soft delete to leaf tables;
  - scope application queries to `deleted_at IS NULL`;
  - repeat the index predicate in upsert conflict targets; see [DML, upserts, and RETURNING](dml-upserts-and-returning.md);
  - define a purge/retention job.
- Use generated columns for values derived from the same row; virtual by default, `STORED` when the column is indexed, hot on the read path, expensive to compute, or must flow through logical replication.
- Give business defaults with `DEFAULT` at the column (`state text NOT NULL DEFAULT 'pending'`).

## Avoid

- Do not maintain `updated_at` from application code; any write path outside the ORM silently leaves it stale.
- Do not add `deleted_at` to tables "just in case"; unpaired with partial unique indexes and query scoping it is a latent bug, and history without a consumer is dead weight.
- Do not mix soft- and hard-delete semantics for the same table.
- Do not maintain derived values with update triggers or application writes when a generated column can express them.
- Do not index a virtual generated column; PostgreSQL requires `STORED` for that.

## Example

```sql
CREATE TABLE documents (
  id uuid DEFAULT uuidv7() PRIMARY KEY,
  title text NOT NULL,
  body text NOT NULL,
  -- Cheap derivation, never indexed: virtual (PG18 default).
  word_count bigint GENERATED ALWAYS AS
    (array_length(regexp_split_to_array(body, '\s+'), 1)),
  deleted_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TRIGGER documents_set_updated_at_trigger
  BEFORE UPDATE ON documents
  FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Soft delete requires partial uniqueness:
CREATE UNIQUE INDEX documents_title_key
  ON documents (title) WHERE deleted_at IS NULL;
```

## Version Notes

- Virtual generated columns are the PG18 default; on PG17 and older, all generated columns are `STORED`.

## Exceptions

- Immutable append-only tables (events, audit logs) need `created_at` only; skip `updated_at` and its trigger.
- Regulatory retention requirements may mandate soft delete or archival regardless of product needs; document the driver on the table's migration.
