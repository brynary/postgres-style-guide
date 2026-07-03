# Roles, Privileges, and Row-Level Security

## Activation

Load this page when creating roles, granting privileges, configuring connections, or when tenant/row scoping questions come up.

## Rule

Run every database with the three-role topology — owner/migration role (DDL), app runtime role (DML only), read-only role — with deny-by-default grants to roles, and enforce row scoping in the application, not RLS.

## Why

An application that cannot `ALTER TABLE` cannot be injected into schema changes. Deny-by-default grants make access reviewable. App-layer scoping keeps row visibility in testable code instead of policy machinery every connection must configure correctly.

## Do

- Create three group roles per database:
  - `{app}_owner`: owns the database and every object; a login role with exactly one client, the migration pipeline.
  - `{app}_rw`: `SELECT`/`INSERT`/`UPDATE`/`DELETE` on application tables; the app connects as (a login member of) this role.
  - `{app}_ro`: `SELECT` only; reporting, analytics, and humans connect through it.
- Create the database with `OWNER {app}_owner`; since PG15 only the database owner has `CREATE` on schema `public`, and migrations need it.
- Run every migration as `{app}_owner` and nothing else: `ALTER DEFAULT PRIVILEGES FOR ROLE {app}_owner` fires only for objects created by that role, so DDL run as any other role silently produces tables the app cannot read.
- Grant privileges to group roles; login roles get access via membership, never direct grants. (`{app}_owner` is the one login that holds privileges directly — by owning, not by grant.)
- Set `ALTER DEFAULT PRIVILEGES FOR ROLE {app}_owner` so objects created by future migrations inherit the grants, including `REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC`; PostgreSQL grants function execution to `PUBLIC` by default.
- Revoke world access once per database: `REVOKE CONNECT ON DATABASE {app} FROM PUBLIC;` and `REVOKE CREATE ON SCHEMA public FROM PUBLIC;` per [schema layout and search_path](schema-layout-and-search-path.md).
- Carve sensitive tables out of the blanket read grant: in the migration that creates a table holding credentials, tokens, or regulated PII, `REVOKE SELECT ON {table} FROM {app}_ro`; masked [views](views-and-materialized-views.md) are the sanctioned reporting surface over such tables.
- Carve audit tables out of the blanket write grant: `REVOKE UPDATE, DELETE ON {audit_table} FROM {app}_rw` in the migration that creates it, so the audit trail stays append-only even for a compromised app connection; see [triggers](triggers.md).
- Enforce tenant and row scoping in the application query layer (`WHERE tenant_id = $1` via the framework's scoping mechanism) — and remember it never applies to `{app}_ro` connections: on multi-tenant databases, human or BI access through `{app}_ro` is unscoped and must be a deliberate decision.
- Review any `SECURITY DEFINER` function as part of this topology; see [functions and procedures](functions-and-procedures.md).

## Avoid

- Do not let the application connect as the object owner or a superuser.
- Do not run DDL as any role other than `{app}_owner`; default privileges bind to the creating role.
- Do not grant privileges to individual login users; membership in group roles only.
- Do not use RLS; if a hard row-level isolation requirement arrives (compliance, direct third-party DB access), treat it as an architecture decision made outside these defaults.
- Do not scatter one-off `GRANT`s in application code or ad hoc sessions; grants live in migrations.
- Do not share one login role between the app and humans; humans go through `{app}_ro` (or their own audited logins).

## Example

```sql
-- One-time role topology for app "shop" (run as the platform admin):
CREATE ROLE shop_owner LOGIN;  -- exactly one client: the migration pipeline
CREATE ROLE shop_rw NOLOGIN;
CREATE ROLE shop_ro NOLOGIN;

CREATE DATABASE shop OWNER shop_owner;

-- Connected to the shop database:
REVOKE CONNECT ON DATABASE shop FROM PUBLIC;
GRANT CONNECT ON DATABASE shop TO shop_owner, shop_rw, shop_ro;
GRANT USAGE ON SCHEMA public TO shop_rw, shop_ro;

-- Objects created by future migrations (which run as shop_owner)
-- inherit these grants; DDL run as any other role would not.
ALTER DEFAULT PRIVILEGES FOR ROLE shop_owner IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO shop_rw;
ALTER DEFAULT PRIVILEGES FOR ROLE shop_owner IN SCHEMA public
  GRANT SELECT ON TABLES TO shop_ro;
ALTER DEFAULT PRIVILEGES FOR ROLE shop_owner IN SCHEMA public
  GRANT USAGE ON SEQUENCES TO shop_rw;
ALTER DEFAULT PRIVILEGES FOR ROLE shop_owner IN SCHEMA public
  REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

-- Login roles are members, and get nothing directly:
CREATE ROLE shop_app LOGIN IN ROLE shop_rw;
CREATE ROLE shop_metabase LOGIN IN ROLE shop_ro;

-- Later, in the migration that creates a sensitive table:
REVOKE SELECT ON api_tokens FROM shop_ro;

-- And in the migration that creates an audit table:
REVOKE UPDATE, DELETE ON order_state_changes FROM shop_rw;
```

## Exceptions

- Multi-service databases may add per-service `_rw` roles on top of the base topology when services need different table access; keep the grant matrix in migrations.
- Managed platforms (RDS, Cloud SQL) reserve superuser; their provided admin role substitutes for it in setup scripts, and needs `GRANT {app}_owner TO {admin}` before it can create the database with that owner or run the `FOR ROLE {app}_owner` default-privilege statements.
