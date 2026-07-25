# AMN2 Phase 12 — Spain Migration Entry

## Current operational override — 2026-07-25: AMN2 contour absent; exact ledger finalize ready

The approved resume removed the exact AMN2 units, trees, runtime and user. The
primary group was automatically removed with that user, leaving its ledger
object `committed` although the OS identity was already absent; the resume
therefore failed closed before its receipt. Read-only evidence proves every
AMN2 unit is `not-found`, all owned trees and identities are absent, and the
transaction/capsule are unchanged. Current ledger SHA-256 is
`990A6668BF31F16668AC8F7098F309B156E1E182F4B2B28AC188047F0CBCBC78`:
one committed group, 34 removed objects and five pending objects.

The exact idempotent finalize writes only the missing group `removed` ledger
event and proves both run009-to-current and current before/after dynamic foreign
equality. Executor SHA-256 is
`B425E32A61C45F1615C3AB2223BB899CB1B1E82F985A301A18057DCE13D5DD4D`
(`152917` bytes); runner SHA-256 is
`98C9B8A6F4E28D9E80C6C1919FE7A5B271AFD4568F193212CADF0AB2A9E49E98`.
Double build byte-equal; `258 passed, 4 skipped`; parse/diff checks passed.

## Current operational override — 2026-07-25: first resume failed before mutation; corrected v3 ready

The first exact terminal resume failed closed before mutation because mixed-gid
`/etc/amn2-spain` objects were all inspected through `config_fs`, while the
root-owned secrets require `root_fs`. A following read-only safety audit proved
the ledger unchanged at `0EE87DFA…E660C9`, with only the dedicated Docker unit
active/enabled and all three retained AMN2 trees intact. The foreign service and
USA were unchanged.

Corrected v3 binds each audited object to its exact filesystem owner and checks
the secret identity separately. Executor SHA-256 is
`07FA623C7C919A0263C738FACBC816717102526B3A126CDEDAA03E70E6DF5060`
(`151989` bytes); runner SHA-256 is
`15E243C0251FD2528987A0A67C50E1D875CC49CB405E9AA1A8AFCBBFB4F6EDFC`.
Double build is byte-equal; scoped verification is `254 passed, 4 skipped`;
PowerShell parse and `git diff --check` passed.

## Current operational override — 2026-07-25: 52FAB7 audit-v2 passed; exact terminal resume ready

Read-only audit-v2 passed on ledger
`0EE87DFA762739457EAFA5D6C8C81168F99DA745B6DDD0F30BC60388F7E660C9`:
29 committed, 6 removed and 5 unrecorded objects, with every recorded stage
matching the sealed blueprint. Exact retained `/opt`, `/etc` and `/var`
inventories are respectively `0F2F2ADE…D25119` (2903/313921242/0755),
`CD947553…CAF5A7` (4/2392/0750), and `8F95E1F1…27BC99` (1/249856/0750).
Only `amn2-spain-docker.service` is active/enabled; the other AMN2 units are
inactive. The foreign service was not stopped or mutated.

The audit-bound terminal resume uses executor
`88FE4633126E3BC5732A68EADD679BE2D30AD5D89A5B780F01FA45BB41CBE480`
(`151821` bytes) and runner
`1EAF78A1F22BFB62217A135AAC2C7490DA34D61B3E26E810B4416086EF7B87A0`.
It can remove only that exact audited AMN2 contour, stop/disable only its
dedicated Docker unit, seal the ledger and verify dynamic foreign equality.
Scoped verification: `254 passed, 4 skipped`; `git diff --check` passed.

## Current operational override — 2026-07-25: `52fab7…` partial terminal recovery; read-only audit ready

Manual cleanup removed only the verified package tree. The following terminal
recovery removed recorded AMN2-owned Docker/config-template/log trees, then
failed closed before the terminal equality receipt while retained files still
made parent trees non-empty. All AMN2 units are inactive and the dedicated
container/network/image are absent. `/opt/amn2-spain`, `/etc/amn2-spain`, and
`/var/lib/amn2-spain` remain recorded AMN2-owned state; install must not be
retried while the transaction is `manual_recovery_required`.

