# AMN2 Phase 10 Product Recovery With Harness Entry

## Closeout 2026-07-14

Phase 10 закрыта как `completed-product-recovered-deployed-accepted`.
Продолжение находится в:

- `docs/AMN2_PHASE_10_FINAL_CLOSEOUT_PACKET.ru.md`;
- `docs/AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS_ENTRY.ru.md`;
- `docs/NEXT_CHAT_AMN2_PHASE_11_CONTROLLED_LAUNCH_AND_OPERATIONS.ru.md`.

Не использовать старую Phase 10 first-command как активный план.

Дата: 2026-07-04.

## Назначение

Phase 10 открывается в отдельном следующем чате как recovery-фаза после Phase
9/9.2 closeout и Phase 9 command-loop. Цель этой фазы - вернуть работу к
product-slice, тестам и проверяемым результатам, а docs/status sync выполнять
только после code/test результата.

Это не открывает live/VPS/SSH/Telegram/public/config/peer действия.

## Источник правды

- текущий git workspace;
- `docs/PROJECT_STATUS_CURRENT.ru.md`;
- `docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md`;
- `docs/AMN2_PHASE_9_9_2_FINAL_CLOSEOUT_PACKET.ru.md`;
- `docs/NEXT_CHAT_AMN2_PHASE_9_NEW_CHAT_START_FROM_HANDOFF.ru.md`;
- новый harness:
  - `scripts/phase9_progress_harness.py`;
  - `tests/test_phase9_progress_harness.py`.

## Обязательный harness

Перед следующей операторской командой, если она должна вести к product-work:

```powershell
python scripts/phase9_progress_harness.py --next-command "<COMMAND>" --require-product-step
```

Команды, состоящие только из `CONFIRM_HOLD_STATE`,
`READY_FOR_OPERATOR_NEXT_DOCS_REQUEST` или `AWAIT_OPERATOR_EXACT_CMD`, должны
получать `FAIL`, если оператор явно не запросил чистую проверку статуса.

Перед закрытием product slice:

```powershell
python scripts/phase9_progress_harness.py --require-product-diff
```

Если product work выполняется в AMN2 worktree, harness запускается с явным
`--repo-root` этого worktree, например:

```powershell
python scripts/phase9_progress_harness.py --repo-root worktrees/amn2-public-config-delivery-policy-contract --require-product-diff
```

## Стоп-линии

```text
execution_go=false
config_generation=false
config_delivery=false
peer_creation=false
live_vps_ssh_telegram_public=false
```

Без отдельного exact gate запрещены:

- live VPS/SSH commands;
- Telegram live send/polling;
- public exposure;
- config generation/delivery;
- peer creation;
- service restart/apply/upload;
- provider/rebuild/import/reboot action;
- вывод `.conf`, QR, `vpn://`, private keys, PSK, tokens, passwords, raw logs.

Если для результата нужен live/read GitHub/VPS gate, помощник должен явно
назвать нужное разрешение и причину, а не превращать отсутствие разрешения в
бесконечный docs-only цикл.

## Рабочее правило новой фазы

1. Сначала product-slice или проверяемая инженерная проверка.
2. Затем scoped tests.
3. Затем review diff.
4. Только после этого docs/status sync.
5. При смене фазы проверять и ретаргетить active automations/heartbeats,
   чтобы они не продолжали старый phase thread.
6. После каждого результата выводить план в формате:
   `Одиночная`, `Двойная`, `Тройная`, `Более`, с явной моделью.

## Модельные правила

`КОДЕКС SPARK`:

- повторяемые implementation/test/product-slice задачи;
- harness runs;
- scoped pytest;
- review diff;
- локальный docs sync после выполненного product результата.

`GPT-5.5`:

- выбор нового крупного трека;
- risk decision;
- exact gate decision;
- live/VPS/SSH/Telegram/public/config/peer approval framing.

