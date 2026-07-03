# Topic Terrain Map — A PostgreSQL 18 Style Guide "Skill" for AI Coding Agents

## TL;DR
- The style guide should be organized into **9 sections and 24 one-page topics**, each carrying an explicit "Decisions to make" list that separates *settled community consensus* (e.g., `timestamptz` over `timestamp`, `text` over `varchar(n)`, identity over `serial`, `jsonb` over `json`, explicit JOIN syntax) from *genuine preference choices* the user must arbitrate (singular vs. plural table names, UUIDv7 vs. bigint keys, CTE decomposition thresholds, leading vs. trailing commas, soft vs. hard delete, enum vs. lookup vs. CHECK).
- PostgreSQL 18 (released September 25, 2025) and 17 introduce authoring-relevant features that should shape topic coverage: **`uuidv7()`** (timestamp-ordered UUIDs), **virtual generated columns as the new default**, **temporal constraints** (`WITHOUT OVERLAPS` / `PERIOD`), **`RETURNING OLD`/`NEW`**, **`NOT NULL NOT VALID`** for safer migrations, and PG17's **`JSON_TABLE`** and **`MERGE ... RETURNING`**.
- The largest clusters of decisions are **schema design/data types** and **query decomposition style**; the report flags **19 genuine preference decision points** as a pre-drafting checklist and recommends excluding/merging ~5 candidate topics (partitioning, full-text search, RLS depth, extensions, LISTEN/NOTIFY) to stay within the ~25-page budget.

## Key Findings

**The consensus/preference split is the organizing principle.** A large fraction of "SQL style" questions are already settled in the well-regarded PostgreSQL community sources — the "Don't Do This" wiki, Simon Holywell's SQL style guide, GitLab's migration guides, and vendor engineering blogs (Crunchy Data, Cybertec, EnterpriseDB, AWS). The skill's value for an AI agent is (a) encoding those settled defaults so the agent stops making common mistakes, and (b) recording the user's chosen side on the genuinely contested questions so output is consistent. Each topic page should therefore lead with settled defaults, then flag the preference choices.

**PG17/18 features change what "good modern SQL" looks like.** Verified against official release notes and documentation (postgresql.org/docs/18/):
- **`uuidv7()`** — Per the official PostgreSQL 18 press release, "PostgreSQL 18 also adds UUIDv7 generation through the uuidv7() function, letting you generate random UUIDs that are timestamp-ordered to support better caching strategies. PostgreSQL 18 includes uuidv4() as an alias for gen_random_uuid()." The `uuidv7()` function also accepts an optional `shift interval` argument, and `uuid_extract_timestamp()`/`uuid_extract_version()` operate on v7 values. This materially changes the UUID-vs-bigint decision because v7 largely eliminates the index-locality penalty of random v4 UUIDs.
- **Virtual generated columns** — Per the PG18 release notes, "Virtual generated columns that compute their values during read operations. This is now the default for generated columns." Virtual columns cannot be indexed and cannot have a user-defined type (docs, verbatim: "A virtual generated column cannot have a user-defined type, and the generation expression … must not reference user-defined functions or types"); `STORED` remains for indexable/hot-read cases and is the only kind supported in logical replication.
- **Temporal constraints** — PG18 adds `PRIMARY KEY`/`UNIQUE ... WITHOUT OVERLAPS` and `FOREIGN KEY ... PERIOD`. Per CREATE TABLE docs, "The WITHOUT OVERLAPS column must have a range or multirange type," and the constraint is enforced via a GiST exclusion constraint (e.g., `UNIQUE (id, valid_at WITHOUT OVERLAPS)` behaves like `EXCLUDE USING GIST (id WITH =, valid_at WITH &&)`). `ON DELETE`/`ON UPDATE` actions are not supported for temporal foreign keys.
- **`RETURNING OLD`/`NEW`** — PG18 lets INSERT/UPDATE/DELETE/MERGE return both old and new row values via `old.`/`new.` aliases (docs example: `RETURNING name, old.price AS old_price, new.price AS new_price`).
- **`NOT NULL NOT VALID`** — PG18 allows adding a `NOT NULL` constraint as `NOT VALID` and validating it separately. Per Bytebase's PG18 review, the pattern is `ALTER TABLE table_name ADD CONSTRAINT constraint_name NOT NULL (column) NOT VALID;` followed by a separate `VALIDATE`, enabling "adding NOT NULL without a full table scan" — safer than the old `CHECK (col IS NOT NULL) NOT VALID` workaround.
- **PG17**: `JSON_TABLE()`, SQL/JSON query functions (`JSON_EXISTS`, `JSON_QUERY`, `JSON_VALUE`), `MERGE ... RETURNING` and `MERGE` on updatable views, and predefined roles like `pg_maintain`.

