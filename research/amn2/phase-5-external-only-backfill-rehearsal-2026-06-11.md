# Phase 5 external-only backfill rehearsal 2026-06-11

Дата: 2026-06-11.

## Итог

`P5-I002` закрыт как AMN2 local-only slice.

AMN2:

- branch: `codex/external-only-backfill-rehearsal`;
- commit: `23f18ef Add external-only backfill rehearsal`;
- fast-forward target: `amn2/codex-vps-test-prep`.

## Что добавлено

Добавлен локальный CLI rehearsal для старых внешне выданных test configs:

```bash
python -m app.cli device backfill-external \
  --db-copy data/amneziya-copy.sqlite3 \
  --input external-devices.json \
  --dry-run \
  --pretty
```

И apply только в указанную копию базы:

```bash
python -m app.cli device backfill-external \
  --db-copy data/amneziya-copy.sqlite3 \
  --input external-devices.json \
  --apply \
  --pretty
```

Контракт:

- входной JSON содержит только metadata для старых external peers;
- dry-run не создает и не меняет `--db-copy`;
- apply пишет только в локальную копию базы, указанную оператором;
- создаваемые устройства получают `config_material_status=external_only`;
- config resend remains unavailable;
- safe output не содержит peer public key, private key, preshared key, `.conf`, QR или `vpn://`;
- secret-bearing input fields are rejected before any DB write.

## Проверка

RED:

```text
tests/cli/test_device_import.py
result: import error on missing run_device_backfill_external as expected
```

GREEN:

```text
tests/cli/test_device_import.py -q
result: 6 passed

tests/cli/test_device_import.py tests/bot/test_bot_workflows.py tests/web/test_users.py tests/services/test_config_delivery.py -q
result: 58 passed, 1 warning

tests -q
result: 662 passed, 1 warning
```

`git diff --check` and staged `git diff --cached --check` passed.

## Safety

No live VPS command, SSH command, service restart, deploy, package apply, production peer/user mutation, public exposure, `/api/clients` CRUD, config delivery, Local Agent mutation, backup/import/reboot, destructive provider action or upstream code copy was performed.

This slice does not recover or reconstruct old client config material. It only makes already issued external test devices visible to AMN2 as `external_only`, so bot/web can show them without pretending resend/secrets are available.

## Следующая рекомендация

The original next safe local-only recommendation, `P5-I004` Operator-only smoke checklist, was completed later in `research/amn2/phase-5-operator-only-smoke-checklist-2026-06-11.md`.

Current next safe local-only recommendation: `P5-M003` AMN3 evidence discipline.

Rationale: after old external devices can be rehearsed safely on a DB copy, the next useful local-only step is a checklist that tells the operator exactly what to smoke in web/admin, bot dry/local behavior and read-only API routes before any package apply/rebuild/live gate.
