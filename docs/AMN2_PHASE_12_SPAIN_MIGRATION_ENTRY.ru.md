# AMN2 Phase 12 — Spain Migration Entry

## Current operational override — 2026-07-24: v14 reached Docker; transaction `544db…` requires recovery

The approved v14 install reached `docker_started`, but its retained mutation
ledger shows `awg_image_loaded=abandoned`. Automatic rollback made all four
AMN2 units `inactive`; it could not complete normal cleanup of the dedicated
Docker tree and therefore left only current transaction
`544db99ee620bc0139914c75db98c9a2e16797aadffa6c106923825fc17a6b54` in
`manual_recovery_required`.

Read-only exact bindings are transaction
`89a9bec68c026ff6aa2865ab65f1a91333046e458746499ee29738b3a663c5cf`, capsule
`6411c3a47d8055cf70dc4a2082d4fd23752c94698f6dcfde96da4ff3026af723`, Docker
tree `0a086299782791b40464cf51087c9e72cbfbac254200cd4e39191f395e06c331`
(`2268` entries, `42532407` bytes, root mode `0710`, two regular block devices
RDEV `64770`, zero whiteouts, one filesystem/no nested mounts).

Next live order is exact manual cleanup of `/opt/amn2-spain-package`, then
exact terminal recovery of the recorded current contour with foreign equality.
Do not retry install or claim foreign equality until that terminal receipt
passes. USA remains rollback contour; foreign Spain service is immutable.

## Previous operational override — 2026-07-24: transaction `2315…` recovered; v14 classic-vfs package locally verified

Transaction `2315caba94df97a4a34c665fb58401f0bd56e1721a7cea59af20c38f23b8046c`
terminally recovered: checksum-bound receipt=`passed`, action=
`verified_previously_removed_owned_objects`, persistent foreign equality=`true`,
volatile=`0/0`. AMN2 remains stopped; no foreign-service or USA mutation occurred.

The failed Docker 29 image-load path was investigated read-only: allowlisted
category=`unsupported`, `overlayfs_present=false`. The new fresh package keeps
the dedicated `storage-driver=vfs` and adds sealed
`features.containerd-snapshotter=false`; it changes no listener, firewall or
network policy. Double builds are byte-equal and offline verify/extract passed.

```text
package=984A2D87CC46EE84302E2462571659141D649CFE94206DE9FA6BBCF7AD8FA15B
manifest=7C897DA62CD64F77B008DABE4A9684DA1A9E06C637725EEAB69AD49468E14592
executor=D792D9CABB6B7FE3FABD7BC4B07D833D27549FE1484900770B54214D38FEAC29
next=scoped_local_verification_then_commit_push_readback_then_exact_install
```

## Previous operational override — 2026-07-24: vfs attempt ended in terminal recovery

Approved vfs-bound install выполнил package staging, clean DB, units и
dedicated Docker startup, однако `docker image load` action `awg_image_loaded`
стал abandoned. Automatic rollback не запускал AMN2 и удалил normal owned
contour, но оставил transaction
`2315caba94df97a4a34c665fb58401f0bd56e1721a7cea59af20c38f23b8046c` в
`manual_recovery_required`. Install повторять нельзя.

Read-only canonical recovery scan привязан к transaction
`e4507cd1483d9b6aeb89da825ffed9b18bba8239ce7aacbba97e1b9e36aedc74`,
capsule `e9e2b849a8afa296cad980396f5bec81dc5fe15913a99d5df738fa15cb4cef12`
и AMN2-owned Docker tree
`067776d5cff3b28c7404ff9f9a6494ea2bd7c7fb473b410dcc62f37282a419e4`
(2268 entries, 42532407 bytes, `0710`, one filesystem/no nested mounts,
two canonical regular block entries with `rdev=64770`, zero whiteouts).
Следующий gate — two-step checksum-bound
manual cleanup then terminal recovery with dynamic foreign equality. Foreign
Spain service остаётся immutable; USA остаётся rollback contour.

## Current operational override — 2026-07-24: terminal recovery passed, vfs package ready

Transaction `2f647…887ed` больше не требует recovery action: checksum-bound
manual cleanup и terminal recovery прошли. Они удалили только exact AMN2-owned
package/runtime/config/DB/Docker-data contour, сохранили terminal ledger и
подтвердили dynamic foreign equality: persistent=`true`, volatile=`0/0`.
Pinned post-check: шесть owned paths отсутствуют, четыре AMN2 units inactive.
Foreign Spain service не останавливался и не изменялся; USA остаётся rollback
contour.

Read-only diagnosis после recovery установил фактический blocker предыдущей
попытки: Docker journal category=`unsupported`, `overlayfs_present=false`
(cgroup v2, userns=1). Новый checksum-bound package выбирает dedicated Docker
`storage-driver=vfs`; иных runtime/network/firewall/listener changes нет.
Package SHA-256=`192189BA6E8832223322FF5D90574265D9137DB281E3F14FE43B3DA76BD95C1F`,
manifest=`5D6CB1F3CD76503A9C5301CF4AD2747C4595E0A5A7E251CE4E98C1D51AB72609`,
executor=`D792D9CABB6B7FE3FABD7BC4B07D833D27549FE1484900770B54214D38FEAC29`.
Double build, package verification, no-follow clean-room extract/source
expansion и scoped suite `290 passed, 4 skipped` прошли локально. Next gate:
publish/readback, then checksum-bound vfs install; no blind retry of old
package.

## Previous operational override — 2026-07-24

