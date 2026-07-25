# Next task — AMN2 Phase 12 Spain Migration

## Current override 2026-07-25: transaction `52fab7…` runtime contour removed; exact cleanup is next

Do not retry install. The approved bounded runtime recovery removed only the
AMN2 container/network/image contour for nonce
`52fab7ac3eaf2ea1d1c7bf5f21778662ddc5964a9796188d29c98b0fcafee246`.
The runner's local stdout framing was fail-closed, but read-only state proves
all AMN2 units inactive, those objects absent, and mutation-ledger events
`70..72` removed; its current SHA is
`CA48BF5F3C7AA6C1A2D09E2AD380812AA89BA098BB193371ABD690EC11CC0A71`.
The transaction remains `manual_recovery_required`; the verified package tree
still exists.

Current executor:
`4D110B0DC169BE38A65B16A89DD8A9B54AEB5840117E5F4B443CC4538939D4DC`
(`147586` bytes). Dedicated Docker-root read-only binding:
`9AAF13904FD0738D88FE13DB54527F6426F783B06664E3BAF6E41FF140755AEE`,
49 entries, 262199 bytes, mode `0710`. Prepared next sequence is exact manual
cleanup runner `41B35A8AF7B82A8CEAD1950801CBF9E240482D01246187D0BD68503AB1944971`,
then exact terminal recovery runner
`D11E18FE83C30717FA7E295D05C23E0A00C70C2F8DA1D01896524225F056BF41`.
No foreign equality is claimed until the terminal receipt passes. Scoped suite:
`244 passed, 4 skipped`.

## Current override 2026-07-25: v19 transport timed out before executor; post-timeout staging recovery passed

v18 is consumed and fully recovered: manual cleanup and terminal recovery for
nonce `00d9daecb6701b443d5714e7d08ec8715ad8ce6aa01712607463b572a5212972`
passed. Only verified AMN2-owned objects were removed; persistent foreign
equality is `true`, volatile `0/0`, and six owned paths plus web/bot/Docker/
network/AWG are absent/inactive. Foreign service and USA remain unchanged.

Source analysis and a RED/GREEN regression test establish the exact defect:
the owned AWG archive loads an intentionally untagged image, while Docker's
default `image ls` hides dangling images. The old observer saw `absent`, never
issued the owned tag, then emitted the bounded post-load label. v19 adds only
`--all` to that allowlisted observer and rebuilds all checksum-bound artifacts.

```text
transaction_sha256=704C0C085B5F4CEC40FC7A8C9E7F7C7E55F29027F4D3168393E16C26B9090CE4
manual_cleanup_receipt=8D5844259EAD4DC00CB9AF149EEB1EC856583F98871C824DF8DAE062157D358A
terminal_recovery_receipt=06E1AF92C39EC799187A9304C2A4C5499E3668DC86873A4A77B26111AC57E9F4
foreign=persistent_true|volatile_0_0
package_sha256=FF9E8FA4604C4E9F7A3EE139B1D7B96D53FA4693E4555808B7E1725BDBAD4974
package_bytes=139970560
manifest_sha256=3B0B6574F982ADF8745A13AD77CA49824A04ACEFD4BD065E763B2E29B628FB70
executor_sha256=04B0F5142E7D7464C7CA6555E482A17F4C3D79D1F209A0E7327CD44144AD6978
executor_bytes=146014
runner_sha256=C8C82E4A73A3ECB700255720A90A6B53F01FA6639B277AE0F0AAD85F32857050
verification=red_green_dangling_image|double_build_byte_equal|offline_clean_room_revalidated|source_55dc243_verified|scoped_240_passed_4_skipped|powershell_parser_passed
v19_upload=timed_out_900_seconds_before_remote_hash_or_executor
post_timeout_recovery_runner=FE46BC1F099EECDE1FA0A3B59ED9E64609B2A717EBDC30354B56FA871CE93E2F
post_timeout_recovery=passed|package_a_absent|executor_a_absent|active_install_transaction_false|amn2_units_active_false|action_none|removed_count_0
post_timeout_local=tooling_158_passed|powershell_parser_passed|single_receipt_wrapper_passed|diff_check_passed
next=transport_remediation|fresh_checksum_bound_install_approval
```

No SCP/upload is active. The timeout happened before executor invocation, and
the recovery receipt confirms no retained staging or active AMN2 transaction.
Do not retry v18 or blindly reuse the consumed v19 install authority. The next
live candidate needs a new transport decision and fresh checksum-bound install
approval; it must still forbid foreign-service mutation and keep USA as rollback
contour.

