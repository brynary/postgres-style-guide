# PostgreSQL Style Guide Skill Outline

This file maps each packaged page to its decision-register owner. Detailed scope lives in the page itself; drafting rules live in [DRAFTING.md](DRAFTING.md), and the required page shape lives in [TEMPLATE.md](TEMPLATE.md).

The packaged skill uses [SKILL.md](../SKILL.md) as its router, [guidelines.md](../guidelines.md) as its policy index, focused pages under `guidelines/`, and procedures under `workflows/`.

## Guideline Map

| Area | Page | Decisions |
| --- | --- | --- |
| Foundations | [House style and Postgres philosophy](../guidelines/house-style-and-postgres-philosophy.md) | D1, D2 |
| Foundations | [Identifier casing and quoting](../guidelines/identifier-casing-and-quoting.md) | D3 |
| Foundations | [Object naming](../guidelines/object-naming.md) | D7-D9 |
| Foundations | [Schema layout and search_path](../guidelines/schema-layout-and-search-path.md) | D10, D11 |
| Foundations | [SQL formatting and comments](../guidelines/sql-formatting-and-comments.md) | D4-D6, D34 |
| Schema design | [Primary keys and row identity](../guidelines/primary-keys-and-row-identity.md) | D12, D13 |
| Schema design | [Foreign keys and relationships](../guidelines/foreign-keys-and-relationships.md) | D14, D15 |
| Schema design | [Scalar types](../guidelines/scalar-types.md) | D16-D18 |
| Schema design | [Temporal data and time zones](../guidelines/temporal-data-and-time-zones.md) | D19, D20 |
| Schema design | [JSONB, arrays, and normalization](../guidelines/jsonb-arrays-and-normalization.md) | D21, D22 |
| Schema design | [Enums, domains, and lookup tables](../guidelines/enums-domains-and-lookup-tables.md) | D23, D24 |
| Schema design | [Standard columns and row lifecycle](../guidelines/standard-columns-and-row-lifecycle.md) | D25-D27 |
| Constraints and indexes | [Constraints and NULL semantics](../guidelines/constraints-and-null-semantics.md) | D28, D29 |
| Constraints and indexes | [Index basics](../guidelines/index-basics.md) | D30, D32 |
| Constraints and indexes | [Advanced indexes](../guidelines/advanced-indexes.md) | D31 |
| Query style | [SELECT structure and join style](../guidelines/select-structure-and-join-style.md) | D33, D35 |
| Query style | [Subqueries, EXISTS, and LATERAL](../guidelines/subqueries-exists-and-lateral.md) | D36 |
| Query style | [CTEs and query decomposition](../guidelines/ctes-and-query-decomposition.md) | D37 |
| Query style | [Aggregation, window functions, and pagination](../guidelines/aggregation-window-functions-and-pagination.md) | D38 |
| Query style | [DML, upserts, and RETURNING](../guidelines/dml-upserts-and-returning.md) | D39, D40 |
| Database logic | [Functions and procedures](../guidelines/functions-and-procedures.md) | D41 |
| Database logic | [Views and materialized views](../guidelines/views-and-materialized-views.md) | D43 |
| Database logic | [Triggers](../guidelines/triggers.md) | D42 |
| Security | [Roles, privileges, and row-level security](../guidelines/roles-privileges-and-row-level-security.md) | D44, D45, D48 |

## Workflow Map

| Workflow | Scope | Decisions |
| --- | --- | --- |
| [Safe schema migration](../workflows/safe-schema-migration.md) | Live-database locks, staged constraints, concurrent indexes, backfills, expand/contract | D46, D47 |
| [New database setup](../workflows/new-database-setup.md) | Version, roles, grants, schemas, extensions, first migrations | D1, D10, D44, D48 |
| [Query performance investigation](../workflows/query-performance-investigation.md) | Measurement, plan reading, query rewrites, index verification | - |
| [Schema and query review](../workflows/schema-and-query-review.md) | Severity-ordered review against the relevant guideline pages | - |

## Deferred Topics

Add a dedicated page only when a real project need justifies it:

- Partitioning and full-text search.
- Locale-specific collation.
- `LISTEN`/`NOTIFY` and database queues.
- Connection pooling and application transaction posture.
- ORM-specific conventions.
- Logical replication, backups, and major-version upgrades.
