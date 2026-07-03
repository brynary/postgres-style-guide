# Guidelines

Load this file for PostgreSQL style policy, then load only the guideline pages needed for the task.

Guideline pages are policy. Do not load every guideline page by default.

## Foundations

- [House style and Postgres philosophy](guidelines/house-style-and-postgres-philosophy.md) - load for overall posture: integrity in the database, logic in the application, normalized-first modeling, and version assumptions.
- [Identifier casing and quoting](guidelines/identifier-casing-and-quoting.md) - load when creating any named object; covers snake_case, quoting bans, reserved words, and length limits.
- [Object naming](guidelines/object-naming.md) - load when naming tables, columns, constraints, indexes, functions, triggers, or views.
- [Schema layout and search_path](guidelines/schema-layout-and-search-path.md) - load when choosing schemas, qualifying references, or handling `search_path`.
- [SQL formatting and comments](guidelines/sql-formatting-and-comments.md) - load for keyword casing, commas, indentation, aliases, and `COMMENT ON`.

## Schema Design and Data Types

- [Primary keys and row identity](guidelines/primary-keys-and-row-identity.md) - load when choosing PK types, `uuidv7()` vs identity columns, or natural vs surrogate keys.
- [Foreign keys and relationships](guidelines/foreign-keys-and-relationships.md) - load when adding references, choosing `ON DELETE` actions, or modeling hierarchies.
- [Scalar types](guidelines/scalar-types.md) - load when choosing string, numeric, integer, or boolean column types.
- [Temporal data and time zones](guidelines/temporal-data-and-time-zones.md) - load when adding timestamps, dates, intervals, or validity periods.
- [JSONB, arrays, and normalization](guidelines/jsonb-arrays-and-normalization.md) - load when deciding between relational columns, `jsonb`, and arrays.
- [Enums, domains, and lookup tables](guidelines/enums-domains-and-lookup-tables.md) - load when modeling status fields, categories, or reusable scalar validation.
- [Standard columns and row lifecycle](guidelines/standard-columns-and-row-lifecycle.md) - load for `created_at`/`updated_at`, defaults, generated columns, and soft vs hard delete.

## Constraints and Indexes

- [Constraints and NULL semantics](guidelines/constraints-and-null-semantics.md) - load for `NOT NULL` policy, `CHECK` constraints, uniqueness, and temporal constraints.
- [Index basics](guidelines/index-basics.md) - load when adding ordinary indexes, indexing FKs, or choosing unique constraint vs unique index.
- [Advanced indexes](guidelines/advanced-indexes.md) - load for partial, expression, multicolumn, covering, or GIN indexes.

## Query Style

- [SELECT structure and join style](guidelines/select-structure-and-join-style.md) - load when writing joins, qualifying columns, or deciding on `SELECT *`.
- [Subqueries, EXISTS, and LATERAL](guidelines/subqueries-exists-and-lateral.md) - load for semi-joins, `NOT IN` traps, `ANY`, and `LATERAL`.
- [CTEs and query decomposition](guidelines/ctes-and-query-decomposition.md) - load when structuring nontrivial queries or considering materialization.
- [Aggregation, window functions, and pagination](guidelines/aggregation-window-functions-and-pagination.md) - load for `GROUP BY`, ranking, ordering, and pagination.
- [DML, upserts, and RETURNING](guidelines/dml-upserts-and-returning.md) - load when writing `INSERT`/`UPDATE`/`DELETE`, upserts, `MERGE`, or `RETURNING`.

## Database Logic

- [Functions and procedures](guidelines/functions-and-procedures.md) - load when writing database functions; covers language choice, volatility, and security modes.
- [Views and materialized views](guidelines/views-and-materialized-views.md) - load when adding views or materialized views and their refresh strategies.
- [Triggers](guidelines/triggers.md) - load when a trigger is proposed; covers the minimal-trigger doctrine and the narrow valid cases.

## Security

- [Roles, privileges, and row-level security](guidelines/roles-privileges-and-row-level-security.md) - load when configuring roles, grants, default privileges, or RLS.

## Routing Notes

- For schema changes on existing databases, load [workflows/safe-schema-migration.md](workflows/safe-schema-migration.md) before individual DDL guidelines.
- For new database setup, load [workflows/new-database-setup.md](workflows/new-database-setup.md) before individual setup guidelines.
- For slow queries, load [workflows/query-performance-investigation.md](workflows/query-performance-investigation.md) before adding indexes.
- For review or refactor work, load [workflows/schema-and-query-review.md](workflows/schema-and-query-review.md) first.
- For new tables, always include object naming, primary keys, constraints, and standard columns.
- For anything touching `SECURITY DEFINER`, grants, or multi-tenant data, include roles/privileges/RLS.
- For advanced topics like triggers, materialized views, or RLS, load the page only when the task directly needs it.