**CTE materialization behavior is a hard dependency for the CTE topic.** Per Tom Lane's PG12 commit 608b167f (Feb 16, 2019): "By default, we will inline them into the outer query (removing the optimization fence) if they are called just once. If they are called more than once, we will keep the old behavior by default, but the user can override this … by specifying NOT MATERIALIZED." This means the user's stated preference — "introduce CTEs once a query gets large, for clarity" — is now essentially free of the old performance penalty for single-use, non-recursive, side-effect-free CTEs, and the guide can endorse it with a caveat about `MATERIALIZED` when a fence is deliberately wanted.

## Details — Proposed Topic List (24 topics in 9 sections)

### Section A — Foundations & Formatting

**1. Formatting & Layout Conventions.** Keyword capitalization, indentation, line breaks, alignment, and clause structure for queries and DDL. Establishes the house style an agent applies to every statement.
- *Decisions:* **[PREFERENCE]** Leading vs. trailing commas. **[PREFERENCE]** "River" alignment (Holywell style) vs. simple left-aligned/2- or 4-space indentation (the river style is criticized on Hacker News as high-maintenance when editing queries). **[PREFERENCE]** Max line length / when to break clauses. **[CONSENSUS]** Uppercase SQL keywords, lowercase identifiers.

**2. Identifiers, Quoting & Case Folding.** snake_case, unquoted lowercase, avoiding reserved words, no double-quoted mixed-case names. Explains PostgreSQL's lowercase folding of unquoted identifiers and why quoted CamelCase is an anti-pattern.
- *Decisions:* **[CONSENSUS]** snake_case, all-lowercase, never rely on double-quoted identifiers. **[CONSENSUS]** Avoid reserved words (`user`, `order`, `date`) as names. **[PREFERENCE]** Identifier length policy (Postgres truncates at 63 bytes) and abbreviation rules.

**3. Comments & Self-Documentation.** When/how to comment SQL and using `COMMENT ON` for tables/columns to embed a data dictionary in the catalog.
- *Decisions:* **[PREFERENCE]** `--` vs. `/* */`. **[PREFERENCE]** Whether `COMMENT ON` documentation is mandatory. **[CONSENSUS]** Comment intent, not mechanics; don't commit commented-out SQL.

### Section B — Naming

**4. Table & Schema Naming.** Naming rules for tables, junction/join tables, and schemas; whether to use `public` or dedicated schemas.
- *Decisions:* **[PREFERENCE — flagship]** Singular vs. plural table names — Holywell's guide prefers the collective/plural term ("staff instead of employees"), while many "default convention" cheat-sheets enforce singular for clarity; PostgreSQL enforces neither. **[PREFERENCE]** Junction table naming (`a_b` vs. descriptive). **[CONSENSUS]** No `tbl_`/Hungarian prefixes. **[PREFERENCE]** Dedicated schemas per module vs. single `public`.

