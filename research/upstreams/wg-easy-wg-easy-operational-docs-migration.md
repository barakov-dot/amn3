# wg-easy/wg-easy: operational docs и migration guide

## Паспорт deep-dive

- Upstream: https://github.com/wg-easy/wg-easy
- Дата анализа: 2026-05-30
- Область: docs site, getting started, tag policy, setup/migration docs, unattended setup, API docs, CLI docs, update docs.
- License verdict: AGPL-3.0-only, режим `research-only`.
- Production verdict для `amn2`: переносить только maturity patterns, checklist и risk signals; не копировать docs text, commands, migration code, UI или schemas.

## Краткий вывод

`wg-easy` показывает, что production-подход к VPN-панели состоит не только из API и UI. У проекта есть отдельная docs surface: getting started, setup, CLI, 2FA, metrics, unattended setup, auto-updates, API warning и migration guide from v14 to v15.

Для `amn2` главный полезный вывод: docs должны быть частью safety model. Если продукт умеет устанавливать VPN, выдавать configs, мигрировать state или обновляться, документация должна явно фиксировать supported paths, backup steps, version tags, breaking changes, recovery и security caveats.

Главный risk signal: некоторые upstream docs честно описывают небезопасные или незрелые места. Например API docs говорят, что API использует Basic Authentication, а при включенной 2FA API не работает. Для `amn2` такой подход нельзя переносить как production API model, но сам факт честного предупреждения полезен как operational maturity pattern.

## Operational docs surfaces

| Surface | Upstream file | Что фиксирует | Вывод для `amn2` |
| --- | --- | --- | --- |
| Getting started | `docs/content/getting-started.md` | requirements, supported architecture, container runtime, image tags, warning about compose up/down | docs must pin deployment assumptions and unsafe commands |
| Migration index | `docs/content/advanced/migrate/index.md` | list of migration guides | migration docs should be versioned per breaking change |
| v14 to v15 migration | `docs/content/advanced/migrate/from-14-to-15.md` | backup, old container stop, new setup wizard import, env variable caveat | migration must start with backup and explicit compatibility limits |
| Setup guide | `docs/content/guides/setup.md` | first-run flow and existing config import | setup docs should match actual wizard paths |
| Unattended setup | `docs/content/advanced/config/unattended-setup.md` | first-start env vars, grouping constraints, security note | headless setup needs one-time semantics and secret cleanup guidance |
| CLI guide | `docs/content/guides/cli.md` | admin password reset, clients list, QR output | recovery/CLI surfaces need risk classification |
| API guide | `docs/content/advanced/api.md` | unstable API warning, Basic Auth, 2FA limitation | docs should expose limitations, but production API needs scoped tokens |
| Auto updates | `docs/content/examples/tutorials/auto-updates.md` | compose update, Watchtower, podman auto-update | update path needs pinning, rollback, supply-chain guidance |
| Release utility | `src/server/utils/release.ts` | latest release fetch and cached changelog | UI can surface update info, but network fetch must be optional and robust |

## Migration guide pattern

The v14 to v15 migration guide has useful structure:

- states that v15 is a complete rewrite;
- names architecture limitations for armv6/armv7;
- calls out HTTP access requiring `INSECURE=true`;
- starts with backup of existing `wg0.json`;
- tells user to back up old environment variables;
- separates old container stop from new container start;
- sends user through setup wizard import;
- warns that v15 changed environment variables and many settings moved to Admin Panel.

This is useful for `amn2` as a documentation pattern:

- every breaking migration needs a dedicated guide;
- backup comes before stopping/changing services;
- compatibility limits must be explicit;
- changed configuration model must be named;
- import path should be linked to UI flow and API behavior;
- successful migration should define what was migrated and what was not.

What is not enough for `amn2`:

- no visible preflight/dry-run result in the guide;
- no visible rollback path after failed import;
- no checksum/signature guidance for backup file;
- no explicit secret inventory for imported file;
- no audit/recovery note requirement;
- no production test plan for migration.

## Migration implementation signals

The setup migration route:

