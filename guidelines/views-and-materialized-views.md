# Views and Materialized Views

## Activation

Apply this page when creating or reviewing a view or materialized view, or when deciding whether an analytics report should become one.

## Rule

Create views sparingly — stable read models, column masking, and read-only analytics reports exposed to multiple surfaces — and materialized views only with a documented refresh strategy.

## Why

Views are a public contract over the schema: cheap to create, expensive to evolve, and stacked views hide query cost. The sanctioned cases share one property: multiple consumers need the same defined result shape.

## Do

- Define a view when a read-only analytics report is consumed by more than one surface (app, admin, BI); the view is the single definition of the report.
- Use views for column masking: exposing a safe subset of a sensitive table to a restricted role. A masking view runs with its owner's privileges (the default): do not set `security_invoker`, grant the restricted role `SELECT` on the view only, keep its base-table access revoked per [roles, privileges, and row-level security](roles-privileges-and-row-level-security.md), and review the view like a `SECURITY DEFINER` boundary.
- Set `security_invoker = true` on views whose consumers already hold the base-table privileges, so the querying role's own permissions apply. The two patterns are mutually exclusive per view: a masking view with `security_invoker` either fails with permission errors or forces the base-table grant it exists to avoid.
- Alias every output column explicitly; no `SELECT *` in a view body, where column changes underneath silently change the contract (see [SELECT structure and join style](select-structure-and-join-style.md)).
- Write view bodies with the same CTE decomposition rules as queries.
- Use a materialized view only when the underlying query is measured-too-slow for live reads; document the refresh strategy (what refreshes it, how often, acceptable staleness) in the migration.
- Create the unique index every materialized view needs for `REFRESH MATERIALIZED VIEW CONCURRENTLY`, and refresh concurrently.

## Avoid

- Do not use views as a general query-reuse mechanism; application-side query composition owns that.
- Do not stack views on views; one level deep.
- Do not create a materialized view without a refresh plan; it is a cache with no invalidation.
- Do not write through updatable views; write to tables.

## Example

```sql
-- One report definition, consumed by app dashboard, admin, and BI.
-- All consumers hold base-table SELECT, so security_invoker applies
-- (a masking view would instead rely on owner privileges):
CREATE VIEW monthly_revenue_by_plan
WITH (security_invoker = true) AS
WITH paid_orders AS (
  SELECT o.id, o.total, o.created_at, s.plan
  FROM orders o
  JOIN subscriptions s ON s.user_id = o.user_id
  WHERE o.state = 'paid'
)
SELECT
  date_trunc('month', po.created_at) AS month,
  po.plan AS plan,
  count(*) AS order_count,
  sum(po.total) AS revenue
FROM paid_orders po
GROUP BY month, po.plan;

-- Materialized only after this is measured too slow live:
-- CREATE MATERIALIZED VIEW ... ; CREATE UNIQUE INDEX ... (month, plan);
-- REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_revenue_by_plan;
```

## Exceptions

- Compatibility views that preserve an old shape mid-migration are legitimate and temporary; the contract step of the safe schema migration workflow removes them.
- BI-tool-owned views living in a dedicated reporting schema follow that tool's conventions.
