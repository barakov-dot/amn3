/GO PHASE 16 — AWG3 FAMILY 3.1, SPAIN PREFLIGHT, CONTROLLED STAGE AND ONE PILOT

Выполнить единую Phase 16 внутри проекта VPS-OPS-LAB. Эта фаза объединяет ранее предполагавшиеся Phase 16 и Phase 17. Не создавать отдельную Phase 17.

Модель:
- GPT-5.6 SOL High;
- reasoning High;
- один основной агент;
- не использовать subagents и независимых reviewers.

Цель:
1. Довести семейство AWG3 до текущей ревизии 3.1.
2. Один раз собрать новый checksum-bound Phase 16 package.
3. Выполнить checksum-bound Spain read-only preflight.
4. После отдельного approval выполнить controlled stage.
5. После отдельного approval выдать ровно один операторский AWG3.1 pilot config.
6. Проверить его на реальном клиенте и принять либо откатить пилот.

РАБОЧИЙ КОНТЕКСТ

Основной проект:
C:\Users\SooL\Documents\VPS-OPS-LAB

Exact Phase 15 application source baseline:
- worktree:
  C:\Users\SooL\Documents\amn2-phase15-local-package-bootstrap-readiness
- HEAD:
  c01c2e34ca506102e485ee3fa50b9420de6e591a

Exact Phase 15 tooling/receipt baseline:
- worktree:
  C:\Users\SooL\Documents\VPS-OPS-LAB-phase15-local-package-bootstrap-readiness
- HEAD:
  1c945dcfcda92c2945fe71ee95f9219546c1f4e3

Phase 15 baseline package:
- package ID:
  phase15-dual-protocol-bootstrap-20260811-001
- package identity:
  00b56972a7e3f3423fb3a1d6437f877910b6f23c690fe9a398ce8263d74faf1d
- manifest:
  d99e6e6b7df651f7cda6f63de2ee9b2a353afef4bfe1c93e82391d5c48aac6df
- collector:
  e122315df1db91f654da0411ef08cadaa15a4a4e6318f1973444ec1d531b6465
- source-readiness receipt:
  0d45708c6aab6b7812ffa8ca05d052f1db175086f57c504b5af8e1f6a99c4eb8
- package-readiness receipt:
  040a9959f60ce725a9aa626d299d482b782da317fed11de0fd39193fe71f911d
- runtime lock:
  a381be185b19777b9198526e11df8dcfa0faf7f15acccd829809e698d679fab
- test lock:
  52967d6e2babc5d05b60615c9a9c950a4541436f7a521dfee49d62b98264a235

Phase 15 package является baseline/readiness evidence. Не использовать его для AWG3.1 staging: текущие stage scripts намеренно inert, а application renderer ещё не содержит AWG3.1 fields.

УТВЕРЖДЁННОЕ ПРОДУКТОВОЕ РЕШЕНИЕ

- `awg3` — постоянное семейство протокола AWG 3.*.
- Текущая активная ревизия — exact `3.1`.
- Не создавать `ProtocolVersion.AWG31`, отдельный protocol profile или отдельную Phase 14.1.
- Сохранять `ProtocolVersion.AWG3 = "awg3"` и существующую dual-protocol модель AWG2/AWG3.
- Для новой выдачи использовать exact config revision `amneziawg_v3_1`.
- Старый `amneziawg_v3` считать известным предыдущим форматом, но не использовать для нового pilot issuance.
- Будущие `3.2`, `3.3` и другие `3.*` относятся к семейству `awg3`, но не принимаются автоматически: exact revision/runtime/capability/client admission остаётся обязательным.

OFFICIAL UPSTREAM BASIS

Использовать только как независимо реализуемый контракт, без копирования GPL client code/UI:

1. AmneziaVPN AWG3.1:
   PR #2984
   merge commit 44c10b39e38471a78f6090c96acffac626faec82

2. Android AWG3.1:
   PR #91
   merge commit d6cd6647465a9a593aa9ccadbbd20c44bf600d5b

3. Runtime AWG3.1:
   amneziawg-go commit
   1f50ad736ecca22a9bfc7b4606805ec9ca49fe48

4. Android pilot candidate:
   AmneziaWG v3.1.20260814
   release commit 5c16489e2cd9ed3a0a7a27c7445bba5238132f86

5. AmneziaVPN 5.0.1.5 официально помечен как PRE-RELEASE.
   Не классифицировать его как stable.
   Разрешать только как явно подтверждённый admin pilot candidate.

6. Не включать незавершённый `libagw` PR #3028.

TASK 0 — EXACT LOCAL BASELINE

Read-only подтвердить:

