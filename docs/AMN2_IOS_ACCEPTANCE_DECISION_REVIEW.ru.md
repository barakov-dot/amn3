# AMN2 iOS acceptance decision review

Дата: 2026-06-27.
Модель решения: `GPT-5.5` (подтверждена оператором).
Статус: `completed-docs-only-review`.

Этот review использует существующие Phase 7/8/9 evidence. Live/VPS/SSH/config/
Telegram/public gates этим документом не открывались.

## Decision

```text
gate_name=AMN2_IOS_ACCEPTANCE_DECISION_REVIEW
selected_phase9_lane=HARDENING_PRODUCTIZATION
review_status=passed
ios_acceptance_required_for_current_lane=false
ios_defaultvpn_status=failed-not-accepted
ios_defaultvpn_config_import_status=failed-no-tested-import-path
ios_defaultvpn_qr_import_status=failed
ios_defaultvpn_non_qr_import_status=failed
ios_release_acceptance_status=deferred-not-hardening-blocker
ios_release_claim_allowed=false
ios_config_delivery_claim_allowed=false
next_live_or_mutating_step_requires_exact_named_gate=true
```

Итог: iOS acceptance не является blocker для текущего Phase 9
`HARDENING_PRODUCTIZATION` lane. При этом iOS DefaultVPN нельзя описывать как
рабочий, release-accepted, supported-primary или production-ready. По текущей
операторской проверке конфиги в iOS DefaultVPN не добавляются ни по QR, ни по
другому проверенному пути.

## Evidence base

Использованные документы:

- `research/amn2/phase-7-ios-android-client-compatibility-diagnostic-471bca8-2026-06-20.md`;
- `research/amn2/phase-7-mobile-telegram-ux-failure-conf-first-fix-6d5cf3e-2026-06-20.md`;
- `research/amn2/phase-7-android-acceptance-contract-471bca8-2026-06-21.md`;
- `docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md`;
- `docs/AMN2_PHASE_9_ENTRY_DECISION.ru.md`;
- `docs/AMN2_PHASE_9_HARDENING_ENTRY_REVIEW.ru.md`.

Ключевая база:

```text
phase7_ios_defaultvpn_result=failed-functional-acceptance
phase7_ios_defaultvpn_policy=experimental_ios
operator_2026_06_27_ios_defaultvpn_config_import=failed-no-tested-import-path
operator_2026_06_27_ios_defaultvpn_qr_import=failed
phase8_ios_defaultvpn_status=experimental_unreliable
phase8_ios_release_acceptance_status=next-phase-or-optional-not-phase8-blocker
phase9_selected_lane=HARDENING_PRODUCTIZATION
```

## Why iOS is not a current blocker

Текущий Phase 9 lane не открывает public launch, controlled config delivery или
production rollout. Он укрепляет эксплуатацию, helper/runbook reliability и
статусы. Поэтому iOS acceptance не нужен как gating condition для продолжения
hardening work.

Android private/operator RC proof уже закрыт с явными ограничениями:

```text
android_private_operator_rc_proof=complete-with-explicit-limitations
third_party_android_phone_status=passed-manual-and-server-side
telegram_private_operator_rc_proof=passed-private-operator-no-config-delivery
```

Это не переносит статус на iOS. iOS остается отдельно ограниченным направлением.
Для DefaultVPN на iOS текущий практический статус жестче: конфиг не удалось
добавить в приложение через проверенные operator paths.

## What remains forbidden

Без отдельного exact named gate нельзя:

- заявлять iOS как release-primary или production-ready;
- заявлять iOS DefaultVPN как рабочий путь импорта;
- доставлять iOS config;
- создавать новый peer/config для iOS;
- выводить `.conf`, QR, `vpn://`, private key, PSK, token/password;
- запускать Telegram live config delivery;
- открывать public exposure;
- менять runtime/package/services/firewall/sshd/auth/provider;
- выполнять restore/import/reboot/provider rebuild.

## Future exact gate, if needed

Если цель следующего этапа включает iOS users, нужен отдельный review и затем
execution gate:

```text
AMN2_IOS_ACCEPTANCE_GATE_REVIEW
```

Минимальная будущая граница:

- выбрать конкретный iOS client path (`DefaultVPN`, installed/legacy
  `AmneziaWG Apple`, другой approved client);
- использовать one fresh per-device config only;
- private handoff only;
- не выводить payload/secrets;
- проверить import/connect/traffic;
- при возможности подтвердить server-side handshake/endpoint/rx-tx;
- не смешивать с public launch, public exposure или production rollout.

## Status for current Phase 9

```text
phase9_ios_acceptance_decision_status=passed
phase9_ios_acceptance_blocker=false
phase9_ios_acceptance_future_gate_required=true
recommended_current_lane_action=continue-hardening-docs-or-next-approved-hardening-gate
default_hold=ЖДАТЬ_ЗАПРОСА_ОПЕРАТОРА
```
