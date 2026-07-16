# AMN2 combined overlay `0b858c5`

Дата: 2026-07-16.

Назначение: private source-overlay candidate для
`amn2/codex-vps-test-prep` commit
`0b858c5cdbc5b565cc265966a2edfe2d339d65e0`, объединяющий canonical square
logo, wide language-selection header и local persistent Telegram hardening.

Подготовка пакета не разрешает upload, extraction, source apply, service
changes, Telegram API/profile mutation, bot start/enable, database writes,
peer/config actions, public exposure или provider mutation.

```text
source_commit=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
previous_vps_overlay=801f8c3
source_zip=amn2-codex-vps-test-prep-0b858c5-source.zip
source_zip_sha256=E03F13FD6A7BB5CBC5FCEE7179F395EA8C2864EBCEAB01BC351C5904F3CFF975
source_zip_bytes=9277869
source_archive_entries=383
source_delta_paths=31
source_deleted_paths=app/web/static/brand-full.jpg
canonical_square_logo_sha256=40ACD9465DC9FDA06644D2D829DA996E1D9BF6C856E95298B624B31154FEC791
language_header_sha256=BBDDFA72D1D1FC37E412D2F4A9B4124001FF91FBD641635E31A47E008FC4611F
schema_delta=none
production_database_migration=not_required
regular_bot_runtime=inactive_disabled_before_and_after
telegram_profile_photo=unchanged
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
```

## Exact source delta `801f8c3..0b858c5`

1. `.env.example`;
2. `app/bot/assets.py`;
3. `app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png`;
4. `app/bot/assets/NEOBYATNAYA-AMNZ-LANGUAGE-HEADER.png`;
5. `app/bot/handlers.py`;
6. `app/bot/persistent_runtime.py`;
7. `app/config/settings.py`;
8. `app/main.py`;
9. `app/systemd_notify.py`;
10. удаление `app/web/static/brand-full.jpg`;
11. `app/web/static/brand-full.png`;
12. `app/web/templates/dashboard.html`;
13. `app/web/templates/login.html`;
14. `deploy/runtime/manifest.yml`;
15. `deploy/systemd/amneziya-bot.service.example`;
16. `docs/superpowers/plans/2026-07-15-phase11-telegram-002a-persistent-admission-unit-hardening.md`;
17. `docs/superpowers/plans/2026-07-16-phase11-language-selection-wide-header.en.md`;
18. `docs/superpowers/plans/2026-07-16-phase11-language-selection-wide-header.ru.md`;
19. `docs/superpowers/specs/2026-07-15-phase11-telegram-002a-persistent-admission-unit-hardening-design.md`;
20. `docs/superpowers/specs/2026-07-16-phase11-language-selection-wide-header-design.en.md`;
21. `docs/superpowers/specs/2026-07-16-phase11-language-selection-wide-header-design.ru.md`;
22. `pyproject.toml`;
23. `tests/bot/test_app_bootstrap.py`;
24. `tests/bot/test_bot_assets.py`;
25. `tests/bot/test_bot_handlers.py`;
26. `tests/bot/test_persistent_runtime.py`;
27. `tests/config/test_settings.py`;
28. `tests/deploy/test_runtime_registry.py`;
29. `tests/deploy/test_systemd_templates.py`;
30. `tests/test_systemd_notify.py`;
31. `tests/web/test_app.py`.

Число `source_delta_paths=31` совпадает в machine-readable `name-status` и
`name-only` views. Удалённый JPG и добавленный PNG являются отдельными Git
records. Перед live gate необходимо повторить обе проверки.

## Functional boundary

- Canonical square PNG остаётся общим для существующего bot header и private
  web login/dashboard; bot/web bytes идентичны.
- Wide PNG используется только `/start` language-selection header; при его
  отсутствии handler сохраняет text-only fallback.
- Persistent Telegram admission/runtime и hardened unit example входят в
  source, но installed production unit/env в этом rollout не устанавливаются
  и не меняются. Bot остаётся inactive/disabled.
- Existing production `.env`, `servers.yml`, `data`, `venv` и private evidence
  должны сохраняться. Schema initialization запрещён.

## Package boundary

Source archive является exact `git archive` commit `0b858c5`; untracked,
private и working-tree files исключены. Helper проверяет exact SHA-256 и
сохраняет private/runtime state. Rollout orchestrator обязан создать tracked
source snapshot и явно удалить только stale tracked
`app/web/static/brand-full.jpg` после overlay.

## Future live rollout contract

Отдельный exact live gate обязан:

1. Проверить outer/inner SHA-256, full source commit в ZIP comment, exact Git
   delta, оба asset SHA-256, wide-header package-data contract и отсутствие
   forbidden/secret/runtime entries.
2. Потребовать production overlay `801f8c3`, write gates false/false, regular
   bot inactive/disabled, web active/healthy/loopback-only, database integrity
   и running AWG с неизменными restart count и peer-set digest.
3. До apply создать mode-0700 rollback directory, tracked-source snapshot,
   overlay-marker copy и SQLite backup; зафиксировать installed bot unit/env
   как read-only evidence, не устанавливая и не изменяя их.
4. Остановить только `amneziya-web.service`, повторно проверить database и
   AWG, offline применить source `0b858c5`, удалить только stale tracked JPG и
   не запускать schema initialization или Telegram bot.
5. Запустить только `amneziya-web.service`; проверить login/dashboard, served
   square PNG, exact wide PNG в source/package, imports, overlay marker,
   database logical/count/file invariants, private listeners, bot
   inactive/disabled и AWG continuity.
6. При любом нарушении binding/source/web/database/bot/AWG invariant вернуть
   tracked source, marker и database backup, восстановить web health и повторно
   доказать bot disabled и AWG continuity.

AWG нельзя останавливать, перезапускать, пересоздавать или перенастраивать.
Успешный source rollout не разрешает persistent bot activation или Telegram
profile-photo mutation.

## Future approved command inputs

```text
AMN2_DIR=/opt/amn2
AMN2_SOURCE_ZIP=/root/amn2-combined-overlay-0b858c5/amn2-codex-vps-test-prep-0b858c5-source.zip
AMN2_EXPECTED_SOURCE_SHA=E03F13FD6A7BB5CBC5FCEE7179F395EA8C2864EBCEAB01BC351C5904F3CFF975
AMN2_EXPECTED_SOURCE_COMMIT=0b858c5
VPS_APPLY_ENABLED=false
OPERATOR_DEVICE_CREATE_ENABLED=false
```

Любой upload, extraction, source apply, web stop/start или live verification
требует новой exact Phase 11 combined-overlay approval phrase вне этого
package.
