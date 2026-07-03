# PostgreSQL Style Guide Skill Outline

This outline is for a PostgreSQL style guide packaged as an AI-agent skill. The skill should not teach SQL or re-explain the PostgreSQL manual. It should give agents clear defaults, exceptions, and small examples for the decisions they face while writing schemas, queries, migrations, and database code.

Target size: 24 guideline pages plus 4 workflow pages. Each guideline should fit on one focused markdown page.

## Drafting Instructions

Use [DRAFTING.md](DRAFTING.md) for drafting order, scope, and page-writing guidance.

## Page Template

Use [TEMPLATE.md](TEMPLATE.md) for every guideline page.

## Packaged Skill Shape

The final skill should follow the progressive-disclosure pattern in [SKILL.md](SKILL.md) and [guidelines.md](guidelines.md): a small root router, focused guideline pages, and task workflows under `workflows/`. Planning files and research reports should not be part of the packaged skill by default.

## Decision Register

Use [DECISIONS.md](DECISIONS.md) to resolve style decisions before drafting final policy pages.

## Guideline Map

### Foundations

1. **House Style and Postgres Philosophy**
   - Set the overall posture: readability-first SQL, integrity enforced in the database, business logic in the application, normalized-first modeling, and the assumed PostgreSQL version.
   - Decision points: D1, D2.

2. **Identifier Casing and Quoting**
   - Cover snake_case lowercase identifiers, the near-ban on quoted identifiers, identifier folding, reserved words, and the 63-byte limit.
   - Decision points: D3.

3. **Object Naming**
   - Cover table naming and plurality, junction tables, column naming, `id` and `<singular>_id` conventions, boolean and timestamp column names, and explicit names with stable suffixes for constraints, indexes, functions, triggers, and views.
   - Decision points: D7, D8, D9.

4. **Schema Layout and search_path**
   - Cover schema organization, `public` schema policy, when to schema-qualify references, and safe `search_path` handling in application SQL, functions, and migrations.
   - Decision points: D10, D11.

5. **SQL Formatting and Comments**
   - Cover keyword casing, comma placement, indentation, line breaks, alias conventions, column qualification, `--` vs `/* */`, and the no-`COMMENT ON` policy.
   - Decision points: D4, D5, D6, D34.

### Schema Design and Data Types

6. **Primary Keys and Row Identity**
   - Cover the default PK type, `uuidv7()` vs `bigint GENERATED ALWAYS AS IDENTITY`, the `serial` ban, surrogate vs natural keys, and external identifier exposure.
   - Decision points: D12, D13.

7. **Foreign Keys and Relationships**
   - Cover FK requirements, `ON DELETE`/`ON UPDATE` actions, composite and self-referential FKs, deferrability, and when soft references are tolerable.
   - Decision points: D14, D15.

8. **Scalar Types**
   - Cover `text` vs `varchar(n)`, the `char(n)` and `money` bans, `numeric` for exact values, integer widths, and booleans.
   - Decision points: D16, D17, D18.

9. **Temporal Data and Time Zones**
   - Cover `timestamptz` policy, `date`, `interval`, the narrow `timestamp without time zone` exception, and range types for validity periods.
   - Decision points: D19, D20.

10. **JSONB, Arrays, and Normalization**
    - Cover the normalized-first default, when `jsonb` is appropriate, `jsonb` vs `json`, keeping hot attributes as real columns, and when arrays beat child tables.
    - Decision points: D21, D22.

11. **Enums, Domains, and Lookup Tables**
    - Cover closed value sets: `text` plus `CHECK` as the default, lookup tables for rich or large sets, native enums only for truly static sets, and the ban on domain types.
    - Decision points: D23, D24.

12. **Standard Columns and Row Lifecycle**
    - Cover `created_at`/`updated_at` conventions and maintenance, column defaults, identity columns, virtual vs stored generated columns, and soft delete vs hard delete with partial-unique-index implications.
    - Decision points: D25, D26, D27.

### Constraints and Indexes

13. **Constraints and NULL Semantics**
    - Cover the `NOT NULL` default posture, `CHECK` constraints for domain rules, `UNIQUE` with `NULLS NOT DISTINCT`, exclusion constraints, and PG18 temporal constraints (`WITHOUT OVERLAPS`, `PERIOD`).
    - Decision points: D28, D29.

