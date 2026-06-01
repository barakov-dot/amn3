# Docker Manager Design Note for `amn2`

Дата: 2026-06-01.

Назначение: зафиксировать минимальный безопасный contract для будущего Docker AmneziaWG manager до расширения live apply/revoke.

Это не implementation plan и не разрешение на изменение production runtime. Документ нужен как safety input после VPS gate.

## Current verified runtime fact

Verified live VPS cycle подтвердил Docker AmneziaWG runtime:

```text
container: amnezia-awg2
persistent config: /opt/amnezia/awg/awg0.conf
live network: 10.8.1.0/24
```

Эти значения являются текущим evidence, а не универсальным hard-code contract. Будущий manager должен читать runtime settings из server config/runtime registry.

## Manager responsibilities

Минимальный Docker manager должен уметь:

- читать persistent AmneziaWG config как secret-bearing artifact;
- строить dry-run diff без публикации private key, PSK и full config;
- делать backup-before-write перед любым изменением;
- применять ровно один peer add/remove за операцию;
- перезагружать/restart только явно описанным способом;
- возвращать structured result: operation id, risk class, side effects, consistency status, rollback/recovery note;
- писать audit metadata без raw command strings и secret values.

## Required operation flow

Любая state-changing операция:

1. Validate input: public key, VPN IP, server alias, runtime type.
2. Read current config through a redacted-safe parser path.
3. Build operation plan with dry-run metadata.
4. On `--dry-run`, stop before remote write.
5. On `--apply`, create timestamped backup.
6. Apply the smallest config change possible.
7. Reload/restart through allowlisted command.
8. Re-read state and compare expected peer state.
9. Return structured result with recovery note.

## Backup-before-write contract

Перед изменением:

- backup создается рядом с persistent config или в явно настроенном backup dir;
- backup filename содержит timestamp и operation id;
- backup content считается secret-bearing и не попадает в logs/evidence;
- failure to create backup blocks apply;
- rollback note указывает, какой backup нужен оператору, но не публикует его содержимое.

## Reload/restart contract

До implementation нужно выбрать один поддерживаемый путь:

- config rewrite + container-specific reload command, если runtime это поддерживает;
- config rewrite + controlled container restart, если reload невозможен;
- no-op dry-run для preview.

Нельзя смешивать несколько reload стратегий в одном operation result. Если runtime не распознан, operation должна перейти в `manual-review-required`.

## Concurrency and recovery

Будущий manager должен иметь:

- per-server operation lock;
- idempotency/replay policy для повторного apply/revoke;
- `partial-failure` result, если remote write прошел, а local DB/audit не завершились;
- manual recovery note для test peer и production peer отдельно;
- запрет на destructive cleanup без отдельного operation class.

## Tests before implementation

Перед production code slice нужны local tests:

- dry-run не меняет fake config;
- apply создает backup before write;
- backup failure blocks apply;
- reload failure returns redacted error and recovery note;
- parser/diff не раскрывает private key, PSK, full config;
- repeated revoke of missing peer is safe and auditable;
- concurrent operation lock blocks second mutation.

Live VPS нужен только после local green и только по отдельному gate.