## Current override 2026-07-24: terminal recovery passed; v18 is the sole local install candidate

v17 is consumed and must not be retried. The exact cleanup and terminal
recovery of nonce
`e968810382104e77e136565b6e3b5b28987a670d314efcd9fb9b7982ef168c82` passed
with transaction SHA-256
`9BA96EF4766BB4905D327519EB41A4D25917AD2D084A6B1D0A066F340A859D2D`:
`recovery_action=removed_verified_owned_objects`, persistent foreign equality
`true`, volatile `0/0`. AMN2 did not start; the foreign Spain service and USA
rollback contour are unchanged.

v18 is a narrow diagnostics correction, not a claim about Docker root cause:
the image archive is intentionally untagged and structurally valid, while any
bounded `awg_image_loaded` create/tag/post-state error is retained as a fixed
`docker_image_load_*` label through recovery. No raw stderr is persisted.

```text
package_sha256=D44DDB455E831D2FD7EB4E303579203D09C8F402CB1EBADCF5679B4F9CE1E0FB
package_bytes=139970560
manifest_sha256=3F2BA2524775A3DF5AFE6B68CC2FFF721F914293F25A8FF61C79BFFF1DAA78AA
executor_sha256=C5704E0F83FEFDAFAFC6A7EE174F29C0559E39A1B2429E30D5EA0DF955BE690E
executor_bytes=146011
runner_sha256=1015AFACE40004422DD1B6232613061CFD98663AD542A90E1C2D999B22660D82
verification=double_build_byte_equal|package_verify_passed|offline_clean_room_68_artifacts|source_55dc243_verified|powershell_parser_passed|scoped_235_passed_4_skipped
next=diff_review|commit_push_origin_readback|exact_checksum_bound_v18_install
```

No SCP/upload is active. Proceed locally through diff review and publish
readback; then use only the new v18 literal for install.

## Previous override 2026-07-24: v17 package cleanup passed; current work is exact terminal recovery

The approved v17 runner reached the remote state machine and returned
`production runtime rollback failed`. Do not retry it. Pinned read-only state
confirms newest transaction
`e968810382104e77e136565b6e3b5b28987a670d314efcd9fb9b7982ef168c82`, SHA-256
`9BA96EF4766BB4905D327519EB41A4D25917AD2D084A6B1D0A066F340A859D2D`, status
`manual_recovery_required`.

`manual-cleanup-bound` passed: it removed only verified retained
`/opt/amn2-spain-package` and preserved terminal ledger. The current
read-only Docker-tree binding is
`DB16C4E758FE4D210E1F74EE0C2774A1B100FE535FA4B24C706E1FBE5A86467D`,
2268 entries, 42532407 bytes, mode `0710`, two `rdev=64770` blocks, one
filesystem/no nested mounts. Next is exact terminal recovery using executor
`B2E90D67CBC9172A9C099155E4B67FBBADBB47DA1FEF6AD8A724DB79228555E9`
(`145873` bytes). Only its passed receipt establishes post-failure foreign
equality. Queried web, bot, AWG and Docker units are inactive; no
foreign-service mutation is authorized and USA remains rollback contour.

## Current override 2026-07-24: v17 bounded cgroup FD retry is locally and read-only verified

The v16 install candidate stopped before transaction/tombstone creation and
before install mutation. Its second bootstrap critical collector received the
allowlisted read-only envelope `systemd_cgroup_ports|fd_readlink|78`: a foreign
service FD disappeared during enumeration. Do not retry v16.

v17 retries one full cgroup snapshot only after that transient FD condition;
the second `fd_readlink` and every other subreason remain fail-closed. The
checksum-bound collector `4705…` has passed two pinned SSH/stdin read-only
probes: JSON, host/boot identity and semantic preconditions all passed. No
remote file write, AMN2/AWG start, foreign-service mutation, or USA change
occurred. No SCP is active now.

```text
package_sha256=1B01019DB68A50811AD093E9D2DCA51BD86A143A7ABBD2D0765056394700C768
manifest_sha256=D5830841AC55FD1B89552934C5A18C22955DF19B1C7B56F1E1DD4C5BE0F3B74A
executor_sha256=B2E90D67CBC9172A9C099155E4B67FBBADBB47DA1FEF6AD8A724DB79228555E9
executor_bytes=145873
collector_sha256=4705B22EC68A0EA2820BDE82E41DB8D364EBD41D884A2A3D080FFE214CBC4D8D
install_runner_sha256=AFA21BDE076DD59D596394985CF56C9C95EAD0DDD534C64D51624DBEF078124B
verification=package_executor_double_build_byte_equal|offline_clean_room_passed|scoped_295_passed_4_skipped|two_pinned_read_only_probes_passed
next=powershell_parse|diff_review|commit_push_origin_readback|exact_v17_install_approval
```

