# AMN2 Phase 7 P7-M003 + P7-N002 + P7-S002

Дата: 2026-06-14.

Статус: completed local-only RC readiness slice.

Scope:

- `P7-M003` Multi-instance/IPAM model incorporation;
- `P7-N002` API/docs taxonomy RC drift check;
- `P7-S002` Release notes skeleton.

Gate: `local-only/docs/tests`.

## Result

AMN2 clean installer RC planning now carries the Phase 6 multi-instance/IPAM
conflict model into fresh installer decisions:

- manifest key: `multi_instance_ipam_rc_decision`;
- rendered phase: `multi-instance-ipam-rc-decision`;
- policy doc: `docs/MULTI_INSTANCE_IPAM_CONFLICT_MODEL.ru.md`;
- live multi-instance apply, runtime config write, firewall change, peer
  migration, config delivery and service restart remain disabled.

AMN2 integration status now exposes an API/docs taxonomy RC drift check:

- key: `api_docs_taxonomy_rc_drift_check`;
- mode: `local_only`;
- public OpenAPI publication: disabled;
- new route exposure: disabled;
- write route enablement: disabled;
- implemented API route count remains six;
- safe metadata marker vocabulary is explicitly guarded.

AMN2 docs now include a release notes skeleton:

- `docs/RELEASE_NOTES_RC_SKELETON.ru.md`;
- it is a future RC draft only;
- it does not declare public launch, live smoke, config delivery, write API or
  destructive execution.

## AMN2 Files Changed

- `app/services/fresh_install_wizard.py`;
- `app/services/integration_status.py`;
- `tests/services/test_fresh_install_wizard.py`;
- `tests/api/test_api_integration_status.py`;
- `docs/FRESH_INSTALL_WIZARD.ru.md`;
- `docs/FRESH_INSTALLER_OPERATOR_INDEX.ru.md`;
- `docs/RELEASE_NOTES_RC_SKELETON.ru.md`.

## Verification

RED:

```text
tests/services/test_fresh_install_wizard.py tests/api/test_api_integration_status.py::test_integration_status_returns_safe_read_only_report_and_audit -v
3 failed, 15 passed, 1 StarletteDeprecationWarning
```

Focused GREEN:

```text
tests/services/test_fresh_install_wizard.py tests/api/test_api_integration_status.py::test_integration_status_returns_safe_read_only_report_and_audit -v
18 passed, 1 StarletteDeprecationWarning
```

Expanded GREEN:

```text
tests/services/test_fresh_install_wizard.py tests/api/test_api_integration_status.py tests/web/test_web_integration_status.py tests/security/test_surface_policy.py tests/security/test_surface_policy_bindings.py tests/test_file_hygiene.py -v
56 passed, 1 StarletteDeprecationWarning
```

Full AMN2 suite:

```text
tests -v
728 passed, 1 StarletteDeprecationWarning
```

AMN3 coordination checks:

```text
git diff --check
exit 0, CRLF warnings only

python -m unittest tests.test_amn2_apply_source_zip tests.test_markdown_hygiene
4 tests OK

python scripts/check_markdown_hygiene.py <changed Phase 7 docs/evidence>
exit 0
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

- `P7-M003`;
- `P7-N002`;
- `P7-S002`.

Recommended next local-only bundle:

```text
P7-N001 + P7-N003
```

Optional triple:

```text
P7-N001 + P7-N003 + P7-X001
```
