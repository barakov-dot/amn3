# Spain preflight 006 — отдельная approval

## Статус

Этот документ описывает только будущий single-use read-only preflight.
Он не запускает SSH и не даёт authority без отправки exact literal approval.
Outcome `spain-fresh-20260720-006` пока не создан и не выполнялся.

## Exact approval

```text
APPROVE POST_RELEASE_SPAIN_READ_ONLY_PREFLIGHT_RUNNER_SHA_FF9D9B731A2AEE12C7E1A98CA0AACB8B533F051D666E1D4C4352BFDE0F6B143D_REMOTE_SCRIPT_SHA_228E53330DF694F18BBA6C2F13A7837C7F0B5F2A0D5D4757A134E126FB18945D_SOURCE_55DC243B8E6C6BDB57F8301B56326E4CD4072D19_TRUST_RUN_ID_SPAIN_FRESH_20260720_006_IMMUTABLE_TRUST_BUNDLE_SPAIN_FRESH_20260720_001_NEW_OUTCOME_RUN_SPAIN_FRESH_20260720_006_DEDICATED_ED25519_EXACT_PRIVATE_TARGET_AND_INDEPENDENT_HOST_KEY_PIN_READ_ONLY_OS_CAPACITY_PORT_SERVICE_DOCKER_SYSTEMD_FIREWALL_SSH_CLOCK_AND_UNRELATED_SERVICE_FINGERPRINT_NO_INSTALL_NO_RESTART_NO_STOP_NO_CONFIG_SECRET_TELEGRAM_OR_AWG_MUTATION
```

После отдельного approval разрешён ровно один запуск checksum-bound runner с
`-Mode preflight -RunId spain-fresh-20260720-006`. Он только читает OS,
capacity, ports, Docker, systemd, firewall, SSH policy, clock и fingerprint
unrelated service. Не разрешены install, restart, stop, config/secret actions,
Telegram actions, web mutation или любые AWG actions. При любом invariant
failure: остановиться, сохранить только sanitized evidence и не выполнять
blind remediation.