- оба exact HEAD;
- named branches;
- linked-worktree state;
- clean tracked worktrees;
- отсутствие unexpected source/tooling diffs;
- Phase 15 package/receipt identities.

Не удалять и не изменять unrelated untracked files.

При несовпадении exact baseline:
STOP и сообщить только конкретное несовпадение.

TASK 1 — BOUNDED LOCAL AWG3.1 DELTA

Application:

1. Сохранить `ProtocolVersion.AWG3 = "awg3"`.

2. Добавить exact config revision:
   `amneziawg_v3_1`.

3. Новая AWG3 issuance должна использовать только `amneziawg_v3_1`.

4. Расширить typed AWG3 config input двумя обязательными параметрами:

   RandomTrailers = on
   DisableCookies = on

5. Использовать точные native config keys:

   `RandomTrailers`
   `DisableCookies`

6. Значения должны иметь строгий typed boolean/on-off contract.
   Blank, malformed, contradictory, missing или unknown capability должны fail closed до генерации ключей, БД и peer/runtime side effects.

7. Связать в provider/receipt identities:

   - protocol_family = awg3;
   - protocol_revision = 3.1;
   - exact runtime identity;
   - exact capability set;
   - exact client application/platform/version/build;
   - exact compatibility evidence.

8. Runtime должен быть закреплён на официальном artifact/digest, реально поддерживающем UAPI:

   - random_trailers;
   - disable_cookies.

9. Не принимать runtime только по названию/tag. Нужны pinned digest и capability evidence.

10. Сохранить AWG2 golden bytes, AWG2 allocation, runtime, profiles, peers и Phase 14 contracts без изменений.

Tooling:

11. Реализовать существующие Phase 15 inert stage envelopes как Phase 16 controlled stage operations.

12. Новый package ID:

   phase16-awg3-family-3-1-spain-pilot-20260824-002

13. Stage scripts должны оставаться checksum-bound, state-bound, claim-bound, fail-closed и rollback-aware.

14. Никаких Spain/SSH/remote действий во время Task 1.

TASK 1 TESTING

Использовать TDD, но только targeted tests:

- AWG3.1 typed config rendering;
- exact `RandomTrailers = on`;
- exact `DisableCookies = on`;
- missing/malformed/unknown revision and capability rejection;
- exact config revision mapping;
- runtime/evidence/build/provider content identity;
- prerelease client remains candidate, not globally accepted;
- stage claim and rollback boundaries;
- AWG2 preservation tests непосредственно рядом с изменённым кодом.

Не выполнять:

- полный source suite;
- полный legacy tooling suite;
- четыре независимых review;
- whole-branch review;
- Codex Security whole-diff scan;
- повторные fresh-review rounds;
- многократную package materialization;
- повтор verifier после receipt-only commit;
- subagents.

Разрешены:

- один focused RED/GREEN cycle на изменяемый контракт;
- один targeted regression suite;
- `git diff --check`;
- exact changed-file scope check;
- короткий added-line secret scan;
- один package materialization;
- один package verifier pass.

При первом unexpected test failure:
- диагностировать;
- разрешён один bounded scoped correction.

При втором unexpected failure или расширении scope:
STOP и сообщить blocker, без самостоятельного fix/review loop.

TASK 1 OUTPUT

После PASS:

- сделать локальные commits;
- materialize package ровно один раз;
- verifier выполнить ровно один раз;
- вывести exact:
  - application source SHA;
  - tooling SHA;
  - package ID;
  - package identity;
  - manifest SHA-256;
  - collector SHA-256;
  - receipts;
  - runtime/client artifact identities;
  - targeted test result;
  - clean status.

Receipts изменять только при реальном изменении evidence.

TASK 2 — CHECKSUM-BOUND SPAIN READ-ONLY PREFLIGHT

Этот `/GO` явно разрешает после успешного Task 1 выполнить один Spain read-only preflight новым Phase 16 package.

Разрешено:

- один checksum-bound upload/transport нового пакета;
- read-only SSH;
- read-only OS/runtime/application/AWG2/resource inspection;
- проверка exact current-state SHA;
- проверка свободных AWG3 resources;
- проверка rollback prerequisites;
- удаление только созданных этой операцией временных transport artifacts.

Запрещено:

- stage;
- install;
- service mutation;
- container creation/start;
- firewall/routes mutation;
- DB migration;
- peer/config/QR creation;
- issuance;
- AWG2 restart/stop/change;
- live AWG3 runtime start;
- push.

При transport timeout:
- проверить отсутствие orphan upload process и partial remote artifact;
- не делать blind retry;
- STOP с точным transport status.

При любом preflight mismatch:
STOP без fix loop и без staging.

TASK 2 OUTPUT / STAGE GATE

После PASS подготовить:

- preflight receipt;
- observed state SHA;
- new package/checksum identities;
- exact intended stage resources;
- rollback scope.

Затем STOP.

Вывести один exact следующий approval:

/APPROVE PHASE16 SPAIN APPLICATION_AND_AWG31_STAGE PACKAGE_<PACKAGE_ID> IDENTITY_<PACKAGE_IDENTITY> STATE_<STATE_SHA256> MANDATORY_ROLLBACK_ON_FAILURE AWG2_UNTOUCHED

Не выполнять stage без этого отдельного сообщения пользователя.

TASK 3 — CONTROLLED STAGE

Только после exact `/APPROVE ... STAGE`:

1. Stage application.
2. Stage isolated AWG3.1 runtime.
3. Не включать general issuance.
4. Не создавать peers/configs.
5. Не менять AWG2.
6. Проверить:
   - service/container health;
   - UDP/listener/interface/bridge/CIDR ownership;
   - runtime revision/capabilities;
   - application bootstrap;
   - AWG2 equality;
   - отсутствие recovery markers.

При failure выполнить только заранее ограниченный rollback из approval и подтвердить его readback.

После PASS — STOP.

TASK 3 OUTPUT / PILOT GATE

Зафиксировать:

- staged application/runtime identities;
- AWG2 equality receipt;
- health result;
- exact pilot client candidate;
- exact proposed pilot device/passport;
- exact rollback target.

Затем вывести один approval:

/APPROVE PHASE16 ONE_AWG31_OPERATOR_PILOT CLIENT_<APPLICATION_PLATFORM_VERSION_BUILD> RUNTIME_<RUNTIME_IDENTITY> PACKAGE_<PACKAGE_ID> MANDATORY_PEER_ROLLBACK_ON_FAILURE NO_GLOBAL_ISSUANCE

Не создавать peer/config до этого сообщения.

TASK 4 — ONE AWG3.1 PILOT

Только после exact pilot approval:

1. Принять ровно один exact client build.

2. Предпочтительный Android target:
   AmneziaWG v3.1.20260814, exact installed build readback required.

3. Если используется AmneziaVPN 5.0.1.5:
   - сохранить release_kind=prerelease;
   - только admin pilot;
   - не включать global acceptance.

4. Создать ровно один AWG3.1 operator-owned profile/peer/config.

5. Delivery:
   - только `.conf`;
   - не создавать QR;
   - не создавать `vpn://`;
   - не включать public/self-service/global issuance.

6. Config должен содержать:

   - HeaderProtectionKey;
   - ContentPaddingAddition;
   - RekeyAfterTime;
   - RekeyTimeout;
   - RejectAfterTime;
   - KeepaliveTimeout;
   - MaxHandshakeAttempts;
   - RandomTrailers = on;
   - DisableCookies = on;
   - AllowedIPs = 0.0.0.0/0, ::/0.

Не печатать и не сохранять private key, PSK, HPK или полный config в logs/receipts.

TASK 5 — REAL CLIENT ACCEPTANCE

С участием оператора проверить:

- `.conf` import;
- tunnel activation;
- handshake;
- IPv4 traffic;
- DNS;
- reconnect;
- Wi-Fi/mobile network switch;
- client restart;
- server/application restart, только если отдельно подтверждён в pilot approval;
- отсутствие AWG2 regression.

При pilot failure:

- остановить general progression;
- выполнить только заранее утверждённый pilot peer rollback;
- подтвердить отсутствие orphan peer/profile/reservation;
- AWG3 general issuance оставить disabled.

TASK 6 — CONCISE CLOSEOUT

Подготовить один краткий handoff:

- final source/tooling/package identities;
- preflight result;
- staged runtime result;
- exact client build;
- pilot result;
- AWG2 equality;
- rollback status;
- что разрешено дальше;
- что остаётся disabled.

Не выполнять:

- повторные full suites;
- новые independent reviews;
- whole-branch review;
- повтор package materialization;
- rollout на других пользователей;
- global AWG3 issuance;
- push.

ОГРАНИЧЕНИЯ ВСЕЙ PHASE 16

- Один новый чат и одна Phase 16.
- Не создавать Phase 17.
- Не повторять процедуры Task 7/Task 8 Phase 15.
- Не изменять AWG2 golden bytes/runtime/peers.
- Не останавливать AWG2 для тестов.
- Не менять Phase 14 contracts, кроме минимального additive AWG3 revision wiring.
- Не трогать unrelated untracked files.
- Не делать push.
- Не расширять scope на QR, vpn://, general import subsystem, libagw или global rollout.
- Любой scope expansion требует отдельного решения пользователя.

Ожидаемое время при штатном прохождении:
3–5 часов.

Начать с Task 0.