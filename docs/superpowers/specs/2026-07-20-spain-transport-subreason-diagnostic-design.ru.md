# Phase 11 Spain transport-stage subreason diagnostic — дизайн

## Контекст

Single-use run `spain-fresh-20260720-006` создал claim, но OpenSSH завершился
с `exit=255` без remote probe envelope. Существующий runner подавляет stderr,
поэтому безопасно отличить timeout, отказ аутентификации или host-key failure
невозможно. Run `006` consumed и никогда не повторяется.

## Выбранный подход

Runner получает stdout/stderr OpenSSH только во временную память процесса.
Новый pure classifier просматривает строки, сопоставляет их с закрытым набором
anchored OpenSSH patterns и возвращает только нейтральный subreason. Raw text,
target, user, port, path, host key, fingerprint и command output не пишутся в
evidence, Git или отдельный файл и обнуляются до `Write-EvidenceCreateNew`.

Другие варианты отклонены: дополнительные ping/TCP/SSH probes расширяют live
authority, а сохранение stderr в private artifact создаёт ненужный sensitive
log. Общий `unavailable` без диагностики уже показал недостаточность в run 006.

## Allowlist

Classifier работает только при `exit=255` и возвращает одно из:

- `connect_timeout` — connect/banner timeout;
- `connection_refused` — TCP connection refused;
- `no_route` — no route to host;
- `name_resolution` — hostname resolution failure;
- `host_key` — strict host-key verification failure;
- `authentication` — public-key authentication denied;
- `remote_closed` — remote side closed the connection;
- `remote_reset` — connection reset.

Если совпали две разные категории, не совпала ни одна, exit не равен `255` или
строка имеет неизвестную форму, результат строго `unavailable`. Значения из
regex capture groups не используются и не сохраняются.

## Outcome и границы

- Новый outcome: `spain-fresh-20260720-007`.
- Immutable trust bundle: `spain-fresh-20260720-001`.
- Remote probe bytes/source revision не меняются.
- Runner/approval получают новый SHA после реализации.
- До отдельной literal approval SSH не запускается.
- Нет install/restart/stop/config/secret/Telegram/web/AWG mutation.
- `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` вне scope.

## Acceptance

1. TDD harness подтверждает каждую allowlisted категорию и `unavailable` для
   ambiguous, unknown и non-255 inputs.
2. Static test доказывает отсутствие stderr/out-file persistence и очистку
   in-memory output до evidence write.
3. Exact approval preview совпадает с отдельным run 007 approval document.
4. Scoped/full tests, diff/security review и origin readback проходят до
   выдачи approval; run 007 остаётся `not_run`.
