# SQL Formatting and Comments

## Rule

Write UPPERCASE keywords with lowercase identifiers and built-in functions, trailing commas, 2-space indentation, one clause per line in nontrivial statements, and meaningful table aliases.

## Why

A single mechanical layout makes agent-generated SQL diff-stable and reviewable. Keywords stand out without highlighting; simple indentation survives edits without re-alignment.

## Do

- UPPERCASE SQL keywords (`SELECT`, `FROM`, `WHERE`, `JOIN`, `ON`, `GROUP BY`); lowercase identifiers and built-in functions (`date_trunc`, `count`, `coalesce`).
- Start each clause keyword on its own line in nontrivial statements; indent continuation lines 2 spaces.
- Use trailing commas; one select-list item per line once the list does not fit on one line.
- Wrap lines around 100 characters.
- Alias tables with a short name derived from the table: `users` as `u`, `order_items` as `oi`; single letters are fine with one or two tables, banned in larger queries.
- Use `AS` for column aliases: `SUM(oi.quantity) AS total_quantity`.
- Comment with `--` line comments; use `/* */` only for multi-line file headers.
- Comment intent and non-obvious choices, not mechanics; document schema meaning in migrations and application code, not `COMMENT ON`.
- Keep one-line statements on one line: `SELECT count(*) FROM users` needs no layout.

## Avoid

- Do not use river alignment or column alignment that must be rebuilt on every edit.
- Do not use leading commas.
- Do not use `COMMENT ON`; catalog comments are unmaintained documentation in this house style.
- Do not commit commented-out SQL.
- Do not uppercase identifiers or built-in function names.
- Do not alias unless a query references more than one table or the alias genuinely shortens a long name.

## Example

```sql
SELECT
  usr.id,
  usr.email,
  SUM(oi.quantity * oi.unit_price) AS lifetime_value
FROM users usr
JOIN orders ord ON ord.user_id = usr.id
JOIN order_items oi ON oi.order_id = ord.id
WHERE ord.state = 'paid'
  AND ord.created_at >= date_trunc('year', now())
GROUP BY usr.id, usr.email
ORDER BY lifetime_value DESC, usr.id
LIMIT 20;
```

## Exceptions

- Generated or vendored SQL keeps its generator's formatting; do not hand-reformat it.
- psql meta-commands and ad hoc exploratory queries are exempt from layout rules.
