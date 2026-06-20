# AMN2 Phase 7 P7-N001 + P7-N003 + P7-X001

Дата: 2026-06-14.

Статус: completed local-only RC readiness slice.

Scope:

- `P7-N001` automation intake for Phase 7;
- `P7-N003` client compatibility watch refresh;
- `P7-X001` operator copy polish for clean installer.

Gate: `local-only/docs/tests/watch-only`.

## Result

Automation intake remains a Phase 7 input lane only:

- `prvtpro-weekly-upstream-refresh`;
- `weekly-kyoresuas-upstream-refresh`;
- `amnezia-weekly-upstream-refresh`.

Their outputs are release-candidate intake signals, not automatic permission for
live VPS, public exposure, config delivery, write API, destructive execution or
Telegram identity changes.

Client compatibility watch refresh is now reflected in AMN2:

- `CLIENT_COMPATIBILITY_WATCH` records the local 2026-06-14 Amnezia ecosystem
  intake;
- integration status exposes `client_compatibility_boundary.watch_refresh`;
- config delivery remains disabled;
- live client import verification remains not run.

Clean installer operator copy was polished:

- public/config/write/destructive questions are Russian-first;
- stable answer values such as `yes/no`, `docker` and `host_systemd` remain
  unchanged;
- prompt copy no longer uses `production`, `destructive`, `cleanup` or
  `credential`.

## AMN2 Files Changed

- `app/vpn/client_compatibility.py`;
- `app/services/integration_status.py`;
- `app/services/fresh_install_wizard.py`;
- `tests/vpn/test_client_compatibility.py`;
- `tests/api/test_api_integration_status.py`;
- `tests/services/test_fresh_install_wizard.py`.

## Verification

RED:

```text
tests/vpn/test_client_compatibility.py tests/services/test_fresh_install_wizard.py::test_build_fresh_install_manifest_describes_questions_without_secrets tests/api/test_api_integration_status.py::test_integration_status_returns_safe_read_only_report_and_audit -v
1 import error, 1 StarletteDeprecationWarning
```

Focused GREEN:

```text
tests/vpn/test_client_compatibility.py tests/services/test_fresh_install_wizard.py::test_build_fresh_install_manifest_describes_questions_without_secrets tests/api/test_api_integration_status.py::test_integration_status_returns_safe_read_only_report_and_audit -v
10 passed, 1 StarletteDeprecationWarning
```

Expanded GREEN:

```text
tests/vpn/test_client_compatibility.py tests/services/test_fresh_install_wizard.py tests/api/test_api_integration_status.py tests/services/test_integration_status_service.py tests/web/test_web_integration_status.py tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py tests/test_file_hygiene.py -v
68 passed, 1 StarletteDeprecationWarning
```

Full AMN2 suite:

```text
tests -v
729 passed, 1 StarletteDeprecationWarning
```

## Explicit Non-Actions

No live VPS command, SSH command, package upload/apply/rebuild on VPS, service
restart/deploy, public exposure, public OpenAPI publication, config delivery,
write API, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive action, Telegram token use, live bot send, Telegram
identity/profile/media mutation, secret publication or upstream/GPL code copy
was performed.

`0de7a77` remains the latest known-good VPS-smoked baseline. `b121865` remains
the current local RC package-ready checkpoint until a separate named `P7-C001`
gate updates VPS evidence.

## Plan Update

Removed from active Phase 7 plan:

- `P7-N001`;
- `P7-N003`;
- `P7-X001`.

Recommended next local-only item:

```text
P7-S001
```
