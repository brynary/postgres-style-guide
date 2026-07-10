# House Style and Postgres Philosophy

## Rule

Write readable, explicit SQL for PostgreSQL 18+: the database owns data integrity through constraints, the application owns business logic, and data is modeled relationally first.

## Why

These defaults keep schemas, queries, and migrations consistent across write paths.

## Do

- Assume PostgreSQL 18+ for new work and follow each page's fallback for older targets.
- Use [constraints](constraints-and-null-semantics.md) for integrity and keep workflow decisions in application code; database logic is limited to the cases sanctioned by [functions](functions-and-procedures.md) and [triggers](triggers.md).
- Model core data relationally; use [JSONB and arrays](jsonb-arrays-and-normalization.md) only for their documented cases.
- Prefer decomposed queries and route live schema changes through the [safe schema migration workflow](../workflows/safe-schema-migration.md).

## Avoid

- Do not treat this overview as a substitute for the relevant owner page.
- Do not use a version-gated feature before confirming the target version.

## Example

```sql
-- Integrity belongs in the database.
ALTER TABLE payments
  ADD CONSTRAINT payments_amount_check CHECK (amount > 0);

-- Refund eligibility remains application logic.
```

## Exceptions

- Older target databases: keep these conventions but substitute the fallbacks named in each page's `Version Notes`.
- Analytics and reporting contexts may relax query-shape rules where a page explicitly says so; schema rules still apply.