**5. Column Naming.** Column names, PK columns (`id` vs. `table_id`), FKs (`referenced_table_singular_id`), boolean prefixes (`is_`/`has_`), timestamp columns (`created_at`/`updated_at`).
- *Decisions:* **[PREFERENCE]** Bare `id` PK vs. `tablename_id` PK. **[CONSENSUS]** FK named `<referenced_table_singular>_id`. **[PREFERENCE]** `created_at`/`updated_at` vs. `_time` suffixes. **[CONSENSUS]** Boolean `is_`/`has_` prefixes; descriptive over generic (`year_founded` not `year`); avoid reserved system column names.

**6. Constraint & Index Naming.** Suffixes/prefixes for PK, FK, unique, check, index; whether to always name constraints explicitly.
- *Decisions:* **[CONSENSUS]** Always name constraints explicitly — relying on auto-generated names causes brittle migrations and cross-environment inconsistency. **[PREFERENCE]** PostgreSQL default suffix scheme (`_pkey`, `_key`, `_fkey`, `_check`, `_idx`) vs. custom prefixes (`fk_`, `uniq_`, `chk_`, `idx_`). **[PREFERENCE]** Index name pattern `idx_{table}_{cols}` vs. `{table}_{cols}_idx`.

### Section C — Schema Design & Data Types

**7. Choosing Scalar Data Types.** Settled defaults: `text` over `varchar(n)`, `timestamptz` over `timestamp`, `numeric` for money, `bigint`/identity over `serial`, no `char(n)`, no `money`.
- *Decisions:* **[CONSENSUS]** `text` (or `varchar` w/o length) over `varchar(n)`; use CHECK for length limits. **[CONSENSUS]** `timestamptz` over `timestamp`. **[CONSENSUS]** `numeric` for exact/money, never `float`/`money`. **[CONSENSUS]** Avoid `char(n)`. **[PREFERENCE — narrow]** Whether to ever use `timestamp`/local-time-plus-zone for future wall-clock events (the documented exception in the "Don't Do This" discussion, e.g., appointments whose UTC offset may change with tzdata updates).

**8. Primary Key Strategy: UUID vs. bigint identity.** The single most consequential schema decision. `bigint GENERATED ALWAYS AS IDENTITY` vs. `uuid` (v4 vs. v7), surrogate vs. natural keys, split internal-PK/external-ID patterns.
- *Decisions:* **[CONSENSUS]** Prefer `GENERATED ALWAYS AS IDENTITY` over `serial`/`bigserial` (SQL-standard, insert-safe, cleaner schema, portable). **[PREFERENCE — flagship]** bigint identity vs. UUID keys. **[CONSENSUS, conditional]** If UUIDs, use v7 not v4: in the Scaling Postgres ep. 302 benchmark, inserting 1M rows took 375s for UUID v4 versus an identical 290s for both UUID v7 and bigint ("UUIDv7 performance is so good, it basically matched bigint"), and v4 index leaf pages are ~40% larger than bigint. **[CAVEAT to record]** v7's time-ordering concentrates concurrent inserts on the rightmost B-tree leaf; under very high write concurrency this "rightmost leaf contention" can *hurt* (kkm-mako.com cites a Spring Boot case where a v4→v7 switch dropped throughput from ~12,000 to under 3,000 inserts/sec), so v4 or partitioning/fillfactor tuning can be more stable at extreme concurrency. **[PREFERENCE]** Surrogate vs. natural keys. **[PREFERENCE]** Dual-column pattern (bigint internal PK + UUID public ID) for opaque, non-enumerable external identifiers.

