# POST-RELEASE: локальная выдача бессрочных неназначенных access slots

Дата: 2026-07-20

Статус: локальная реализация и проверка завершены; Spain/VPS/production не
контактировались, live gate не открывался.

## Реализованный контракт

- `admin-config issue-manifest` принимает `recipient_unassigned` и `quantity=1..100`;
- отсутствие `expiry` означает `indefinite`: `duration_days=NULL`,
  `expires_at=NULL`;
- одному получателю можно одной заявкой выпустить несколько сразу активных
  slots без выдуманного физического устройства и без Device Passport;
- для четырёх slots формируются стабильные имена
  `NEOBYATNAYA.NET-<recipient>-01.conf` ... `-04.conf`;
- request fingerprint связывает server, recipient, mode, expiry и развёрнутые
  slots; точный replay не создаёт повторные peer, receipts или файлы;
- full-batch quota и filename collision проверяются до recipient/key/file/peer
  mutation;
- каждый slot независимо отключается и отзывается remote-first;
- поздняя явная assignment создаёт один реальный Device Passport из сохранённого
  fingerprint без смены peer, VPN IP или уже выданного filename;
- dry-run выдачи не открывает БД/Settings/SSH и не генерирует ключи; lifecycle
  dry-run использует SQLite `mode=ro` и `query_only`;
- apply остаётся configured-admin-only и проходит через existing exact VPS live
  gate; lifecycle дополнительно сверяет сохранённые name/host/SSH port/endpoint/
  VPN port с выбранным private server config.

## Source и проверки

```text
amn2_branch=codex-vps-test-prep
amn2_source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
baseline=51fdba29ee1b33442bd109a0d0611c4d1348f4da
focused_security_hardening=61_passed
full_tests=1029_passed|1_skipped|1_preexisting_starlette_httpx_warning
diff_check=pass
added_line_secret_scan=matches_0
security_diff_review=reportable_findings_0
```

В ходе pre-publication review были найдены и до commit устранены три safety
gap: DB-mutating lifecycle dry-run, поздний filename collision после remote
apply и name-only server target binding. Для каждого добавлена regression-
проверка. SQLite access migration выполняется одной транзакцией, сохраняет
существующие `indefinite`/assignment/fingerprint значения и использует строгую
hex-проверку fingerprint.

## Negative live evidence

```text
spain_network_contact=false
spain_install_or_preflight=false
production_bot_web_database=false
production_awg=untouched
telegram_actions=false
config_payloads_in_git=false
private_targets_or_credentials_in_git=false
```

Следующий отдельный operational gate — публикация source/docs, затем только
ранее спроектированный dedicated Spain trust onboarding и новое точное
разрешение на read-only preflight. Эта реализация сама не разрешает SSH,
установку, peer generation на Spain или перенос production.
