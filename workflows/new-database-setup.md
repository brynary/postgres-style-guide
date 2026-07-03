# New Database Setup

Use this workflow when standing up a new PostgreSQL database for an application: schemas, roles, privileges, extensions, and the first migrations.

## Required Guidelines

Load [guidelines.md](../guidelines.md), then load these guideline pages as needed:

- [House style and Postgres philosophy](../guidelines/house-style-and-postgres-philosophy.md)
- [Schema layout and search_path](../guidelines/schema-layout-and-search-path.md)
- [Roles, privileges, and row-level security](../guidelines/roles-privileges-and-row-level-security.md)
- [Object naming](../guidelines/object-naming.md)
- [Primary keys and row identity](../guidelines/primary-keys-and-row-identity.md)
- [Standard columns and row lifecycle](../guidelines/standard-columns-and-row-lifecycle.md)

## Workflow

1. Confirm the PostgreSQL version; target PG18+. Record the version assumption where the project documents its stack.
2. Create the database with `UTF8` encoding and, unless the project has a locale requirement, a deterministic default collation.
3. Lock down the schema: keep application objects in `public` and run `REVOKE CREATE ON SCHEMA public FROM PUBLIC;`.
4. Create the three-role topology (`{app}_owner`, `{app}_rw`, `{app}_ro`), grants, and `ALTER DEFAULT PRIVILEGES`, per the roles guideline; create login roles as members.
5. Configure the migration tool to connect as `{app}_owner` and the application as the `{app}_rw` login member; verify the app connection cannot run DDL.
6. Install only extensions the project needs now, each in its own migration with a comment saying what uses it.
7. Create the shared `set_updated_at()` trigger function before the first table migration so tables can attach it immediately.
8. Write the first table migrations following the schema-design guidelines: `uuidv7()` keys, lifecycle columns with triggers, FKs with indexes, `NOT NULL` defaults, named constraints.
9. Seed lookup tables in migrations, not by hand.
10. Set up the safe-migration guardrails from day one: `lock_timeout` in the migration template and the safe schema migration workflow linked from the project docs, so habits do not change when the database goes live.
11. Verify the topology before first deploy: connect as each role and confirm it can do exactly what it should (owner: DDL; rw: DML only; ro: SELECT only).

## Avoid

- Do not develop and deploy as a superuser or the owner role from the application.
- Do not install extensions speculatively.
- Do not hand-create objects outside migrations, even during setup; the first environment rebuild will miss them.
- Do not defer the role topology "until production"; retrofitting grants across an accumulated schema is the painful version.
- Do not copy configuration from another project without checking the version assumptions and extension list.