**9. Normalization vs. JSON/Array Denormalization.** When to model relationally vs. reach for `jsonb`/arrays. OLTP-appropriate JSONB use (variable/sparse attributes, external API payloads, settings, feature flags) vs. anti-patterns.
- *Decisions:* **[PREFERENCE — flagship]** Normalized-first vs. JSONB-for-flexibility default posture. **[CONSENSUS]** `jsonb` over `json` (binary, normalized, indexable; `json` also lacks an equality operator, breaking `SELECT DISTINCT`). **[CONSENSUS]** Prefer one `jsonb` column holding an array over a `jsonb[]` column. **[CONSENSUS]** Keep frequently-queried/joined attributes out of JSONB — the planner keeps no statistics on JSONB fields (Heap documented a ~2000× slowdown from a bad estimate), TOAST adds retrieval overhead >2KB, any field update rewrites the whole value, and repeated keys can more than double storage. **[PREFERENCE]** Hybrid rule: fixed hot attributes as real columns, variable tail in JSONB. **[PREFERENCE]** When arrays are acceptable vs. a child table.

**10. Enums: Native Type vs. Lookup Table vs. CHECK.** Three ways to constrain a column to a closed value set, with lifecycle tradeoffs.
- *Decisions:* **[PREFERENCE — flagship]** Native `ENUM` vs. lookup/reference table (FK) vs. `text` + `CHECK IN (...)`. Characterize: appending to an ENUM is a cheap metadata-only `ALTER TYPE` and transactional, but *removing/renaming* values requires a workaround or a full-table rewrite under an ACCESS EXCLUSIVE lock (Cybertec, Close.com, ivanluminaria all document weekend-migration pain); CHECK is flexible for stable short sets but changing values means DROP/ADD constraint (can be done `NOT VALID` then `VALIDATE` under a lighter lock); a lookup table is most flexible (add labels, ordering, i18n, runtime activation) at the cost of joins and possibly worse row estimates. **[GUIDANCE]** Default to a lookup table when the vocabulary evolves or needs attributes; ENUM/CHECK when truly static (Cybertec: "An enum type is the best solution if you never have to remove values").

**11. Columns: Ordering, Defaults, Generated & Identity.** Column-level DDL: order, defaults, `GENERATED ALWAYS AS IDENTITY`, PG18 virtual vs. stored generated columns.
- *Decisions:* **[PREFERENCE]** Column ordering (PK first; audit columns last; alphabetization to reduce schema churn). **[CONSENSUS]** Identity over serial. **[PREFERENCE]** Virtual (PG18 default, compute-on-read, no index, no UDT) vs. STORED (indexable, hot-read) generated columns. **[GUIDANCE]** Prefer STORED when the column is indexed or on a hot read path; virtual otherwise (write-heavy, large/rarely-read derived values).

### Section D — Constraints & Integrity

**12. Constraints & Referential Integrity.** PK, unique, NOT NULL, CHECK, exclusion, FK design, FK referential actions, PG18 temporal constraints. NULL-handling philosophy lives here.
- *Decisions:* **[PREFERENCE — flagship]** `ON DELETE CASCADE` vs. `RESTRICT`/`NO ACTION` default. **[PREFERENCE]** NULL philosophy — how aggressively to require `NOT NULL`; NULL vs. sentinel/empty-string. **[CONSENSUS]** Always index FK columns. **[PREFERENCE]** Whether to always add explicit CHECKs for domain rules (positive amounts, `updated_at >= created_at`). **[NEW — PG18]** Whether to adopt temporal `WITHOUT OVERLAPS`/`PERIOD` constraints for validity-period tables. **[CONSENSUS]** Define constraints in-database, not only in the app.

**13. Soft Delete vs. Hard Delete.** Whether rows are physically deleted or flagged (`deleted_at`), and effects on uniqueness, querying, FKs.
- *Decisions:* **[PREFERENCE — flagship]** Soft delete vs. hard delete (vs. archive table). **[CONSENSUS, conditional]** If soft-deleting, enforce uniqueness with a *partial unique index* `WHERE deleted_at IS NULL` (the idiomatic Postgres solution; the `COALESCE(deleted_at,'1970-01-01')` composite is the fallback for engines without partial indexes). **[PREFERENCE]** How deleted rows are hidden: `active_*` views, RLS policy, or app-level filter. **[PREFERENCE]** Purge/retention strategy.