14. **Index Basics**
    - Cover the default indexing doctrine: index FKs and unique business keys, avoid speculative indexes, B-tree defaults, index naming, and unique constraint vs unique index.
    - Decision points: D30, D32.

15. **Advanced Indexes**
    - Cover partial, expression, multicolumn, covering (`INCLUDE`), and GIN indexes; `jsonb` operator classes; and multicolumn ordering rules.
    - Decision points: D31.

### Query Style

16. **SELECT Structure and Join Style**
    - Cover explicit `JOIN ... ON`, the comma-join and `NATURAL JOIN` bans, `ON` vs `USING`, column qualification in multi-table queries, and the `SELECT *` policy.
    - Decision points: D33, D35.

17. **Subqueries, EXISTS, and LATERAL**
    - Cover `EXISTS` for semi-joins, the `NOT IN` null trap, `= ANY` vs `IN`, correlated subqueries, and when `LATERAL` improves clarity.
    - Decision points: D36.

18. **CTEs and Query Decomposition**
    - Cover the clarity-first CTE default, decomposition thresholds, CTE inlining since PG12, and deliberate `MATERIALIZED`/`NOT MATERIALIZED` use.
    - Decision points: D37.

19. **Aggregation, Window Functions, and Pagination**
    - Cover `GROUP BY` style, window functions over self-joins, explicit `ORDER BY` with `LIMIT`, and keyset vs offset pagination.
    - Decision points: D38.

20. **DML, Upserts, and RETURNING**
    - Cover `INSERT ... ON CONFLICT` vs `MERGE`, `RETURNING` instead of follow-up reads, PG18 `RETURNING OLD/NEW`, WHERE-qualified `UPDATE`/`DELETE`, and bulk change patterns.
    - Decision points: D39, D40.

### Database Logic

21. **Functions and Procedures**
    - Cover the minimal-database-logic default, SQL functions vs PL/pgSQL, volatility labeling, `SECURITY INVOKER` vs `SECURITY DEFINER`, and when procedures are justified.
    - Decision points: D41.

22. **Views and Materialized Views**
    - Cover when views earn their place, column aliasing, `security_invoker`, materialized views with refresh plans, and `REFRESH ... CONCURRENTLY` requirements.
    - Decision points: D43.

23. **Triggers**
    - Cover the sanctioned trigger roles (audit tables, derived data such as `updated_at` and counters), the ban on business workflow logic in triggers, and preferring constraints and generated columns where they can express the rule.
    - Decision points: D42.

### Security

24. **Roles, Privileges, and Row-Level Security**
    - Cover the three-role topology (owner/migration, app runtime, read-only), deny-by-default grants, `ALTER DEFAULT PRIVILEGES`, locking down `PUBLIC`, and the avoid-RLS posture (app-layer scoping instead).
    - Decision points: D44, D45.

## Workflow Map

1. **Safe Schema Migration**
   - Procedure for zero-downtime schema changes: expand/contract, `CREATE INDEX CONCURRENTLY`, `NOT VALID` then `VALIDATE`, batched backfills, `lock_timeout`, and column-drop protocol.
   - Decision points: D46, D47.

2. **New Database Setup**
   - Procedure for standing up a new database: schemas, role topology, default privileges, baseline extensions, and initial migration structure.
   - Decision points: D1, D10, D44.

3. **Query Performance Investigation**
   - Procedure for diagnosing slow queries: `EXPLAIN (ANALYZE, BUFFERS)`, reading plans, index evaluation, and verifying fixes without cargo-cult indexing.

4. **Schema and Query Review**
   - Procedure for reviewing or refactoring existing schemas, migrations, and queries against the guidelines.

## Topics Folded In

These are important, but probably do not need standalone pages in v1 unless the target databases depend on them heavily:

- Partitioning: fold a threshold note into index basics or the migration workflow; add a page only when a real large-table need appears.
- Full-text search: fold into advanced indexes; add a page only if search features are built.
- Collation and locale: fold a note into scalar types; add a page for multi-locale text handling if needed.
- Extensions policy: fold into new database setup.
- LISTEN/NOTIFY and queues: add a page only if the application uses them.
- Connection pooling and transaction posture: application-side concern; add only if agents write connection handling.
- ORM interaction: out of scope until a specific ORM is standardized.
- Logical replication, backup, and major version upgrades: operational concerns; fold minimal notes into the migration workflow.
- Deep EXPLAIN and performance tuning: kept to the performance investigation workflow, not guideline pages.
