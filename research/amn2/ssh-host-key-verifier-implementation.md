# `amn2`: SSH host key identity verifier

Дата: 2026-06-01.

Статус: `implemented-pushed-local-gate-complete`.

Production branch:

```text
codex/ssh-host-key-identity-verifier
```

Production commit:

```text
dd20364 Add SSH host key verifier
```

## Что добавлено

В `amn2` добавлен local-only verifier для SSH host key identity:

- парсинг OpenSSH host key/public key строк;
- вычисление `SHA256:` fingerprint по key blob;
- сравнение с заранее проверенным expected pin;
- проверка expected host, если он задан;
- блокирующие статусы для `missing-pin`, `invalid-host-key`, `host-mismatch`, `fingerprint-mismatch`;
- safe metadata без raw key blob, комментария строки, `.env`, паролей или приватных ключей.

Документация в `amn2`:

- `docs/SSH_HOST_KEY_VERIFICATION.ru.md`;
- короткая ссылка из `docs/VPS_RETEST_PROTOCOL.ru.md`.

## Граница среза

Срез не подключается к VPS, не читает `.env`, не меняет `servers.yml`, не выполняет SSH-команды и не меняет текущий live SSH behavior.

Это именно local-only safety contract перед будущим app-managed host key pinning. Для ближайшего реального VPS gate он дает проверяемую основу, но сам gate все еще должен начинаться с operator-side Phase 0 host key verification.

## Проверка

Focused:

```text
tests/security/test_ssh_host_key.py tests/server/test_system_ssh.py tests/security/test_surface_policy.py -v
result: 29 passed
```

Full local suite:

```text
tests -v
result: 550 passed, 1 StarletteDeprecationWarning
```

Также `git diff --check` прошел без замечаний.

Известное окружение Windows иногда печатает ignored pytest temp cleanup `PermissionError` после успешного exit code `0`; это не меняет результат тестов.

## Следующее решение

Перед live VPS gate можно использовать этот срез как отдельный merge/cherry-pick candidate в рабочую ветку проверки. Следующий production-срез из локального списка: scoped API token lifecycle gate или manager config export contract.
