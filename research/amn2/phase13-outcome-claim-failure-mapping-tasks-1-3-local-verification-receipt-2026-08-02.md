# AMN2 Phase 13 — квитанция локальной интеграционной проверки Outcome-Claim Failure-Mapping Tasks 1–3

Дата проверки: 2026-08-02

Статус: `local_outcome_claim_failure_mapping_verified_not_manifest_or_live_authorized`

## Основание и границы

Проверена локальная fail-closed цепочка Phase 13 Outcome-Claim Failure-Mapping
на root head `bd477232e1a62e278f3a876ceda400839c46448c`. В scope вошли только
следующие commits:

- `0fb7b45f24d2db176c381318afe7d2f9052329f0` — pure claim failure mapping;
- `e348b2b101b13761aaad432d5eb2944c8b96efcd` — typed claim boundaries;
- `bd477232e1a62e278f3a876ceda400839c46448c` — интеграция `Invoke-RunnerMain`
  и secret-safe terminal line.

Проверка использовала только local fake harness. Не создавались новый outcome
или manifest; не выполнялись package build, SSH/preflight, deploy, config/peer
issuance, AWG stop/restart/recreate/upgrade, reboot, rollback rehearsal,
Spain/USA mutation, изменение постороннего Spain-сервиса, USA shutdown,
cleanup или reuse.

## Результаты

- Phase 13 focused suite:
  `tests/test_phase13_awg3_preflight_contract.py` и
  `tests/test_phase13_awg3_readonly_preflight.py` — `128 passed`;
- утверждённый Phase 12 Spain regression scope:
  `tests/test_post_release_spain_readonly_preflight.py` и
  `tests/test_phase12_spain_package_tooling.py` — `233 passed, 1 skipped`;
- Bash, PowerShell и Python syntax — passed;
- `git diff --check` диапазона Tasks 1–3 — passed;
- scoped secret review, static mutation review и manual scoped security review
  — passed, reportable findings отсутствуют.

Подтверждена единая fail-closed цепочка: expired manifest завершается с
`exit 64` до private state и network; только existing valid canonical claim
даёт `exit 66` и `outcome_replay`; ACL, filesystem, partial, invalid,
claim-write и internal failures дают `exit 75` и `observation_ambiguous`.
Terminal line содержит только allowlisted `stage`, `reason` и
`claim_subreason`; SID, path, exception, system error, target и raw output не
выводятся.

## Исторические границы и security review

Исторические failure evidence V1/V2, manifest artifact count и consumed
`spain-awg3-20260802-003` не изменялись. Указанный consumed outcome не
повторялся. Новый broad security scan, durable security report и scan
artifacts не создавались.

## Stale/live boundary

Текущие materialized manifest/outcome stale относительно проверенных bytes и
не могут применяться. Live gate отсутствует. Новый checksum-bound
manifest/outcome, package build, SSH approval, Spain preflight и любые live
actions требуют отдельных exact gates. AWG3 остаётся candidate; Spain AWG2
d1–d7 — принятый baseline. USA остаётся rollback contour: shutdown, cleanup
или reuse требуют отдельного USA retirement readiness gate и exact live
approval.
