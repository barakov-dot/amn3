# Дополнение по защите данных

## Цель

Усилить первый локальный MVP так, чтобы секреты не утекали через БД, logs, backup, exceptions, документацию или тестовые данные.

## Какие данные защищаем

Критичные секреты:

- Telegram bot token;
- `APP_SECRET_KEY`;
- SSH private keys and passwords;
- AmneziaWG private keys;
- preshared keys;
- full client `.conf`;
- QR-коды;
- backup archives;
- payment identifiers where applicable.

## Правила хранения

- `APP_SECRET_KEY` хранится только вне репозитория.
- User peer private key и PSK шифруются перед записью в БД.
- `.env`, `servers.yml`, backup archives, `.conf` и QR-файлы игнорируются Git.
- `.env.example` содержит только placeholders.

## Правила логирования

Логи и отчеты не должны содержать:

- full config blocks;
- `PrivateKey`;
- `PresharedKey`;
- Telegram bot token;
- `APP_SECRET_KEY`;
- payment external IDs where they could identify a real payment.

Перед выводом используется redaction layer.

## Ошибки и Exceptions

Ошибки шифрования/дешифрования должны быть безопасными:

- не раскрывать raw token;
- не раскрывать тип криптографической ошибки;
- не печатать plaintext;
- возвращать понятное публичное сообщение.

## Backup

Backup должен быть encrypted и checksum-protected. Restore должен проверять, что encrypted secrets можно расшифровать текущим `APP_SECRET_KEY`, до записи target DB.

## Tests

Тесты должны проверять:

- rejection weak secrets;
- encryption round-trip;
- no plaintext private key in encrypted payload;
- redaction of tokens/configs/keys;
- `.gitignore` protects runtime secret files;
- `.env.example` uses placeholders only.

## Acceptance Criteria

- Real secrets are not present in repository files.
- Secret scan has only fake test values or regex examples.
- Backup restore cannot silently accept secrets encrypted with another key.
- Public errors are useful but not revealing.
