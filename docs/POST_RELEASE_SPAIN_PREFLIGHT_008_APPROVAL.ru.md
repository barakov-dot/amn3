# Spain preflight 008 — отдельная approval

## Статус

Approval подготовлена, но не использована. Outcome
`spain-fresh-20260721-008` не создан и не запускался. Literal действует ровно
один раз только для checksum-bound read-only runner ниже.

## Exact approval

```text
APPROVE POST_RELEASE_SPAIN_READ_ONLY_PREFLIGHT_RUNNER_SHA_C4F00EC9E0C53D9B9582B083ED8598BD3CB3F7DC202AA638AF7B197F8B730652_REMOTE_SCRIPT_SHA_228E53330DF694F18BBA6C2F13A7837C7F0B5F2A0D5D4757A134E126FB18945D_SOURCE_55DC243B8E6C6BDB57F8301B56326E4CD4072D19_TRUST_RUN_ID_SPAIN_FRESH_20260721_008_IMMUTABLE_TRUST_BUNDLE_SPAIN_FRESH_20260720_001_NEW_OUTCOME_RUN_SPAIN_FRESH_20260721_008_DEDICATED_ED25519_EXACT_PRIVATE_TARGET_AND_INDEPENDENT_HOST_KEY_PIN_READ_ONLY_OS_CAPACITY_PORT_SERVICE_DOCKER_SYSTEMD_FIREWALL_SSH_CLOCK_AND_UNRELATED_SERVICE_FINGERPRINT_NO_INSTALL_NO_RESTART_NO_STOP_NO_CONFIG_SECRET_TELEGRAM_OR_AWG_MUTATION
```

После использования повторять literal нельзя. Failure evidence может содержать
только sanitized allowlisted classification/subreason; raw OpenSSH output,
private target и config secrets не сохраняются. Approval не разрешает install,
restart, stop, Telegram или AWG mutation.

## Лимит дальнейших запусков

Если run 008 докажет конкретную локально исправимую причину, допускается один
новый checksum-bound run 009 после отдельного review и approval. В противном
случае или после неуспеха 009 используется provider console/иной подход.