Manual 20-MiB package staging и final remote hash/size verification прошли:
package `CB972C…7575A` (`139970560` bytes), executor `D792D…AC29`
(`145505` bytes). Approved install runner пропустил upload, дошёл до
`package_verified_remote`, затем вернул fail-closed
`production runtime rollback failed`. Новый install retry запрещён.

Read-only pinned inventory фиксирует: AMN2 units отсутствуют, Docker inactive,
foreign service untouched; current transaction
`2f647f44976725fc569b045f923452b523db75c5edc86d651197875e1be887ed`
имеет `manual_recovery_required`. Capsule SHA-256:
`b0470aa26f836b78cfbc961bda7d12457e08bebe9cf981e1df404093cc42fb93`.
Docker data-root scanner receipt:
`41b0b3b43e5177a03ad7e75e2efa3655d4464988485b576a87803ae2564bea65`,
916 entries, 41902300 bytes, block RDEV 64770, single filesystem, nested
mounts 0.

Recovery sequence is fixed: (1) checksum-bound `manual-cleanup-bound` removes
only `/opt/amn2-spain-package` after CAS verification and preserves terminal
ledger; (2) checksum-bound `terminal-recovery-bound` removes only exact
recorded owned contour and verifies dynamic foreign equality. No AMN2 start,
no foreign-service mutation, USA remains rollback contour.

## Current operational override — 2026-07-22

Install boundary использует executor-embedded in-memory collector, run009
baseline и resource plan: remote precondition receipt, baseline и collector не
загружаются отдельными файлами. Foreign-service equality действует как
`dynamic_persistent_v1`: persistent identities обязаны совпасть; volatile
identities только записываются. Spain foreign service не останавливается и не
изменяется. Тихая SCP upload v5 завершилась с remote hash equality, но executor
fail-closed до tombstone/state machine на volatile full-snapshot critical
recheck; AMN2 services не запускались. v6 повторно валидирует полные
preconditions под lock и связывает critical equality только с host/boot.
Текущие v6 локальные
artifacts до commit/push: package
`77789F7AADB39DBA2E463AF178596A178577ABC3EF28A5DF71627848446F682F`, executor
`BF42F14D43FD74887FB7019FC9EEE40D26EF67BEBF8F188895A2707D04CD70DA`.
Policy receipt фиксирует `persistent_equal` и числа volatile entries до/после;
полностью volatile membership допустим, но любое изменение stable fields
persistent identity остаётся fail-closed. Volatile fields persistent identity:
`bound_port_set`, `restart_count`.
Firewall equality использует approved semantic rebaseline `nft`, rule count
`129`, SHA-256 `FB8E1D41F6F4F0EBCEB7C89D65E4E5E440E0AC0A4E780B4F638F96CEE1B9A682`;
raw counter hash не является equality gate.

До exact checksum-bound install approval любые Spain upload/install/mutation
запрещены. USA остаётся rollback contour.

## Objective

Deploy a fresh AMN2 production contour on the separate Spain VPS, accept it
with disposable lifecycle evidence, switch the existing private Telegram bot
disabled-first, and issue only new operator-requested configurations. Existing
USA configs/users/peers are not migrated and are not deleted by Codex.

## Authoritative baseline

```text
phase11=completed-controlled-private-release
spain_preflight_009=passed|consumed|never_repeat
spain_evidence_sha256=8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8
amn2_source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
usa_production_overlay=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
docs_branch=codex-spark-phase9-docs-sync
spain_docker=absent
occupied_ports=tcp_22_53_443_8080_10050|udp_53_443
unrelated_fingerprint_entries=148
```

## Migration contract

1. Fresh install, clean DB. Do not restore USA DB, peers, configs or secrets as
   production state.
2. Preserve the unrelated Spain service byte-for-byte/state-for-state where
   applicable; its normalized fingerprint must equal the run-009 snapshot after
   install, acceptance and cutover.
3. Select new conflict-free container/unit names, Docker network, VPN subnet,
   AWG port and loopback web port. Do not bind TCP/UDP 53/443, TCP 8080/10050,
   or SSH 22.
4. Docker installation is a separate explicit mutation inside the install gate.
5. USA remains live rollback contour until Spain disposable acceptance, bot
   cutover and first real batch are accepted. Never stop/mutate USA AWG for
   testing.
6. Bot cutover is disabled-first with one polling owner, exact identity,
   webhook/backlog checks, rollback watchdog and independent postflight.
7. New configs use `NEOBYATNAYA.NET — recipient — slot/device`. Device may be
   unknown at issuance. Multiple active unassigned slots per recipient are
   allowed; default expiry is indefinite unless operator explicitly supplies
   an expiry.
8. Operator sends one batch message listing recipients and quantities; AMN2
   creates separate peers/passports/receipts. Operator distributes configs
   manually. Disable/revoke remains per slot and per recipient.

## Exact gate sequence

```text
P0 INSTALL_DESIGN_AND_PACKAGE
P0 INSTALL_SNAPSHOT_APPLY_VERIFY_OR_ROLLBACK
P0 DISPOSABLE_CREATE_IMPORT_CONNECT_DISABLE_REVOKE_CLEANUP
P0 DISABLED_FIRST_TELEGRAM_BOT_CUTOVER
P0 FIRST_REAL_OPERATOR_BATCH_ISSUANCE
P1 60_MINUTE_STABILITY_AND_FINAL_ACCEPTANCE
```

Every live mutation requires its own checksum-bound literal approval. Never
reuse Phase 11 approvals.

## Exit to Phase 13

Phase 12 closes only after Spain services are healthy, web remains loopback or
private-only, DB integrity/FK pass, one bot instance is stable, AWG lifecycle
acceptance passes, real batch receipts exist, unrelated fingerprint is equal,
and USA rollback/retirement decision is separately documented.
