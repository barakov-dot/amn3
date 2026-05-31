# Route/Auth/Operation Policy

Дата: 2026-05-31.

Этот документ фиксирует первый безопасный API-readiness slice после verified live VPS baseline.

## Статус

`app/security/surface_policy.py` является inventory-only policy registry. Он не включает новые endpoints и не меняет runtime behavior.

## Правило для следующих изменений

Новый route, bot action, CLI command или remote operation не добавляется в production без policy entry, где указаны:

- actor;
- auth method;
- risk class;
- secret class;
- side effects;
- gates;
- audit decision;
- operation contract;
- live retest trigger;
- test references.

## Запреты первого slice

- Не включать `GET /agent/clients`.
- Не добавлять config/self-service API.
- Не добавлять backup, restore, reboot или generic write API.
- Не трогать live VPS.
- Не копировать upstream code.

## Live Retest Rule

Новый live retest нужен, если меняется хотя бы одна из областей:

- peer apply/revoke;
- config template/defaults;
- IP allocation;
- peer sync classification;
- disable/enable/delete device flows;
- Docker runtime write/restart behavior.

Policy-only changes and tests do not require live VPS retest.
