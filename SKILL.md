---
name: postgres-style-guide
description: Apply this PostgreSQL style guide when designing schemas, writing queries, authoring migrations, or configuring database roles for this project. Covers PostgreSQL 18 conventions, naming and formatting, keys and identity, data types, jsonb and normalization, constraints, indexes, join and CTE style, DML and upserts, functions, triggers, views, roles and grants, and safe schema migrations.
---

# PostgreSQL Style Guide

Use this skill to apply the project's PostgreSQL style conventions while designing schemas or writing SQL.

## First Steps

1. Load [root.md](root.md).
2. Identify whether the request is ordinary SQL/schema work or a workflow.
3. For ordinary SQL/schema work, load [guidelines.md](guidelines.md), then only the relevant guideline pages.
4. For schema changes to an existing database, load [workflows/safe-schema-migration.md](workflows/safe-schema-migration.md).
5. For new database setup, load [workflows/new-database-setup.md](workflows/new-database-setup.md).
6. For slow-query diagnosis, load [workflows/query-performance-investigation.md](workflows/query-performance-investigation.md).
7. For schema or query review work, load [workflows/schema-and-query-review.md](workflows/schema-and-query-review.md).
8. Apply the loaded rules directly. If required project context is missing, ask one focused question before broad changes.

[root.md](root.md) carries the routing examples and core behavior rules; follow it rather than duplicating its guidance here.