Current mutation-ledger SHA-256 is
`0EE87DFA762739457EAFA5D6C8C81168F99DA745B6DDD0F30BC60388F7E660C9`.
Audit-v1 failed closed without install/cleanup/start because it incorrectly
required every ledger object to be terminal `committed/removed`; recovery
ledgers legitimately retain `abandoned/unrecorded` states. Audit-v2 reports a
sealed full state map and is bound to executor
`AA4602CF011790EBDB3DC8C4D815361FA683E2B378958620BC9BEE9D02D9821A`
(`149242` bytes) and runner
`9F1E1C6F8CF725A3B4141C93D5E8485FB1FB8EA81E8817BF6DF2F445535D2657`.
It can only observe the exact ledger, systemd state, and no-follow inventories
of those three owned trees. Scoped verification is `250 passed, 4 skipped`;
`git diff --check` passed. Foreign equality remains unclaimed until a later
terminal receipt passes.

## Current operational override — 2026-07-25: transaction `52fab7…` runtime recovery is verified; cleanup is next

The approved runtime recovery for nonce
`52fab7ac3eaf2ea1d1c7bf5f21778662ddc5964a9796188d29c98b0fcafee246`
removed only the exact AMN2 container/network/image contour. Its stdout framing
was rejected locally, so it must not be retried; independent read-only evidence
confirms all AMN2 units inactive, those three objects absent, and ledger events
`70..72` removed. Ledger SHA is now
`CA48BF5F3C7AA6C1A2D09E2AD380812AA89BA098BB193371ABD690EC11CC0A71`.
The transaction remains `manual_recovery_required` and the verified package tree
is retained.

The current executor is
`4D110B0DC169BE38A65B16A89DD8A9B54AEB5840117E5F4B443CC4538939D4DC`
(`147586` bytes). The dedicated Docker root read-only binding is
`9AAF13904FD0738D88FE13DB54527F6426F783B06664E3BAF6E41FF140755AEE`,
49 entries, 262199 bytes, mode `0710`. Two current-transaction runners are
local-ready: manual cleanup SHA
`41B35A8AF7B82A8CEAD1950801CBF9E240482D01246187D0BD68503AB1944971`, then
terminal recovery SHA
`D11E18FE83C30717FA7E295D05C23E0A00C70C2F8DA1D01896524225F056BF41`.
Scoped verification is `244 passed, 4 skipped`. Terminal receipt remains the
first permitted claim of post-failure foreign equality.

## Current operational override — 2026-07-25: v19 transport timed out before executor; post-timeout staging recovery passed

Exact manual cleanup and terminal recovery for v18 transaction
`00d9daecb6701b443d5714e7d08ec8715ad8ce6aa01712607463b572a5212972` passed.
They removed only recorded AMN2-owned objects; terminal receipt proves
persistent foreign equality `true`, volatile `0/0`, and the pinned postcheck
finds all six owned paths absent and web/bot/Docker/network/AWG inactive.

The specific v18 failure mechanism is now source-proved: the sealed AWG archive
is deliberately untagged, but default Docker `image ls` hides that dangling
image. The old action therefore observed `absent` after a successful load,
skipped the owned tag, and returned the bounded post-load failure label. A
RED/GREEN regression test reproduces that sequence. v19 changes only the exact
allowlisted image-list argv by adding `--all`; no host, transport, firewall,
foreign-service or USA-contour behavior changes.

