# SSH host key verification

Цель: перед первым live SSH-действием убедиться, что `amn2` подключается именно к ожидаемому VPS, а не доверяет неизвестному host key автоматически.

Этот срез добавляет локальный verifier в `app.security.ssh_host_key`. Он не подключается к VPS сам, не читает `.env`, не меняет `servers.yml` и не выполняет SSH-команды. Его задача - безопасно разобрать строку host key, посчитать `SHA256:` fingerprint и сравнить его с заранее проверенным pin.

## Как оператор проверяет VPS

1. Получить host key с сервера отдельной командой:

```bash
ssh-keyscan -p 22 YOUR_VPS_HOST > host-key.txt
```

2. Посчитать SHA256 fingerprint:

```bash
ssh-keygen -lf host-key.txt -E sha256
```

3. Сверить fingerprint вне SSH-сессии: через панель провайдера, rescue console, уже доверенный канал или заранее сохраненный pin.

4. Только после совпадения pin переходить к read-only/dry-run VPS gate.

Если fingerprint неизвестен, изменился неожиданно или host key line не парсится, запуск live SSH-backed операций нужно остановить до ручной проверки.

## Локальный contract

```python
from app.security.ssh_host_key import verify_ssh_host_key_pin

result = verify_ssh_host_key_pin(
    "203.0.113.10 ssh-ed25519 AAAA...",
    expected_sha256_fingerprint="SHA256:...",
    expected_host="203.0.113.10",
)
```

Разрешающий результат:

```text
status: verified
trusted: true
```

Блокирующие результаты:

- `missing-pin` - fingerprint не задан;
- `invalid-host-key` - строка host key некорректна;
- `host-mismatch` - host в строке не совпадает с ожидаемым;
- `fingerprint-mismatch` - fingerprint не совпадает с pin.

`safe_metadata()` возвращает только status, trust flag, key type, fingerprint и expected host. Raw key blob, комментарий строки и секреты в metadata не попадают.

## Граница текущего среза

Сейчас verifier является local-only safety contract. Он нужен для ближайшего VPS gate и будущего app-managed host key pinning, но этот срез не меняет live SSH behavior и не включает автоматическую запись known_hosts.

Следующий production-шаг после проверки на реальном VPS: подключить verifier к SSH-backed операциям так, чтобы missing/mismatched pin блокировал live remote operations до ручного подтверждения.
