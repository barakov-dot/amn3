# AMN2 Support/News Bot Asset Inventory

Дата: 2026-06-11.

Статус: `P5-M001` closed as AMN3 docs-only/local-only inventory.

Этот документ фиксирует границу будущих отдельных support/news-ботов. Он не
добавляет runtime, не копирует ассеты в AMN2, не включает новые Telegram tokens
и не меняет текущий access bot.

## Safety Boundary

По умолчанию Phase 5 остается controlled operator-only pilot:

- live VPS commands: no;
- SSH commands: no;
- deploy/restart/package apply: no;
- public exposure: no;
- config delivery, `.conf`, QR, `vpn://`: no;
- `/api/clients` write CRUD: no;
- Local Agent mutations: no;
- backup/import/reboot: no;
- production peer/user mutation: no;
- destructive VPS/provider action: no;
- upstream/GPL code or asset copy: no.

`VPS_APPLY_ENABLED` остается `false`.

## Known Assets

| Asset | Intended owner | Current status | Notes |
| --- | --- | --- | --- |
| `NEOBYATNAYA-AMNZ-BOT.png` | Current access bot | Tracked in AMN2 current remote head at `app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png` | Used by current `/start` access-bot header. Observed in existing AMN2 worktrees with size `7984633` bytes. |
| `NEOBYATNAYA-AMNZ-SUPPORT-BOT.png` | Future support bot | Planning-only reference | Not tracked in AMN2 current remote head; not found in the local AMN3/AMN2 filesystem search for this slice. |
| `NEOBYATNAYA-AMNZ-NEWS-BOT.png` | Future news bot | Planning-only reference | Not tracked in AMN2 current remote head; not found in the local AMN3/AMN2 filesystem search for this slice. |
| `NEOBYATNAYA-AMNZ-ADMIN-PANEL.png` | Future admin panel design slice | Out of scope for support/news bot inventory | Belongs to `P5-M004` admin panel header asset boundary, not to any bot runtime. |

## Bot Media Surfaces

There are two different bot media surfaces, and they must not be treated as the
same control.

External reference checked on 2026-06-11: Telegram Bot API documents
`sendPhoto` for message photos and `setMyProfilePhoto` / `removeMyProfilePhoto`
for bot profile photos:

```text
https://core.telegram.org/bots/api
```

| Surface | Where it belongs | Phase 5 default | Future tool shape |
| --- | --- | --- | --- |
| Start/header image sent inside `/start` or onboarding messages | AMN2 bot runtime/assets | Local-only design and tests are allowed; no live send by Codex | Operator-only local upload/registry can validate and select per-bot header images before runtime implementation. |
| Telegram bot profile icon/avatar shown by Telegram client | Telegram bot identity for each bot token/username | No live mutation without a named Telegram identity gate | Technically can be changed through Telegram Bot API `setMyProfilePhoto`/`removeMyProfilePhoto` or manually by the operator; any apply is live Telegram-side mutation. |

Implication:

- support/news/access bot header images can be designed as AMN2 local assets;
- profile icons for access/support/news bots require per-bot identity ownership
  and separate operator approval;
- a public/user bot command must not upload or change bot media;
- upload, if implemented, belongs in an operator-only admin/CLI surface with
  local validation first.

Suggested future local registry fields:

```text
bot_kind: access | support | news
telegram_username: operator-filled, no token
start_header_asset: local path or packaged asset id
profile_icon_asset: local path or operator-selected asset id
profile_icon_apply_mode: manual-botfather | telegram-bot-api-gated
telegram_file_id_cache: optional, after operator-approved live upload only
status: planning | local-validated | staged | applied-by-operator
```

Validation requirements before any implementation:

- allowed file types and max size are explicit;
- image dimensions and transparent background behavior are documented;
- filenames do not include secrets, tokens or user identifiers;
- safe metadata excludes raw Telegram tokens and live `file_id` values unless
  the operator explicitly classifies them;
- tests prove that normal users cannot upload, replace or apply bot media.

## Current Access Bot Ownership

The current AMN2 access bot remains the only bot runtime in scope today.

It owns:

