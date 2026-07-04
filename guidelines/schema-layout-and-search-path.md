# Schema Layout and search_path

## Rule

Keep a single-application database's objects in `public` with `CREATE` revoked from `PUBLIC`, and pin `search_path` in every function body instead of trusting the caller's path.

## Why

One schema keeps DDL, tooling, and queries simple; the real risks are unprivileged users creating objects and functions resolving names through a caller-controlled `search_path`, both of which are closed by this rule.

## Do

- Put application objects in `public` for single-application databases.
- Revoke schema creation from the world once per database: `REVOKE CREATE ON SCHEMA public FROM PUBLIC;` (default since PG15; keep it explicit in setup).
- Let application SQL rely on the default `search_path` in single-schema databases; do not scatter `public.` qualifiers through queries.
- Pin the path in every function: `SET search_path = public, pg_temp` in the function definition; see [functions and procedures](functions-and-procedures.md).
- Schema-qualify object references inside `SECURITY DEFINER` functions even with a pinned path; they execute with the owner's privileges.
- Split into domain schemas only when one database genuinely hosts multiple domains; then qualify all cross-schema references explicitly.

## Avoid

- Do not create a parallel `app` schema for a single application; it adds path configuration everywhere for no isolation gain.
- Do not rely on `search_path` inside function bodies; the caller controls it unless pinned.
- Do not put application objects in extension-managed or catalog schemas.
- Do not set a custom `search_path` per role or per connection as a naming mechanism.

## Example

```sql
-- One-time database setup:
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

-- Every function definition pins its path; name resolution cannot be
-- hijacked. Body elided; full definitions live with their owner pages
-- (set_updated_at in triggers, normalize_email in functions).
CREATE FUNCTION set_updated_at() RETURNS trigger
LANGUAGE plpgsql
SET search_path = public, pg_temp
AS $$ ... $$;
```

## Exceptions

- Multi-domain databases: use one schema per domain (`billing`, `identity`), qualify cross-schema references, and grant per schema.
- Extensions that install into their own schema: leave them there; do not relocate their objects into `public`.
