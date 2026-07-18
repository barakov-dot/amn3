# TELEGRAM-GROUP-ICON-001: local fail-closed gate evidence

Дата: `2026-07-18`.

## Решение

Локальный checksum-bound и target-bound исполнитель смены фотографии
production Telegram-группы готов к отдельному live gate. В этом slice не было
SSH-подключения к VPS, вызова Telegram API или изменения production.

```text
written_design_approval=APPROVE_WRITTEN_DEVICE_001_AND_TELEGRAM_GROUP_ICON_001_SPEC_57EFE86
amn2_design_commit=57efe86
amn3_tdd_plan_commit=d6236cec664f8c9d4d68f860874a1e34e0dcca66
source_overlay=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
remote_executor_sha256=F533CF7EFCB49EE494CE1E75B80F4CCC6EA6C06D2DB46D72669AC6FC23BA623F
runner_sha256=02D43C423D097165EA79692325CD9F08B669781E49171A2FE8AC336245C5F423
canonical_asset_sha256=40ACD9465DC9FDA06644D2D829DA996E1D9BF6C856E95298B624B31154FEC791
canonical_asset_dimensions=1254x1254
focused_tests=20_passed
root_full_tests=148_passed
bash_syntax=pass
powershell_parser=pass
diff_check=pass
live_group_icon_unchanged=true
telegram_api_called=false
messages_sent=0
production_bot_web_database=not_contacted|unchanged
production_awg=untouched
```

## Исполнитель и границы

Добавлены:

- `scripts/vps/post_release_telegram_group_icon_001_remote.sh`;
- `scripts/vps/post_release_telegram_group_icon_001_ssh_runner.ps1`;
- `tests/test_post_release_telegram_group_icon_001_executor.py`.

Публичные режимы ограничены `fingerprint`, `preflight` и `apply`.
`fingerprint` не вызывает Telegram API и выводит только namespaced SHA-256
private target JSON. `preflight` и `apply` требуют exact fingerprint и новый
literal approval, связанный с финальным SHA remote executor. `apply` дополнен
single-use receipt и допускает ровно один `setChatPhoto` после preflight.

Private target остаётся вне Git и содержит только exact `chat_id`,
`expected_title`, `expected_type` в root-owned regular `0600` JSON. Raw ID,
title, bot token, Telegram file path и token-bearing URL не выводятся.

До мутации исполнитель сохраняет прежнюю фотографию в root-only state и
вооружает rollback240. На failure возвращается прежняя фотография; если её не
было, внутренний rollback удаляет только новую. На success доказаны invariants
bot/DB/web/AWG, rollback helper остановлен и повторно проверен неактивным, а
private state удалён.

Запрещены сообщения, `getUpdates`, webhook/profile mutation, bot/web service
mutation, DB write/restore, overlay/package/Docker mutation и любые AWG writes.

## TDD и инженерная проверка

RED начинался с `13 failed`, потому что оба исполнителя отсутствовали. После
GREEN и проверки lifecycle suite достиг `20 passed`. Scoped и full root suites:

```text
python -m pytest tests/test_post_release_telegram_group_icon_001_executor.py -q
20 passed

python -m pytest tests -q
148 passed
```

В ходе review обнаружена инженерная rollback-cancellation race: поздний
transient helper теоретически мог стартовать после внешне успешной отмены.
Исправление добавило проверку helper до отмены, остановку timer, доказательство
inactive, повторную проверку непосредственно перед receipt/cleanup и явный
`asyncio.timeout(60)` в helper. Regression tests закрепляют обе границы.

## Security diff review

Первый сохранённый scan зафиксировал race-кандидат, статически подтвердил его
как engineering correctness defect и не повысил до reportable vulnerability:
путь доступен только оператору с новым exact approval и не даёт отдельного
низкопривилегированного attack path. Дефект всё равно исправлен до commit.

Финальный post-hardening scan:

```text
scan_id=d6236ce_20260718T102337Z
snapshot=codex-security-snapshot/v1:sha256:bddce231d1baf9e201bc8cb2f8d3cba4fb82439cecb7583026488e40dc6efa20
work_ledger=3_of_3
coverage=complete
deferred=0
findings=0
report=C:/Users/SooL/AppData/Local/Temp/codex-security-scans/VPS-OPS-LAB/d6236ce_20260718T102337Z/report.md
```

Финальный diff перечитан полностью: remote `834/834`, runner `201/201`, tests
`347/347`. Защищённый `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` исключён и
не затронут.

## Stop line

Этот gate не меняет живую иконку. После commit/push и origin readback допустим
только отдельный read-only `fingerprint`, если private target уже безопасно
создан. `preflight` и `apply` запрещены до нового exact live approval с
привязкой к target fingerprint и SHA
`F533CF7EFCB49EE494CE1E75B80F4CCC6EA6C06D2DB46D72669AC6FC23BA623F`.
