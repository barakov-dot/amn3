# Phase 11 TELEGRAM-002A local persistent admission and unit hardening evidence

Дата завершения: 2026-07-16.

## Итог

`PHASE11-TELEGRAM-002A` завершён как local engineering slice и pushed в
`codex-vps-test-prep`:

```text
source_commit=08c56f2beff65145380fdb3736d94c0709a2b33a
origin_sync=true
production_overlay=801f8c3|unchanged
regular_bot=inactive_disabled
telegram_api_called=false
vps_or_provider_mutation=false
production_web_or_database_mutation=false
production_awg=untouched
```

Live activation, production `.env`, Telegram profile photo, package upload,
`systemctl enable/start/restart` и любые AWG actions в этот slice не входили.

## Реализованный contract

- expected bot username обязателен при persistent start;
- identity, webhook empty, backlog `0` и non-acknowledging zero-time ownership
  probe проверяются до workflow/DB initialization;
- identity/webhook/backlog повторно проверяются непосредственно до polling;
- локальный process-lifetime lock исключает второй экземпляр;
- allowed updates зафиксированы как `message,callback_query`;
- polling использует `handle_as_tasks=True` и конечный concurrency limit `8`;
- initial admission, workflow/dispatcher construction и repeated state check
  делят один overall startup budget `1..120` seconds;
- readiness отправляется только после фактического старта polling task;
- watchdog, stopping и ошибки имеют stable sanitized messages;
- systemd template использует `Type=notify`, `WatchdogSec=60s`,
  `TimeoutStartSec=135s`, restart throttling, empty capability sets,
  `ProtectSystem=strict`, `ProtectHome=true`, narrow writable paths и остаётся
  declarative/disabled.

## TDD и проверки

До исправления security review controls целевой набор дал ожидаемый RED:

```text
3 failed|11 passed
```

Падения точно покрывали отсутствующий finite update-task limit, отсутствие
единого startup timeout и старый `TimeoutStartSec=45s`. После минимального
исправления тот же набор: `14 passed`.

Fresh pinned-runtime verification:

```text
python=CPython 3.12.13|toolchain_passed
scoped_telegram_runtime=113 passed
full_source=915 passed|1 skipped|1 known Starlette deprecation warning
compileall=passed
git_diff_check=passed
staged_diff_check=passed
```

Source commit содержит ровно 15 запланированных files: settings/env/manifest,
persistent runtime/notifier/coordinator, bot unit, approved design/TDD plan и
их regression tests.

## Security review

Initial diff review подтвердил два пути:

1. unbounded aiogram update tasks до admin workflow checks;
2. две последовательные admission windows при `TimeoutStartSec=45s`.

Оба закрыты TDD-изменениями выше. Clean Codex Security diff scan:

```text
scan_id=beec2b5_telegram002a_clean_20260716T045525Z
base=beec2b571e242d4920472a828a6833e8f506a374
snapshot=da0f5ec50e574c749029210fe783b5dbc3a0ee97749b13ad44a8a83ddcc15105
full_file_receipts=15_of_15
coverage=complete
findings=0
deferred=0
report_sha256=7da0367ebe339a5a28cdf98c02c98d996a013d170a543633e8577586484c3e9a
```

`ProtectHome=true` не ослаблялся. Перед отдельным будущим VPS-write activation
gate нужен service-readable non-home SSH key/known-hosts path или узкий
проверенный read-only bind; home-rooted key path не должен стать скрытым live
failure.

## Следующий live boundary

Commit `08c56f2` является потомком logo commit `6abc620`, поэтому следующий
production package должен быть новым combined overlay на exact source
`08c56f2`, а не отдельным применением старого logo-only package. Сначала
package/checksum/rollback review, затем отдельный exact web-only rollout с
bot inactive/disabled, и только после postflight — отдельный persistent bot
admission/activation gate. AWG во всех шагах остаётся untouched.
