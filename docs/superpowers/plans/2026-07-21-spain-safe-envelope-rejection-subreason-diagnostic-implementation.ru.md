# Spain safe envelope rejection diagnostic — implementation plan

1. Добавить RED-тест PowerShell classifier для `prefix_count`, `shape`, `stage`,
   `exit`, `stage_exit_mapping` и `unavailable`.
2. Реализовать локальный allowlisted classifier без сохранения raw values.
3. Подключить classifier только к ветке `failure prefix present + strict parser
   rejected`; писать `classification=envelope_rejected` и
   `stage=unavailable`.
4. Перевести checksum-bound runner на single-use outcome
   `spain-fresh-20260721-008`; immutable trust bundle и remote probe не менять.
5. Запустить focused и full tests, diff check, secret scan и scoped security
   review.
6. Синхронизировать Phase 11/current handoff и отдельный approval документ,
   не трогая `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`.
7. Commit, push, origin readback; вывести literal approval. SSH/run 008 в этот
   план не входит.