- accepts uploaded file content;
- parses JSON;
- validates expected v14 shape with Zod;
- imports server private/public key;
- derives IPv4 CIDR from old server address;
- assigns default IPv6 CIDR;
- imports clients with private key, public key, pre-shared key, name, address and enabled state;
- sets setup step to done.

Positive signals:

- schema validation exists before import;
- migration runs only through setup handler state;
- old client ids are treated as compatibility detail and not required;
- config import is part of first-run setup, not a hidden admin endpoint.

Risk signals:

- migration writes secret material and client state directly;
- imported backup contains private keys and pre-shared keys;
- no visible dry-run/preview in the route;
- no visible rollback snapshot in the route;
- no visible audit event in setup migration;
- default IPv6 assignment may surprise operator if old deployment was IPv4-only;
- errors are not described as operator-facing recovery steps in the guide.

Для `amn2`: migration/import is a `state-write` plus `secret-import` operation. If it touches live server config, it can become `remote-exec`. It needs a preflight plan, redacted summary, backup-before-write, rollback note and tests.

## Tagging and update docs

Getting started docs explicitly describe image tags:

- major tag `15` recommended as latest minor for the major version;
- minor tag `15.0`;
- patch tag `15.0.0`;
- `edge`;
- `development`;
- `latest`, which points to v14 and should be avoided.

This is a strong maturity signal: docs warn that `latest` is not the safe path.

Auto-update docs show simple update commands and Watchtower/Podman paths. Useful idea: operational docs should include an update path. Risk for `amn2`: automatic update through mutable tags or third-party updater is not enough as production guidance unless there is:

- pinned version strategy;
- changelog and breaking-change gate;
- backup-before-update;
- rollback path;
- health check after update;
- notification/audit;
- supply-chain policy for images.

## API docs honesty

API docs have a warning that API is not stable and endpoints are not documented yet. They also say API uses Basic Authentication with the same username/password as web login, and if 2FA is used, API will not work.

For `amn2`, this creates two separate conclusions:

- good pattern: docs must honestly mark unstable API and auth limitations;
- rejected pattern: Basic Auth API that conflicts with 2FA is not acceptable production API.

Production alternative:

- stable API contract only after route policy;
- OpenAPI or endpoint matrix tied to tests;
- scoped API tokens for integration access;
- 2FA remains browser/session account protection;
- sensitive endpoints require scopes, expiry, revoke and audit.

## Unattended setup

Unattended setup docs describe first-start environment variables and group constraints. They also warn that initial username/password are not checked for complexity and recommend removing variables after setup.

Useful idea:

- headless setup is important for automation/Ansible-like deployment;
- grouped configuration constraints should be documented;
- first-start only semantics should be explicit.

Risk:

- environment variables can leak through process inspection, compose files, shell history or support bundles;
- weak initial password can pass unattended setup;
- docs rely on operator cleanup after setup;
- no visible one-time bootstrap secret or automatic redaction model in docs.

For `amn2`: headless bootstrap should use one-time bootstrap token or local first-run secret, reject weak credentials, and record that bootstrap was closed.

## CLI and recovery

CLI docs include admin password reset and client QR display. These are useful recovery/operator surfaces, but they are not neutral:

- password reset is account recovery and should be audited or restricted to local/admin environment;
- QR display is config delivery and should be treated as `secret-read`;
- client list can leak metadata;
- CLI flags such as IPv6 behavior need to match deployment state.

For `amn2`, CLI/recovery commands should be part of the same policy matrix as API/UI:

- command id;
- risk class;
- required local context;
- secret output policy;
- audit/recovery note;
- tests for redaction.

## Что полезно для `amn2`

- Versioned migration guides for breaking changes.
- Backup-first migration instructions.
- Compatibility limitations called out before migration.
- Setup wizard path for config import.
- Tagging convention docs and warning against unsafe tags.
- Honest API stability/auth limitations in docs.
- Unattended setup docs with grouped variables and first-start semantics.
- CLI recovery docs.
- Update docs with explicit commands.

## Что полезно для будущего гибридного проекта

