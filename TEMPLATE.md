# Guideline Page Template

Use this format for PostgreSQL style guide guideline pages.

```markdown
# Guideline Name

## Rule

One sentence the agent can follow by default.

## Why

Short rationale.

## Do

- Preferred patterns.
- Naming or DDL/query conventions.

## Avoid

- Common anti-patterns.
- Cases where agents usually overreach.

## Example

Small preferred SQL example.

## Exceptions

Narrow cases where the default can be broken.
```

Optional sections:

- `Activation`
- `Version Notes`
- `Migration Notes`
- `Security Notes`
- `Performance Notes`
- `Decision Points`

Use `Activation` for conditional or advanced guideline pages such as advanced indexes, triggers, row-level security, and materialized views. It should say when to load the page and when not to.

Use `Version Notes` when a rule depends on a PostgreSQL version (for example PG18 `uuidv7()`, virtual generated columns, or temporal constraints), stating the minimum version and the fallback for older targets.

Use `Migration Notes` when adopting the rule on an existing production table needs care (locks, rewrites, backfills); link to the safe schema migration workflow instead of restating it.
