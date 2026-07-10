# Maintenance Instructions

Use these instructions when changing the completed style guide.

## Policy Changes

1. Add or amend the relevant row in [DECISIONS.md](DECISIONS.md).
2. Update the one guideline page that owns the rule.
3. Keep the page's decision references in [OUTLINE.md](OUTLINE.md) current.
4. Update derived routing, workflows, review checklists, or checks only when affected.
5. Run `bash checks/check.sh`.

## Page Rules

- Use [TEMPLATE.md](TEMPLATE.md); only `Rule` is universal, and conditional pages also require `Activation`.
- Give every rule one owner page. Sibling pages may use one linked reminder.
- Keep guideline pages at or below 100 lines.
- Add rationale, bullets, examples, or exceptions only when they add information.
- Keep examples small and make incidental SQL follow the whole guide.
- Mark version-gated guidance with its minimum PostgreSQL version and fallback.
- Put unresolved policy in `Decision Points` and [DECISIONS.md](DECISIONS.md).

## Routing Contract

- `SKILL.md` owns workflow discovery, direct policy fast paths, and the fallback to `guidelines.md`.
- `guidelines.md` indexes policy pages only; it never links workflows.
- Each workflow appears exactly once in `SKILL.md`.
- Each guideline appears exactly once in `guidelines.md`.
- Workflow tasks route to the workflow alone; the workflow selects policy pages in `Guideline Routing`.
- Routing descriptions state when to select conditional pages; their `Activation` sections confirm whether to apply or skip them after loading.
- Avoid deep reference chains and unrelated co-loads.

## Workflow Format

- `Guideline Routing` identifies always-loaded and conditional policy pages.
- `Workflow` contains the procedure.
- `Avoid` is optional and includes only workflow-specific failure modes.
- Live-database safety workflows take precedence over ordinary DDL policy.

## Scope

- Give agents conventions, not a SQL tutorial or feature survey.
- Keep OLTP application databases as the primary audience.
- Keep deep tuning in the performance workflow.
- Keep planning notes and research outside the packaged skill.
- Do not edit `.ai/research/` as part of policy maintenance.
