# Safe Schema Migration

Use this workflow when changing the schema of an existing database that serves traffic: adding or dropping columns, adding constraints or indexes, changing types, or backfilling data.

## Required Guidelines

Load [guidelines.md](../guidelines.md), then load these guideline pages as needed:

- [Object naming](../guidelines/object-naming.md)
- [Constraints and NULL semantics](../guidelines/constraints-and-null-semantics.md)
- [Index basics](../guidelines/index-basics.md)
- [Advanced indexes](../guidelines/advanced-indexes.md)
- [Standard columns and row lifecycle](../guidelines/standard-columns-and-row-lifecycle.md)

Greenfield setup with no traffic can use plain DDL; this workflow's rules exist because of live locks.

## Workflow

1. Classify the change: additive (new table, new nullable column, new index), constraining (new constraint, `NOT NULL`, type narrowing), or breaking (rename, drop, type change, split/merge).
2. Use the project's framework-native migration tool and file conventions; keep each migration one deliberate step.
3. Set a short `lock_timeout` (for example `5s`) at the top of every migration so blocked DDL fails fast instead of queueing behind long transactions; retry rather than wait.
4. For additive changes:
   - `ADD COLUMN` with a constant or `STABLE` default (`now()`) is safe — no rewrite since PG11, though every existing row receives the same evaluated value. Truly volatile defaults (`uuidv7()`, `gen_random_uuid()`) force a rewrite on large tables: add the column, then set the default, backfill, then constrain.
   - Create every index on an existing table with `CREATE INDEX CONCURRENTLY`, outside a transaction; check for `INVALID` indexes after a failed run and drop them with `DROP INDEX CONCURRENTLY`.
5. For constraining changes, use the two-stage pattern:
   - Add the constraint `NOT VALID` (FK, `CHECK`, and on PG18 `NOT NULL`).
   - Backfill or fix violating rows in batches.
   - `VALIDATE CONSTRAINT` separately; it takes only a light lock.
6. For backfills:
   - Batch by key range (a few thousand rows per statement), committing between batches.
   - Run backfills as data migrations or scripts, not inside the DDL transaction.
   - Throttle if replication lag or lock waits climb.
   - Decide trigger behavior explicitly: a table-wide backfill bumps every row's `updated_at` (re-syncing any downstream consumer keyed on it) and fires audit triggers per row. Either accept that and warn consumers, or disable the trigger for the run — documented and restored in the same migration.
7. For breaking changes, use expand/contract across releases:
   - Expand: add the new column/table/shape alongside the old; dual-write from the application (or a temporary sync trigger, commented and removed at contract).
   - Migrate: backfill old data into the new shape; verify counts and spot-check values.
   - Contract: switch reads, stop dual-writing, then drop the old shape in a later release once no deployed code references it.
8. To drop a column: remove all application references in one release, mark it ignored in the ORM if applicable, and `DROP COLUMN` in a later release.
9. Before running against production: state the expected lock level and duration for each statement, and test the migration against a production-sized copy when the table is large.
10. After running: confirm constraint validity (`\d` shows no `NOT VALID` leftovers, no `INVALID` indexes) and that the application error rate is clean.

## Version Notes

- `NOT NULL ... NOT VALID` requires PostgreSQL 18. On PG12-17, add `CHECK (col IS NOT NULL) NOT VALID`, `VALIDATE CONSTRAINT`, then `SET NOT NULL` (which uses the validated check to skip the table scan), then drop the redundant check.

## Avoid

- Do not run `CREATE INDEX` (non-concurrent), full-table `UPDATE`, or `VALIDATE`-at-add on large live tables.
- Do not batch multiple risky DDL statements in one transaction; each holds its locks until the transaction ends.
- Do not rename columns or tables in place on a live system; that is a breaking change and takes the expand/contract path.
- Do not change a column's type in place when it forces a rewrite; add a new column and migrate.
- Do not leave `NOT VALID` constraints or `INVALID` indexes behind; validate or drop them in the same change series.
- Do not skip `lock_timeout` because the table "is small"; a lock queue behind an idle transaction blocks reads on any table.
