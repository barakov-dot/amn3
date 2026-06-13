# Next Project Bootstrap

Скопировать этот пакет в первый чат нового проекта и заполнить поля в квадратных
скобках.

```text
Начинаем новый проект:

[PROJECT_NAME]

Рабочая папка:
[ABSOLUTE_WORKING_FOLDER]

Источник правды:
- primary repo: [owner/name or local path], branch [branch]
- current checkpoint: [commit/status]
- latest deployed/smoked checkpoint: [commit/status or none]

Сначала создай или обнови:
- PROJECT_CONTEXT.md
- CURRENT_STATUS.md
- BACKLOG.md
- IMPLEMENTATION_PLAN.md
- SAFETY_BOUNDARIES.md
- DECISIONS.md
- NEXT_CHAT.md

Границы:
- по умолчанию только local-only/docs/tests/security review;
- live infra commands, deploy/restart/package apply, public exposure, secret or
  config delivery, write API, production mutation, backup/restore/import apply,
  destructive provider actions and identity/token mutations запрещены без
  отдельного named gate;
- несовместимый upstream/license code не копируем.

Приоритеты:
- критичные;
- очень важные;
- важные;
- нормальные;
- простые;
- косметические.

Правила:
- после закрытия задачи удалить ее из активного плана;
- выводить оставшийся план;
- давать следующую рекомендацию;
- предлагать одиночные, парные и тройные bundles, когда это полезно;
- новые полезные мысли сразу добавлять в план по шкале приоритетов и сообщать,
  куда добавлены.

Первый рекомендуемый шаг:
[FIRST_SAFE_STEP]
```

## Минимальный стартовый backlog

### Критичные

- `P0-C001` Safety boundaries and named-gate policy.

### Очень важные

- `P0-I001` Architecture and source-of-truth setup.

### Важные

- `P0-M001` First local testable slice.

### Нормальные

- `P0-N001` Documentation and handoff rhythm.

### Простые

- `P0-S001` Repo hygiene, formatting and verification commands.

### Косметические

- `P0-X001` Naming/copy polish after first working slice.
