# AMN2 QA клиентских инструкций доставки конфигурации

Дата: 2026-06-11.

Назначение: дать оператору Phase 5 безопасный чеклист проверки клиентских инструкций доставки конфигурации в Telegram без публикации реальных секретов и без выполнения live delivery. Документ покрывает `.conf`, QR, `vpn://`, Android, iOS, Desktop и отдельное требование: import-ссылка может отправляться отдельным сообщением, но должна копироваться в буфер одним нажатием.

Этот документ не разрешает live VPS commands, SSH commands, deploy/restart/package apply, public exposure, config delivery, `/api/clients` write CRUD, Local Agent mutations, backup/import/reboot, production peer/user mutation, Telegram token use, live bot send or Telegram profile mutation. Любая проверка на реальном пользователе, реальном конфиге, live bot runtime или target VPS требует отдельного named gate.

## Текущий AMN2 Контекст

Источник поведения на момент создания QA: `barakov-dot/amn2`, branch `codex-vps-test-prep`, head `23f18ef`.

Статус follow-up на 2026-06-11: `P5-M006` advanced `codex-vps-test-prep` to `ad6aa1b` and added a bounded local Telegram copy affordance for import links that fit Bot API copy-text limits.

Текущая модель доставки:

- bot delivery формирует `.conf` файл;
- `vpn://` строится как `vpn://` + URL-safe base64 от полного UTF-8 текста `.conf`;
- QR содержит тот же `vpn://` payload;
- бот отправляет import-ссылку отдельным текстовым сообщением;
- ссылки на приложения отправляются отдельным сообщением;
- `.conf` остается надежным fallback;
- DefaultVPN QR не считается универсальным путем импорта;
- Android/iOS/Desktop совместимость зафиксирована в AMN2 compatibility matrix.

Артефакты `.conf`, QR payload/PNG и `vpn://` являются `client-config-secret`. Даже если `vpn://` не показывает `PrivateKey` как строку, он обратимо кодирует полный конфиг.

## Safe Evidence Policy

Разрешено фиксировать:

- redacted screenshots, где реальная `vpn://` ссылка, QR, `.conf` body, endpoint, private key, PSK and tokens скрыты;
- synthetic screenshots или local test fixtures без production secrets;
- boolean/status summary: `visible`, `copy_affordance_present`, `fallback_present`, `needs_fix`;
- client/platform name and version only when it does not reveal user/private state;
- safe issue labels and next actions.

Запрещено фиксировать:

- raw `.conf`;
- raw QR payload или QR image with real config;
- raw `vpn://`;
- private key, PSK, endpoint values, peer public key, Telegram token, admin/user identifiers;
- full Telegram export, full bot logs, full screenshots with visible secret-bearing payloads;
- user-specific production config files.

## Delivery Instruction QA Matrix

Для каждого проверенного клиента заполнять только safe summary.

```text
platform: Android | iOS | Windows Desktop | macOS Desktop | Linux Desktop
telegram_client:
target_app: AmneziaVPN | DefaultVPN | AmneziaWG | other
evidence_source: synthetic | redacted_operator_screenshot | local_test_fixture
real_secret_visible: no
main_message_russian_first: yes/no/not_checked
device_name_visible: yes/no/not_checked
config_version_visible: yes/no/not_checked
conf_file_visible: yes/no/not_checked
conf_filename_expected: yes/no/not_checked
vpn_link_separate_message: yes/no/not_checked
vpn_link_copy_affordance: copy_button | selectable_text_only | absent | not_checked
vpn_link_tap_behavior_claim: opens_import | copies_to_clipboard | not_claimed | unclear
qr_caption_honest: yes/no/not_checked
defaultvpn_fallback_text_visible: yes/no/not_applicable/not_checked
app_links_separate_message: yes/no/not_checked
platform_constraints_visible: yes/no/not_applicable/not_checked
secret_artifact_in_evidence: no
decision: pass | fallback_ok | needs_fix | defer | no-go
notes:
```

Pass criteria common to all clients:

- Russian-first text is clear and not mixed into an English-first block.
- `.conf` is presented as the reliable fallback.
- `vpn://` is separate from the long instruction text.
- QR caption says it contains an import link, not a universal guarantee.
- DefaultVPN guidance does not promise universal QR support.
- App links are in a separate message.
- Evidence contains no raw secret-bearing artifact.

## Android Checks

Target paths:

- Telegram for Android;
- AmneziaVPN Android 9+;
- AmneziaWG Android;
- older Android limitations as documented by the compatibility matrix.

Expected QA observations:

- `.conf` file can be identified by a device-name-based filename, e.g. `Neobyatnaya-AMNZ-N.conf`;
- `vpn://` is visible as a separate import link message;
- user can either open/import the link or copy it through an explicit copy affordance/fallback;
- QR is not described as the only or guaranteed path;
- app guidance does not promise unsupported Android 7/8 builds;
- no screenshot includes raw `vpn://`, QR payload or config body.

## iOS Checks

Target paths:

- Telegram for iOS;
- DefaultVPN on iOS;
- AmneziaWG Apple where applicable.

Expected QA observations:

- `.conf` is treated as the primary reliable fallback;
- `vpn://` appears as a separate import link message;
- DefaultVPN text says to use `.conf` or the separate import link if QR import fails;
- QR is marked as possibly unreliable for DefaultVPN;
- App Store availability wording is not overpromised;
- copy behavior is recorded as explicit copy button, selectable text fallback or unresolved issue.

## Desktop Checks

Target paths:

- Telegram Desktop on Windows/macOS/Linux;
- AmneziaWG Windows;
- AmneziaVPN desktop availability according to current compatibility notes.

Expected QA observations:

- `.conf` attachment is easy to locate and download;
- QR is not treated as the primary desktop path;
- `vpn://` text is visible/selectable if no copy button is available;
- Desktop platform constraints are not hidden behind mobile-only copy;
- no public/self-service route or web download is introduced to compensate for Telegram UX.

## Copy-to-Clipboard Requirement

Operator requirement: the bot may send the config import link as a separate message, but the user-facing UX goal is one tap to copy that link to the clipboard.

Current AMN2 state:

- the bot sends `vpn://` as a plain separate text message;
- there is no inline `copy_text` button in the current bot delivery;
- a normal text link tap should not be counted as satisfying this requirement because Telegram clients may treat link taps as open/import actions rather than clipboard copy.

Telegram Bot API feasibility:

- `InlineKeyboardButton.copy_text` can describe a button that copies specified text to clipboard: `https://core.telegram.org/bots/api#inlinekeyboardbutton`;
- the copied text is represented by `CopyTextButton.text`: `https://core.telegram.org/bots/api#copytextbutton`;
- Telegram documents `CopyTextButton.text` as 1-256 characters.

AMN2-specific constraint:

- current `vpn://` contains URL-safe base64 of the full UTF-8 `.conf`;
- real AMN2 `vpn://` payloads are expected to be longer than 256 characters;
- therefore a Bot API `copy_text` button cannot be assumed to copy the full raw `vpn://` link until the generated link length is measured and tested.

QA classification:

```text
copy_ready:
  A one-tap UI control explicitly named "Скопировать ссылку" copies the exact full import link, link length is within the supported limit, and local tests verify no truncation.

temporary_fallback_only:
  The raw import link is too long or client support is uncertain, but the full link remains visible/selectable, the `.conf` fallback is clear, and the bot does not claim that tapping the link copies it. This does not close the one-tap copy requirement.

needs_fix:
  The text says "нажмите, чтобы скопировать" but there is no copy button, the button cannot carry the full link, the link is hidden behind an unsupported flow, or fallback instructions are missing.

defer:
  One-tap copy requires a short tokenized delivery link, Telegram Web App, public/self-service route, or any new secret-bearing delivery surface.
```

Important boundary: short tokenized links, web download pages, Telegram Web App clipboard flows and public/self-service delivery are not Phase 5 defaults. They require a separate config-delivery/public/self-service gate because they change the secret-bearing delivery model.

## Stop Lines

Stop and record `decision: no-go` if QA would require:

- sending a real config by Codex;
- showing raw `.conf`, QR, `vpn://`, private key, PSK or endpoint in AMN3 evidence;
- deploying or restarting the live bot;
- using a Telegram bot token;
- adding a public/share/download route;
- introducing a short public config link without a config-delivery gate;
- opening public API/panel exposure;
- setting `VPS_APPLY_ENABLED=true`;
- touching live VPS, SSH, package apply/rebuild, service restart or production peer/user state.

## Handoff Template

```text
check_id: P5-M002
date/time:
operator:
scope: docs-only | local-only | redacted-screenshot-review | named-gate-live-delivery-review
AMN2 selected head:
delivery_artifacts_checked: conf | vpn_link | qr | app_links
platforms_checked:
copy_requirement_status: copy_ready | temporary_fallback_only | needs_fix | defer
copy_text_limit_checked: yes/no/not_applicable
real_config_delivered_by_codex: no
live_bot_deploy_restart: no
telegram_token_used: no
secret_artifact_in_evidence: no
blocked_or_unclear_items:
decision: pass | fallback_ok | needs_fix | defer | no-go
next_recommended_slice:
```

## Decision

`P5-M002` closes as a docs-only/local-only QA checklist. It records that current AMN2 instructions are structurally safe for `.conf`, QR and `vpn://` review, but the operator's one-tap copy-to-clipboard requirement is not satisfied by the current bot behavior. Sending the import link as a separate message is acceptable; requiring manual text selection is only a temporary fallback, not the target UX.

Follow-up выполнен: `P5-M006` Одно нажатие для копирования import-ссылки в Telegram. AMN2 now adds a safe local-tested `Скопировать ссылку` button only when the exact full `vpn://` link fits Telegram copy-text limits. Over-limit raw links remain visible/selectable with `.conf`/QR fallback and must not be described as one-tap copy-ready without a separate config-delivery gate.
