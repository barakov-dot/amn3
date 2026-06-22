# AMN2 private/operator RC ready hold

Дата: 2026-06-22.

Статус:

```text
ready_hold_status=active-docs-only
phase8_final_status=launch-ready-with-explicit-limitations
private_operator_rc_launch_ready=true
public_launch_status=not-approved
blocked_with_exact_remaining_blockers=false
remaining_blockers_inside_listed_limitations=none
```

Этот документ фиксирует удержание AMN2 в состоянии private/operator RC ready.
Он использует только существующие Phase 8 evidence и не открывает live,
destructive, config delivery, Telegram send или public exposure gates.

## Что означает hold

AMN2 находится в безопасном финальном состоянии Phase 8:

- закрытый private/operator RC разрешен в пределах зафиксированного scope;
- public launch не одобрен;
- public exposure остается закрытой по умолчанию;
- Telegram live send и bot polling не выполнялись;
- config delivery не открывается автоматически;
- provider rebuild, restore/import и broader rollout не разрешены без нового
  exact named gate.

## Head на момент hold

```text
amn3_evidence_head_before_ready_hold=92ddaca Record private operator RC closeout
amn2_current_fixes_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447 Persist Android-compatible AWG defaults
latest_vps_applied_package_smoked_head=187949bffb927a0a6d6c1f260fc0bb9ebb972447
package_name=dist/amn2-vps-update-and-smoke-kit-187949b.zip
package_sha256=7FA073E4C66C0981673061D167D525BB9BCD6DFDDAA075E15701F0C2608E2E82
```

## Evidence base

Читать сначала:

```text
docs/AMN2_PRIVATE_OPERATOR_RC_CLOSEOUT.ru.md
docs/AMN2_PRIVATE_OPERATOR_RC_FINAL_PACKAGE.ru.md
docs/AMN2_PRIVATE_OPERATOR_RC_HANDOFF.ru.md
docs/AMN2_PRIVATE_OPERATOR_RC_RUN_CHECKLIST.ru.md
research/amn2/phase-8-rc-ready-hold-2026-06-22.md
```

Ключевые Phase 8 evidence:

```text
research/amn2/phase-8-p8-c001-fresh-android-config-acceptance-2026-06-21.md
research/amn2/phase-8-p8-c002-187949b-package-apply-smoke-2026-06-21.md
research/amn2/phase-8-p8-c003-fresh-zero-rehearsal-2026-06-22.md
research/amn2/phase-8-sfinal-launch-readiness-freeze-2026-06-22.md
research/amn2/phase-8-rc-closeout-2026-06-22.md
```

## Условия выхода из hold

Выход из hold разрешен только через новый exact named gate.

Минимальные варианты:

```text
PRIVATE-RC-OPERATOR-RUN-GATE
CONFIG-DELIVERY-GATE
TELEGRAM-LIVE-DELIVERY-GATE
PUBLIC-EXPOSURE-GATE
RESTORE-IMPORT-DR-GATE
PROVIDER-REBUILD-GATE
PRODUCTION-ROLLOUT-GATE
FRESH-ANDROID-PHONE-POST-RC-RECHECK-GATE
```

## Stop-lines

Пока hold активен, без нового exact named gate нельзя:

- выполнять live VPS/SSH command;
- выполнять package upload/apply;
- перезапускать сервисы;
- открывать public exposure;
- менять firewall/listener/TLS/reverse proxy/Cloudflare/ngrok;
- выводить `.conf`, QR, `vpn://`, private key, PSK, token или password;
- выполнять Telegram live send;
- запускать bot polling;
- менять Telegram profile/media;
- выполнять config delivery;
- выполнять backup restore/import/reboot;
- выполнять provider rebuild;
- менять production peer/user;
- начинать broader rollout.

## Текущая рекомендация

Если оператор не просит реальную RC-операцию или расширение scope, ничего не
открывать:

```text
current_recommendation=hold
next_action=wait_for_explicit_exact_named_gate
```
