# AMN2 Bot Media Asset Upload/Apply Boundary

Дата: 2026-06-11.

Статус: `P5-M005` closed as AMN3 docs-only/local-only design boundary.

Этот документ фиксирует безопасную модель для будущего инструмента загрузки и
выбора медиа для access/support/news ботов. Он не реализует upload runtime, не
копирует ассеты в AMN2, не вызывает Telegram API и не меняет live bot identity.

## Scope

Covered bot kinds:

- `access`: текущий AMN2 access bot;
- `support`: будущий отдельный support bot;
- `news`: будущий отдельный news bot.

Covered media surfaces:

- `start_header`: картинка, отправляемая внутри `/start` или onboarding
  сообщения;
- `profile_icon`: иконка/аватар самого Telegram-бота.

External Telegram reference checked on 2026-06-11:

```text
https://core.telegram.org/bots/api
relevant methods: sendPhoto, setMyProfilePhoto, removeMyProfilePhoto
```

## Surface Boundary

| Surface | Technical mechanism | Phase 5 default | Gate |
| --- | --- | --- | --- |
| `start_header` | AMN2 stores/selects local asset, bot runtime later sends it with message/photo flow | Local-only registry/design/tests allowed | Runtime send still needs an AMN2 local implementation slice; live send by Codex is not allowed by default. |
| `profile_icon` | Telegram bot profile photo for a specific bot token/username | Local-only staging/metadata only | Any apply through Bot API or manual BotFather/operator action is a live Telegram identity mutation and needs a named gate. |

The two surfaces may use the same source image file, but they are different
controls. A valid header image does not automatically authorize changing the
Telegram profile icon.

## Recommended Approach

Use a three-stage model.

1. Local validation.
   Operator provides a local image path. AMN2 validates file type, size,
   dimensions, readable bytes and safe filename. No Telegram call is made.

2. Local registry selection.
   AMN2 records safe metadata and selected bot/surface mapping. It can support
   packaged assets and operator-uploaded private assets. The registry does not
   store Telegram tokens.

3. Separate apply decision.
   `start_header` runtime use can be implemented later as AMN2 local-only
   behavior. `profile_icon` apply requires a named Telegram identity gate and
   an operator-supplied token channel.

This is preferred over a direct "upload and apply" button because it gives the
operator preview, audit and stop points before any live Telegram mutation.

## Alternatives Considered

### A. Manual-only asset management

The operator places files in the repo/worktree and changes BotFather or
Telegram settings manually.

Pros:

- smallest implementation surface;
- no Telegram API integration;
- simple for one bot.

Cons:

- easy to drift across access/support/news bots;
- no local validation contract;
- no repeatable evidence for which asset belongs to which bot.

### B. Operator-only local registry

AMN2 provides CLI/admin-local validation and selection, but does not perform
live Telegram profile changes by default.

Pros:

- repeatable and testable;
- keeps tokens out of stored metadata;
- supports separate access/support/news assets;
- future runtime can consume one clean manifest.

Cons:

- requires a small local implementation slice later;
- profile icon still needs a separate apply gate.

Verdict: recommended first implementation path.

### C. Full Telegram API apply from AMN2

AMN2 validates, uploads and applies profile icons through Telegram Bot API.

Pros:

- convenient once production ownership is mature;
- can produce audit evidence for applied icons.

Cons:

- needs live bot token access;
- mutates external Telegram identity;
- requires stronger auth, audit, rollback and operator confirmation;
- out of Phase 5 default scope.

Verdict: future named-gate-only path.

## Future Registry Contract

Suggested safe metadata fields:

```text
asset_id: stable local id
bot_kind: access | support | news
telegram_username: operator-filled username, no token
surface: start_header | profile_icon
source_filename: sanitized basename
content_sha256: hash of local file bytes
mime_type: image/png | image/jpeg | image/webp
byte_size: integer
width_px: integer
height_px: integer
validation_status: valid | invalid
selected_for_runtime: true | false
apply_status: local-only | staged-for-operator | applied-by-operator
applied_at: optional operator-recorded timestamp
applied_by: optional operator identity
notes: optional safe text
```

Fields that must not be stored by default:

- raw Telegram bot token;
- raw API request/response with token-bearing URL or headers;
- secret-bearing diagnostic output;
- user-uploaded filename if it contains tokens, IDs or private support data;
- live Telegram `file_id` unless separately classified and redacted.

## Validation Requirements

Before any AMN2 implementation, define exact limits in tests/docs:

- accepted extensions and MIME types;
- maximum bytes for each surface;
- minimum and recommended dimensions;
- square/crop expectations for `profile_icon`;
- aspect ratio expectations for `start_header`;
- behavior for transparent PNG/WebP;
- image decoding failure behavior;
- deterministic content hash;
- safe copy path outside public/static routes unless explicitly approved;
- no executable content, archives or remote URLs.

Suggested conservative defaults for the first local slice:

```text
accepted types: PNG, JPEG, WebP
max bytes: 10 MB
profile_icon recommended: square image, at least 512x512
start_header recommended: landscape or square image, at least 512px wide
remote URL upload: disabled
normal user upload: disabled
```

The exact limits should be adjusted during AMN2 implementation against the
current bot library and Telegram API behavior.

## Operator UX Boundary

Allowed future local surfaces:

- CLI validation command;
- CLI registry/select command;
- private/admin-only web form after route/auth review;
- read-only registry preview in admin UI.

Not allowed by default:

- public upload route;
- Telegram user command to upload media;
- applying `profile_icon` from a normal user flow;
- automatic apply during deploy/restart;
- storing tokens in the media registry;
- exposing uploaded files through public static URLs.

Candidate future CLI shape:

```text
python -m app.cli bot-media validate --bot-kind access --surface start_header --path <local-image>
python -m app.cli bot-media stage --bot-kind support --surface profile_icon --path <local-image>
python -m app.cli bot-media select --bot-kind news --surface start_header --asset-id <asset-id>
python -m app.cli bot-media manifest
```

Future gated apply command, not Phase 5 default:

```text
python -m app.cli bot-media apply-profile-icon --bot-kind support --asset-id <asset-id> --named-gate <gate-id>
```

The apply command must be impossible to run unless a named Telegram identity
gate exists, the operator provides the token through a local secret channel and
the command prints a secret-free preview before making the Bot API request.

## Audit And Evidence

Local validation/selection evidence may include:

- bot kind;
- surface;
- asset id;
- SHA-256;
- sanitized filename;
- dimensions;
- MIME type;
- byte size;
- validation result;
- selected runtime mapping.

Live apply evidence, only after a named gate, may include:

- gate id;
- bot kind and username;
- asset id and SHA-256;
- before/after profile-photo status as safe summary;
- Telegram API method name;
- redacted success/failure status.

Live apply evidence must not include:

- bot token;
- raw Authorization/header/query material;
- raw multipart payload;
- private support/user data.

## Stop Conditions

Stop and do not implement/apply if any of these are true:

- upload path requires public exposure;
- profile icon apply would need token storage in repo/docs/registry;
- normal users can upload or change bot media;
- support/news bot token ownership is not separate from access bot;
- asset source/license is unclear;
- image contains secrets, QR codes, `.conf`, `vpn://`, private server data or
  user identifiers;
- live Telegram apply is requested without a named gate.

## Active Plan Update

Remove from active Phase 5 plan:

```text
P5-M005 Bot media asset upload/apply boundary
```

The original next safe local-only recommendation was completed later:

```text
P5-M004 Admin panel header asset boundary
```

Current next safe local-only recommendation:

```text
P5-M002 QA клиентских инструкций доставки конфигурации
```
