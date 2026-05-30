# Идеи для общего Codex skill

Здесь фиксируются выводы, которые могут стать частью общего Codex skill для безопасного анализа внешних проектов.

## Первый вывод

При анализе внешнего VPN-проекта всегда начинать с license verdict:

- какая лицензия указана;
- можно ли переносить код;
- можно ли переносить только идеи;
- какие части требуют отдельной юридической проверки;
- какие идеи должны быть перепроектированы с нуля.

## Из PRVTPRO/Amnezia-Web-Panel

- Для GPL-3.0 upstream по умолчанию использовать режим `research-only`.
- Отделять `architecture idea` от `code implementation`.
- В карточке upstream явно писать: что можно изучать, что нельзя копировать, какие проверки нужны перед production-переносом.
- Для VPN/control-panel проектов отдельно проверять хранение секретов, SSH-модель, default credentials, rollback, audit log и тестовый план destructive operations.

## Auth/secrets checklist для VPN/control-panel upstream

При углубленном анализе auth и secrets обязательно фиксировать:

- bootstrap model: default password, one-time token, forced setup или external secret;
- session secret policy: persistent, generated, rotated, required in production;
- password hashing policy и наличие rate limiting;
- role matrix: какие endpoints доступны admin/support/user;
- auth method matrix: session cookie, bearer token, public link, bot callback;
- token model: plaintext/hash, prefix, scope, expiry, revoke, owner inheritance, audit;
- public config surfaces: share links, Telegram, self-service API, file download;
- secret inventory: SSH passwords, private keys, panel tokens, bot tokens, external API keys, SSL keys;
- backup policy: redacted/full, encrypted/plain, restore validation, audit;
- SSH host key policy и sudo policy;
- logging redaction: команды, stderr/stdout, tracebacks, external API errors.
