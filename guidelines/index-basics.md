# Index Basics

## Rule

Index every foreign key column at creation and enforce unique business keys with unique constraints; add any other index only for a known query pattern.

## Why

PostgreSQL does not index FK columns automatically, and unindexed FKs turn parent deletes and joins into child-table scans. Every index taxes every write, so speculative indexes are pure cost until a real query needs them.

## Do

- Create an index on every FK column in the same migration that adds the FK.
- Enforce natural/business uniqueness with a `UNIQUE` constraint; it shows intent in `\d` and is FK-referenceable.
- Use a standalone `CREATE UNIQUE INDEX` only when the uniqueness is partial (`WHERE deleted_at IS NULL`) or over an expression (`lower(email)`).
- Add non-unique indexes only when a known query filters or sorts on the column; name the query pattern in the migration.
- Accept the implicit B-tree indexes that PK and unique constraints create; do not duplicate them.
- Name indexes per [object naming](object-naming.md).
- Drop indexes that no query uses; unused indexes still cost every write and vacuum.

## Avoid

- Do not create an FK without its index "for now".
- Do not index low-cardinality flags (`is_active`) by themselves; a partial index on the interesting subset may qualify under [advanced indexes](advanced-indexes.md).
- Do not add an index for every column that appears in any WHERE clause; demand-driven means a known, recurring pattern.
- Do not create a single-column index on a column already leading a composite index.
- Do not enforce uniqueness in application code; concurrent writers make check-then-insert racy.

## Example

```sql
CREATE TABLE api_tokens (
  id uuid DEFAULT uuidv7() PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  token_digest text NOT NULL,
  expires_at timestamptz NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  -- Business key: unique constraint, not a bare index.
  CONSTRAINT api_tokens_token_digest_key UNIQUE (token_digest)
);

-- FK column indexed in the same migration.
CREATE INDEX api_tokens_user_id_idx ON api_tokens (user_id);

-- Known pattern: the reaper scans for expired tokens.
CREATE INDEX api_tokens_expires_at_idx ON api_tokens (expires_at);
```

## Migration Notes

- On existing tables, always `CREATE INDEX CONCURRENTLY` (outside a transaction); see the safe schema migration workflow.

## Exceptions

- FK columns on high-volume append-only tables that are never joined from the parent side may skip the index, with the reason documented next to the soft-reference decision.
- Columns covered as the leading column of a composite index needed by a known query do not also get a single-column index.
