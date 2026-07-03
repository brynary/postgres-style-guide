# Identifier Casing and Quoting

## Rule

Name every database object in lowercase snake_case and never quote identifiers.

## Why

PostgreSQL folds unquoted identifiers to lowercase; quoting makes a name case-sensitive forever, forcing every future query, tool, and migration to reproduce the exact casing. Unquoted snake_case names work everywhere without ceremony.

## Do

- Use lowercase letters, digits, and underscores: `order_items`, `user_id`, `paid_at`.
- Start every identifier with a letter.
- Keep identifiers under 63 bytes; PostgreSQL silently truncates longer names.
- Avoid reserved and near-reserved words as identifiers: `user`, `order`, `group`, `table`, `check`, `default`, `limit`, `offset`, `primary`, `references`, `where`.
- Spell words out; abbreviate only universally understood terms (`id`, `url`, `ip`).
- Keep acronyms lowercase like any other word: `api_tokens`, `http_status`, `url_path`.

## Avoid

- Do not create quoted identifiers: `"userAccounts"`, `"Order"`, `"created At"`.
- Do not use camelCase or PascalCase even unquoted; it folds to an unreadable lowercase run (`useraccounts`).
- Do not end identifiers with an underscore or use consecutive underscores.
- Do not invent project-specific abbreviations (`usr_acct_bal`) to save characters.
- Do not work around a reserved word by quoting it; pick a different name.

## Example

```sql
-- Good: unquoted snake_case, no reserved words.
CREATE TABLE api_tokens (
  id uuid DEFAULT uuidv7() PRIMARY KEY,
  user_id uuid NOT NULL REFERENCES users (id) ON DELETE CASCADE,
  token_digest text NOT NULL,
  expires_at timestamptz NOT NULL
);

-- Bad: quoted mixed case; every consumer must now quote it forever.
-- CREATE TABLE "ApiTokens" ("userId" uuid, "tokenDigest" text);
```

## Exceptions

- Interoperating with legacy objects that were created quoted: quote exactly those existing names, and do not create new ones.
- Generated interop columns matching an external system's casing may be quoted when a translation layer is not practical; isolate them and comment why.
