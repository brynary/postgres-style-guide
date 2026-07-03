# Scalar Types

## Rule

Use `text` for strings, `numeric` for money and exact quantities, `bigint` for integers, and `boolean NOT NULL` for flags; `char(n)`, `money`, and floating-point money are banned.

## Why

PostgreSQL's `text` and `varchar` perform identically, so length limits belong in constraints that can change cheaply. Exact and growing values need types that never overflow or round.

## Do

- Use `text` for all strings; enforce business length limits with a named `CHECK` on `char_length(...)`.
- Use `numeric` for money and exact decimal quantities; store a `currency text` column alongside amounts when multi-currency.
- Use `bigint` for counters and any integer that can grow; `integer`/`smallint` only for values with a known small bound (ages, positions, percentages).
- Use `boolean NOT NULL` with an explicit `DEFAULT` for flags; a nullable boolean is a three-state value in disguise.
- Use `double precision` only for genuinely approximate measurements (coordinates, scores).
- Use `bytea` for binary payloads; prefer external object storage with a `text` reference for large blobs.

## Avoid

- Do not use `varchar(n)`; changing the limit is a type change, while a `CHECK` swaps under light locks.
- Do not use `char(n)`; it space-pads values and surprises comparisons.
- Do not use the `money` type; locale-dependent formatting and weak arithmetic.
- Do not use `real`/`double precision` for money or anything summed for business purposes.
- Do not store numbers or booleans as strings.
- Do not default to `integer` because the ORM does; overflowing a hot column in production is a notorious outage class.

## Example

```sql
CREATE TABLE invoices (
  id uuid DEFAULT uuidv7() PRIMARY KEY,
  reference text NOT NULL,
  amount numeric NOT NULL,
  currency text NOT NULL DEFAULT 'USD',
  attempt_count bigint NOT NULL DEFAULT 0,
  is_paid boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT invoices_reference_check CHECK (char_length(reference) <= 40),
  CONSTRAINT invoices_amount_check CHECK (amount > 0)
);
```

## Exceptions

- Interop schemas mirroring an external system may keep that system's declared types, including `varchar(n)`, to match the contract; comment the source.
- Timestamps and dates are owned by [temporal data and time zones](temporal-data-and-time-zones.md); identifiers by [primary keys and row identity](primary-keys-and-row-identity.md).