- `/start` onboarding and language selection;
- config request and approval workflow;
- tariff, traffic and device views;
- admin pending/users/traffic/templates views;
- admin approval and local device workflows;
- config delivery/resend paths when allowed by existing AMN2 policy;
- manual admin commands already present in AMN2.

Future support/news bots must not reuse current access-bot callbacks, tokens or
admin workflows.

## Future Support Bot Boundary

Purpose: operator support intake, safe help text and public-safe status
guidance.

Candidate command set:

- `/start`
- `/help`
- `/status`
- `/faq`
- `/contact`
- `/support` or `/ticket`
- `/privacy`

Allowed content:

- Russian-first support intake copy;
- generic troubleshooting guidance;
- support ticket or manual triage wording after a separate design gate;
- aggregate/public-safe service status only.

Forbidden by default:

- config issuance, `.conf`, QR or `vpn://` output;
- approval/revoke/create peer actions;
- per-user traffic/device/private account data;
- AMN2 database mutations;
- access-bot admin commands such as admin grant, user add or order creation;
- live VPS commands, deploy/restart/package apply, backup/import/reboot;
- sharing tokens, endpoints, server config or private support diagnostics.

Draft Russian-first copy inventory:

```text
/start:
Здравствуйте. Это бот поддержки NEOBYATNAYA AMNZ. Здесь можно описать проблему с подключением или оплатой. Конфиги и QR здесь не выдаются.

/help:
Опишите проблему одним сообщением. Не отправляйте private key, PSK, QR, vpn:// или .conf в чат.

/status:
Статус сервиса публикуется только в общем виде. Персональные устройства, трафик и конфиги здесь не показываются.
```

Implementation gate before any code:

- separate Telegram token and bot username;
- separate header image and profile icon decision;
- separate runtime/process decision;
- data retention and privacy policy for support messages;
- no access to config delivery by default;
- local tests for command routing and secret-output denial;
- named gate if support writes tickets, touches AMN2 data or posts to an external system.

## Future News Bot Boundary

Purpose: announcements only.

Candidate command set:

- `/start`
- `/subscribe`
- `/unsubscribe`
- `/latest`
- `/archive`
- `/language`

Allowed content:

- service announcements;
- operator-written instructions;
- maintenance notices;
- public-safe links and copy.

Forbidden by default:

- support intake that asks for personal VPN data;
- config issuance, `.conf`, QR or `vpn://` output;
- per-user traffic/device/account state;
- admin actions or approval workflows;
- AMN2 database mutations;
- live VPS commands, deploy/restart/package apply, backup/import/reboot;
- secrets, endpoints, private server config or non-public URLs.

Draft Russian-first copy inventory:

```text
/start:
Новости NEOBYATNAYA AMNZ: обновления сервиса, инструкции и плановые уведомления. Конфиги и поддержка здесь не выдаются.

/latest:
Последние новости и инструкции публикуются без персональных данных, ключей, QR, .conf и vpn:// ссылок.

/unsubscribe:
Вы отписались от новостей. Это не меняет VPN-доступ, устройства или тариф.
```

Implementation gate before any code:

- separate Telegram token and bot username;
- separate header image and profile icon decision;
- explicit subscribe/unsubscribe and consent behavior;
- broadcast rate and audit policy;
- local tests for public-safe copy and secret-output denial;
- named gate if any broadcast touches real users or external delivery systems.

## Shared Negative Controls

Future support/news bot work must keep these controls unless a separate named
gate changes them:

- no current access-bot token reuse;
- no live Telegram sends by Codex;
- no bot profile icon/avatar changes by Codex without a named Telegram identity
  gate;
- no config delivery or import artifact output;
- no AMN2 production peer/user mutation;
- no Local Agent write/config routes;
- no public/self-service expansion;
- no upstream/GPL code, UI, workflow or asset copy.

## Next Step

`P5-M001` is closed. The next safe local-only recommendation is `P5-M005`
Bot media asset upload/apply boundary, because per-bot header images and
Telegram profile icons now need a separate operator-only upload/registry design
before any implementation or live Telegram identity mutation.
