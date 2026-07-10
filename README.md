# PostgreSQL Style Guide Skill

This repository contains a PostgreSQL style guide packaged as a skill for AI coding agents. The goal is to give agents concrete, opinionated defaults for designing schemas, writing queries, authoring migrations, and configuring database access in the project owner's preferred style.

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

## mdBook

The guide can be built as an mdBook for browsing:

```sh
mdbook build
mdbook serve --open
```

Book source lives under [src/](src). The book source uses symlinks to expose packaged skill files without duplicating the canonical copies at the repository root, and a preprocessor strips SKILL.md's frontmatter from the rendered book.

GitHub Pages deployment is handled by [.github/workflows/deploy.yml](.github/workflows/deploy.yml). For first-time setup, set the repository's Pages source to "GitHub Actions" under Settings > Pages. Pushes to `main` will build the book and deploy the generated `book/` output.
