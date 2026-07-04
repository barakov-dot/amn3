# AMN2 Phase 10 Product Recovery With Harness Entry

Дата: 2026-07-04.

## Назначение

Phase 10 открывается как recovery-фаза после Phase 9 command-loop. Цель этой
фазы - вернуть работу к product-slice, тестам и проверяемым результатам, а
docs/status sync выполнять только после code/test результата.

Это не открывает live/VPS/SSH/Telegram/public/config/peer действия.

## Источник правды

- текущий git workspace;
- `docs/PROJECT_STATUS_CURRENT.ru.md`;
- `docs/AMN2_PHASE_9_TASK_MATRIX_REFRESH.ru.md`;
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
5. После каждого результата выводить план в формате:
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
config_share_restore_schema_index_declaration_contract_status=completed-local-code
config_share_restore_schema_index_declaration_contract_commit=dcaed34
config_share_restore_schema_index_declaration_contract_test_status=scoped_pytest_144_not_run
```

Phase 10 начинает не с hold, а с проверки этого хвоста.

Первая точная команда:

```text
КОДЕКС SPARK -> START_PHASE10_CONFIG_SHARE_RESTORE_SCHEMA_INDEX_TEST_VERIFICATION_SLICE -> RUN_SCOPED_TESTS_FOR_SELECTED_SLICE -> REVIEW_SELECTED_LOCAL_PRODUCT_SLICE_DIFF
```

Ожидаемый результат:

- найти AMN2 worktree/branch с `dcaed34`;
- прогнать scoped tests для schema index declaration contract;
- если тесты падают, исправить product code/tests;
- если тесты проходят, обновить статус с `scoped_pytest_144_not_run` на реальный
  результат;
- docs sync делать только после product/test evidence.

## Следующие цели фазы

Критично:

- закрыть `scoped_pytest_144_not_run` по schema index declaration contract;
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
