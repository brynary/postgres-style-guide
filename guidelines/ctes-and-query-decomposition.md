# CTEs and Query Decomposition

## Rule

Decompose any query with more than one level of nesting or more than one logical step into sequential named CTEs, each one comprehensible unit.

## Why

Named steps read top to bottom like a pipeline; nested subqueries read inside out. Since PG12, single-use non-recursive CTEs inline into the outer query, so this clarity is free of the old optimization-fence penalty.

## Do

- Introduce a `WITH` clause the moment a query grows a second logical step or a second nesting level.
- Name each CTE for what its rows are (`paid_orders`, `latest_logins`, `overage_by_user`), not `t1`/`cte2`.
- Keep each CTE one comprehensible unit: one join cluster, one aggregation, one filter stage.
- Let the final `SELECT` read as the summary of the steps above it.
- Trust inlining; write `MATERIALIZED` only to deliberately fence a step (with a comment saying why), and `NOT MATERIALIZED` only to force inlining of a multiply-referenced CTE.
- Use data-modifying CTEs (`WITH ... UPDATE ... RETURNING`) for multi-step writes per [DML, upserts, and RETURNING](dml-upserts-and-returning.md).
- Use `WITH RECURSIVE` for tree and graph traversal; keep the base and recursive terms visually separate.

## Avoid

- Do not nest subqueries two levels deep; that is the decomposition threshold.
- Do not create single-use CTEs for trivial one-step queries; `SELECT ... FROM ... WHERE ...` needs no pipeline.
- Do not write `MATERIALIZED`/`NOT MATERIALIZED` by habit or superstition; each use is a deliberate, commented choice.
- Do not reuse a CTE name within a statement or shadow a table name with a CTE.
- Do not build write pipelines that depend on seeing their own statement's effects; all CTEs in one statement see the same snapshot.

## Example

```sql
-- Which plans' users generated the most revenue this quarter?
WITH paid_orders AS (
  SELECT o.user_id, o.total
  FROM orders o
  WHERE o.state = 'paid'
    AND o.created_at >= date_trunc('quarter', now())
),
revenue_by_user AS (
  SELECT po.user_id, sum(po.total) AS revenue
  FROM paid_orders po
  GROUP BY po.user_id
)
SELECT
  s.plan,
  count(*) AS paying_users,
  sum(rbu.revenue) AS plan_revenue
FROM revenue_by_user rbu
JOIN subscriptions s ON s.user_id = rbu.user_id
GROUP BY s.plan
ORDER BY plan_revenue DESC, s.plan;
```

## Exceptions

- A hot query where profiling shows inlined CTE shape hurts: rewrite with subqueries or fences, keep the `EXPLAIN` evidence in the commit, and comment the deviation.
- One level of simple subquery (`WHERE EXISTS (...)`, a single derived table) is fine without a CTE; see [subqueries, EXISTS, and LATERAL](subqueries-exists-and-lateral.md).
