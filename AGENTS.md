# AGENTS.md

## Project Purpose

This repository is a PostgreSQL style guide packaged as a skill for AI coding agents. The guide should help agents design schemas, write queries, author migrations, and configure database access using the project owner's conventions.

Keep the work simple, explicit, and useful for agents. Do not turn the guide into a SQL textbook.

## Key Files

- [authoring/DRAFTING.md](authoring/DRAFTING.md): maintenance entrypoint for decisions, ownership, and page shape.
- [SKILL.md](SKILL.md): skill entrypoint and root router.
- [guidelines.md](guidelines.md): guideline index for progressive disclosure.
- [guidelines/](guidelines): focused PostgreSQL style policy pages.
- [workflows/](workflows): procedural workflows for larger tasks.
- [checks/](checks): validation harness for the packaged skill.
- [.ai/research/](.ai/research): source research reports used to create the outline.

## Working Rules

- Follow [authoring/DRAFTING.md](authoring/DRAFTING.md) when maintaining the guide; it routes to the decision register, ownership map, and page template.
- Keep guideline pages short, concrete, and mechanical enough for an agent to follow.
- Keep [SKILL.md](SKILL.md) small. Put detailed policy in `guidelines/` and procedures in `workflows/`.
- Link each workflow exactly once from [SKILL.md](SKILL.md) and each guideline exactly once from [guidelines.md](guidelines.md); use direct guideline links in `SKILL.md` only for policy fast paths.
- Run `bash checks/check.sh` before committing skill changes.
- Do not edit files in [.ai/research/](.ai/research) unless explicitly asked.

## Style Guide Bias

The intended guide is production-first PostgreSQL 18+ with an app-first posture:

- The database owns data integrity (constraints, FKs, CHECKs); the application owns business logic.
- Model core business data relationally first; use `jsonb` deliberately, not by default.
- Prefer readable, explicit, decomposed SQL over clever single statements.
- Treat schema changes to live databases as production changes with strict lock discipline.
- Keep migration guidance stricter than greenfield DDL guidance.

## Editing Expectations

- Preserve ASCII-only markdown unless a file already uses non-ASCII intentionally.
- Keep changes narrowly scoped to the requested document.
- Avoid adding new guideline or workflow files unless the user asks for new pages.
- Do not include planning docs or research reports in the packaged skill unless explicitly requested.