- Docs as product surface: install, setup, migration, API, CLI, metrics, examples.
- Per-protocol migration guide pattern.
- Config import wizard as migration/onboarding flow.
- Operational playbooks: backup, update, rollback, recovery.
- Tag/version policy visible to operators.
- Automation/headless setup path for teams.

## Что нельзя переносить как есть

- AGPL-licensed docs text, migration UI/API code or schema.
- Basic Auth API that requires disabling 2FA.
- Migration import without dry-run/preview/rollback/audit.
- Secret-bearing backup import without secret inventory and redacted diagnostics.
- Headless setup credentials that remain in env/config after first start.
- Auto-update guidance without pinning, backup, health check and rollback.
- CLI QR/config output without `secret-read` policy.

## Risk findings

| Finding | Почему важно для `amn2` |
| --- | --- |
| Migration backup contains private keys and client secrets | backup/import must be secret-aware and redacted in diagnostics |
| Migration route writes state directly after parse | production import should have preflight, preview and rollback |
| API docs require Basic Auth and say 2FA users cannot use API | integration auth must be scoped tokens, not password auth |
| Unattended setup passes initial password through env | bootstrap secrets need one-time handling and cleanup |
| Auto-update docs include mutable-update flows | production update needs pinned versions, backup and rollback |
| CLI can reset password and display QR config | CLI commands need risk classification and secret-output policy |

## Test-plan идеи для `amn2`

Минимальные tests перед production-переносом похожих идей:

- migration file validation rejects invalid schema before any write;
- migration preflight reports what will change without writing;
- migration redacted preview never includes private keys or pre-shared keys;
- migration creates backup-before-write or blocks if backup unavailable;
- failed migration leaves old state untouched or provides recovery note;
- successful migration records source version and migration id;
- imported secrets enter secret inventory;
- setup/bootstrap cannot run after completion;
- unattended setup rejects weak initial password;
- bootstrap secret removed or invalidated after first use;
- API docs/generated route matrix matches actual auth guards;
- integration API cannot require disabling 2FA;
- CLI QR/config commands are classified as `secret-read`;
- update flow requires pinned version or explicit risk acknowledgement;
- update docs link to rollback and health check.

## Решение для lab

Статус deep-dive: `completed-first-pass`.

Для `amn2` docs/migration work should become a transfer gate, not a late polish task. Any feature that changes deployment, secrets, config delivery, backup/import or remote server state needs:

- operator-facing docs;
- backup and rollback story;
- route/CLI policy;
- tests that docs assumptions match behavior;
- explicit rejected patterns for unsafe shortcuts.

Before real production transfer, open current `amn2` and inventory existing docs for install, update, backup, migration, API, CLI and recovery.

## Источники

- Репозиторий: https://github.com/wg-easy/wg-easy
- README: https://github.com/wg-easy/wg-easy/blob/master/README.md
- Getting started: https://github.com/wg-easy/wg-easy/blob/master/docs/content/getting-started.md
- Migration index: https://github.com/wg-easy/wg-easy/blob/master/docs/content/advanced/migrate/index.md
- v14 to v15 migration: https://github.com/wg-easy/wg-easy/blob/master/docs/content/advanced/migrate/from-14-to-15.md
- Setup guide: https://github.com/wg-easy/wg-easy/blob/master/docs/content/guides/setup.md
- Unattended setup: https://github.com/wg-easy/wg-easy/blob/master/docs/content/advanced/config/unattended-setup.md
- CLI guide: https://github.com/wg-easy/wg-easy/blob/master/docs/content/guides/cli.md
- API guide: https://github.com/wg-easy/wg-easy/blob/master/docs/content/advanced/api.md
- Auto updates: https://github.com/wg-easy/wg-easy/blob/master/docs/content/examples/tutorials/auto-updates.md
- `setup/migrate.post.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/api/setup/migrate.post.ts
- `setup/migrate.vue`: https://github.com/wg-easy/wg-easy/blob/master/src/app/pages/setup/migrate.vue
- `release.ts`: https://github.com/wg-easy/wg-easy/blob/master/src/server/utils/release.ts
- First-pass upstream card: [wg-easy-wg-easy.md](wg-easy-wg-easy.md)
