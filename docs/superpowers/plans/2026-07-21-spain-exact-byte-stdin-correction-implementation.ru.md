# Spain exact-byte stdin correction — implementation plan

1. Зафиксировать consumed/fail-closed evidence run 008 и LF-only probe facts.
2. Добавить RED tests для exact-byte stdin и Windows argument quoting.
3. Заменить object pipeline на pinned `ProcessStartInfo` + BaseStream bytes.
4. Перевести runner на single-use final outcome 009; remote probe/trust bundle
   не менять.
5. Запустить scoped/full tests, diff/security/secret review.
6. Синхронизировать status/gate/approval, commit/push и origin readback.
7. Выдать exact approval; run 009 без неё не выполнять.
