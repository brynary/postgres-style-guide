# PostgreSQL Style Guide Skill

This repository contains a PostgreSQL style guide packaged as a skill for AI coding agents. The goal is to give agents concrete, opinionated defaults for designing schemas, writing queries, authoring migrations, and configuring database access in the project owner's preferred style.

The packaged skill shape is `SKILL.md` as the root router, focused policy pages under `guidelines/`, and procedure pages under `workflows/`. Planning files remain in the repo as source material, but ordinary skill use should load only the router and relevant guidelines or workflows.

## Start Here

- [SKILL.md](SKILL.md): skill entrypoint and root router for progressive disclosure.
- [guidelines.md](guidelines.md): guideline index for the packaged skill.
- [guidelines/](guidelines): focused PostgreSQL style policy pages.
- [workflows/](workflows): procedural workflows for larger tasks.
- [OUTLINE.md](OUTLINE.md): the guideline map used to draft the guide.
- [DECISIONS.md](DECISIONS.md): resolved style decision register.
- [DRAFTING.md](DRAFTING.md): drafting order, page rules, and scope rules.
- [TEMPLATE.md](TEMPLATE.md): the required format for each guideline page.
- [AGENTS.md](AGENTS.md): repository instructions for AI coding agents.

## Research

The source research reports live in [.ai/research/](.ai/research). They were used to synthesize the outline and decision register. Treat them as background material, not as final policy.

## Intended Style

The guide is production-first PostgreSQL 18+ with an app-first posture:

- The database owns data integrity through constraints; the application owns business logic.
- Model core business data relationally first; use `jsonb` deliberately, not by default.
- Prefer readable, explicit, decomposed SQL over clever single statements.
- Treat schema changes to live databases as production changes with strict lock discipline.
- Keep migration guidance stricter than greenfield DDL guidance.

## Workflow

1. Update [DECISIONS.md](DECISIONS.md) when policy changes.
2. Update the relevant page under [guidelines/](guidelines) or [workflows/](workflows).
3. Keep [guidelines.md](guidelines.md) linked to every packaged guideline page.
4. Keep [SKILL.md](SKILL.md) small and route through progressive disclosure.
5. Run `bash checks/check.sh` before committing skill changes.
6. Use [DRAFTING.md](DRAFTING.md) and [TEMPLATE.md](TEMPLATE.md) only when adding or reshaping pages.

## Packaging Model

The skill uses progressive disclosure:

- `SKILL.md` stays small and routes tasks to relevant guidelines and workflows.
- `guidelines.md` indexes the available guideline pages.
- Focused policy pages live under `guidelines/`.
- Procedural pages live under `workflows/`.
- Planning files like `README.md`, `OUTLINE.md`, `DRAFTING.md`, `DECISIONS.md`, and `.ai/research/` stay outside the packaged skill unless explicitly needed.
