# Advanced Indexes

## Activation

Apply this page when a partial, expression, multicolumn, covering (`INCLUDE`), or GIN index is proposed, or when indexing `jsonb`, arrays, or ranges. For ordinary single-column B-trees and FK indexing, [index basics](index-basics.md) is enough.

## Rule

Use advanced index forms only with a stated query pattern recorded in the migration, and index searched `jsonb`/array columns with GIN queried through containment operators.

## Why

Advanced indexes are precision tools: each serves a specific query shape and is dead weight (or silently unused) outside it. Naming the pattern keeps the index honest and reviewable.

## Do

- Record the query pattern every advanced index serves as a comment in the migration that creates it.
- Use partial indexes for consistently filtered hot subsets: `WHERE deleted_at IS NULL`, `WHERE state = 'pending'`.
- Use expression indexes when queries filter on a computed value: `lower(email)`, `date_trunc('day', created_at)`; the query must use the identical expression.
- Order multicolumn indexes with equality-filtered, most-selective columns first, then range/sort columns; a `(a, b)` index serves `a`-only queries, not `b`-only.
- Use `INCLUDE` columns to make a hot, measured query index-only, sparingly.
- Use GIN for searched `jsonb` and array columns, and query with containment (`@>`, `<@`, `?`); plain `=` bypasses GIN.
- Use `jsonb_path_ops` for containment-only `jsonb` workloads (smaller, faster); default `jsonb_ops` when key-existence (`?`) queries are needed.
- Use GiST for range and exclusion cases, per [temporal data and time zones](temporal-data-and-time-zones.md).

## Avoid

- Do not create an advanced index without a named query pattern; decorative complexity.
- Do not create overlapping partial indexes per state value when one B-tree on the column serves them all.
- Do not index whole `jsonb` documents with GIN "for flexibility" on tables that are never containment-queried.
- Do not stack `INCLUDE` columns into covering indexes by default; wide indexes tax every write.
- Do not use hash indexes without a measured reason; B-tree covers equality well.
- Do not guess between `jsonb_ops` and `jsonb_path_ops`; derive from the actual operators in the query.

## Example

```sql
-- Pattern: login lookup is case-insensitive.
CREATE UNIQUE INDEX users_lower_email_key ON users (lower(email));

-- Pattern: dashboard lists a user's paid orders by recency.
CREATE INDEX orders_user_id_created_at_idx
  ON orders (user_id, created_at DESC)
  WHERE state = 'paid';

-- Pattern: containment search over imported attributes.
CREATE INDEX imported_listings_raw_attributes_idx
  ON imported_listings USING gin (raw_attributes jsonb_path_ops);

SELECT il.id
FROM imported_listings il
WHERE il.raw_attributes @> '{"heating": "gas"}';
```

## Migration Notes

- All index creation on existing tables uses `CREATE INDEX CONCURRENTLY`; see the safe schema migration workflow.

## Exceptions

- Very large append-mostly tables with time-correlated data may use BRIN for range scans over insertion order; measure before and after.
- Full-text search (`tsvector` + GIN) follows this page's gating; a dedicated page is added only if search becomes a real feature.
