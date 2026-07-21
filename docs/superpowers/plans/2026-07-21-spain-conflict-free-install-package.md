# Phase 12 Spain conflict-free install package implementation plan

Дата: 2026-07-21
Design: `docs/superpowers/specs/2026-07-21-spain-conflict-free-install-package-design.ru.md`

## Gate 0 — подтверждённые ограничения

- [x] Прочитаны обязательные Phase 12 contracts.
- [x] Run 009 не повторяется; защищённое evidence связано SHA-256.
- [x] Выполнено независимое GPT-5.6 SOL review без SSH/mutation.
- [x] Зафиксированы projection equality, closed owned delta и ledger rollback.
- [x] Install gate отделён от issuance/broker gate.

## Task 1 — определить безопасную границу no-restart peer lifecycle

Working tree: `worktrees/amn2-p7-c005-write-install`

1. Добавить failing tests для Docker apply/revoke:
   - отсутствует `docker restart`;
   - persistent config пишется атомарно;
   - live apply/remove выполняется через `awg set`;
   - runtime state проверяется через `awg show ... dump`;
   - apply/revoke failure восстанавливает исходный persistent config;
   - PSK не появляется в command, stdout, stderr или exception.
2. Запустить focused tests и сохранить RED evidence.
3. Реализовать минимальный transaction/compensation path.
4. Запустить focused tests до GREEN.
5. Запустить весь `tests/server/test_peer_apply.py` и связанный workflow/security scope.
6. Независимое review выявило отсутствие full-transaction lock/CAS и неточный
   revoke rollback в stateless multi-SSH варианте; full suite также не прошёл.
7. Удалить rejected diff byte-exact и сохранить AMN2 worktree clean на `55dc243...`.
8. Перенести no-restart transaction в отдельный typed AF_UNIX broker/issuance gate;
   до него bot и `VPS_APPLY_ENABLED` остаются выключены.

## Task 2 — материализовать exact upstream runtime inputs

1. Связать authoritative AMN2 source commit после Task 1.
2. Создать runtime-only source archive; исключить `.git`, caches, local DB, secrets и private artifacts.
3. Получить/проверить точный Linux x86_64 Python wheelhouse по hash lock.
4. Получить/проверить static Docker bundle для обнаруженной live architecture.
5. Выбрать exact AWG platform manifest; не использовать floating execution reference.
6. Создать OCI/docker image archive и проверить все blob/config/layer digests offline.
7. Записать upstream provenance URLs/commits/digests.

## Task 3 — TDD для package verifier

1. Failing tests:
   - повреждённый member/hash отклоняется;
   - лишний archive member отклоняется;
   - path traversal/symlink escape отклоняется;
   - floating image reference отклоняется;
   - отсутствующий required artifact отклоняется;
   - self-referential hash contract отсутствует;
   - canonical resource/fingerprint digests воспроизводимы.
2. Реализовать manifest schema и offline verifier.
3. GREEN focused tests.

## Task 4 — TDD для live precondition collector

1. Failing fixture tests для conflicts по path/name/user/port/interface/address/route/CIDR.
2. Failing tests для несовместимой OS/arch/Python, disk/inode/memory shortage.
3. Failing tests для baseline systemd/nft mismatch.
4. Реализовать read-only collector/validator без mutation-capable branch.
5. Проверить, что первый mutation невозможен без signed/canonical `preconditions_passed` receipt.

## Task 5 — TDD для installer/rollback state machine

1. Fixture/fake-root tests каждой стадии и каждой fault injection point.
2. Доказать reverse-order rollback только ledger-owned objects.
3. Доказать refusal при pre-existing collision.
4. Доказать clean DB/no peers/write-disabled/bot-disabled/loopback-only результат.
5. Доказать baseline projection и firewall projection checks после install и rollback.
6. Реализовать scripts, units, config templates и journal/ledger.

## Task 6 — assemble checksum-bound archive

1. Собрать package staging только из manifest allowlist.
2. Выполнить две независимые сборки и сравнить canonical inventories/digests.
3. Создать отдельно remote executor и его digest.
4. Выполнить offline clean-room verify/extract/dry-run.
5. Сохранить immutable approval binding receipt.

## Task 7 — verification and review

1. Scoped package tests.
2. Scoped AMN2 peer lifecycle tests.
3. Full AMN2 test suite.
4. Root repository tests/checks.
5. `git diff --check` в обоих repositories.
6. Независимый code review.
7. Security diff scan и закрытие всех reportable findings.
8. Повторить tests после исправлений.

## Task 8 — docs/status, commits, push, exact read-only approval

1. Синхронизировать Phase 12 evidence/status/current handoff.
2. Не изменять `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` и посторонние untracked docs.
3. Commit AMN2 source change; push; verify origin object.
4. Commit VPS-OPS-LAB package/docs; push; verify origin object.
5. Вывести exact read-only resource-confirmation approval, который связывает:
   - target Spain host identity;
   - collector/runner/package hashes;
   - разрешённые read-only commands/output fields;
   - прямой запрет upload/install/write.
6. Остановиться до явного exact approval оператора.

## Task 9 — после exact read-only approval

1. Выполнить только checksum-bound resource collector.
2. Проверить current 148-entry fingerprint equality с run 009.
3. Сохранить distro/arch/Python/capacity/routes/addresses/listeners/nft snapshot receipt.
4. При любом mismatch остановиться без upload/mutation.
5. Синхронизировать evidence/docs, commit/push и origin readback.
6. Вывести второй exact install approval, который связывает:
   - target Spain host identity;
   - package/executor/source/Docker/AWG/wheel/resource/baseline hashes;
   - resource-confirmation receipt hash;
   - exact resources/mutations;
   - no-peer/write-disabled/bot-disabled initial state;
   - automatic rollback and equality acceptance rule.
7. Остановиться до явного exact install approval оператора.

## Task 10 — только после exact install approval

1. Выполнить remote `precondition` read-only mode.
2. Если receipt отличается от approval binding — остановиться и запросить новый approval.
3. Upload exact package; проверить remote hashes.
4. Выполнить install state machine.
5. Проверить clean DB, zero peers, loopback web, AWG health без restart test.
6. Получить post-install baseline projection/owned delta/equality receipt.
7. При любой ошибке выполнить ledger rollback и доказать полное equality.
8. Синхронизировать evidence и перейти к отдельному broker/issuance gate.