## Previous override 2026-07-24: `a75d9d…` recovered; commit/push v16 before one new install attempt

The exact cleanup and terminal recovery of transaction
`a75d9d957ace99c8d74c20d45c029e2e08d355a2c5a370d0066972561e73a1ac` passed.
They removed only recorded AMN2-owned objects and proved
`foreign_service_persistent_equal=true`, volatile `0/0`. No AMN2/AWG start,
foreign-service mutation, or USA change occurred. There is no active SCP or
remote install now.

v16 is the only local candidate. It maps the formerly unclassified ordinary
exception from the Docker image-load closed runner to the fixed
`docker_image_load_command_failed` label; it exposes no stderr and makes no
claim about the underlying Docker cause. The package delta is only its manifest
and live-backend script; resource plan and runtime payload stay unchanged.

```text
package_sha256=1B01019DB68A50811AD093E9D2DCA51BD86A143A7ABBD2D0765056394700C768
manifest_sha256=D5830841AC55FD1B89552934C5A18C22955DF19B1C7B56F1E1DD4C5BE0F3B74A
executor_sha256=79A6EF80B1209F35E05958709B671A14CADB26F62647C39BCE6132787AE3A5BB
executor_bytes=145806
install_runner_sha256=C6DB6A5AE4F4491A79789A9E2746B632257EDBE028C0AD450D6E6593D86ED6C2
verification=double_build_byte_equal|offline_clean_room_passed|scoped_234_passed_4_skipped|powershell_parse_passed
next=diff_review|commit_push_origin_readback|exact_v16_install_approval
```

## Previous override 2026-07-24: recover `a75d9d…` before any v15 retry

The approved v15 install is fail-closed, not a retry candidate. Its only safe
current state is transaction
`a75d9d957ace99c8d74c20d45c029e2e08d355a2c5a370d0066972561e73a1ac`:
`manual_recovery_required`, retained package tree present, normal automatic
rollback incomplete. The remote output did not produce an allowlisted causal
Docker-load label.

```text
transaction_sha256=B87AD6123C37DB4D10F7E082951A411FE313E18F584AC91579CD5AFCF3E686E3
capsule_sha256=C5E164098E25AB9643FABAF707BD1F760108805F06663E1E825CCDF8E7B7F350
executor_sha256=07E066F15FA671DBF9B9F74ECAD2373C00D4A7551972E316F51BCB8265B630CC
docker_tree_sha256=F6CAF7B0DC1DA9C100DDA22049957F7501748D01A01A99F359B4DE19D2E7E8E9
docker_tree=2268|42532407|rdev_64770|single_fs|no_nested_mounts
manual_cleanup_runner_sha256=4F2FC7F35542C15B61259FE354E918C85CBD4F69E4838AF052B9B41AA3379EC7
terminal_recovery_runner_sha256=6C5E28C05430BA6D5CC04F40A47697B256CF2D2FF703074F8E234C5EA9EE6D1B
next=commit_push_readback|exact_manual_cleanup|exact_terminal_recovery|foreign_equality_receipt
```

Manual cleanup can remove only `/opt/amn2-spain-package` after exact transaction
and executor checksum checks. Terminal recovery may then remove only the exact
recorded AMN2 contour and prove persistent foreign equality with a volatile
receipt. No AMN2/AWG start, foreign-service mutation, USA change, or install
retry is allowed before that receipt.

## Previous override 2026-07-24: `544db…` terminal recovery passed; v15 is the only local install candidate

## Current override 2026-07-24: `544db…` terminal recovery passed; v15 is the only local install candidate

Transaction `544db99ee620bc0139914c75db98c9a2e16797aadffa6c106923825fc17a6b54`
is no longer a recovery blocker. Exact manual cleanup removed only the verified
package tree; exact terminal recovery removed only verified AMN2-owned current
objects and returned `foreign_service_persistent_equal=true`, volatile `0/0`.
There was no AMN2 start, AWG stop, foreign-service mutation, or USA change.

Do not infer a runtime cause from the old generic journal `unsupported`: a
read-only line-bound receipt ties it only to containerd/snapshotter logging.
The v15 package preserves classic-vfs policy and makes closed Docker image-load
transport failures observable as allowlisted labels without revealing stderr.

