# AMN2 Phase 7 Config Delivery Channel Readiness

Дата: 2026-06-14.

Задача: `P7-I006 Config delivery channel readiness`.

Статус: completed.

Importance: very important.

Gate: local-only/docs/tests.

## Цель

Подготовить `P7-C003` как отдельный prerequisite checklist после того, как
combined `P7-C002 + P7-C003 + P7-C005` preflight был закрыт как
`blocked-by-preconditions`.

Эта задача не открывает config delivery и не выполняет live delivery actions.

## Изменения AMN2

AMN2 fresh installer manifest now exposes
`config_delivery_channel_readiness` with schema
`config-delivery-channel-readiness.v1`.

Contract:

- status: `readiness_design_ready`;
- mode: `local_only_docs_tests`;
- gate: `P7-I006`;
- target gate: `P7-C003`;
- source evidence:
  `research/amn2/phase-7-public-config-write-preflight-b121865-2026-06-14.md`;
- live delivery allowed: `false`;
- apply requires named gate: `P7-C003 config delivery gate`.

Required checklists:

- `delivery-channel-decision`: allowed channels are `smtp_email` and
  `operator_local`;
- `secret-safe-evidence-protocol`: evidence must stay secret-safe. The wizard
  manifest keeps exact forbidden evidence names for local validation, while
  rendered plan and `/api/integration/status` expose only count/policy so API
  status does not repeat secret-bearing marker vocabulary;
- `client-import-matrix`: required artifacts are `conf_file`,
  `vpn_import_link` and `qr_vpn_import_link`;
- `one-time-delivery-policy`: delivery must be `single_use`, `short_ttl`,
  `purpose_bound` and `audit_redacted`;
- `delivery-revocation-story`: required steps are
  `disable_delivery_channel`, `revoke_or_expire_delivery_token` and
  `record_safe_revocation_summary`.

Blocked actions:

- `config_artifact_output`;
- `smtp_send`;
- `telegram_config_send`;
- `public_config_link_issue`;
- `public_config_link_redeem`;
- `qr_generation_for_delivery`.

Updated files in AMN2:

- `app/services/fresh_install_wizard.py`;
- `app/services/integration_status.py`;
- `tests/services/test_fresh_install_wizard.py`;
- `tests/api/test_api_integration_status.py`;
- `docs/FRESH_INSTALL_WIZARD.ru.md`;
- `docs/FRESH_INSTALLER_OPERATOR_INDEX.ru.md`.

## TDD Evidence

RED focused:

```text
3 failed, 23 passed, 1 StarletteDeprecationWarning
```

First GREEN attempt exposed an API-safe payload regression:
`/api/integration/status` must not repeat forbidden marker words. The fix keeps
exact forbidden evidence names in the local wizard manifest, but redacts them to
count/policy in API status and rendered plan.

Focused GREEN:

```text
26 passed, 1 StarletteDeprecationWarning
```

Expanded AMN2 verification:

```text
32 passed, 1 StarletteDeprecationWarning
```

Full AMN2 suite:

```text
735 passed, 1 StarletteDeprecationWarning
```

AMN2 diff hygiene:

```text
git diff --check: passed
```

## Не Выполнялось

- no live VPS command;
- no SSH command;
- no package upload/apply/rebuild on VPS;
- no service restart/deploy;
- no public exposure;
- no config artifact output;
- no SMTP/Telegram config send;
- no QR generation for delivery;
- no public config link issue/redeem;
- no write API enablement;
- no Local Agent mutation;
- no backup/import/reboot;
- no production peer/user mutation;
- no destructive action;
- no Telegram identity/profile/media mutation;
- no secret-bearing evidence publication;
- no upstream/GPL code copy.

## Вывод

`P7-I006` закрыт как local-only readiness/design. `P7-C003` остается critical
named gate and is not opened by this work.
