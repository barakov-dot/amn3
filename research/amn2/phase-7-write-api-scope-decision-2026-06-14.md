# AMN2 Phase 7 Write API Scope Decision

Дата: 2026-06-14.

Задача: `P7-I007 Write API scope/implementation decision`.

Статус: completed.

Importance: very important.

Gate: local-only/docs/tests.

## Цель

Выделить `P7-C005` из combined public/config/write preflight в отдельный
machine-readable RC decision. Задача отвечает на вопрос: остается ли public API
read-only для RC или нужен отдельный write implementation slice.

Выбранная RC policy:

```text
keep_public_api_read_only_for_rc
```

## Изменения AMN2

AMN2 fresh installer manifest now exposes `write_api_scope_decision` with schema
`write-api-scope-decision.v1`.

Contract:

- status: `decision_ready`;
- mode: `local_only_docs_tests`;
- gate: `P7-I007`;
- target gate: `P7-C005`;
- source evidence:
  `research/amn2/phase-7-public-config-write-preflight-b121865-2026-06-14.md`;
- selected policy: `keep_public_api_read_only_for_rc`;
- write API enabled: `false`;
- public write routes allowed: `false`;
- Local Agent mutation allowed: `false`;
- production peer/user mutation allowed: `false`;
- apply requires named gate: `P7-C005 write API / install mutation gate`.

Decision options:

- `keep-public-api-read-only-for-rc`: selected for RC, no write routes;
- `separate-write-api-implementation-slice`: deferred, requires `P7-C005`;
- `operator-only-web-write-window`: deferred, requires `P7-C005`.

Required before any future write:

- `route_inventory_still_zero_or_explicitly_scoped`;
- `auth_scope_model_for_write`;
- `idempotency_and_audit_contract`;
- `rollback_or_compensating_action_story`;
- `operator_confirmation_boundary`;
- `safe_evidence_no_secret_or_peer_material`.

Blocked actions:

- `write_api_route_enablement`;
- `api_clients_crud`;
- `install_mutation_route`;
- `local_agent_mutation`;
- `vps_apply_enabled_true`;
- `production_peer_user_mutation`;
- `server_config_rewrite`.

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
3 failed, 25 passed, 1 StarletteDeprecationWarning
```

Focused GREEN:

```text
28 passed, 1 StarletteDeprecationWarning
```

Expanded AMN2 verification:

```text
34 passed, 1 StarletteDeprecationWarning
```

Full AMN2 suite:

```text
737 passed, 1 StarletteDeprecationWarning
```

## Не Выполнялось

- no live VPS command;
- no SSH command;
- no package upload/apply/rebuild on VPS;
- no service restart/deploy;
- no public exposure;
- no config delivery;
- no write API route enablement;
- no `/api/clients` CRUD;
- no install mutation route;
- no Local Agent mutation;
- no `VPS_APPLY_ENABLED=true`;
- no production peer/user mutation;
- no server config rewrite;
- no backup/import/reboot;
- no destructive action;
- no Telegram identity/profile/media mutation;
- no secret-bearing evidence publication;
- no upstream/GPL code copy.

## Вывод

`P7-I007` закрыт как local-only decision. `P7-C005` remains a critical named
gate and is not opened by this work.
