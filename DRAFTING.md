# Drafting Instructions

Use these instructions when turning the outline into guideline pages.

## Priorities

1. Resolve the decision register in [DECISIONS.md](DECISIONS.md), flagship decisions first (D7, D12, D15, D21, D23, D26, D37, D42).
2. Keep [SKILL.md](SKILL.md) small and use it as the router.
3. Draft the core guideline pages first: naming, keys, scalar and temporal types, constraints, indexes, join style, CTEs, and DML.
4. Add workflow pages only where repeated task procedures need more than policy.
5. Add advanced guideline pages only where the target databases need them.
6. Keep every page mechanical enough for an agent to follow.

## Drafting Order

1. Foundations
2. Schema design and data types
3. Constraints and indexes
4. Query style
5. Database logic
6. Security
7. Workflows

## Page Rules

- Use [TEMPLATE.md](TEMPLATE.md) for every guideline page.
- Give every rule exactly one owner page; sibling pages may carry at most a one-line reminder that links to the owner.
- Make examples demonstrate only the owning page's rules; incidental SQL in an example follows other pages' rules but does not showcase them.
- Make the `Rule` section a direct default, not a discussion.
- Keep `Why` short and practical.
- Prefer concrete guidance over philosophy.
- Include exceptions only when an agent could reasonably encounter them.
- Add a small preferred SQL example when the topic affects statement or DDL shape.
- Mark version-gated guidance with the PostgreSQL version it requires (for example PG18 for `uuidv7()`, virtual generated columns, and temporal constraints).
- Put unresolved choices in `Decision Points` instead of burying them in prose.

## Progressive Disclosure

- Treat [SKILL.md](SKILL.md) as the skill entrypoint and root router, not the guide itself.
- Keep detailed policy in `guidelines/` pages.
- Keep procedural task flows in `workflows/` pages.
- Keep [guidelines.md](guidelines.md) as the one-page guideline index.
- Link guideline and workflow files directly from [SKILL.md](SKILL.md) or [guidelines.md](guidelines.md); avoid deep reference chains.
- Do not load every guideline page for ordinary tasks.
- Use routing examples for common task types so agents know which pages to load.

## Scope Rules

- Do not re-teach SQL syntax or relational basics unless a style choice depends on them.
- Do not include long surveys of PostgreSQL features on guideline pages.
- Do not add advanced topics unless they affect likely agent output.
- Keep OLTP application databases as the primary audience; call out analytics/reporting differences only where the right answer changes.
- Keep performance material to correctness-relevant defaults on guideline pages; deep tuning belongs in the performance workflow.
- Treat migration safety guidance as stricter for production databases than for greenfield setup.
- Do not package planning files or research reports into the final skill unless the user explicitly asks for them.