```text
package_sha256=DAA40D48B88B2AFB0FC4A57A1E5313D8B2851BCED89AEC655B628CB859AEA585
package_bytes=139970560
manifest_sha256=F13A7C4A02F7B9233629AD06DF06265BB1FC84B69478B4BDB03F1484515C79F2
executor_sha256=07E066F15FA671DBF9B9F74ECAD2373C00D4A7551972E316F51BCB8265B630CC
executor_bytes=145791
install_runner_sha256=762428179994934DE358F08CE55E0D6489E5095DD7C48742AA827B851C16AE9B
resource_plan_sha256=8BC5375F244F7CDD77A12BD4173CA19BE7430C35E49756D7B846906719369F43
collector_sha256=70316AEED9CF2BB4A45484F4E0A0A50CDD0D6359044CE6537B92241BCF52847A
source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
verification=double_build_byte_equal|offline_clean_room_69_artifacts|scoped_233_passed_4_skipped|powershell_parse_passed
next=diff_review|commit_push_origin_readback|exact_v15_install_approval
```

## Previous override 2026-07-24: v14 install is fail-closed; recover `544db…` before any diagnosis/retry

v14 reached `docker_started`; its bounded ledger then recorded
`awg_image_loaded=abandoned`. Normal automatic rollback left all AMN2 units
inactive, but current transaction requires terminal recovery because the exact
Docker tree retained two regular block devices. No further install is allowed.

```text
nonce=544db99ee620bc0139914c75db98c9a2e16797aadffa6c106923825fc17a6b54
transaction_sha256=89a9bec68c026ff6aa2865ab65f1a91333046e458746499ee29738b3a663c5cf
capsule_sha256=6411c3a47d8055cf70dc4a2082d4fd23752c94698f6dcfde96da4ff3026af723
docker_tree_sha256=0a086299782791b40464cf51087c9e72cbfbac254200cd4e39191f395e06c331
docker_tree=2268|42532407|0710|2_regular_blocks_rdev_64770|whiteouts_0|single_fs
next=exact_manual_cleanup|exact_terminal_recovery|foreign_equality_receipt|bounded_docker_load_diagnosis
```

Terminal recovery must remove only exact current AMN2-owned objects and prove
foreign persistent/volatile equality. No AWG stop, foreign-service mutation,
USA data change, or blind install retry is permitted.

## Previous override 2026-07-24: transaction `2315…` recovered; v14 package is the only retry candidate

Terminal recovery for transaction
`2315caba94df97a4a34c665fb58401f0bd56e1721a7cea59af20c38f23b8046c` passed
with `foreign_service_persistent_equal=true` and volatile receipt `0/0`.
`recovery_action=verified_previously_removed_owned_objects`; AMN2 remains
stopped and foreign Spain/USA contours remain untouched.

Only the new package may be used after local gates: it seals
`storage-driver=vfs` plus `features.containerd-snapshotter=false`, based on
read-only evidence `unsupported` + `overlayfs_present=false` after Docker 29
image load. No network/listener/firewall policy changed.

```text
package_sha256=984A2D87CC46EE84302E2462571659141D649CFE94206DE9FA6BBCF7AD8FA15B
manifest_sha256=7C897DA62CD64F77B008DABE4A9684DA1A9E06C637725EEAB69AD49468E14592
executor_sha256=D792D9CABB6B7FE3FABD7BC4B07D833D27549FE1484900770B54214D38FEAC29
package_bytes=139970560
executor_bytes=145505
verification=double_build_byte_equal|package_verify_passed|offline_extract_68_artifacts
next=scoped_tests|diff_review|commit_push_readback|exact_install_approval
```

## Previous override 2026-07-24: transaction `2315…` must be recovered before any retry

The approved vfs-bound install reached `docker_started`, observed the dedicated
vfs driver, then failed on abandoned `docker image load` action
`awg_image_loaded`. Automatic rollback removed the normal AMN2 contour, but
current transaction remains `manual_recovery_required`; no install retry is
permitted.

```text
nonce=2315caba94df97a4a34c665fb58401f0bd56e1721a7cea59af20c38f23b8046c
transaction_sha256=e4507cd1483d9b6aeb89da825ffed9b18bba8239ce7aacbba97e1b9e36aedc74
capsule_sha256=e9e2b849a8afa296cad980396f5bec81dc5fe15913a99d5df738fa15cb4cef12
executor_sha256=D792D9CABB6B7FE3FABD7BC4B07D833D27549FE1484900770B54214D38FEAC29
docker_tree_sha256=067776d5cff3b28c7404ff9f9a6494ea2bd7c7fb473b410dcc62f37282a419e4
docker_tree=entries_2268|bytes_42532407|root_mode_0710|single_filesystem|nested_mounts_0|regular_blocks_2_rdev_64770|whiteouts_0
next_gate=commit_push_then_exact_manual_cleanup_then_exact_terminal_recovery
```

