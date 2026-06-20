# AMN2 Phase 7 Evidence Index / Watch Intake / Dry Checklist / RC Notes

Дата: 2026-06-14.

Задачи:

- `P7-N004` Evidence index cleanup;
- watch-only automation/client refresh intake;
- named-gate dry checklist review;
- final RC notes polish.

Статус: completed.

Importance: normal + normal + normal + cosmetic/simple.

Gate: local-only/docs/watch-only.

## Итог

Добавлен evidence index:

```text
docs/AMN2_PHASE_7_EVIDENCE_INDEX.ru.md
```

Он фиксирует:

- current truth для Phase 7;
- core evidence;
- readiness evidence;
- handoff/navigation evidence;
- watch-only automation intake status;
- named-gate dry checklist review;
- final RC notes status.

AMN2 release notes skeleton обновлен:

```text
C:\Users\SooL\Documents\Amneziya\docs\RELEASE_NOTES_RC_SKELETON.ru.md
```

Теперь он отражает, что `b121865` является latest known-good VPS-smoked/package
baseline after `P7-C001`, а `0de7a77` остается previous known-good
history/rollback evidence. Public launch, public exposure, config delivery,
write API, backup/import, destructive execution and Telegram mutation remain
unopened.

## Watch-Only Intake

Automation chain remains intake-only:

- `prvtpro-weekly-upstream-refresh` - Sunday 10:00;
- `weekly-kyoresuas-upstream-refresh` - Sunday 11:00;
- `amnezia-weekly-upstream-refresh` - Sunday 12:00.

Automation output may inform research/watch-only notes, but it does not grant
permission for live/public/config/write/destructive/Telegram work.

## Named-Gate Dry Checklist

Before any exact named gate, confirm:

- exact gate phrase;
- target commit/head;
- narrow action scope;
- rollback/stop criteria;
- safe evidence destination;
- no secret-bearing payload in evidence;
- explicit `VPS_APPLY_ENABLED` decision only when needed;
- operator confirmation/password flow for live commands.

## Что Не Выполнялось

Не выполнялись:

- live VPS commands;
- SSH commands;
- package upload/apply/rebuild on VPS;
- service restart/deploy;
- public exposure;
- config delivery;
- write API enablement;
- Local Agent mutation;
- backup/import/reboot/restore apply;
- production peer/user mutation;
- destructive action;
- Telegram token use;
- live bot send;
- Telegram profile/media mutation;
- secret publication;
- upstream/GPL code copy.
