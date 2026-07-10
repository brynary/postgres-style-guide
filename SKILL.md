---
name: postgres-style-guide
description: Apply this PostgreSQL style guide when designing schemas, writing queries, authoring migrations, or configuring database roles for this project. Covers PostgreSQL 18 conventions, naming and formatting, keys and identity, data types, jsonb and normalization, constraints, indexes, join and CTE style, DML and upserts, functions, triggers, views, roles and grants, and safe schema migrations. Also use when investigating slow queries or reviewing schemas, migrations, and SQL changes.
---

# PostgreSQL Style Guide

Apply the loaded policy pages directly.

## Routing

### Workflows

| Task | Load |
| --- | --- |
| Change a live database schema | [safe migration workflow](workflows/safe-schema-migration.md) |
| Stand up a new database | [database setup workflow](workflows/new-database-setup.md) |
| Investigate a slow query | [performance workflow](workflows/query-performance-investigation.md) |
| Review schema, migration, or query changes | [review workflow](workflows/schema-and-query-review.md) |

### Policy Fast Paths

| Task | Load |
| --- | --- |
| Design a new table | [object naming](guidelines/object-naming.md), [primary keys](guidelines/primary-keys-and-row-identity.md), [foreign keys](guidelines/foreign-keys-and-relationships.md), [scalar types](guidelines/scalar-types.md), [constraints](guidelines/constraints-and-null-semantics.md), [standard columns](guidelines/standard-columns-and-row-lifecycle.md) |
| Choose a primary key or ID type | [primary keys and row identity](guidelines/primary-keys-and-row-identity.md) |
| Model a status or category | [enums/domains/lookups](guidelines/enums-domains-and-lookup-tables.md), [constraints](guidelines/constraints-and-null-semantics.md) |
| Choose columns, JSONB, or arrays | [JSONB and normalization](guidelines/jsonb-arrays-and-normalization.md), [advanced indexes](guidelines/advanced-indexes.md) |
| Write a multi-step or reporting query | [CTEs](guidelines/ctes-and-query-decomposition.md), [join style](guidelines/select-structure-and-join-style.md), [aggregation and pagination](guidelines/aggregation-window-functions-and-pagination.md) |
| Write an upsert or bulk write | [DML and upserts](guidelines/dml-upserts-and-returning.md) |
| Add an index | [index basics](guidelines/index-basics.md), plus [advanced indexes](guidelines/advanced-indexes.md) for partial, expression, multicolumn, covering, GIN, JSONB, array, or range indexes |
| Add a database function | [functions and procedures](guidelines/functions-and-procedures.md) |
| Add a trigger | [triggers](guidelines/triggers.md) |
| Add a view or materialized view | [views and materialized views](guidelines/views-and-materialized-views.md) |
| Configure roles, grants, or RLS | [roles, privileges, and RLS](guidelines/roles-privileges-and-row-level-security.md) |
| Other PostgreSQL policy work | [guideline index](guidelines.md) |

## Core Behavior

- Workflows own multi-step procedures and route to their policy pages.
- Fast paths load only the directly linked owner pages.
- Use the guideline index only when no workflow or fast path matches.
- Select conditional pages using task descriptions in this router, the guideline index, or workflow routing.
- After loading a conditional page, apply it only when its `Activation` section matches.
- Treat live-database migrations as stricter than greenfield DDL.
- Prefer concrete PostgreSQL guidance over SQL tutorials.
- Ask one focused question only when required project context is missing.
