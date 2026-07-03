# JSONB, Arrays, and Normalization

## Rule

Model core business data as relational columns; use `jsonb` only for document-shaped payloads, and arrays only for flat lists of primitives.

## Why

Data inside `jsonb` loses what the database provides: type checking, constraints, foreign keys, and planner statistics. Reserving it for genuinely document-shaped data keeps integrity where it matters and flexibility where it helps.

## Do

- Model attributes that are queried, joined, constrained, or indexed as real columns.
- Use `jsonb` for document-shaped payloads: external API responses, webhook bodies, user-defined settings, sparse fast-evolving attribute bags. Litmus test: would storing it in object storage with a reference be acceptable? Then `jsonb` is fine.
- Use the hot/cold pattern for externally sourced data: promote the attributes you query into columns, keep the raw remainder in one `jsonb` column (`payload`, `raw_attributes`).
- Always use `jsonb`, never `json`; `json` stores text and lacks an equality operator.
- Use arrays only for flat lists of primitives with no FK targets and no per-element metadata (`tags text[]`).
- Reach for a child or junction table the moment list elements reference another table or carry attributes.
- Query `jsonb` and arrays with containment operators (`@>`, `<@`, `?`); GIN indexing rules live in [advanced indexes](advanced-indexes.md).
- Validate required `jsonb` structure with a `CHECK` when a key is load-bearing: `CHECK (payload ? 'event_type')`.

## Avoid

- Do not put core business attributes in `jsonb` to avoid a migration; that trades a cheap `ADD COLUMN` for permanent statistics blindness.
- Do not join on values inside `jsonb` documents.
- Do not use `jsonb[]`; use one `jsonb` column holding an array.
- Do not store arrays of IDs referencing other tables; array elements cannot have FK constraints, so orphans accumulate silently.
- Do not update single fields of large `jsonb` values on hot paths; every update rewrites the whole value.
- Do not mirror the same fact in both a column and a `jsonb` document; pick one owner.

## Example

```sql
-- Hot/cold for imported data: queried fields are columns, the rest stays raw.
CREATE TABLE imported_listings (
  id uuid DEFAULT uuidv7() PRIMARY KEY,
  source text NOT NULL,
  external_id text NOT NULL,
  price numeric NOT NULL,
  city text NOT NULL,
  raw_attributes jsonb NOT NULL,
  tags text[] NOT NULL DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT imported_listings_source_external_id_key UNIQUE (source, external_id)
);

-- Containment query against the cold side:
SELECT il.id
FROM imported_listings il
WHERE il.raw_attributes @> '{"heating": "gas"}';
```

## Exceptions

- Ingestion staging tables may be a single `jsonb` column plus bookkeeping fields; promotion to columns happens downstream.
- Read-model/cache tables rebuilt from canonical data may denormalize freely, including `jsonb` projections; they must be rebuildable, not sources of truth.