Recovery removes only the exact retained AMN2 package/runtime/config/DB/Docker
contour and verifies persistent foreign equality with volatile receipt. It does
not stop AMN2/AWG (all units are inactive), alter the foreign service, or
touch USA. The only runtime causal label remains `unsupported`; do not treat
vfs as a reason to retry before recovery and a new bounded diagnosis.

## Current override 2026-07-24: vfs-bound retry ready after transaction `2f647…` recovery

Transaction `2f647f44976725fc569b045f923452b523db75c5edc86d651197875e1be887ed`
is recovered, not pending. Exact manual cleanup removed only the retained
package tree; exact terminal recovery removed only recorded AMN2-owned
objects. Its receipt passed persistent foreign equality with volatile counts
`0/0`. Pinned post-check passed: six AMN2 owned paths are absent, four AMN2
units are inactive, and terminal ledger remains `manual_recovery_required`.
No AMN2 start, foreign-service mutation, USA mutation or AWG stop occurred.

Root cause is evidenced rather than guessed: Docker journal returned
allowlisted `unsupported` and a read-only host probe returned
`overlayfs_present=false` (cgroup v2, userns=1). The new fresh-install package
changes only sealed Docker config to `storage-driver=vfs`.

```text
package_sha256=192189BA6E8832223322FF5D90574265D9137DB281E3F14FE43B3DA76BD95C1F
package_bytes=139970560
manifest_sha256=5D6CB1F3CD76503A9C5301CF4AD2747C4595E0A5A7E251CE4E98C1D51AB72609
executor_sha256=D792D9CABB6B7FE3FABD7BC4B07D833D27549FE1484900770B54214D38FEAC29
executor_bytes=145505
install_runner_sha256=3C68CB302BA4948E220B6148052D9BCAE50C95B49E19CF618AFDEF2B4AB89F6A
resource_plan_sha256=8BC5375F244F7CDD77A12BD4173CA19BE7430C35E49756D7B846906719369F43
collector_sha256=70316AEED9CF2BB4A45484F4E0A0A50CDD0D6359044CE6537B92241BCF52847A
source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
foreign_equality=terminal_recovery_persistent_true|volatile_0_0
local_verification=package_executor_double_build_byte_equal|package_verify_passed|offline_clean_room_69_artifacts|source_55dc243_verified|scoped_290_passed_4_skipped|powershell_parser_passed|diff_check_passed
next_gate=commit_push_origin_readback_then_checksum_bound_vfs_install
```

## Previous override 2026-07-24: transaction `2f647…` recovery required

Manual split-upload assembly is verified exactly: final package
`CB972C722F1B676DF48CA22497C1DFE85E21DB3B53663A0703FA1BD54C37575A`,
`139970560` bytes; final executor
`D792D9CABB6B7FE3FABD7BC4B07D833D27549FE1484900770B54214D38FEAC29`,
`145505` bytes. The approved runner skipped upload and reached
`package_verified_remote`, but fail-closed with
`production runtime rollback failed`; do not retry install.

Pinned read-only inventory found no AMN2 units and inactive Docker. Current
transaction nonce=`2f647f44976725fc569b045f923452b523db75c5edc86d651197875e1be887ed`,
transaction SHA=`44ed0fc0273854100a6cccdf44230081ea90051b29c94d64bffe221614337f28`,
capsule SHA=`b0470aa26f836b78cfbc961bda7d12457e08bebe9cf981e1df404093cc42fb93`,
status=`manual_recovery_required`. Retained contour is AMN2-owned only.
Docker scanner receipt is
`41b0b3b43e5177a03ad7e75e2efa3655d4464988485b576a87803ae2564bea65`,
916 entries, 41902300 bytes, RDEV 64770, one filesystem/no nested mounts.

Local, not-yet-pushed gates:

1. `phase12_spain_transaction_2f647_manual_cleanup_ssh_runner.ps1` — SHA
   `4E50A01DC83042F053DB7855A1CC095C297BADACA76F7AE5C1730D8155C4A018`;
   removes only verified retained `/opt/amn2-spain-package`.
2. `phase12_spain_transaction_2f647_terminal_recovery_ssh_runner.ps1` — SHA
   `86A81022EC3D2943D8BD563E59BCCF8021DBE636994EAFD7B9811205F7E8EEAD`;
   then rolls back exact recorded owned current contour, validates RDEV and
   foreign equality.

