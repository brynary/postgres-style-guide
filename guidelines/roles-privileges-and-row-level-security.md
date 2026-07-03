# Roles, Privileges, and Row-Level Security

## Activation

Load this page when creating roles, granting privileges, configuring connections, or when tenant/row scoping questions come up.

## Rule

Run every database with the three-role topology — owner/migration role (DDL), app runtime role (DML only), read-only role — with deny-by-default grants to roles, and enforce row scoping in the application, not RLS.

## Why

An application that cannot `ALTER TABLE` cannot be injected into schema changes. Deny-by-default grants make access reviewable. App-layer scoping keeps row visibility in testable code instead of policy machinery every connection must configure correctly.

## Do

- Create three group roles per database:
  - `{app}_owner`: owns all objects; migrations connect as this role.
  - `{app}_rw`: `SELECT`/`INSERT`/`UPDATE`/`DELETE` on application tables; the app connects as (a login member of) this role.
  - `{app}_ro`: `SELECT` only; reporting, analytics, and humans connect through it.
- Grant privileges to group roles; login roles get access via membership, never direct grants.
- Set `ALTER DEFAULT PRIVILEGES FOR ROLE {app}_owner` so objects created by future migrations inherit the grants.
- Revoke world access once per database: `REVOKE CREATE ON SCHEMA public FROM PUBLIC;` per [schema layout and search_path](schema-layout-and-search-path.md).
- Point the read-only role at [views](views-and-materialized-views.md) when it should see masked or report-shaped data rather than raw tables.
- Enforce tenant and row scoping in the application query layer (`WHERE tenant_id = $1` via the framework's scoping mechanism).
- Review any `SECURITY DEFINER` function as part of this topology; see [functions and procedures](functions-and-procedures.md).

## Avoid

- Do not let the application connect as the object owner or a superuser.
- Do not grant privileges to individual login users; membership in group roles only.
- Do not use RLS; if a hard row-level isolation requirement arrives (compliance, direct third-party DB access), treat it as an architecture decision made outside these defaults.
- Do not scatter one-off `GRANT`s in application code or ad hoc sessions; grants live in migrations.
- Do not share one login role between the app and humans; humans go through `{app}_ro` (or their own audited logins).

## Example

```sql
-- One-time role topology for app "shop":
CREATE ROLE shop_owner NOLOGIN;
CREATE ROLE shop_rw NOLOGIN;
CREATE ROLE shop_ro NOLOGIN;

GRANT USAGE ON SCHEMA public TO shop_rw, shop_ro;

ALTER DEFAULT PRIVILEGES FOR ROLE shop_owner IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO shop_rw;
ALTER DEFAULT PRIVILEGES FOR ROLE shop_owner IN SCHEMA public
  GRANT SELECT ON TABLES TO shop_ro;
ALTER DEFAULT PRIVILEGES FOR ROLE shop_owner IN SCHEMA public
  GRANT USAGE ON SEQUENCES TO shop_rw;

-- Login roles are members, and get nothing directly:
CREATE ROLE shop_app LOGIN IN ROLE shop_rw;
CREATE ROLE shop_metabase LOGIN IN ROLE shop_ro;
```

## Exceptions

- Multi-service databases may add per-service `_rw` roles on top of the base topology when services need different table access; keep the grant matrix in migrations.
- Managed platforms (RDS, Cloud SQL) reserve superuser; their provided admin role substitutes for it in setup scripts.
