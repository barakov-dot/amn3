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

## API surface checklist для VPN/control-panel upstream

При анализе API surface фиксировать:

- OpenAPI/tag groups и совпадают ли они с фактическими route groups;
- какие endpoints являются UI templates, JSON API, self-service или public links;
- какой guard используется: session, bearer token, public token, bot callback;
- какие роли допускаются: admin, support, user, anonymous;
- где есть secret-read operations: config download, token creation, backup download;
- где есть remote-exec operations: install, uninstall, restart, reboot, clear;
- где есть destructive operations и есть ли dry-run/confirmation/audit;
- где raw config редактируется напрямую;
- есть ли единая policy matrix или guards разбросаны по handlers;
- какие tests нужны для forbidden access и ownership boundaries.

## Manager architecture checklist для VPN/control-panel upstream

При анализе manager/SSH/protocol слоя обязательно фиксировать:

- есть ли общий remote execution layer или команды разбросаны по manager-ам;
- как проверяются SSH host keys и есть ли enrollment/pinning;
- как передаются sudo credentials и могут ли они попасть в command line;
- логируются ли команды, stdout/stderr и как работает redaction;
- какие операции являются read-only, state-write, remote-exec и destructive;
- есть ли dry-run, plan preview, explicit confirmation и recovery note;
- какие manager-ы меняют firewall, sysctl, Docker networks, volumes, images и host files;
- используются ли pinned images/artifacts или `latest`/download-at-install;
- есть ли static network/IP assumptions и conflict detection;
- как manager распознает existing server layout и отличает read-only detect от auto-fix;
- как устроены long-running operations: sync request, background job, progress, timeout, cancellation;
- какие test doubles нужны для SSH runner и protocol manager contract.

## Повторяющиеся сигналы между upstream-проектами

Если две и более независимые VPN/control-panel системы повторяют одну идею, повышать ее приоритет как candidate для design review, но не снижать license/security gate.

После `PRVTPRO/Amnezia-Web-Panel` и `wg-easy/wg-easy` отдельно проверять:

- config delivery как `secret-read` surface;
- public/share/one-time links: token entropy, hash storage, expiry, revoke, rate limit, audit;
- public-safe read models без private keys и pre-shared keys;
- route permission wrappers и обязательный resource/ownership check;
- metrics labels как возможную утечку user/client/IP metadata;
- Docker capabilities, sysctls, firewall и host network changes как remote/host risk;
- client expiration и disable/revoke semantics.

## Config delivery checklist для VPN/control-panel upstream

При deep-dive по выдаче VPN-конфигов проверять:

- какие delivery surfaces есть: authenticated download, QR, public link, API token, bot;
- считается ли config/QR/URI `secret-read`;
- где проверяется ownership/resource permission;
- как генерируется public/share/one-time token;
- хранится ли token как hash или plaintext;
- есть ли server-side expiry check до выдачи config;
- что происходит при повторном использовании one-time link;
- есть ли revoke, rate limit и audit;
- попадают ли config body, QR payload или token в logs/errors/backup;
- есть ли public-safe read models без private keys и pre-shared keys.