Оператор переключает модель вручную в этом же чате. Каждая рекомендация должна
начинаться с модели, например:

```text
КОДЕКС SPARK -> START_...
GPT-5.5 -> REVIEW_...
```

## Текущий переносимый state

```text
phase9_package_prep_status=prepared-docs-only
phase9_package_prep_commit=9fb6196
origin_sync=true
canonical_client_display_name=NeobyatnayaNET
canonical_client_display_name_alias=НеобъятнаяNET
windows_policy=Neobyatnaya-AMNZ-N.conf -> Neobyatnaya-AMNZ-N
android_status=DOCUMENTED_LIMITATION
android_observed=Сервер 1|Сервер 3
android_fallback=manual_rename
ios_status=not_proven/manual_rename_fallback
android_multi_device_private_config_execution_status=completed-private-operator-only
android_multi_device_private_config_execution_run_id=20260628T231440
```

## Первый product-slice новой фазы

В Phase 9 уже закрыта длинная цепочка config-share restore guards. Последний
видимый незакрытый инженерный риск:

```text
config_share_restore_schema_index_declaration_contract_status=completed-product-fix-pushed
config_share_restore_schema_index_declaration_contract_commit=60b77fd
config_share_restore_schema_index_declaration_contract_test_status=scoped_pytest_66_passed
config_share_restore_schema_index_declaration_contract_extended_test_status=scoped_pytest_151_passed
```

Phase 10 начинает не с hold, а с проверки этого хвоста.

Первая точная команда:

```text
ТЕКУЩАЯ МОДЕЛЬ -> SELECT_NEXT_PHASE10_PRODUCT_SLICE_AFTER_FRESH_INSTALLER_RECOVERY_MERGE -> START_SELECTED_PHASE10_PRODUCT_SLICE -> RUN_SCOPED_TESTS_FOR_SELECTED_SLICE
```

Ожидаемый результат:

- schema index declaration contract закрыт product fix commit `60b77fd`;
- scoped backup tests: `66 passed`;
- extended scoped suite: `151 passed`;
- client display-name root-cause закрыт product policy commit `d2d3099`;
- display-name scoped tests: `14 passed`;
- filename canonicalization закрыт product commit `26bb22e`;
- filename canonicalization scoped tests: `18 passed`;
- compatibility branch rebased на `amn2/codex-vps-test-prep@471bca8`;
- post-rebase scoped tests: `22 passed`;
- broad regression contract fix закрыт product commit `d61c6be`;
- broad scoped suite: `130 passed`;
- compatibility branch fast-forward merged в `amn2/codex-vps-test-prep` и pushed;
- post-merge broad scoped suite: `130 passed`;
- fresh-installer recovery branch rebased, fast-forward merged в
  `amn2/codex-vps-test-prep` и pushed as `4326cae`;
- fresh-installer recovery post-merge broad scoped suite: `164 passed`;
- следующий Phase 10 product slice:
  `SELECT_NEXT_PHASE10_PRODUCT_SLICE_AFTER_FRESH_INSTALLER_RECOVERY_MERGE`;
- docs sync делать только после product/test evidence.

## Следующие цели фазы

Критично:

- продолжать Phase 10 только через real product slices и scoped tests;
- остановить повтор `CONFIRM_HOLD_STATE` как next-step;
- держать harness обязательным перед product closure.

Очень важно:

- вернуться к Amnezia client display-name root-cause analysis по коду клиента,
  а не по предположениям;
- если для чтения GitHub/upstream нужен network gate, запросить его явно;
- сохранить цель имени: `NeobyatnayaNET` / `НеобъятнаяNET` без суффиксов в
  пользовательском отображении, где это технически возможно.

Важно:

- продолжить config-share / restore / backup hardening только через code + tests;
- не делать отдельный docs-only status sync без предшествующего product результата.

Просто:

- после каждого закрытого product slice синхронизировать AMN3 docs одним
  компактным docs-tail, без ручного многократного кликанья.
