# Functions and Procedures

## Activation

Apply this page when writing or reviewing any `CREATE FUNCTION`/`CREATE PROCEDURE`, including trigger functions. If the task is deciding whether logic belongs in the database at all, start with [house style and Postgres philosophy](house-style-and-postgres-philosophy.md).

## Rule

Keep database functions few and small, label each with the strictest correct volatility, and default to `SECURITY INVOKER`.

## Why

Database functions are harder to test and debug than application code, and a mislabeled volatility gives the optimizer a false contract.

## Do

- Write a database function only for the sanctioned cases: trigger functions (see [triggers](triggers.md)), expression-index helpers, and constraint predicates too complex for inline `CHECK`.
- Use plain `LANGUAGE sql` when the body is a single statement; reserve `plpgsql` for control flow. (A function with a pinned `search_path` is never inlined into calling queries, so this choice buys clarity, not performance.)
- Label the strictest correct volatility: `IMMUTABLE` only for pure functions of their arguments; `STABLE` for anything reading tables; `VOLATILE` when it writes or depends on changing state.
- Declare `STRICT` (returns NULL on NULL input) when that is the real contract; it saves the null-handling boilerplate.
- Keep `SECURITY INVOKER` (the default). Use `SECURITY DEFINER` only for a specific privilege boundary; treat inputs as hostile, revoke default `PUBLIC` execution, and grant only the intended role.
- Apply the mandatory path pinning and qualification rules from [schema layout and search_path](schema-layout-and-search-path.md).
- Use a procedure (`CREATE PROCEDURE` + `CALL`) only when the body genuinely needs transaction control (batched maintenance with periodic `COMMIT`).
- Name functions after their behavior (`set_updated_at`, `normalize_email`), per [object naming](object-naming.md).

## Avoid

- Do not put business workflow logic in functions; it belongs in the application (see [house style and Postgres philosophy](house-style-and-postgres-philosophy.md)).
- Do not mark a table-reading function `IMMUTABLE` to make it usable in an index; the index will hold stale values. Use a `STORED` generated column or fix the design.
- Do not default to `plpgsql` for one-statement bodies.
- Do not create overloaded function families that differ only in argument types; agents and humans both pick the wrong one.
- Do not hide `SELECT`-able logic behind functions when a view or plain query works; see [views and materialized views](views-and-materialized-views.md).

## Example

```sql
-- Expression-index helper: pure, so IMMUTABLE is correct.
CREATE FUNCTION normalize_email(email text) RETURNS text
LANGUAGE sql
IMMUTABLE
STRICT
SET search_path = public, pg_temp
RETURN lower(trim(email));

CREATE UNIQUE INDEX users_normalized_email_key
  ON users (normalize_email(email));
```

## Exceptions

- Batch maintenance procedures with explicit transaction control are legitimate; keep them in migrations or documented maintenance scripts, not hidden in application flows.
- `SECURITY DEFINER` is required for controlled privilege elevation (for example, letting the read-only role refresh one materialized view); apply the full hardening from Do above and review with [roles, privileges, and row-level security](roles-privileges-and-row-level-security.md).