Local verification: scoped suite `154 passed`, both PowerShell runners parsed,
and `git diff --check` passed. Next: commit/push/readback, exact manual-cleanup
approval, then exact terminal-recovery approval. Do not mutate foreign Spain
service, USA, AWG or unrelated files.

## Current override 2026-07-23: capacity-bound upload local gate complete

Current transaction `1d7511…` is terminally recovered. Bound terminal receipt
`bb700842…` passed: it removed only verified AMN2-owned objects, preserved the
terminal ledger, confirmed persistent foreign-service equality and recorded
zero volatile entries. Pinned post-check found no AMN2 package/runtime/config/
Docker-data paths and all AMN2/Docker units inactive. The foreign Spain service
was not stopped or mutated; USA remains the rollback contour.

The previous install reached Docker image load, then automatic rollback ended
terminally. v12 adds no new mutation or resource behaviour: it retains only an
allowlisted `docker_image_load_*` causal label through a nested rollback
failure, never raw stderr/output/secrets. Package/executor are double-built
byte-identical; verify and clean-room extract passed; scoped suite=`155 passed`.

The approved v12 legacy-SCP and v13 pinned-SSH stdin attempts both stopped at
their first artifact upload after the same 300-second bound. Remote SHA,
activation and executor were not reached; AMN2 install did not start. Do not
repeat an install runner blindly.

The nonpersistent 16 MiB `/dev/null` probe with compression disabled also
timed out at 60 seconds. It did not call AMN2, package/executor, install,
rollback or foreign service, and made no persistent remote file. This proves
the existing 300-second bound is insufficient: even at the probe's upper
throughput bound, the 139970560-byte package needs over 500 seconds. The next
runner changes only its bounded upload allowance to 900 seconds; all artifact
hashes, remote SHA checks and rollback behaviour stay unchanged.

```text
package_sha256=CB972C722F1B676DF48CA22497C1DFE85E21DB3B53663A0703FA1BD54C37575A
package_bytes=139970560
manifest_sha256=AAA7980BDEF2787DC889C22D007177FDC2A75578CCA23DE71E2BC7733E552DD0
resource_plan_sha256=8BC5375F244F7CDD77A12BD4173CA19BE7430C35E49756D7B846906719369F43
executor_sha256=D792D9CABB6B7FE3FABD7BC4B07D833D27549FE1484900770B54214D38FEAC29
executor_bytes=145505
runner_sha256=172A0FBA9E9FB403D205EF40D9A3CB6A12A247A0AF29DB3FE9F4848E54133E6D
collector_sha256=70316AEED9CF2BB4A45484F4E0A0A50CDD0D6359044CE6537B92241BCF52847A
source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
run009_evidence_sha256=8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8
fingerprint_array_sha256=E15219CB5204D54A9AD11263CFBA1F7C86E16DAB3287C752A8B6F136EC4A5ED5
capacity=root_free_13969006592|root_inodes_1165185|run_free_99786752|run_inodes_122377|policy_passed
latest_live_transport=legacy_scp_timeout_300_seconds_and_pinned_ssh_stdin_timeout_300_seconds_before_remote_hash_activation_or_executor|no_amn2_install_started
ssh_data_path_diagnostic_runner_sha256=DC858AC0441AB02422BDBCB3B9E946A4870F3E8FFA46801EFA9C4B281FEAECC2
ssh_data_path_diagnostic=16MiB_to_dev_null|compression_disabled|timeout_60_seconds|no_persistent_remote_file|no_amn2_start
ssh_data_path_diagnostic_attempt_v1=local_receipt_normalization_failed|no_canonical_receipt|no_amn2_start
ssh_data_path_diagnostic_attempt_v2=timeout_60_seconds|no_amn2_start|no_persistent_remote_file
fresh_install_upload_timeout_policy=900_seconds|derived_from_16MiB_timeout_60_seconds|package_lower_bound_over_500_seconds
next_gate=commit_push_origin_readback_then_one_exact_900_second_install_approval
```

Do not repeat runs 001–009, resource-confirmation retries, prior builds,
SOL review or security scans. Do not stop AWG. Do not stop/mutate the foreign
Spain service. Do not migrate/delete USA data.

## Historical hand-off

Current state: v10 `install-bound` прошёл до intent `awg_image_loaded`
(`docker load`), но action не был committed. Automatic rollback удалил Docker
enable/start, все AMN2 units, DB/config/runtime objects. Receipt подтверждает:
AMN2 units inactive; foreign Spain service не останавливался и не изменялся;
USA остаётся rollback contour.

`manual-cleanup-bound` receipt=`passed`: CAS-verified retained
`/opt/amn2-spain-package` удалён, terminal ledger сохранён. Scoped read-only
receipt подтвердил inactive Docker/network/web/bot units. Foreign Spain
service не затрагивался.

