# Primary Keys and Row Identity

## Rule

Give every table `id uuid DEFAULT uuidv7() PRIMARY KEY`; enforce natural keys as unique constraints, never as primary keys.

## Why

UUIDv7 values are time-ordered, so they index like sequential keys while staying globally unique, non-enumerable, and safe to expose in URLs and APIs. Surrogate keys keep identity stable when business attributes change.

## Do

- Declare `id uuid DEFAULT uuidv7() PRIMARY KEY` on every new table.
- Expose the `id` directly in APIs and URLs by default; no second public identifier is needed.
- When the product requires prefixed identifiers (`usr_V1StGXR8Z5`), add `public_id text NOT NULL` with a unique constraint: the type prefix plus an independently generated random suffix. The uuid `id` stays internal for every FK; APIs and URLs then expose only `public_id`.
- Enforce natural keys (email, SKU, external reference) with unique constraints; see [index basics](index-basics.md) for constraint vs index.
- Use `bigint GENERATED ALWAYS AS IDENTITY` instead only when key compactness or extreme insert concurrency demonstrably matters, and note why in the migration.
- Give junction tables their own `id` plus a unique constraint over the pair of foreign keys.

## Avoid

- Do not use `serial` or `bigserial`; identity columns replaced them.
- Do not use random v4 UUIDs (`gen_random_uuid()`) as primary keys; random inserts fragment the B-tree.
- Do not use natural keys as primary keys, even "stable" ones; emails change and codes get recycled, and the change ripples through every foreign key.
- Do not use composite primary keys on business tables; use `id` plus a unique constraint.
- Do not mix key strategies within a schema without a documented reason.
- Do not derive `public_id` from the PK bits (TypeID-style encoding) or the PK from `public_id`; the two are independent values joined by an indexed lookup.

## Example

```sql
CREATE TABLE products (
  id uuid DEFAULT uuidv7() PRIMARY KEY,
  sku text NOT NULL,
  name text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT products_sku_key UNIQUE (sku)
);
```

## Version Notes

- `uuidv7()` requires PostgreSQL 18. On older targets, generate UUIDv7 values in the application, or fall back to `bigint GENERATED ALWAYS AS IDENTITY` (PG10+) when application-side generation is not practical.

## Exceptions

- High-write-concurrency tables can contend on the rightmost index leaf with time-ordered keys; if measured, `bigint` identity or fillfactor tuning is the escape hatch.
- Static lookup tables (see [enums, domains, and lookup tables](enums-domains-and-lookup-tables.md)) still get `id` keys; their natural codes stay unique-constrained columns.
