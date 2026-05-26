# Documentation Language Policy

## Decision

All new specifications, plans, technical requirements, guides, and architecture notes must be prepared in two language versions:

- Russian file;
- English file.

Languages must not be mixed in the same document, except for short technical terms, commands, file names, API names, and quotes from external tools.

## Naming Rule

New documents use a language suffix before `.md`:

```text
docs/superpowers/specs/2026-05-27-feature-name.ru.md
docs/superpowers/specs/2026-05-27-feature-name.en.md
```

The same rule applies to plans:

```text
docs/superpowers/plans/2026-05-27-feature-name.ru.md
docs/superpowers/plans/2026-05-27-feature-name.en.md
```

For user-facing guides:

```text
docs/NEXT_STAGE_BEGINNER_GUIDE.ru.md
docs/NEXT_STAGE_BEGINNER_GUIDE.en.md
```

## Completion Criteria

A document is considered complete only when both versions exist:

- `.ru.md` with Russian content;
- `.en.md` with English content.

The files must be equivalent in meaning: structure, decisions, requirements, risks, commands, and acceptance criteria must match.

## Legacy Documents

Documents without a language suffix are considered legacy documents. They do not need to be renamed urgently without a separate task, but when substantially revised they must be split into two versions:

- `.ru.md`;
- `.en.md`.

## Working Order

1. Prepare the Russian version first if the task discussion is in Russian.
2. Then prepare the English version in a separate file.
3. Before completing the task, verify that both versions were added or updated.