```text
transaction=704C0C085B5F4CEC40FC7A8C9E7F7C7E55F29027F4D3168393E16C26B9090CE4
capsule=19ADD794051040AC287D6DDB842E82DC01A96322BD135F9951A1412D18597A95
manual_cleanup=passed|8D5844259EAD4DC00CB9AF149EEB1EC856583F98871C824DF8DAE062157D358A
terminal_recovery=passed|06E1AF92C39EC799187A9304C2A4C5499E3668DC86873A4A77B26111AC57E9F4
foreign=persistent_true|volatile_0_0
v19_package=FF9E8FA4604C4E9F7A3EE139B1D7B96D53FA4693E4555808B7E1725BDBAD4974|139970560
v19_manifest=3B0B6574F982ADF8745A13AD77CA49824A04ACEFD4BD065E763B2E29B628FB70
v19_executor=04B0F5142E7D7464C7CA6555E482A17F4C3D79D1F209A0E7327CD44144AD6978|146014
v19_runner=C8C82E4A73A3ECB700255720A90A6B53F01FA6639B277AE0F0AAD85F32857050
local=red_green|package_executor_double_build_equal|offline_clean_room_revalidated|scoped_240_passed_4_skipped|powershell_parser_passed
v19_upload=timed_out_900_seconds_before_remote_hash_or_executor
post_timeout_recovery_runner=FE46BC1F099EECDE1FA0A3B59ED9E64609B2A717EBDC30354B56FA871CE93E2F
post_timeout_recovery=passed|package_a_absent|executor_a_absent|active_install_transaction_false|amn2_units_active_false|action_none|removed_count_0
post_timeout_local=tooling_158_passed|powershell_parser_passed|single_receipt_wrapper_passed|diff_check_passed
next=transport_remediation|fresh_checksum_bound_install_approval
```

No SCP/upload is active. The v19 transport timeout occurred before executor
invocation, so AMN2 did not start. The recovery receipt confirms no retained
staging paths or active AMN2 transaction. Foreign service and USA were not
changed. A new transport decision and fresh checksum-bound install approval are
required; blind retry is forbidden.

## Current operational override — 2026-07-24: terminal recovery passed; v18 diagnostic install candidate is locally verified

The v17 transaction `e968810382104e77e136565b6e3b5b28987a670d314efcd9fb9b7982ef168c82`
is no longer pending recovery. Exact manual cleanup and terminal recovery
passed against transaction SHA-256
`9BA96EF4766BB4905D327519EB41A4D25917AD2D084A6B1D0A066F340A859D2D`:
only exact AMN2-owned objects were removed; foreign equality is persistent
`true`, volatile `0/0`. No AMN2/AWG start, foreign-service mutation, or USA
change occurred.

Local v18 preserves the same pinned inputs and changes only the failure
boundary of `awg_image_loaded`: post-load/tag/state `BackendError` is emitted
as one existing bounded `docker_image_load_*` label. The sealed inner AWG
archive is intentionally untagged (`RepoTags=null`, `repositories={}`), then
tagged by the owned local Docker action; this is not a static archive mismatch.
The actual Docker root cause remains unproven and is not claimed.

```text
v18_package=D44DDB455E831D2FD7EB4E303579203D09C8F402CB1EBADCF5679B4F9CE1E0FB|139970560
v18_manifest=3F2BA2524775A3DF5AFE6B68CC2FFF721F914293F25A8FF61C79BFFF1DAA78AA
v18_executor=C5704E0F83FEFDAFAFC6A7EE174F29C0559E39A1B2429E30D5EA0DF955BE690E|146011
v18_runner=1015AFACE40004422DD1B6232613061CFD98663AD542A90E1C2D999B22660D82
terminal_recovery=passed|removed_verified_owned_objects|persistent_true|volatile_0_0
local=double_build_byte_equal|offline_clean_room_68_artifacts|source_55dc243_verified|powershell_parser_passed|scoped_235_passed_4_skipped
next=diff_review|commit_push_readback|exact_checksum_bound_v18_install
```

No SCP/upload is active. v17 must not be retried; only the published v18
checksum-bound literal may start a new install attempt.

## Previous operational override — 2026-07-24: v17 cleanup passed; exact terminal recovery is next

