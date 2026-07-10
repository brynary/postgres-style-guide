# Schema and Query Review

Use this workflow when reviewing a migration, a schema design, or SQL changes in a pull request, or when refactoring existing database code toward the guidelines.

## Required Guidelines

Load [guidelines.md](../guidelines.md), then load the guideline pages matching what the change touches. For schema changes, always include the new-table page set from [SKILL.md](../SKILL.md)'s routing table:

- [Object naming](../guidelines/object-naming.md)
- [Primary keys and row identity](../guidelines/primary-keys-and-row-identity.md)
- [Foreign keys and relationships](../guidelines/foreign-keys-and-relationships.md)
- [Scalar types](../guidelines/scalar-types.md)
- [Constraints and NULL semantics](../guidelines/constraints-and-null-semantics.md)
- [Standard columns and row lifecycle](../guidelines/standard-columns-and-row-lifecycle.md)

And for query changes:

- [SELECT structure and join style](../guidelines/select-structure-and-join-style.md)
- [CTEs and query decomposition](../guidelines/ctes-and-query-decomposition.md)
- [DML, upserts, and RETURNING](../guidelines/dml-upserts-and-returning.md)

## Workflow

1. Identify what the change touches: DDL, queries, DML, database logic (functions/triggers/views), or grants. Load the matching guideline pages before reading the diff in detail.
2. For migrations against a live database, review safety first via the [safe schema migration](safe-schema-migration.md) workflow: lock levels, `CONCURRENTLY`, `NOT VALID`/`VALIDATE`, batched backfills, `lock_timeout`.
3. Review new tables as a unit against the schema guidelines: key strategy, column types, `NOT NULL` posture, named constraints, FK actions and indexes, lifecycle columns and trigger.
4. Review queries against the query-style guidelines: join style, qualification, decomposition, `SELECT *`, pagination shape, unqualified `UPDATE`/`DELETE`.
5. Review any function, trigger, or view against its guideline's sanctioned cases; flag business logic in the database and unpinned `search_path`.
6. Check consistency with the surrounding schema: names, patterns, and conventions should match neighbors unless the change deliberately migrates them.
7. Classify each finding by severity: correctness or data-loss risk, production-safety risk (locks, rewrites), convention violation, style nit. Lead with the first two.
8. For refactor work, change one convention at a time across the affected objects and route schema changes through the safe schema migration workflow; do not mix convention cleanup with behavior changes.
9. Confirm anything uncertain against the actual database (`\d table`, catalog queries) rather than assuming the diff shows the whole state.

## Review Checklist

- Every new FK has an index and an explicit `ON DELETE` action.
- Every constraint and index has the canonical suffix name; noncanonical generated names are overridden explicitly.
- No `serial`/`bigserial`, `gen_random_uuid()` primary keys, `varchar(n)`, `char(n)`, `money`, `timestamp without time zone`, `json`, or `CREATE DOMAIN` in new DDL.
- New columns are `NOT NULL` or the nullability is meaningful.
- Durable tables carry `created_at`/`updated_at` and the `set_updated_at` trigger.
- No unqualified `UPDATE`/`DELETE`; writes needing results use `RETURNING`.
- Migrations on live tables state their lock expectations and use the two-stage constraint pattern.
- New indexes cite the query pattern they serve.
- No business workflow logic in functions or triggers.

## Avoid

- Do not review style before safety on migrations; a well-named table rewrite still takes the site down.
- Do not demand guideline compliance from untouched legacy code in an unrelated change; file it as follow-up refactor work.
- Do not approve "temporary" deviations without a comment marking them and a contract step that removes them.
- Do not rewrite a working query during review for style alone without checking its plan on real data first.
