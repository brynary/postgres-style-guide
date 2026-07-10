# Roles, Privileges, and Row-Level Security

## Activation

Load this page when creating roles, granting privileges, configuring connections, or deciding how tenant rows are scoped.

## Rule

Use an owner/migration role, an app DML role, and a read-only role; grant by role with deny-by-default privileges, and enforce row scoping in the application rather than RLS.

## Why

Separating DDL from runtime access limits injection impact, and centralized grants make access reviewable.

## Do

- Create three roles per database:
  - `{app}_owner`: login owner used only by the migration pipeline.
  - `{app}_rw`: no-login group role with application-table DML.
  - `{app}_ro`: no-login group role with read-only reporting access.
- Create the database with `OWNER {app}_owner` and run every migration as that role; default privileges apply only to objects created by the named owner.
- Give application and human login roles access through group membership, never direct grants.
- Revoke `PUBLIC` access and configure future-object grants once per database:
  - `REVOKE CONNECT ON DATABASE {app} FROM PUBLIC`
  - `REVOKE CREATE ON SCHEMA public FROM PUBLIC`
  - `ALTER DEFAULT PRIVILEGES FOR ROLE {app}_owner ...`
  - `REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC`
- Override blanket grants in the table's migration: remove `{app}_ro` access to sensitive tables and `UPDATE`/`DELETE` access by `{app}_rw` to audit tables.
- Set `statement_timeout` and a short `idle_in_transaction_session_timeout` on each runtime *login* role. Never set them on `{app}_owner` or database-wide; long jobs may override them per session.
- Scope tenant and row access in application queries. Read-only connections remain unscoped, so multi-tenant human or BI access must be an explicit decision.
- Review `SECURITY DEFINER` functions with [functions and procedures](functions-and-procedures.md).

## Avoid

- Do not connect the application as the owner or a superuser.
- Do not run DDL as any role except `{app}_owner`.
- Do not grant privileges directly to individual login roles.
- Do not use RLS under this guide's defaults; hard database-side isolation is a separate architecture decision.
- Do not put one-off grants in application code or ad hoc sessions.
- Do not share a login between applications and humans.

## Example

```sql
-- Run as the platform administrator.
CREATE ROLE shop_owner LOGIN;
CREATE ROLE shop_rw NOLOGIN;
CREATE ROLE shop_ro NOLOGIN;
CREATE DATABASE shop OWNER shop_owner;

-- Connected to shop:
REVOKE CONNECT ON DATABASE shop FROM PUBLIC;
GRANT CONNECT ON DATABASE shop TO shop_owner, shop_rw, shop_ro;
GRANT USAGE ON SCHEMA public TO shop_rw, shop_ro;

ALTER DEFAULT PRIVILEGES FOR ROLE shop_owner IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO shop_rw;
ALTER DEFAULT PRIVILEGES FOR ROLE shop_owner IN SCHEMA public
  GRANT SELECT ON TABLES TO shop_ro;
ALTER DEFAULT PRIVILEGES FOR ROLE shop_owner IN SCHEMA public
  GRANT USAGE ON SEQUENCES TO shop_rw;
ALTER DEFAULT PRIVILEGES FOR ROLE shop_owner IN SCHEMA public
  REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
```

The [new database setup workflow](../workflows/new-database-setup.md) owns login creation, timeout values, and verification order.

## Version Notes

- On PG17+, also set `transaction_timeout` on runtime login roles. Older targets rely on `statement_timeout` and `idle_in_transaction_session_timeout`.

## Exceptions

- Multi-service databases may add per-service `_rw` roles when services need different table access.
- On managed platforms, use the provider's admin role for setup and grant it `{app}_owner` before owner-scoped operations.