The approved v17 install entered the remote state machine and returned
fail-closed `production runtime rollback failed`. A subsequent pinned read-only
receipt identifies newest transaction
`e968810382104e77e136565b6e3b5b28987a670d314efcd9fb9b7982ef168c82`:
`manual_recovery_required`, transaction SHA-256
`9BA96EF4766BB4905D327519EB41A4D25917AD2D084A6B1D0A066F340A859D2D`.
Do not retry install.

Checksum-bound `manual-cleanup-bound` passed and removed only retained
`/opt/amn2-spain-package`; the terminal ledger remains preserved. A read-only
scan of the dedicated Docker root is bound to SHA-256
`DB16C4E758FE4D210E1F74EE0C2774A1B100FE535FA4B24C706E1FBE5A86467D`,
2268 entries, 42532407 bytes, mode `0710`, two block entries `rdev=64770`,
and one filesystem/no nested mounts. The next live action is exact terminal
recovery using executor
`B2E90D67CBC9172A9C099155E4B67FBBADBB47DA1FEF6AD8A724DB79228555E9`
(`145873` bytes). Its passed receipt must establish foreign equality. Queried
web, bot, AWG and Docker units are inactive; USA remains rollback contour.

## Current operational override — 2026-07-24: v17 has passed two read-only collector probes; install remains unstarted

v16 stopped fail-closed before transaction/tombstone creation and before install
mutation. Its second bootstrap collector hit the fixed read-only condition
`systemd_cgroup_ports|fd_readlink` (exit `78`): a foreign process FD vanished
during enumeration. v17 retries exactly one complete cgroup snapshot only for
that subreason; a repeated FD race and all other failures stay fail-closed.

The v17 collector was executed twice over the existing pinned SSH/stdin path,
with no remote file write. Both probes passed JSON, host/boot identity binding
and semantic preconditions. Package bytes are unchanged; the executor delta is
only `scripts/phase12_spain_resource_confirmation_remote.sh`. No SCP/upload
is currently running; AMN2/AWG and the foreign Spain service are untouched,
and USA remains rollback contour.

```text
package=1B01019DB68A50811AD093E9D2DCA51BD86A143A7ABBD2D0765056394700C768
manifest=D5830841AC55FD1B89552934C5A18C22955DF19B1C7B56F1E1DD4C5BE0F3B74A
executor=B2E90D67CBC9172A9C099155E4B67FBBADBB47DA1FEF6AD8A724DB79228555E9|145873
collector=4705B22EC68A0EA2820BDE82E41DB8D364EBD41D884A2A3D080FFE214CBC4D8D
runner=AFA21BDE076DD59D596394985CF56C9C95EAD0DDD534C64D51624DBEF078124B
local=package_executor_double_build_equal|offline_clean_room_passed|scoped_295_passed_4_skipped|two_pinned_read_only_probes_passed
next=powershell_parse|diff_review|commit_push_readback|exact_checksum_bound_v17_install
```

## Previous operational override — 2026-07-24: `a75d9d…` recovered; v16 is the sole local install candidate

Exact manual cleanup and terminal recovery for
`a75d9d957ace99c8d74c20d45c029e2e08d355a2c5a370d0066972561e73a1ac` passed.
Only recorded AMN2-owned objects were removed; the receipt records persistent
foreign equality `true` and volatile counts `0/0`. No AMN2/AWG start, foreign
Spain service mutation, or USA change occurred. No SCP/upload is currently
running.

v16 fixes the closed-runner ordinary-exception path that caused v15 to report
only a generic terminal failure. It converts that image-load-only path to the
fixed `docker_image_load_command_failed` label without exposing stderr. It is
not a claim of a Docker root cause, and it changes no resource plan or runtime
payload.

