# AMN2 Automation Intake And Upstream Refresh Aggregation Plan

Дата: 2026-06-14.

Назначение: единый local-only/docs-only порядок обработки weekly upstream
automations перед Phase 6 final closeout и clean-installer next-phase entry.

Этот документ не открывает live VPS, SSH, public exposure, config delivery,
write API, Local Agent mutation, backup/import/reboot, production peer/user
mutation, destructive cleanup/reinstall, Telegram identity/profile mutation или
upstream/GPL code copy.

## Current Automation Chain

```text
step_1:
  id: prvtpro-weekly-upstream-refresh
  schedule: Sunday 10:00
  role: PRVTPRO upstream scout
  thread_binding: separate heartbeat thread
  output_required: short report plus `Для цепочки`

step_2:
  id: weekly-kyoresuas-upstream-refresh
  schedule: Sunday 11:00
  role: KYORESUAS upstream scout
  thread_binding: separate heartbeat thread
  output_required: short report plus `Для цепочки`

step_3:
  id: amnezia-weekly-upstream-refresh
  schedule: Sunday 12:00
  role: Amnezia ecosystem scout and AMN2 aggregator
  thread_binding: separate heartbeat thread
  output_required: short report plus `Агрегация для AMN2`
```

The app supports only one active heartbeat attached to a single thread at once.
Therefore, the chain must not rely on every upstream report appearing in the
current AMN2 working thread. The AMN2 thread is the decision lane, not the only
source of truth for automation output.

## Intake Card Format

Every automation result must be normalized into this card before it can affect
the AMN2 plan:

```text
Источник:
Automation ID:
Дата проверки:
Upstream URL:
Последний upstream commit/release:
Что изменилось:
Что полезно для AMN2:
Что уже покрыто в AMN2:
Что добавить в план:
Что gated/deferred:
Что нельзя переносить:
Для цепочки:
Рекомендация:
```

## Priority Labels

Only these priority labels are allowed in the aggregation:

```text
критичные gated
очень важные
важные
нормальные
простые
косметические
watch-only
already-covered
rejected
```

## Gate Labels

Each candidate must carry exactly one primary gate label, plus optional
secondary labels when useful:

```text
local-only/docs/tests
security-review
package/preflight only
live VPS gate
public exposure gate
config delivery gate
write API gate
destructive gate
Telegram identity gate
privacy gate
hybrid-only
GPL/upstream-copy forbidden
watch-only
already-covered
```

## Intake Audit Steps

1. Check automation state.

   Confirm the three automation IDs remain active, keep their intended
   schedules and do not have duplicate replacement automations.

2. Locate actual reports.

   Check whether reports are visible in the current AMN2 thread, their own
   heartbeat threads, or already captured in AMN3 research/status docs. If a
   report is not accessible, mark it as `missing-input`, do not invent results,
   and allow the aggregator to continue with explicit missing-input notation.

3. Normalize reports.

   Convert each available report into the intake card format. Keep direct
   source links. Do not copy upstream code, templates, UI, scripts, manager
   implementations or workflow code.

4. Deduplicate.

   Classify each candidate as:

   ```text
   new-candidate
   already-covered
   superseded
   rejected
   watch-only
   gated-deferred
   ```

5. Map gates.

   Every new-candidate or gated-deferred item must name the exact gate class
   before it appears in the remaining plan.

6. Decide AMN2 action.

   Allowed default actions:

   - create/update AMN3 research note;
   - update `ideas/candidates-for-amn2.md`;
   - update `ideas/candidates-for-hybrid.md`;
   - update `docs/PHASE_5_6_FORWARD_PLAN.ru.md`;
   - update `research/amn2/transfer-backlog.md`;
   - update next-chat handoff/status after evidence is written.

   Disallowed by default:

   - AMN2 runtime code changes;
   - package rebuild/apply;
   - live VPS/SSH commands;
   - public/config/write/destructive/Telegram identity actions.

7. Produce final aggregation.

   Write one concise AMN3 evidence note containing:

   - inputs found;
   - inputs missing;
   - normalized cards;
   - deduplicated candidate list;
   - gate map;
   - recommendation for Phase 6 closeout or continued wait.

## Current Known Input

The PRVTPRO step produced a usable report in the current thread on 2026-06-14.
It should be normalized into an AMN3 note after KYORESUAS and Amnezia inputs are
checked.

Known PRVTPRO signals from that report:

- upstream remains GPL-3.0 research-only;
- latest pushed commit seen by the refresh was `fbe5a2b`, dated 2026-06-08;
- Telemt path failure/fix reinforces package asset path preflight before
  upload/apply;
- multiple AmneziaWG instances per server reinforces capability registry,
  port conflict and IPAM planning;
- endpoint/DNS/subnet/IPv6 requests reinforce future dry-run config model and
  client compatibility testing;
- per-user statistics and speed limits remain privacy-sensitive and gated.

## Recommended Next Action

```text
Wait for KYORESUAS and Amnezia aggregator outputs, then run:
Automation intake aggregation + Phase 6 closeout readiness review
```

If the remaining automation outputs are missing or inaccessible after their
scheduled windows, proceed with:

```text
Partial automation intake note with missing-input markers
```

Do not close Phase 6 final closeout until the automation intake note exists.
