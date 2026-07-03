# Object Naming

## Rule

Name tables as plural nouns, columns by fixed conventions (`id`, `<referenced_singular>_id`, `*_at`, `is_*`), and name every constraint and index explicitly using the PostgreSQL default suffix scheme.

## Why

Systematic names make agent-generated DDL predictable: any object's name can be derived from what it is, and migrations that reference constraints or indexes behave identically in every environment.

## Do

- Name tables as plural snake_case nouns: `users`, `orders`, `order_items`.
- Name junction tables for the relationship when a natural name exists (`memberships`, `enrollments`); otherwise join the two table names in alphabetical order and pluralize the last word (`categories_products`).
- Name the primary key column `id`.
- Name foreign key columns `<referenced_singular>_id`: `user_id` references `users`; a second reference to the same table gets a role prefix (`approver_id`, also referencing `users`).
- Suffix timestamps with `_at` (`created_at`, `confirmed_at`) and dates with `_on` or a plain noun (`due_on`, `birth_date`).
- Prefix booleans with `is_` or `has_` (`is_active`, `has_signature`).
- Prefer descriptive column names over generic ones: `year_founded`, not `year`.
- Name constraints and indexes explicitly, matching the PostgreSQL auto-generated pattern:
  - Primary key: `{table}_pkey`
  - Foreign key: `{table}_{column}_fkey`
  - Unique constraint or unique index: `{table}_{columns}_key`
  - Ordinary index: `{table}_{columns}_idx`
  - Check constraint: `{table}_{column}_check` (or `{table}_{rule}_check` for multi-column rules)
- Name triggers `{table}_{action}_trigger` (`users_set_updated_at_trigger`) and their functions after the behavior (`set_updated_at`).
- Name views as plural nouns describing the result rows (`overdue_invoices`); name materialized views the same way.

## Avoid

- Do not rely on auto-generated constraint or index names; creation order can differ across environments.
- Do not use `tbl_`, `col_`, `fk_`, `idx_` prefixes or other Hungarian notation.
- Do not name a junction table `a_to_b` or `a_b_join`.
- Do not encode types into names (`name_text`, `count_int`).
- Do not name columns after their table (`user_name` inside `users`); the qualification is the table's job.

## Example

```sql
CREATE TABLE order_items (
  id uuid DEFAULT uuidv7() PRIMARY KEY,
  order_id uuid NOT NULL,
  product_id uuid NOT NULL,
  quantity bigint NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT order_items_order_id_fkey
    FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
  CONSTRAINT order_items_product_id_fkey
    FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT,
  CONSTRAINT order_items_quantity_check CHECK (quantity > 0),
  CONSTRAINT order_items_order_id_product_id_key UNIQUE (order_id, product_id)
);

CREATE INDEX order_items_product_id_idx ON order_items (product_id);
```

## Exceptions

- Names that would exceed 63 bytes: shorten the column list portion while keeping the table name and suffix intact.
- Legacy tables with established singular names: match the surrounding convention within that table rather than mixing styles.
