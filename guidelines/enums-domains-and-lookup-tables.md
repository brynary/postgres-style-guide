# Enums, Domains, and Lookup Tables

## Rule

Model closed value sets as `text` with a named `CHECK` constraint; promote to a lookup table when values carry attributes or the set is large; native enums only for truly static universal sets, and `CREATE DOMAIN` never.

## Why

`CHECK` lists change cheaply (`NOT VALID` then `VALIDATE`) and stay visible in `\d`. Native enums cannot drop values without a type rebuild under an exclusive lock. Lookup tables earn their join when values are data, not just labels.

## Do

- Use `text` plus a named `CHECK ... IN (...)` for app-owned state machines (`state IN ('pending', 'paid', 'refunded')`).
- Keep the application's enum definition and the `CHECK` list in sync; changing one is a migration touching both.
- Promote to a lookup table with an FK when values carry attributes (label, ordering, activation), need i18n, are user-managed, or the set is large (US states and territories, country codes).
- Seed lookup tables in migrations; give them `id` keys with the natural code as a unique column, per [primary keys and row identity](primary-keys-and-row-identity.md).
- Reserve native `ENUM` types for truly static universal sets that will never lose a value (days of the week, compass directions).

## Avoid

- Do not use `CREATE DOMAIN`; use plain types with per-column named `CHECK` constraints, even when a rule repeats across tables.
- Do not use native enums for business vocabularies; removing or renaming a value requires a table-rewriting type migration.
- Do not leave status columns as unconstrained `text`; bad writes from any path land silently.
- Do not create a lookup table for a three-value state machine that only the code interprets; that is a `CHECK`.
- Do not encode value sets in numeric codes (`state smallint` with meanings in the app).

## Example

```sql
-- App-owned state machine: text + CHECK.
CREATE TABLE orders (
  id uuid DEFAULT uuidv7() PRIMARY KEY,
  state text NOT NULL DEFAULT 'pending',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT orders_state_check
    CHECK (state IN ('pending', 'paid', 'shipped', 'refunded'))
);

-- Rich/large closed set: lookup table.
CREATE TABLE us_states (
  id uuid DEFAULT uuidv7() PRIMARY KEY,
  code text NOT NULL,
  name text NOT NULL,
  is_territory boolean NOT NULL DEFAULT false,
  CONSTRAINT us_states_code_key UNIQUE (code)
);
```

## Migration Notes

- Changing a `CHECK` list on a large table: add the new constraint `NOT VALID`, `VALIDATE CONSTRAINT` separately, then drop the old one; see the safe schema migration workflow.

## Exceptions

- Third-party schemas or extensions that ship enums or domains: use them as provided; do not restructure external contracts.
