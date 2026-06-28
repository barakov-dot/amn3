# Runbook: AMN2 Windows Filename/Basename Readiness (read-only)

Дата: 2026-06-28.
Статус: `prepared-docs-only`.

## Назначение

Выполнить безопасную read-only инвентаризацию workspace для поиска точки,
где в будущей реализации generator-code можно закладывать Windows naming policy:

- canonical filename: `Neobyatnaya-AMNZ-N.conf`
- basename expectation: `Neobyatnaya-AMNZ-N`

Актуально для next track `generator-code readiness / Windows filename-basename policy`
без открытия execution gates.

## Инвентаризация workspace (read-only)

```text
inventory_scope=workspace_read_only
inventory_scope_allowed=docs + worktrees + tracked/untracked filenames
inventory_scope_forbidden=live/vps/ssh/telegram/public
```

### Что проверяем

1. Наличие репозитория/ветки с кодом генерации `.conf`/filename.
2. Точки формирования `config_filename` в коде.
3. Единое место для внедрения правил canonical naming.

### Рекомендуемый порядок read-only проверки

1. `worktree list` и список кандидатов:
   - `worktrees/amn2-public-config-delivery-policy-contract`
   - `worktrees/amn2-redaction-coverage-first-slice`
   - `worktrees/amn2-secret-inventory-registry`
   - `worktrees/amn2-remote-operation-contract-metadata`
2. Поиск кандидатов по `config_filename` / `filename` / `device` в `app/`:
   - `worktrees/amn2-public-config-delivery-policy-contract/app/bot/delivery.py`
   - `worktrees/amn2-public-config-delivery-policy-contract/app/services/config_delivery.py`
   - `worktrees/amn2-public-config-delivery-policy-contract/app/services/config_export.py`
3. Проверка, есть ли отдельный именованный `generator-code`:
   - Поиск по имени папки/ветки/пакета (`generator-code`, `generator_code`) — `нет`.
4. Фиксация найденных путей и текущего filename strategy в read-only artifact.

## Минимальный результат инвентаризации

```text
generator_code_repo_detected=false
generator_code_candidate_repo=worktrees/amn2-public-config-delivery-policy-contract
generator_code_candidate_branch=codex/public-config-delivery-policy-contract
config_filename_current=amneziya-device-{device_id}.conf
config_filename_assigned_in=app/bot/delivery.py:build_config_delivery
windows_basename_strategy_location=where filename composed for payload artifacts
```

## Что не делаем в этом runbook

- Не запускаем live/VPS/SSH/Telegram/public.
- Не меняем code.
- Не генерируем `.conf`, QR, `vpn://` payload.
- Не создаём peers.
- Не печатаем secrets/logs.

## Передача результата

- Зафиксировать найденные пути/поля в docs-артефактах readiness.
- Проставить в status/matrix/next-chat:
  - `execution_go=false`
  - `ready_for_generator_code_readiness=true`
  - `next_gate=AMN2_PHASE_9_WINDOWS_FILENAME_BASENAME_IMPLEMENTATION_READINESS_GATE`