### Section E — Indexes

**14. Index Types & Design.** B-tree default plus GIN (jsonb/arrays/FTS), GiST (ranges/exclusion), BRIN, hash; when each applies in OLTP. Composite column ordering and covering (`INCLUDE`) indexes.
- *Decisions:* **[CONSENSUS]** B-tree default; GIN for `jsonb`/array containment; GiST for exclusion/temporal. **[PREFERENCE]** Whether covering/`INCLUDE` indexes are house style. **[PREFERENCE]** Composite index column-order convention. *(Deep EXPLAIN/perf tuning is out of scope; this topic is about naming, shape, and correctness-relevant choices.)*

**15. Partial, Expression & Unique Indexes.** Partial indexes (soft-delete uniqueness, hot subsets), expression indexes, unique-constraint-vs-unique-index choice.
- *Decisions:* **[CONSENSUS]** Use partial unique indexes for conditional uniqueness. **[PREFERENCE]** `UNIQUE` constraint (named, shows in `\d`, referenceable by FK) vs. standalone `CREATE UNIQUE INDEX` (supports partial/expression). **[PREFERENCE]** Expression indexes vs. stored generated columns for computed lookups.

### Section F — Query Style

**16. JOIN Style.** Explicit ANSI `JOIN` syntax, join ordering/readability, alias conventions.
- *Decisions:* **[CONSENSUS]** Explicit `JOIN ... ON` over comma joins / implicit joins in `WHERE`. **[PREFERENCE]** Table alias policy (short aliases vs. full names; `AS` for column aliases). **[PREFERENCE]** Join ordering (driving table first) for readability.

**17. CTEs vs. Subqueries vs. Long Queries.** The user's flagship stylistic preference: decompose large queries with CTEs for clarity. Covers PG12 inlining and when to force `MATERIALIZED`.
- *Decisions:* **[PREFERENCE — flagship, user-stated]** Monolithic vs. CTE-decomposed queries and the size/complexity threshold to introduce CTEs. **[CONSENSUS/GUIDANCE]** Since PG12, single-use non-recursive side-effect-free CTEs are inlined (no automatic fence), so favoring CTEs for readability is generally safe. **[GUIDANCE]** Use `MATERIALIZED` when a fence is intended; `NOT MATERIALIZED` to force inlining. **[PREFERENCE]** CTE vs. derived-table subquery when both read equally well.

**18. Subqueries: Correlated, LATERAL, EXISTS vs. IN.** Scalar/correlated subqueries, `LATERAL` joins, `EXISTS` vs. `IN` vs. `ANY` (incl. NULL-safety of `NOT IN`).
- *Decisions:* **[CONSENSUS]** Prefer `EXISTS`/`NOT EXISTS` over `IN`/`NOT IN`, especially `NOT IN` (NULL trap). **[PREFERENCE]** When to use `LATERAL` vs. a CTE/derived table. **[PREFERENCE]** `= ANY(array)` vs. `IN (list)`.

**19. DML & Upserts.** INSERT/UPDATE/DELETE conventions, `INSERT ... ON CONFLICT` vs. `MERGE`, `RETURNING` (incl. PG18 `OLD`/`NEW`), always-qualified UPDATE/DELETE.
- *Decisions:* **[PREFERENCE]** `INSERT ... ON CONFLICT` (idiomatic Postgres upsert) vs. `MERGE` (SQL-standard, PG15+, `RETURNING`/`merge_action()` and updatable-view support in PG17). **[CONSENSUS]** Always `WHERE`-qualify UPDATE/DELETE; use `RETURNING` instead of a follow-up SELECT. **[NEW — PG18]** Adopt `RETURNING old.*/new.*` where useful.

### Section G — Procedural & Server-Side Logic

