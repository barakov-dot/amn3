# Spain preflight 007 — отдельная approval

## Статус

Документ подготавливает только будущий single-use read-only preflight.
Outcome `spain-fresh-20260720-007` ещё не создан и не выполнялся. Текст ниже
не даёт authority без его отдельной отправки оператором после origin readback.

## Exact approval

```text
APPROVE POST_RELEASE_SPAIN_READ_ONLY_PREFLIGHT_RUNNER_SHA_9A6BCA57930A685B6D8B997E85972336A37F289D7D39073058EDAD4625DC34A3_REMOTE_SCRIPT_SHA_228E53330DF694F18BBA6C2F13A7837C7F0B5F2A0D5D4757A134E126FB18945D_SOURCE_55DC243B8E6C6BDB57F8301B56326E4CD4072D19_TRUST_RUN_ID_SPAIN_FRESH_20260720_007_IMMUTABLE_TRUST_BUNDLE_SPAIN_FRESH_20260720_001_NEW_OUTCOME_RUN_SPAIN_FRESH_20260720_007_DEDICATED_ED25519_EXACT_PRIVATE_TARGET_AND_INDEPENDENT_HOST_KEY_PIN_READ_ONLY_OS_CAPACITY_PORT_SERVICE_DOCKER_SYSTEMD_FIREWALL_SSH_CLOCK_AND_UNRELATED_SERVICE_FINGERPRINT_NO_INSTALL_NO_RESTART_NO_STOP_NO_CONFIG_SECRET_TELEGRAM_OR_AWG_MUTATION
```

Approval разрешает ровно один запуск reviewed runner с `-Mode preflight` и
точным RunId `spain-fresh-20260720-007`. При success разрешено сохранить только
sanitized read-only evidence. При failure разрешено сохранить только
allowlisted stage/subreason/exit metadata. Запрещены retry, install, restart,
stop, config/secret, Telegram, web и любые AWG actions.
