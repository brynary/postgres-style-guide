# Constraints and NULL Semantics

## Rule

Declare every column `NOT NULL` unless absence is semantically meaningful, and encode cheap, stable, single-row domain rules as named `CHECK` constraints.

## Why

Nullable-by-default schemas leak three-valued logic into every query. Constraints in the database hold on every write path; application validation holds only on the paths that remember to run it.

## Do

- Declare `NOT NULL` on every column unless NULL carries meaning (`confirmed_at IS NULL` means not yet confirmed).
- Let NULL mean exactly "absent/not yet"; never sentinel values (`''`, `0`, epoch) standing in for it.
- Add named `CHECK` constraints for cheap, stable, single-row rules: positive amounts, length limits, value sets, `updated_at >= created_at`.
- Keep complex or fast-changing validation in the application; a rule that changes quarterly does not belong in DDL.
- Use `UNIQUE NULLS NOT DISTINCT` deliberately when NULL should count as a value for uniqueness (at most one row with no value).
- Make constraints deferrable only for a specific proven ordering problem, with a comment.
- Non-overlap and period rules are owned by [temporal data and time zones](temporal-data-and-time-zones.md); uniqueness mechanics by [index basics](index-basics.md); value-set checks by [enums, domains, and lookup tables](enums-domains-and-lookup-tables.md).

## Avoid

- Do not leave columns nullable because the `CREATE TABLE` default is nullable.
- Do not re-implement a `CHECK`-expressible rule as a trigger or app-only validation.
- Do not write multi-row or cross-table rules as `CHECK` constraints; they only see the row at hand and give false confidence.
- Do not forget that plain `UNIQUE` treats NULLs as distinct: multiple rows with NULL pass; make the choice explicit where it matters.
- Do not keep noncanonical generated constraint names; see [object naming](object-naming.md).

## Example

```sql
CREATE TABLE subscriptions (
  id uuid DEFAULT uuidv7() PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES users (id) ON DELETE RESTRICT,
  plan text NOT NULL,
  seats bigint NOT NULL,
  canceled_at timestamptz,           -- NULL = active: absence is meaningful.
  external_ref text,                 -- NULL = none; at most one row without one:
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT subscriptions_seats_check CHECK (seats > 0),
  CONSTRAINT subscriptions_user_id_external_ref_key
    UNIQUE NULLS NOT DISTINCT (user_id, external_ref)
);
```

## Migration Notes

- Adding `NOT NULL` or a `CHECK` to a large existing table: add as `NOT VALID`, backfill, then `VALIDATE CONSTRAINT`; the procedure and its version notes live in the safe schema migration workflow.

## Exceptions

- Staging/ingestion tables may be broadly nullable before cleansing; constraints apply where the data becomes canonical.
- Columns added by expand/contract migrations are temporarily nullable mid-flight; the contract step restores `NOT NULL`.
