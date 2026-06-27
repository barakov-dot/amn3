# AMN2 Phase 9 iOS acceptance decision review

Дата: 2026-06-27.
Модель решения: `GPT-5.5`.
Run type: docs-only review.

## Input evidence

- `research/amn2/phase-7-ios-android-client-compatibility-diagnostic-471bca8-2026-06-20.md`
- `research/amn2/phase-7-mobile-telegram-ux-failure-conf-first-fix-6d5cf3e-2026-06-20.md`
- `research/amn2/phase-7-android-acceptance-contract-471bca8-2026-06-21.md`
- `docs/AMN2_PHASE_8_PRIVATE_RC_FINAL_CLOSEOUT.ru.md`
- `docs/AMN2_PHASE_9_ENTRY_DECISION.ru.md`
- `docs/AMN2_PHASE_9_HARDENING_ENTRY_REVIEW.ru.md`

## Result

`AMN2_IOS_ACCEPTANCE_DECISION_REVIEW` completed as docs-only.

```text
selected_phase9_lane=HARDENING_PRODUCTIZATION
ios_defaultvpn_status=experimental_unreliable
ios_defaultvpn_operator_correction_status=failed-not-accepted
ios_defaultvpn_config_import_status=failed-no-tested-import-path
ios_defaultvpn_qr_import_status=failed
ios_release_acceptance_status=deferred-not-hardening-blocker
ios_acceptance_required_for_current_lane=false
ios_release_claim_allowed=false
future_ios_acceptance_gate_required=true
```

## Rationale

Phase 7 evidence downgraded DefaultVPN iOS after real-device functional
acceptance failed. On 2026-06-27 the operator clarified the practical current
state more strictly: for iOS DefaultVPN, AMN2 has not made a working import
path; configs are not added by QR or by any other tested path. Phase 8 kept iOS
release acceptance as a next-phase or optional task, not a blocker for
private/operator RC. Phase 9 selected `HARDENING_PRODUCTIZATION`, which does
not approve public launch, config delivery or production rollout.

Therefore iOS is not a blocker for current hardening work, but remains
explicitly not accepted for release claims. DefaultVPN iOS should be treated as
failed/not accepted, not merely as a soft reliability caveat.

## Output artifact

- `docs/AMN2_IOS_ACCEPTANCE_DECISION_REVIEW.ru.md`

## Post-condition

No live/VPS/SSH/config/Telegram/public gate was opened. No config, QR,
`vpn://`, private key, PSK, token/password or secret-bearing payload was
printed.
