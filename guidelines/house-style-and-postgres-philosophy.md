# House Style and Postgres Philosophy

## Rule

Write readable, explicit SQL for PostgreSQL 18+: the database owns data integrity through constraints, the application owns business logic, and data is modeled relationally first.

## Why

Agent-written SQL drifts without a fixed posture. PostgreSQL supports many valid styles; these defaults remove improvisation so schemas, queries, and migrations stay consistent, reviewable, and safe across write paths.

## Do

- Assume PostgreSQL 18+ for new databases and new DDL; use modern features (`uuidv7()`, virtual generated columns, temporal constraints, `RETURNING OLD/NEW`) where pages call for them.
- Enforce data integrity in the database: `NOT NULL`, foreign keys, `CHECK` constraints, and unique constraints; see [constraints and NULL semantics](constraints-and-null-semantics.md).
- Keep business workflow logic in the application; database logic is limited to integrity, auditing, and derived data; see [triggers](triggers.md) and [functions and procedures](functions-and-procedures.md).
- Model core business data relationally with real columns and foreign keys; see [JSONB, arrays, and normalization](jsonb-arrays-and-normalization.md).
- Prefer clarity over cleverness in queries; decompose nontrivial queries; see [CTEs and query decomposition](ctes-and-query-decomposition.md).
- Treat schema changes to existing databases as production changes; follow the safe schema migration workflow.
- When a page marks a rule as version-gated, check the target database version before using it.

## Avoid

- Do not put business decisions, side effects, or workflow orchestration in database functions or triggers.
- Do not rely on application code alone for invariants the database can enforce cheaply.
- Do not reach for `jsonb`, arrays, or denormalization as a default modeling tool.
- Do not write clever single-statement SQL when a decomposed query says the same thing clearly.
- Do not use version-gated features without confirming the target version, and do not avoid them out of habit when PG18+ is confirmed.

## Example

```sql
-- Integrity in the database, logic in the application:
CREATE TABLE payments (
  id uuid DEFAULT uuidv7() PRIMARY KEY,
  order_id uuid NOT NULL REFERENCES orders (id) ON DELETE RESTRICT,
  amount numeric NOT NULL,
  state text NOT NULL DEFAULT 'pending',
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT payments_amount_check CHECK (amount > 0),
  CONSTRAINT payments_state_check CHECK (state IN ('pending', 'captured', 'refunded'))
);

-- Whether a payment MAY be refunded is a business decision: application code.
-- That a payment amount is positive is data integrity: database constraint.
```

## Exceptions

- Older target databases: keep these conventions but substitute the fallbacks named in each page's `Version Notes`.
- Analytics and reporting contexts may relax query-shape rules where a page explicitly says so; schema rules still apply.
