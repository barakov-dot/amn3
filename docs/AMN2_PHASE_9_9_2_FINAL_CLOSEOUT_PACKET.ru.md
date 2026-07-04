# AMN2 Phase 9/9.2 Final Closeout Packet

Дата: 2026-07-04

## Назначение

Этот packet закрывает текущий чат как `Phase 9/9.2 closeout` и фиксирует, что
`Phase 10 product recovery with progress harness` должна стартовать в отдельном
следующем чате.

## Текущий статус

```text
current_chat_state=Phase 9/9.2 closeout
next_phase=Phase 10 product recovery with progress harness
phase10_execution_chat_required=true
amn2_branch=codex-vps-test-prep
amn2_head=4326cae
amn2_origin_sync=true
amn3_branch=codex-spark-phase9-docs-sync
phase10_handoff_doc=docs/NEXT_CHAT_AMN2_PHASE_10_PRODUCT_RECOVERY_WITH_HARNESS.ru.md
phase10_entry_doc=docs/AMN2_PHASE_10_PRODUCT_RECOVERY_WITH_HARNESS_ENTRY.ru.md
```

## Закрыто в Phase 9/9.2

- Phase 9 docs-only recovery после broken thread закреплена в repo/docs.
- Private/self config package prep и related status sync сохранены как
  completed existing material.
- Android multi-device private operator-only execution result сохранён как
  completed private/operator-only material без вывода payloads в docs.
- Client display-name policy уточнён: целевое имя `NeobyatnayaNET`, AmneziaVPN
  может показывать client-generated `Сервер N`, standalone AmneziaWG file import
  ориентируется на filename stem.
- AMN2 product recovery material уже интегрирован в `amn2/codex-vps-test-prep`:
  - schema index guard fix: `60b77fd`;
  - client display-name policy: `d2d3099`;
  - standalone AWG filename canonicalization: `26bb22e`;
  - broad regression contract fix: `d61c6be`;
  - fresh-installer recovery merge: `4326cae`.
- Последняя post-merge проверка fresh-installer recovery: `164 passed`.

## Не открыто

```text
execution_go=false
config_generation=false
config_delivery=false
peer_creation=false
live_vps_ssh_telegram_public=false
```

Без отдельного exact gate запрещены live/VPS/SSH/Telegram/public/config/peer
actions, config generation/delivery, peer creation, public launch, service
restart/apply/upload, restore/import/reboot/provider action.

Запрещено печатать secrets, config payloads, QR, `vpn://`, keys, PSK, tokens,
passwords или raw logs.

## Phase 10 handoff

Следующий чат должен начинаться с:

```text
AMN2_PHASE_10_PRODUCT_RECOVERY_WITH_HARNESS_START
```

Источник правды:

- repo/docs;
- current git workspace;
- `docs/NEXT_CHAT_AMN2_PHASE_10_PRODUCT_RECOVERY_WITH_HARNESS.ru.md`;
- `docs/AMN2_PHASE_10_PRODUCT_RECOVERY_WITH_HARNESS_ENTRY.ru.md`;
- `scripts/phase9_progress_harness.py`;
- `tests/test_phase9_progress_harness.py`.

Первый product-step нового Phase 10 чата:

```text
ТЕКУЩАЯ МОДЕЛЬ -> SELECT_NEXT_PHASE10_PRODUCT_SLICE_AFTER_FRESH_INSTALLER_RECOVERY_MERGE -> START_SELECTED_PHASE10_PRODUCT_SLICE -> RUN_SCOPED_TESTS_FOR_SELECTED_SLICE
```

## Проверки перед закрытием

- Safe scan должен не находить unsafe `*_go=true` / live/config/peer true
  markers в актуальных closeout/handoff docs.
- `git diff --check` должен проходить.
- Markdown lint может быть пропущен, если локальный markdownlint не установлен;
  в этом случае обязательны diff review и `git diff --check`.

## Рекомендуемая финальная команда текущего чата

```text
ТЕКУЩАЯ МОДЕЛЬ -> STAGE_AND_COMMIT_PHASE9_9_2_FINAL_CLOSEOUT_PACKET -> PUSH_PHASE9_9_2_FINAL_CLOSEOUT_PACKET -> OPEN_SEPARATE_PHASE10_CHAT
```
