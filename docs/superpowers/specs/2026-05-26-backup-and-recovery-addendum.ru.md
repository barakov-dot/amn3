# Дополнение по backup и восстановлению

## Цель

Реализовать backup данных так, чтобы сервис можно было быстро перенести на другой сервер или восстановить после сбоя с минимальным риском потери связи у клиентов.

## Scope

Первый этап покрывает backup application state:

- SQLite database;
- backup manifest;
- checksum;
- encrypted archive;
- verify command;
- guarded restore command.

Server-side VPN config backup откладывается на VPS integration stage.

## Требования

Backup должен:

- создаваться одной CLI-командой;
- шифроваться с использованием `APP_SECRET_KEY`;
- включать manifest с версией приложения, временем создания, checksum и именем DB-файла;
- не включать лишние файлы;
- не писать plaintext secrets в архив;
- быть проверяемым до restore.

Restore должен:

- требовать существующий backup file;
- проверять archive members allowlist;
- проверять checksum;
- проверять SQLite schema;
- проверять active devices and encrypted peer secrets;
- не перезаписывать target DB без `--force`, если файл уже существует;
- писать target DB только после всех проверок.

## CLI

```powershell
python -m app.cli backup create --db data/amneziya.sqlite3 --output backups
python -m app.cli backup verify --file backups/<backup-file>.tar.enc
python -m app.cli backup restore --file backups/<backup-file>.tar.enc --target-db data/restore-check.sqlite3
```

## Recovery

Если bot server потерян, но VPN VPS жив:

1. Развернуть проект на новом host.
2. Восстановить `.env` с тем же `APP_SECRET_KEY`.
3. Восстановить DB из backup.
4. Проверить restore.
5. Запустить bot.

Клиенты должны продолжить работать, потому что VPN VPS не менялся.

Если VPN VPS потерян и нельзя восстановить тот же endpoint/server keys, существующие клиентские туннели бесшовно сохранить нельзя. Нужно поднять новый VPS и перевыпустить configs.

## Tests

Тесты должны покрывать:

- create/verify/restore happy path;
- checksum mismatch;
- invalid SQLite;
- archive with extra members;
- target overwrite protection;
- incompatible `APP_SECRET_KEY`;
- active device with missing encrypted secrets.

## Acceptance Criteria

- Full test suite passes.
- Restore never writes target DB before verification.
- Backup files remain ignored by Git.
- Recovery procedure is documented for beginners.
