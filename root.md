# PostgreSQL Style Guide

Use this skill to apply the project's PostgreSQL style conventions while designing schemas, writing queries, authoring migrations, or configuring database access.

## Supporting Files

- [guidelines.md](guidelines.md) - index of PostgreSQL style policy pages. Load this for ordinary SQL and schema work, then load only the guideline pages relevant to the task.
- [workflows/safe-schema-migration.md](workflows/safe-schema-migration.md) - workflow for changing schemas on existing databases without downtime: expand/contract, concurrent indexes, staged constraints, and backfills.
- [workflows/new-database-setup.md](workflows/new-database-setup.md) - workflow for standing up a new database: schemas, roles, default privileges, and migration structure.
- [workflows/query-performance-investigation.md](workflows/query-performance-investigation.md) - workflow for diagnosing and fixing slow queries with EXPLAIN and index evaluation.
- [workflows/schema-and-query-review.md](workflows/schema-and-query-review.md) - workflow for reviewing or refactoring existing schemas, migrations, and queries.

## Routing Examples

| Task | Load |
| --- | --- |
| Create or alter a table on a live database | [workflows/safe-schema-migration.md](workflows/safe-schema-migration.md), [guidelines.md](guidelines.md) |
| Stand up a new database | [workflows/new-database-setup.md](workflows/new-database-setup.md), [guidelines.md](guidelines.md) |
| Investigate a slow query | [workflows/query-performance-investigation.md](workflows/query-performance-investigation.md), [guidelines.md](guidelines.md) |
| Review a migration or schema PR | [workflows/schema-and-query-review.md](workflows/schema-and-query-review.md), [guidelines.md](guidelines.md) |
| Design a new table | [guidelines.md](guidelines.md), object naming, primary keys, scalar types, constraints, standard columns |
| Choose a primary key or ID type | [guidelines.md](guidelines.md), primary keys and row identity |
| Model a status or category field | [guidelines.md](guidelines.md), enums/domains/lookup tables, constraints and NULL semantics |
| Decide between columns and jsonb | [guidelines.md](guidelines.md), JSONB/arrays/normalization, advanced indexes |
| Write a multi-step or reporting query | [guidelines.md](guidelines.md), CTEs, join style, aggregation and pagination |
| Write an upsert or bulk write | [guidelines.md](guidelines.md), DML/upserts/RETURNING |
| Add an index | [guidelines.md](guidelines.md), index basics, advanced indexes |
| Add a function, trigger, or view | [guidelines.md](guidelines.md), functions, triggers, views |
| Configure roles or grants | [guidelines.md](guidelines.md), roles/privileges/RLS |

## Core Behavior

- Keep the root router small; use guidelines and workflows for details.
- Prefer concrete PostgreSQL guidance over SQL tutorials.
- Enforce data integrity in the database; keep business logic in the application.
- Prefer normalized relational modeling; use `jsonb` deliberately, not by default.
- Prefer readable, decomposed queries; CTEs are the default tool for clarity.
- Treat migrations on existing databases as stricter than greenfield DDL.
- Treat guideline pages as policy; treat workflow pages as procedures.
- Ask one focused question only when required project context is missing.