Terminal recovery v2 удалил exact AMN2-owned contour `/etc/amn2-spain`,
`/opt/amn2-spain`, `/var/lib/amn2-spain*` и sealed Docker data-root. Immediate
read-only safety receipt подтвердил отсутствие package/runtime/path candidates
и inactive AMN2 Docker/network/web/bot units. Terminal ledger сохранён со
status=`manual_recovery_required`; foreign Spain service не останавливался и
не изменялся.

Первый terminal-recovery attempt fail-closed до delete: Linux scanner выдал
prefixed digest `sha256:<hex>`, а exact intent требует raw 64-hex. v2 исправил
digest и удалил contour, но затем fail-closed на старом equality adapter:
он ошибочно сравнивал owned `existing` inventory до/после. Новый executor
разрешает только этот expected AMN2 delta, по-прежнему требует persistent
foreign equality и записывает volatile fields. Его terminal-recovery receipt
mode строго verify-only: exact ledger обязан уже содержать все `removed`, иначе
он fail-closed без любой дополнительной mutation.

Первый receipt-only run остановился fail-closed на volatile raw nft hash между
двумя read-only samples; повторного удаления, AMN2 start или foreign-service
mutation не было. v3 сохраняет strict semantic firewall equality:
`backend=nft`, rule-count=`129`, semantic SHA=
`FB8E1D41F6F4F0EBCEB7C89D65E4E5E440E0AC0A4E780B4F638F96CEE1B9A682`.
Raw counter/hash drift отдельно не является изменением firewall semantics.
v3 receipt=`passed`: recorded terminal contour verified removed,
foreign persistent equality=`true`, volatile counts=`0`.

v11 добавляет bounded category-only diagnostic для Docker image load. Он
сохраняет только allowlisted label (`no_space`, `archive`, `permission`,
`daemon_unavailable`, `layer_apply`, `unsupported` или exit code), никогда raw
stderr/output/secrets. Package/executor double-built byte-identical; package
verify и clean-room extract прошли.

