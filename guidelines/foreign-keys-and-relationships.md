# Foreign Keys and Relationships

## Rule

Declare a foreign key for every reference between durable tables, with `ON DELETE RESTRICT` unless the child is a true composition owned by the parent.

## Why

Foreign keys make orphaned references impossible regardless of write path. `RESTRICT` makes deletes of referenced rows fail loudly instead of silently fanning out, keeping deletion behavior explicit in application code.

## Do

- Add a foreign key constraint on every `<referenced_singular>_id` column between durable tables.
- Default to `ON DELETE RESTRICT` so a delete with dependents fails until the application handles them.
- Use `ON DELETE CASCADE` only when child rows are meaningless without the parent (`orders` -> `order_items`).
- Use `ON DELETE SET NULL` rarely, only when the reference is genuinely optional, with a comment explaining why.
- Model self-referential trees with a nullable `parent_id` FK to the same table.
- Index every FK column; the rule and rationale live in [index basics](index-basics.md).
- Name FK constraints per [object naming](object-naming.md).

## Avoid

- Do not leave reference columns unconstrained because "the app guarantees it".
- Do not use `ON DELETE CASCADE` as a convenience for cleanup across aggregate boundaries; a cascade through business entities is silent data loss.
- Do not point foreign keys at non-unique columns.
- Do not create circular FK dependencies between tables; restructure or make one side deferrable with a documented reason.

## Example

```sql
CREATE TABLE orders (
  id uuid DEFAULT uuidv7() PRIMARY KEY,
  user_id uuid NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  -- Users own their orders but orders outlive user edits: RESTRICT.
  CONSTRAINT orders_user_id_fkey
    FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE RESTRICT
);

CREATE TABLE order_items (
  id uuid DEFAULT uuidv7() PRIMARY KEY,
  order_id uuid NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  -- Items are part of the order: composition, so CASCADE.
  CONSTRAINT order_items_order_id_fkey
    FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE
);

CREATE INDEX orders_user_id_idx ON orders (user_id);
CREATE INDEX order_items_order_id_idx ON order_items (order_id);
```

## Exceptions

- High-volume append-only event/log tables may hold soft references without FK constraints, with a documented reason; retention jobs should not block business-row deletes.
- Cross-database or cross-service references cannot be FKs; name the column normally and validate in the application.