```text
package=1B01019DB68A50811AD093E9D2DCA51BD86A143A7ABBD2D0765056394700C768
manifest=D5830841AC55FD1B89552934C5A18C22955DF19B1C7B56F1E1DD4C5BE0F3B74A
executor=79A6EF80B1209F35E05958709B671A14CADB26F62647C39BCE6132787AE3A5BB|145806
runner=C6DB6A5AE4F4491A79789A9E2746B632257EDBE028C0AD450D6E6593D86ED6C2
local=package_executor_double_build_equal|offline_clean_room_passed|scoped_234_passed_4_skipped|powershell_parse_passed
next=diff_review|commit_push_readback|exact_checksum_bound_v16_install
```

## Previous operational override — 2026-07-24: v15 install ended fail-closed; `a75d9d…` recovery is required

The approved v15 install reached the remote state machine and returned only
`production runtime rollback failed`; it did not expose a causal Docker label,
so no retry is authorized. Read-only pinned evidence identifies current terminal
transaction `a75d9d957ace99c8d74c20d45c029e2e08d355a2c5a370d0066972561e73a1ac`
as `manual_recovery_required` with retained `/opt/amn2-spain-package`.

```text
transaction=B87AD6123C37DB4D10F7E082951A411FE313E18F584AC91579CD5AFCF3E686E3
capsule=C5E164098E25AB9643FABAF707BD1F760108805F06663E1E825CCDF8E7B7F350
executor=07E066F15FA671DBF9B9F74ECAD2373C00D4A7551972E316F51BCB8265B630CC|145791
docker_tree=F6CAF7B0DC1DA9C100DDA22049957F7501748D01A01A99F359B4DE19D2E7E8E9|2268|42532407|rdev_64770
manual_cleanup_runner=4F2FC7F35542C15B61259FE354E918C85CBD4F69E4838AF052B9B41AA3379EC7
terminal_recovery_runner=6C5E28C05430BA6D5CC04F40A47697B256CF2D2FF703074F8E234C5EA9EE6D1B
```

The exact order is manual cleanup of the verified package tree, then terminal
recovery of only the sealed AMN2 contour with dynamic foreign equality. The
foreign Spain service remains immutable and USA remains the rollback contour.

## Previous operational override — 2026-07-24: `544db…` recovered; v15 package binds bounded image-load diagnosis

## Current operational override — 2026-07-24: `544db…` recovered; v15 package binds bounded image-load diagnosis

Exact manual cleanup and terminal recovery for
`544db99ee620bc0139914c75db98c9a2e16797aadffa6c106923825fc17a6b54` passed.
The cleanup removed only retained `/opt/amn2-spain-package`; terminal recovery
removed only exact recorded AMN2-owned objects. Its receipt is
`recovery_action=removed_verified_owned_objects`, persistent foreign equality
is `true`, volatile counts are `0/0`. AMN2 did not start; the foreign Spain
service and USA rollback contour remain untouched.

The former journal label `unsupported` was narrowed read-only to containerd
snapshotter lines, not accepted as a causal Docker-load diagnosis. v15 keeps
the sealed classic-vfs runtime policy and changes only diagnostic propagation:
Docker load timeout, changed input, oversized output, or other closed-runner
failure becomes a fixed `docker_image_load_*` label. No raw stderr is exposed.

```text
package=DAA40D48B88B2AFB0FC4A57A1E5313D8B2851BCED89AEC655B628CB859AEA585
manifest=F13A7C4A02F7B9233629AD06DF06265BB1FC84B69478B4BDB03F1484515C79F2
executor=07E066F15FA671DBF9B9F74ECAD2373C00D4A7551972E316F51BCB8265B630CC
runner=762428179994934DE358F08CE55E0D6489E5095DD7C48742AA827B851C16AE9B
local=package_executor_double_build_equal|offline_clean_room_passed|scoped_233_passed_4_skipped|powershell_parse_passed
next=diff_review|commit_push_readback|exact_checksum_bound_v15_install
```

## Previous operational override — 2026-07-24: v14 reached Docker; transaction `544db…` requires recovery

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
