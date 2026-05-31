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

## GitHub watch checklist для VPN/control-panel upstream

После первичного deep-dive обязательно делать отдельный GitHub watch pass:

- проверить текущие open issues и PRs, не только README;
- выделить bug classes, которые повторяются у пользователей: config import, QR, empty state, port conflicts, crashes, partial failures;
- отличать feature requests от production-regression signals;
- проверять build/deploy files: Dockerfile, compose, requirements, package lock, workflows;
- искать mismatch между README prerequisites и Docker/runtime image;
- фиксировать encoding/build issues как отдельный repository quality signal;
- превращать issues в test-plan requirements для `amn2`, а не в копирование fixes;
- если issue содержит logs или configs, не переносить секретные фрагменты в lab docs;
- ссылаться на issue/PR URL и пересказывать содержание кратко, без длинного копирования текста.

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
- есть ли public-safe read models без private keys и pre-shared keys;
- разделены ли artifact types: raw `.conf`, import URI, QR payload, downloadable file;
- ясно ли, для какого target client генерируется QR и что именно в нем закодировано;
- есть ли byte-level tests для UTF-8, non-ASCII names и QR decode round-trip;
- проверяется ли `vpn://` как обратимо secret-bearing artifact, а не как обычная ссылка;
- есть ли единый manager export contract для всех protocol manager-ов;
- возвращают ли public/self-service endpoints sanitized errors без внутренних signatures, paths, command output и config fragments.

## Config delivery integrity signals

Если open issues upstream показывают, что QR не импортируется на Android, `.conf` ломается на non-ASCII name или manager падает на `get_client_config` signature mismatch, это фиксировать не как единичный баг, а как требование к test plan:

- QR должен декодироваться в тесте и совпадать с ожидаемым payload;
- `.conf` и import URI должны проходить round-trip без потери UTF-8 bytes;
- все protocol manager-ы должны проходить contract tests на config export;
- UI должен различать `.conf`, import URI и QR для конкретного target client;
- issue/PR выводы пересказывать кратко и со ссылкой, без копирования secret-bearing logs/configs.

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

## Server-installed API wrapper checklist

После анализа `kyoresuas/amnezia-api` добавить отдельный checklist для upstream, которые ставятся на VPN-сервер и дают HTTP API поверх локального runtime:

- какой privilege получает API process: Docker socket, root, sudo, systemd, host filesystem, VPN config paths;
- открыт ли API наружу или слушает local-only bind за reverse proxy;
- есть ли TLS story, если setup сам настраивает nginx;
- защищены ли `/docs`, `/metrics`, `/health`, backup/import и destructive endpoints;
- один ли shared API key используется для всех операций или есть scoped tokens;
- есть ли expiry, revoke, rotation, rate limit и audit для integration tokens;
- какие endpoints являются `read-only`, `secret-read`, `state-write`, `remote-exec`, `destructive`;
- есть ли redacted backup по умолчанию и отдельный encrypted/full backup режим;
- считается ли `vpn://` import link secret-bearing artifact наравне с QR и `.conf`;
- есть ли dry-run/preview для import, delete, reboot, restart и config rewrite;
- есть ли lock/queue для конкурентных writes в один config/clientsTable;
- как описаны partial failures между file write, live sync/restart и local metadata update;
- не попадают ли private key, PSK, API key, config body, QR payload или `vpn://` в logs/errors/metrics;
- есть ли staging/runtime tests, а не только lint/build.

## Redaction coverage checklist для VPN/control-panel work

Перед переносом любой функции, которая выдает config, token, agent credential или remote command output, проверять:

- считается ли `.conf`, QR payload/PNG и `vpn://` единым `client-config-secret`, даже если секрет закодирован обратимо;
- редактируется ли entire `vpn://` URI, а не только decoded config text;
- не попадают ли raw token, bearer header, Local Agent token, TOTP/otpauth URI, backup/recovery codes в logs, audit, diagnostics и errors;
- есть ли focused tests для `redact()` на realistic log formats, quoted/unquoted values, headers и reversible links;
- есть ли route/bot/web tests, что audit metadata содержит только ids/status/purpose, но не config/link/token;
- есть ли remote operation tests, что stdout/stderr/recovery note не раскрывают PSK, config block, private key или agent token;
- для binary QR PNG фиксировать не text-redaction, а запрет попадания в diagnostics/plain backup и отдельный payload round-trip test.