```text
package_sha256=8975804C1D192F59FA94441A84DFCD7B5E0159505BBA5BE620B2FD23B675E154
package_bytes=139970560
manifest_sha256=B7124C5954D32E4FF08CA00E1897953651309BEB505E4067C2437ED946E26461
resource_plan_sha256=8BC5375F244F7CDD77A12BD4173CA19BE7430C35E49756D7B846906719369F43
executor_sha256=E86E0AFD883A7E6DC45F7987CA26062EFAFFA632164546DBF57BEC16F876981D
executor_bytes=144710
runner_sha256=ED7CB371D8E4BB451B7DAB00F7C6E621AAF283DBE4581ADA4CA9D678E95E34A4
manual_cleanup=passed|package_tree_absent|terminal_ledger_preserved|units_inactive
manual_cleanup_executor_sha256=0E736B9DDF950DA050FE945F7D5F6D860F9C782A45066AE42429CCF56EF05585
manual_cleanup_executor_bytes=140277
terminal_recovery_nonce=e022f0b87a972f2256acd7800a4999553a8ceea2396a2644908f43c93a82febd
terminal_recovery_transaction_sha256=C58ED7EC5EA40F47C7C65C4A6D4691667160F2444764679A285A9EE47BEC8788
terminal_recovery_capsule_sha256=FE7E203B3A772811489371C90CAB88E0247882882938045FD85D80709F6B63CC
terminal_docker_tree_sha256=2328DA44BF2BDF6FD831A1AA27B50DF5BCE8649FBBEF015808A01CCD389A1CF4
terminal_docker_tree=entries_916|bytes_41902300|mode_0710|block_rdev_64770|single_filesystem|nested_mounts_0
terminal_recovery_executor_sha256=E86E0AFD883A7E6DC45F7987CA26062EFAFFA632164546DBF57BEC16F876981D
terminal_recovery_executor_bytes=144710
terminal_recovery_runner_sha256=F5959D04CAE8E6BF534474D9CBD308228EF8B0EB424FDCC02F15DB6144BD1C89
terminal_recovery_attempt_v1=failed_closed_before_delete|linux_digest_prefix_mismatch|retained_objects_unchanged|opt_flock_available
terminal_recovery_attempt_v2=owned_terminal_contour_removed|equality_failed_closed_on_owned_inventory_comparator|foreign_untouched
terminal_recovery_receipt_attempt_v1=failed_closed_on_raw_firewall_projection_drift|no_additional_mutation
terminal_recovery_receipt_v3=passed|verified_previously_removed_owned_objects|foreign_persistent_equal_true|volatile_before_0|volatile_after_0
terminal_recovery_receipt_mode=verify_only|requires_exact_removed_ledger|no_repeat_deletion
terminal_recovery_v3_local_verification=148_passed|semantic_firewall_regression_red_green|executor_double_build_byte_identical|offline_zip_verify_passed|unsupported_mode_fail_closed|diff_check_passed
fresh_install_upload_attempt=client_sftp_hung|terminated_local_before_executor|no_second_upload
fresh_install_remote_hash_attempt=failed_closed_before_executor|generic_upload_basename_vs_bound_temp_path
fresh_install_sftp_retry=failed_closed_before_remote_hash_and_executor|bounded_timeout_300_seconds
fresh_install_transport_policy=legacy_scp_o|connect_timeout_20|server_alive_15x4|scp_hard_timeout_300_seconds
fresh_install_remote_temp_binding=package_to_amn2_spain_phase12_install_a_tar|executor_to_amn2_spain_phase12_executor_a_pyz
fresh_install_local_verification=package_executor_double_build_byte_identical|package_verify_passed|clean_room_extract_passed|source_55dc243_verified|scoped_151_passed|powershell_parse_passed
current_install_outcome=legacy_scp_upload_and_executor_reached|production_runtime_rollback_failed|install_retry_forbidden
current_recovery_transaction_nonce=1D7511ED51CB2D908B329386DCB8EB7FD5C727ABC93346452ED35A66342204B4
current_recovery_transaction_sha256=08F1C860652FB561E3C1C921756549D3AACCAF86543CEB6C7FEA4EF845930883
current_recovery_capsule_sha256=2E146365A29C89E9466A8E54E174A3D4D2C969B2BFAEEDC9531A59EC4F756A18
current_recovery_docker_tree_sha256=6051924206A20BAB41384C9DEF68CB7D09AB02756515A0DCC05C7E290E3F3248
current_recovery_docker_tree=entries_916|bytes_41902300|block_rdev_64770|single_filesystem|nested_mounts_0
current_manual_cleanup_runner_sha256=5F0D7786DEA6462B7A4DB2D484677076BA827D37D0EEFDEAF9D4944AC348752D
current_manual_cleanup_executor_sha256=E86E0AFD883A7E6DC45F7987CA26062EFAFFA632164546DBF57BEC16F876981D
current_manual_cleanup_local_verification=scoped_152_passed|powershell_parse_passed|remote_executor_sha_readonly_passed|transaction_digest_readonly_passed
current_manual_cleanup_live_receipt=passed|approval_8b7bf91404b576382b3fa15b80b3e297e5f3c451a93fb2cfe78e523fd90f8eb6|package_tree_absent|terminal_ledger_preserved|units_inactive
current_terminal_recovery_runner_sha256=72A6AB833CF87EC14C16FCA2E548E4E4992740B71F2CEBCAFA83FF6CF66B1653
current_terminal_recovery_local_verification=scoped_153_passed|powershell_parse_passed|remote_executor_transaction_capsule_and_package_absence_preconditions
collector_sha256=70316AEED9CF2BB4A45484F4E0A0A50CDD0D6359044CE6537B92241BCF52847A
source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
run009_evidence_sha256=8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8
fingerprint_array_sha256=E15219CB5204D54A9AD11263CFBA1F7C86E16DAB3287C752A8B6F136EC4A5ED5
foreign_equality_policy=dynamic_persistent_v1
firewall_equality=semantic_nft_rule_count_129_sha256_FB8E1D41F6F4F0EBCEB7C89D65E4E5E440E0AC0A4E780B4F638F96CEE1B9A682
local_verification=double_build_byte_identical|package_verify_pass|clean_room_extract_pass|scoped_136_passed|package_bound_units_test_pass
spain_mutation=v10_attempt_rolled_back|manual_cleanup_package_tree_only|terminal_owned_contour_removed|no_active_amn2_runtime
```

Do not repeat runs 001–009, resource-confirmation retries, prior builds, SOL
review, or security scans. Do not stop AWG. Do not stop or mutate the foreign
Spain service. Do not migrate/delete USA data.

Next gate: stage only Phase 12 files, commit and push current branch, verify
origin readback, then issue one exact current terminal-recovery approval.
Manual cleanup passed and package tree is absent; current transaction remains
`manual_recovery_required`. Do not retry install. The terminal runner requires
remote executor, transaction/capsule SHA and package-tree absence, rolls back
only sealed owned current actions, and proves foreign equality before any fresh
install attempt.
