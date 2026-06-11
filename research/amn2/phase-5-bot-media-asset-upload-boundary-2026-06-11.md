# Phase 5 Bot Media Asset Upload/Apply Boundary 2026-06-11

Дата: 2026-06-11.

## Итог

`P5-M005` закрыт как AMN3 docs-only/local-only design-boundary slice.

Created boundary doc:

```text
docs/AMN2_BOT_MEDIA_ASSET_UPLOAD_BOUNDARY.ru.md
```

## Что зафиксировано

- Bot media split is explicit:
  - `start_header` is an AMN2 local/runtime asset surface for images sent inside
    `/start` or onboarding messages.
  - `profile_icon` is Telegram bot identity for a specific bot token/username.
- `start_header` can be prepared through a future local-only operator
  upload/registry and consumed by a later AMN2 local implementation slice.
- `profile_icon` can be staged locally, but any apply through Telegram Bot API
  or manual operator action is a live Telegram identity mutation and requires a
  separate named gate.
- Recommended future approach is a three-stage model: local validation, local
  registry selection, separate apply decision.
- Direct upload-and-apply is rejected as Phase 5 default because it requires
  bot token access and mutates external Telegram state.
- Future registry fields, validation requirements, operator UX boundaries, safe
  evidence fields and stop conditions are documented.

External Telegram reference checked on 2026-06-11:

```text
https://core.telegram.org/bots/api
methods noted: sendPhoto, setMyProfilePhoto, removeMyProfilePhoto
```

## Safety

No AMN2 runtime code was changed. No asset was copied into AMN2. No upload
handler, web route, CLI command, Telegram API call, Telegram token use, live bot
send, bot profile icon/avatar mutation, live VPS command, SSH command, service
restart, deploy, package apply/rebuild on VPS, production peer/user mutation,
public exposure, `/api/clients` CRUD, config delivery, Local Agent mutation,
backup/import/reboot, destructive provider action or upstream/GPL code copy was
performed.

This slice does not authorize bot media implementation. It only defines a safe
operator-only boundary for future local upload/registry and a named-gate
boundary for live Telegram profile icon apply.

## Active Plan Update

Removed from active Phase 5 plan:

```text
P5-M005 Bot media asset upload/apply boundary
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

The original follow-up, `P5-M004` Граница ассета шапки веб-панели, was
completed later in
`research/amn2/phase-5-web-admin-header-asset-boundary-2026-06-11.md`.

Current next safe local-only recommendation: `P5-M006` Одно нажатие для
копирования import-ссылки в Telegram.
