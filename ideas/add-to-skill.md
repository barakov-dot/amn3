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

## Permissions/auth/2FA checklist для VPN/control-panel upstream

При deep-dive по permissions, auth и 2FA проверять:

- какие auth methods есть: session, Basic Auth, bearer token, public link, bootstrap, bot;
- может ли какой-то auth method обходить 2FA или role checks;
- есть ли forced setup/bootstrap вместо default credentials;
- где хранится session secret и есть ли production persistence/rotation;
- как устроены роли, actions, ownership и resource checks;
- заставляет ли route wrapper handler выполнить ownership check;
- есть ли broad action вроде `custom`, который скрывает разные risk classes;
- как disabled/demoted user влияет на session и tokens;
- как хранится TOTP secret и попадает ли он в backup/logs;
- есть ли recovery codes или documented recovery flow;
- есть ли rate limit, lockout и audit для login/TOTP failures;
- отделены ли browser session и integration tokens по scopes, expiry и revoke.

## Metrics/observability checklist для VPN/control-panel upstream

При deep-dive по metrics surface проверять:

- какие endpoints есть: Prometheus, JSON, health, status, dashboard API;
- включены ли metrics по умолчанию или требуют explicit enable;
- обязательна ли auth, или bearer/password опционален;
- какие labels/fields раскрывают client name, user identity, IP, endpoint, public key, traffic, handshake;
- есть ли separate aggregate и detailed modes;
- какие metrics уходят в long-retention monitoring systems;
- есть ли scoped token, expiry, revoke, owner inheritance и audit;
- не попадают ли metrics token/password/hash в обычный config export;
- есть ли rate limit, scrape allowlist или local-only bind;
- есть ли tests, что private keys, pre-shared keys, raw configs и tokens не попадают в metrics.

## Operational docs/migration checklist для VPN/control-panel upstream

При анализе docs и migration guide проверять:

- есть ли отдельные docs для install, setup, update, migration, API, CLI, recovery;
- описана ли image/tag/version policy и запрещен ли unsafe `latest` default;
- начинается ли migration с backup и compatibility limits;
- есть ли preflight/dry-run, redacted preview, rollback и recovery story;
- какие secrets содержат backup/import files;
- совпадает ли setup/migration guide с реальным UI/API flow;
- есть ли unattended/headless setup и как очищаются bootstrap secrets;
- требует ли API отключения 2FA или использует password-only auth;
- какие CLI команды выводят configs, QR, tokens или secret state;
- есть ли tests или checklist, что docs не расходятся с route guards и behavior.
