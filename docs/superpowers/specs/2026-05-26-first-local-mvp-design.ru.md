# Дизайн первого локального MVP

## Цель

Построить первый рабочий локальный инкремент Amneziya: Python-приложение, которое регистрирует Telegram-пользователя, принимает заявку на доступ, позволяет администратору подтвердить ее, создает устройство, выделяет VPN IP, генерирует клиентский конфиг AmneziaWG 2.0 и готовит QR-код.

Этот инкремент не применяет peer на реальном VPS. Provisioning сервера и живая интеграция с `awg`/`awg-quick` откладываются на следующий этап. Цель - безопасно проверить ядро приложения до любых изменений production VPN-сервера.

Требования по защите данных и backup/restore входят в scope первого каркаса.

## Scope

Включено:

- Python project scaffold с package layout, dependency metadata и `.env.example`.
- Runtime-конфигурация из environment variables.
- SQLite для локального MVP.
- Модель данных для users, servers, devices, plans, orders и admin actions.
- IP allocation из настраиваемого CIDR.
- Генерация AmneziaWG 2.0 client config.
- QR generation из полного config text.
- Зашифрованный local backup, verification и restore CLI.
- Минимальный Telegram bot flow: `/start`, access request и admin approval.
- Service layer для жизненного цикла request-to-device.
- Tests для IPAM, config generation и approval flow.

Исключено:

- Real SSH provisioning.
- Установка AmneziaWG на Debian VPS.
- Live peer apply/revoke на работающем интерфейсе.
- Real payment provider.
- Multi-server selection beyond data model readiness.
- Import-link format до проверки на реальном AmneziaVPN client.

## Архитектура

Приложение использует небольшую layered structure:

```text
app/
  bot/
  config/
  db/
  services/
  backup/
  vpn/
    amneziawg_v2/
    ipam.py
  cli.py
  main.py
tests/
```

`bot` отвечает только за Telegram input/output. Он не выделяет IP, не создает ключи и не пишет VPN records напрямую.

`services` владеет workflow: request access, approve request, create device, generate config payload, record admin actions.

`db` владеет persistence и repository interfaces.

`vpn.ipam` отвечает за CIDR-aware IP allocation и не должен выдавать server address, network address, broadcast address или уже занятые адреса.

`vpn.amneziawg_v2` отвечает за key generation и config rendering. Формат должен иметь версию, например `amneziawg_v2`.

`backup` отвечает за manifest, encrypted archive, verification и guarded restore.

## Data Flow

1. Telegram user sends `/start`.
2. Bot creates or updates `users`.
3. User requests access.
4. App creates `orders` with `manual_review`.
5. Admin approves order.
6. Service creates `devices` with `pending`.
7. Service allocates VPN IP.
8. Service generates keypair and PSK.
9. Service renders client config and QR payload.
10. Service encrypts private key and PSK.
11. Service marks device active and order fulfilled only after the local workflow succeeds.

## Защита данных

- `APP_SECRET_KEY` обязателен и не должен быть слабым.
- Private keys и PSK хранятся только в зашифрованном виде.
- Full configs, tokens и secrets не логируются.
- Errors from decryption are normalized, чтобы не раскрывать детали.
- Redaction применяется к logs/reports.

## Backup и Restore

Backup должен быть encrypted, checksum-protected и иметь manifest. Restore должен:

- проверять archive structure;
- проверять checksum;
- валидировать SQLite schema;
- проверять, что active devices имеют расшифровываемые secrets;
- не перезаписывать target DB до завершения всех проверок.

## Testing

Тесты покрывают:

- settings validation;
- crypto and redaction;
- DB constraints and repositories;
- IP allocation;
- AmneziaWG config rendering;
- access approval transactionality;
- backup create/verify/restore safety;
- minimal bot factory.

## Acceptance Criteria

- Local tests pass.
- Weak `APP_SECRET_KEY` rejected outside explicit test mode.
- Secrets encrypted in DB.
- Restore rejects corrupted or incompatible backups before writing target.
- Admin approval creates active device and fulfilled order atomically.
- Generated config includes expected AmneziaWG 2.0 fields.
