# Phase 16 — package 016: controlled stage STOP, transaction 007

Дата: 2026-08-28. Квитанция одного завершённого вызова frozen runner; не подтверждение успешного stage или завершённого rollback.

## Результат и границы

- Transaction: `phase16-spain-stage-20260828-007`; локальная попытка consumed, повтор запрещён.
- Один invocation packaged stage runner; один старт SSH process. Authentication и удалённое выполнение не подтверждены.
- Runner exit: `64`; fixed stderr token: `AMN2_PHASE16_CONTROLLED_STAGE_RUNNER_STOP`.
- Failure class: `stdin_write`; last completed milestone: `process_started`.
- Stage outcome отсутствует. Удалённые transaction/package/application/runtime/process resources и завершение rollback не подтверждены.
- Start UTC: `2026-08-28T04:49:56.0924832Z`; end UTC: `2026-08-28T04:50:24.1141316Z`; elapsed: `28.022` seconds.
- Europe/Moscow: 07:49:56–07:50:24.
- После STOP не было нового SSH, диагностики, rollback-команды, сигнала процессу, stage/preflight retry, install или issuance.
- Client configs/peers не выпускались; general issuance запрещена.
- Mandatory scoped rollback сохранён в frozen coordinator/envelopes, но данный результат не доказывает, что удалённый код достиг rollback или завершил его.
- AWG2 mutation не разрешена; отдельные AWG2 write-команды не выполнялись. Post-attempt AWG2 equality/health не подтверждены.
- Package 016/015, исходный код и application worktree не изменялись. Регрессии, materialization и отдельный package verifier не повторялись.

## Exact approval и bindings

Из пользовательского approval нормализовано только Markdown escaping underscore.

```text
/APPROVE PHASE16 SPAIN APPLICATION_AND_AWG31_STAGE PACKAGE_phase16-awg3-family-3-1-spain-pilot-20260824-016 IDENTITY_c8bb2f964a3f60a93fe23c600a62c4d1bae2efdf07be35d4e6e549e450a5260b MANIFEST_SHA256_e21c958573b093f6af7bea009cf5fbd42fda621b5b18609572ab32b8aa1ae9bc STATE_b2fb288632b0b2c85e3d8c7f2391aa04ee972b1f6629b9da3ddc27c142323976 ROLLBACK_SCOPE_SHA256_9efad64c2a6bfa717d02da9967c49e049e31425722037d91c8d519c31d75fdb2 TRANSACTION_phase16-spain-stage-20260828-007 MANDATORY_ROLLBACK_ON_FAILURE AWG2_UNTOUCHED
```

- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-016`.
- Identity SHA256: `c8bb2f964a3f60a93fe23c600a62c4d1bae2efdf07be35d4e6e549e450a5260b`.
- Manifest SHA256: `e21c958573b093f6af7bea009cf5fbd42fda621b5b18609572ab32b8aa1ae9bc`.
- Stage runner SHA256: `6364d652181cd6f522dbecd25e2c4b36e8c1d06736cb67a2e6a3e4894da7dd77`.
- Coordinator SHA256: `a016adbdcbf9acd57f6e96e9ffeb5f2289b5b9c1dbe2008e84b36984dbfae4ee`.
- Approval SHA256 (ASCII, no trailing LF): `6859df26e8752b5f835ef8ab7ca36999be3de994af9c6a5869314582d2fae233`.
- Approved state / preflight outcome SHA256: `b2fb288632b0b2c85e3d8c7f2391aa04ee972b1f6629b9da3ddc27c142323976`.
- Rollback scope SHA256: `9efad64c2a6bfa717d02da9967c49e049e31425722037d91c8d519c31d75fdb2`.
- Pre-run HEAD: `2b9b329b3c40f17d3a300567bf90f2132ac99792`.
- Branch: `codex/phase16-awg3-family-3-1-spain-pilot-016`.
- Linked worktree: `C:\Users\SooL\Documents\VPS-OPS-LAB\worktrees\phase16-004`.

Coordinator SHA above is independently bound to the immutable manifest; no coordinator source modification was made.

## Local prelaunch and invocation

- Prelaunch PASS UTC: `2026-08-28T04:48:15.0060654Z`.
- Frozen stage package reader accepted all 172 files, exact manifest/identity, safe paths and file hashes. This was a stage prelaunch integrity check, not another package build/verifier.
- Saved preflight claim 028 evidence had decision `pass`; exact approved state hash and package/host bindings matched.
- Preflight observation window remains `2026-08-28T04:30:34Z`–`2026-08-28T04:30:37Z`; it was not refreshed. The 600-second AWG2 handshake policy was not changed.
- Stage rollback scope and exact approval matched; local trust bundle passed; strict host-key checking stayed enabled.
- Before dispatch: outcome/failure/attempt marker absent; matching Spain SSH and stage-runner processes: `0/0`.
- Created only ignored local reservation `tmp/phase16-package016-stage-transaction007.attempt`; it is retained to prevent reuse.
- Runner invoked by Windows PowerShell 5 with `-NoProfile -NonInteractive -ExecutionPolicy Bypass -File`; only child PSModulePath was removed. No machine/user execution-policy change.
- Frozen packaged entrypoint and its transport were used without replacement, patch, timeout change or retry.
- A local orchestration syntax error occurred before any tool command or stage dispatch; correcting that invocation did not run an extra runner/SSH attempt.
- The outer wrapper captured stdout/stderr only in memory and emitted lengths/hashes plus fixed-token classification. No raw transport output was persisted.

## Local process result and failure artifact

Outer runner stdout: `0` bytes; SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

Outer runner stderr: `43` bytes; SHA256 `9e650e4049eb870274ee7321d57cca26007736a1136ff2860ba43c9cd89aeb48`; fixed STOP token only.

Outcome path, absent:

`C:\ProgramData\AMN2\phase16\controlled-stage\outcomes\phase16-spain-stage-20260828-007.json`

Failure artifact:

`C:\ProgramData\AMN2\phase16\controlled-stage\outcomes\phase16-spain-stage-20260828-007.json.runner-failure.json`

- SHA256: `0f7d4168b0d5b90f3feb07fea48e6f5468f71784b5ef7de929594417faf9e50b`.
- Bytes: `531`; canonical JSON and exact field set: PASS.
- Schema: `amn2.phase16.controlled-stage-runner-failure.v1`; result: `runner_stop`.
- Failure class / last completed milestone: `stdin_write` / `process_started`.
- Transport exit code: `null`.
- Recorded transport stdout/stderr bytes: `0/0`; both hashes are the empty SHA256 above.
- Raw output persisted: `false`.

These transport zero counts/hashes are initialized placeholders: this failure occurred before the runner captured its transport summary. They do not prove that SSH emitted empty streams. The failure does not prove authentication, complete frame delivery, remote transaction creation, application/runtime entry, or remote cleanliness.

The process now returns the correct scalar exit 64 on STOP. The repeated stdin-write failure class does not identify its underlying cause and does not establish whether the local BOM correction was exercised successfully on the remote path. No new transport change or local fix was attempted.

## Terminal local readback

- UTC `2026-08-28T04:50:40.6080416Z`: outcome absent; failure artifact present; matching Spain SSH and stage-runner processes `0/0`.
- UTC `2026-08-28T04:51:51.1933847Z`: canonical failure/field-set/bindings verified; manifest, stage runner, approved preflight state and failure SHA256 unchanged.
- No local orphan transport observed. Remote coordinator/resource absence and rollback completion remain unconfirmed.

## Next exact boundary

STOP before further Spain egress. Request one separately approved read-only recovery-state diagnostic:

- Command ID: `PHASE16_TRANSACTION007_RECOVERY_STATE_V1`.
- Bind the exact target/package/identity/manifest/state/transaction above, this completed receipt's computed SHA256, and the runner-failure SHA256.
- One SSH remote-command attempt; timeout 30 seconds; strict host-key checking.
- Normalized transaction presence, completion milestones, failure-locus classes, application/runtime/coordinator/package/release/service/container/network/interface/listener/backup and AWG2 health classes only.
- No raw values, command lines, secrets or raw persistence; no remote write, signal, rollback, stage/preflight retry, install, config or issuance.
- Transaction absence must be observed, not inferred from a stdin-write STOP. Claim consumption is entry, not completion.
- The exact approval is emitted after this receipt's checksum is fixed, avoiding a self-referential hash. This receipt grants no further egress.

## Статус Phase 16

- ✅ Task 0 — baseline.
- ✅ Task 1 — проверенный immutable package 016.
- ✅ Task 2 — Spain read-only preflight PASS, claim 028.
- ❌ Task 3 — transaction 007 STOP; remote state / rollback не подтверждены.
- ⏳ Task 4 — первый AWG3.1-конфиг для АРМ/Windows.
- ⏳ Task 4.5 — обязательный AWG2 ↔ AWG3.1 transport-quality A/B gate.
- ⏳ Task 5 — клиентская acceptance после Task 4.5.
- ⏳ Task 6 — closeout.

Нестабильность/скорость AWG2 остаётся открытым вопросом Task 4.5; preflight health PASS не означает её исправления.

Только эта квитанция подлежит scoped local commit. Branch/worktree сохраняются. Push не выполнялся: отдельное informed approval публикации накопленной истории в public origin по-прежнему отсутствует; ранее отклонённый push не повторяется.

Профиль следующего gate по утверждённому плану: GPT-5.6 SOL / High. Рекомендация не является разрешением live action или утверждением о текущем runtime model/effort.
