# AMN2 Phase 7 Backup/Restore/Import Readiness

Дата: 2026-06-14.

Задача: `P7-I008 Backup/restore/import prerequisite checklist`.

Статус: completed.

Importance: very important.

Gate: local-only/docs/tests.

## Цель

Подготовить `P7-C006` как отдельный prerequisite checklist без выполнения
backup create, restore apply, archive import, reboot or destructive migration.

## Изменения AMN2

AMN2 fresh installer manifest now exposes `backup_restore_import_readiness`
with schema `backup-restore-import-prerequisite-checklist.v1`.

Contract:

- status: `readiness_checklist_ready`;
- mode: `local_only_docs_tests`;
- gate: `P7-I008`;
- target gate: `P7-C006`;
- source evidence:
  `research/amn2/phase-7-public-config-write-preflight-b121865-2026-06-14.md`;
- live backup allowed: `false`;
- restore apply allowed: `false`;
- archive import allowed: `false`;
- reboot allowed: `false`;
- apply requires named gate: `P7-C006 backup/restore/import gate`.

Required checklists:

- `backup-scope-decision`: source state scope, artifact inventory and operator
  retention choice;
- `encryption-and-retention-policy`: encrypted-at-rest artifacts,
  operator-local secret handoff, declared retention window and safe-only
  evidence;
- `restore-preview-safety`: restore preview only, target isolation and
  no-overwrite stop-line;
- `import-source-validation`: source integrity, schema version, operator
  ownership and safe manifest checks;
- `disaster-recovery-drill-plan`: drill scope, rollback stop-line and
  post-drill relock check.

Blocked actions:

- `backup_archive_create`;
- `restore_apply`;
- `archive_import_apply`;
- `reboot`;
- `destructive_migration`;
- `remote_backup_download`.

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
3 failed, 27 passed, 1 StarletteDeprecationWarning
```

Focused GREEN:

```text
30 passed, 1 StarletteDeprecationWarning
```

Expanded AMN2 verification:

```text
36 passed, 1 StarletteDeprecationWarning
```

Full AMN2 suite:

```text
739 passed, 1 StarletteDeprecationWarning
```

## Не Выполнялось

- no live VPS command;
- no SSH command;
- no package upload/apply/rebuild on VPS;
- no service restart/deploy;
- no public exposure;
- no config delivery;
- no write API enablement;
- no Local Agent mutation;
- no backup archive create;
- no restore apply;
- no archive import apply;
- no reboot;
- no destructive migration;
- no remote backup download;
- no production peer/user mutation;
- no destructive action;
- no Telegram identity/profile/media mutation;
- no secret-bearing evidence publication;
- no upstream/GPL code copy.

## Вывод

`P7-I008` закрыт как local-only prerequisite checklist. `P7-C006` remains a
critical named gate and is not opened by this work.
