# Phase 5 Support/News Bot Asset Inventory 2026-06-11

Дата: 2026-06-11.

## Итог

`P5-M001` закрыт как AMN3 docs-only/local-only inventory slice.

Created inventory:

```text
docs/AMN2_SUPPORT_NEWS_BOT_ASSET_INVENTORY.ru.md
```

## Что зафиксировано

- Current access bot owns only the existing `NEOBYATNAYA-AMNZ-BOT.png` header,
  `/start` language selector, config request/approval, tariff/traffic/device
  views, admin views and existing config delivery/resend paths.
- `NEOBYATNAYA-AMNZ-SUPPORT-BOT.png` and `NEOBYATNAYA-AMNZ-NEWS-BOT.png` remain
  planning-only references for future separate bot runtimes.
- `NEOBYATNAYA-AMNZ-ADMIN-PANEL.png` is explicitly out of support/news bot
  scope and belongs to the separate `P5-M004` admin panel header boundary.
- Future support bot scope is support intake, help/status/FAQ/contact copy and
  manual triage only, with no config output, no peer mutation and no AMN2 DB
  mutation by default.
- Future news bot scope is announcements/subscription/latest/archive copy only,
  with no support intake requiring private VPN data and no config/admin/runtime
  actions.
- Both future bots require separate Telegram tokens, bot usernames, runtime
  decisions, local tests and named gates before any live/user-facing behavior.
- Bot media was split into two surfaces: AMN2 runtime header images sent inside
  bot messages, and Telegram profile icons/avatars for each bot identity.
- Future header image upload can be local-only operator registry work; future
  profile icon apply is a live Telegram identity mutation and requires a
  separate named gate even though Telegram Bot API now exposes profile photo
  methods.

External Telegram reference checked on 2026-06-11:

```text
https://core.telegram.org/bots/api
methods noted: sendPhoto, setMyProfilePhoto, removeMyProfilePhoto
```

## Asset Search Evidence

Current AMN2 remote head checked:

```text
amn2/codex-vps-test-prep
23f18ef Add external-only backfill rehearsal
```

Tracked AMN2 asset result:

```text
app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png
```

No tracked current-head matches were found for:

```text
NEOBYATNAYA-AMNZ-SUPPORT-BOT.png
NEOBYATNAYA-AMNZ-NEWS-BOT.png
NEOBYATNAYA-AMNZ-ADMIN-PANEL.png
```

Local filesystem search found the current access-bot image only in existing
AMN2 worktrees:

```text
worktrees/amn2-bot-onboarding-language-header/app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png
worktrees/amn2-external-only-backfill-rehearsal/app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png
worktrees/amn2-runtime-toolchain-standardization/app/bot/assets/NEOBYATNAYA-AMNZ-BOT.png
size: 7984633 bytes
```

The support/news/admin asset filenames are therefore treated as planning inputs
recorded by prior Phase 4 notes, not as current runtime files.

## Safety

No AMN2 runtime code was changed. No asset was copied into AMN2. No live
Telegram token, live bot send, bot profile icon/avatar mutation, live VPS
command, SSH command, service restart, deploy, package apply/rebuild on VPS,
production peer/user mutation, public exposure, `/api/clients` CRUD, config
delivery, Local Agent mutation, backup/import/reboot, destructive provider
action or upstream/GPL code copy was performed.

This slice does not authorize support/news bot implementation. It only defines
ownership, command/copy boundaries and negative controls for future slices.

## Active Plan Update

Removed from active Phase 5 plan:

```text
P5-M001 Support/news bot asset inventory
```

Remaining gated items stay gated:

```text
P5-C001 Current-head package rebuild gate
P5-C002 VPS retention decision
P5-C003 Live rollout named gate
P5-C004 Secret handoff protocol
VPS-REBUILD-001 destructive gate remains defer
```

## Следующая рекомендация

The original follow-up, `P5-M005` Bot media asset upload/apply boundary, was
completed later in
`research/amn2/phase-5-bot-media-asset-upload-boundary-2026-06-11.md`.

`P5-M004` Граница ассета шапки веб-панели was also completed later in
`research/amn2/phase-5-web-admin-header-asset-boundary-2026-06-11.md`.

Current next safe local-only recommendation: `P5-M006` Одно нажатие для
копирования import-ссылки в Telegram.