**20. Functions & Procedures: Language, Volatility & Scope.** *(Merges functions and stored procedures into one page.)* When to write server-side logic at all, SQL vs. PL/pgSQL, `VOLATILE`/`STABLE`/`IMMUTABLE` labeling, and functions vs. procedures.
- *Decisions:* **[PREFERENCE]** How much logic belongs in the DB vs. the app; whether stored procedures are used at all. **[GUIDANCE]** Prefer plain SQL functions over PL/pgSQL when the logic is a single query (inlinable, simpler); reserve procedures (`CALL`, transaction control) for multi-transaction/batch maintenance. **[CONSENSUS]** Always label volatility with the strictest correct category — mislabeling as `IMMUTABLE` risks stale cached-plan results (a hazard with prepared statements/PL/pgSQL); a function reading tables is `STABLE`, not `IMMUTABLE`. **[PREFERENCE]** New-style `BEGIN ATOMIC` bodies vs. string bodies.

**21. Triggers vs. Application Logic.** When triggers are appropriate (audit, derived data, integrity that can't be a constraint) vs. app logic; trigger naming/patterns; audit-trigger vs. application-level auditing.
- *Decisions:* **[PREFERENCE — flagship]** Trigger-based vs. application-level auditing/derived data. Characterize: DB triggers guarantee coverage regardless of write path but are hard to test/debug, add write amplification, and complicate bulk migrations (Pydantic Logfire migrated audit logging *out* of triggers for exactly these reasons); app-level is testable/flexible but bypassable and easy to forget. **[CONSENSUS]** If auditing in-DB, implement via triggers + trigger functions writing to a shadow/audit table, not scattered app code. **[PREFERENCE]** Trigger naming convention and `BEFORE` vs. `AFTER` defaults. **[GUIDANCE]** Avoid business logic in triggers where a constraint or generated column suffices; note PG18 now runs AFTER triggers as the role active when the event was queued.

**22. Views: Regular, Updatable & Materialized.** Regular views for encapsulation/security, updatable-view rules, and (rarely, in OLTP) materialized views for cached rollups.
- *Decisions:* **[CONSENSUS]** Regular views suit OLTP (encapsulation, access control); materialized views are for reporting/rollups and need a refresh strategy (and `REFRESH ... CONCURRENTLY` requires a unique index). **[PREFERENCE]** View naming (`v_`/`mv_` prefixes vs. none). **[PREFERENCE]** Whether to expose updatable views (and use `MERGE`/`INSTEAD OF` triggers on them). **[PREFERENCE]** Whether materialized views are in scope for this OLTP codebase at all.

### Section H — Security & Access Control

**23. Roles, Privileges, Ownership & Grants.** Least-privilege role design (group roles + login roles), object ownership, `ALTER DEFAULT PRIVILEGES`, locking down `public`/`PUBLIC`, a separate migration role, and schema-qualified names vs. `search_path`.
- *Decisions:* **[CONSENSUS]** Least privilege; the app never connects as superuser or object owner. **[CONSENSUS]** Group roles (`readonly`/`readwrite`) with membership, not per-user grants; assign to per-service login roles. **[CONSENSUS]** `REVOKE CREATE ON SCHEMA public FROM PUBLIC`; use `ALTER DEFAULT PRIVILEGES` so future objects are covered. **[PREFERENCE]** Separate migration/DDL role vs. app role owning objects. **[PREFERENCE]** Schema-qualify object names vs. rely on a set `search_path`. **[PREFERENCE]** Whether to use PG14+ `pg_read_all_data`/`pg_write_all_data` predefined roles.

### Section I — Migrations & Evolution

**24. Safe Migrations & Schema Evolution.** Naming/organizing migration files, backward-compatible (expand/contract) change patterns, and safe-DDL rules distilled from strong_migrations, GitLab, and safe-pg-migrations. Locking is discussed only insofar as it dictates safe conventions.
- *Decisions:* **[CONSENSUS]** Multi-step expand→backfill→contract for breaking changes; adding a column with a non-volatile default is safe since PG11 (no table rewrite); backfill in batches. **[CONSENSUS]** `CREATE INDEX CONCURRENTLY` outside a transaction. **[CONSENSUS]** Add constraints as `NOT VALID` then `VALIDATE CONSTRAINT` separately — PG18 extends this to `NOT NULL` (`ADD CONSTRAINT ... NOT NULL (col) NOT VALID` then `VALIDATE`). **[CONSENSUS]** Set a short `lock_timeout` for migrations; use a separate DDL role. **[PREFERENCE]** Column-drop protocol (ignore-in-app, then drop across releases). **[PREFERENCE]** Migration file naming/versioning scheme and whether down-migrations are required. **[PREFERENCE]** Whether a strong_migrations-style linter is mandated.

## Consolidated Decision Checklist

### A. Settled consensus — encode as defaults (agent should just do these)
1. Uppercase keywords, lowercase snake_case identifiers; never rely on quoted mixed-case names.
2. Avoid reserved words as identifiers.
3. `text` (or unbounded `varchar`) over `varchar(n)`; length limits via CHECK.
4. `timestamptz` over `timestamp`.
5. `numeric` for money/exact decimals; never `float`/`money`; avoid `char(n)`.
6. `GENERATED ALWAYS AS IDENTITY` over `serial`/`bigserial`.
7. `jsonb` over `json`; prefer one `jsonb` array column over `jsonb[]`; keep queried/joined attributes out of JSONB.
8. If using UUID keys, use v7 (`uuidv7()`), not v4 (barring extreme write-concurrency contention — see topic 8 caveat).
9. Name all constraints/indexes explicitly.
10. Index all foreign-key columns.
11. Explicit ANSI `JOIN ... ON`; no implicit/comma joins.
12. Prefer `EXISTS`/`NOT EXISTS` over `IN`/`NOT IN` (NULL safety).
13. Always `WHERE`-qualify UPDATE/DELETE; use `RETURNING` over a follow-up SELECT.
14. Label function volatility with the strictest correct category.
15. Enforce integrity in-database (constraints), not only in the app.
16. Least-privilege roles; app never runs as superuser/owner; lock down `PUBLIC`/`public`; use `ALTER DEFAULT PRIVILEGES`.
17. Safe-migration rules: `CREATE INDEX CONCURRENTLY`; `NOT VALID` + `VALIDATE`; batched backfills; short `lock_timeout`; expand/contract for breaking changes.
18. Partial unique index `WHERE deleted_at IS NULL` if soft-deleting.
19. Regular views for OLTP; materialized views only for rollups with a refresh plan.

### B. Genuine preference choices — user must decide before drafting
1. Singular vs. plural table names.
2. Bare `id` vs. `tablename_id` primary-key column name.
3. Default constraint-naming scheme (Postgres default suffixes vs. custom prefixes).
4. Leading vs. trailing commas.
5. "River" alignment vs. simple indentation; max line length.
6. `--` vs. `/* */` comments; whether `COMMENT ON` is mandatory.
7. bigint identity vs. UUID primary keys (and whether to use the dual internal/external ID pattern).
8. Surrogate vs. natural keys.
9. Normalized-first vs. JSONB-for-flexibility default posture.
10. Enum type vs. lookup table vs. `text` + CHECK for closed value sets.
11. `ON DELETE CASCADE` vs. `RESTRICT`/`NO ACTION` default.
12. NULL-handling philosophy (how aggressively to require NOT NULL).
13. Soft delete vs. hard delete (and purge/retention policy).
14. Virtual vs. STORED default for generated columns.
15. Monolithic vs. CTE-decomposed queries and the complexity threshold (user leans toward CTEs for clarity).
16. `INSERT ... ON CONFLICT` vs. `MERGE` for upserts.
17. Trigger-based vs. application-level auditing/derived data.
18. How much logic lives in the DB (functions/procedures/triggers) vs. the app; whether stored procedures are used at all.
19. Schema-qualified names vs. reliance on `search_path`; separate migration role; view naming prefixes; migration file naming and whether down-migrations/linters are required.

## Recommendations

**Stage 1 — Lock the preference decisions first.** Before drafting any page, have the user walk section B (19 items) and record a one-line ruling for each. These rulings are the actual differentiator of *this* skill versus a generic guide; the agent can already infer section A. Prioritize the six flagship choices (table pluralization, PK type, normalization posture, enum strategy, soft-delete, CTE threshold) because they cascade into many pages.

**Stage 2 — Draft the consensus-heavy pages fast.** Topics 1–3, 7, 14–16, 23, 24 are mostly settled; draft them as prescriptive defaults with short rationale and one good/bad example each, within the one-page budget.

**Stage 3 — Draft the contested pages as "decision + rationale + chosen default."** Topics 4, 8, 9, 10, 12, 13, 17, 21 should each state the options, the tradeoff, and then the user's chosen house rule in an unmistakable callout so the agent applies it deterministically.

**Stage 4 — Bake in PG18/17 currency.** Each relevant page should note the modern feature and when to use it: `uuidv7()` (topic 8), virtual generated columns (11), temporal constraints (12), `RETURNING OLD/NEW` and `MERGE` (19), `JSON_TABLE` (9), `NOT NULL NOT VALID` (24). Verify every version-specific claim against release notes before publishing.

**Benchmarks that would change the topic set:** If the workload later adds analytics/reporting, promote materialized views and partitioning to full topics. If multi-tenant isolation becomes a requirement, promote RLS from a mention to its own page. If the team standardizes on an ORM, the currently out-of-scope ORM-interaction topic would need to be added back. Keep the guide at ≤25 pages; adding a topic should force merging or cutting another.

## Caveats
- **Scope discipline:** ORM conventions and EXPLAIN/performance tuning are explicitly out of scope; several findings (index internals, JSONB statistics, UUID locality) touch performance only where it changes a *correctness or style* default. Keep those mentions brief in the guide.
- **Preference items are genuinely contested:** For the flagship choices there is no single "right" answer — sources actively disagree (Holywell endorses plural tables while many convention cheat-sheets mandate singular; the "Don't Do This" wiki's `serial`/`varchar(n)` entries are debated in the linked Hacker News threads). The guide should pick a side and state it, not present false consensus.
- **UUIDv7 is not universally faster:** The v7 recommendation holds for typical monolithic OLTP apps, but time-ordered keys concentrate concurrent inserts on the rightmost B-tree leaf; at very high write concurrency this can reduce throughput versus v4. Record this caveat rather than presenting v7 as unconditionally best.
- **Version specificity:** `uuidv7()`, virtual generated columns as default, temporal constraints, `RETURNING OLD/NEW`, and `NOT NULL NOT VALID` are PG18; `JSON_TABLE`, SQL/JSON query functions, and `MERGE ... RETURNING` are PG17; CTE inlining dates to PG12. One nuance verified during research: the "virtual generated columns cannot be indexed" restriction is enforced by the server (error string "indexes on virtual generated columns are not supported") but is not stated as prose on the PG18 generated-columns documentation page — the docs verbatim confirm only that such columns "cannot have a user-defined type."
- **Excluded/merged topics:** Partitioning, full-text search, Row-Level Security depth, extension management, and LISTEN/NOTIFY were considered and recommended for exclusion or brief mention to respect the ~25-topic cap; functions and stored procedures are merged into one page (topic 20), bringing the final count to 24.
- **Suffix schemes and auto-generated names:** Some cited naming cheat-sheets recommend adopting PostgreSQL's *default* auto-suffixes while also insisting on *explicit* naming — the guide should resolve this by naming constraints explicitly using names that match the conventional suffix pattern.