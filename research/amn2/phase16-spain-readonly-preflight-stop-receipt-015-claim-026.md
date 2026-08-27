# Phase 16 Spain read-only preflight STOP receipt 015 claim 026

- Recorded: `2026-08-27T05:01:25Z`
- Moscow observation window: `2026-08-27 07:58:27-07:58:32 +03:00`
- Claim: `phase16-spain-preflight-20260827-026`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-015`
- Package identity: `7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509`
- Destination approved: `root@138.124.181.246`
- Claim issued: `2026-08-27T04:57:11Z`
- Claim expires: `2026-08-27T05:02:11Z`
- Collector evidence started: `2026-08-27T04:58:27Z`
- Collector evidence ended: `2026-08-27T04:58:32Z`
- Runner exit: `0`
- Decision: `stop`
- Stop reasons: `observation_failed`
- Transport disposition: `read_only_completed`

## Checksum and local baseline binding

- Manifest SHA-256: `f19f7f177d22b9b66311cb1db552f6b8ae9242f7d374b43d50afc17c09be6c74`
- Collector SHA-256: `244601519bdb7fa003af4dcb0eb8140d946cf8239e83b1098b2242d7d22db992`
- Preflight runner SHA-256: `e5551706eb27ff8e5cb3299f7b57ad7f1f55b9d80bb88bcc7501c29f4ba2d983`
- Canonical single-LF future-claim SHA-256: `e59a4b51591e2090473aab7e0baab3f82d8a45d5a7166a83eeae70ea2bb0fe17`
- Package-bound Python preflight contract SHA-256: `8d37a4f02e7a5bc7d82a19545a11f4138836e660838653506b7a94c570120d6b`
- Package readiness receipt SHA-256: `9f8b84b653a6a7178f6c0f62ad41cf2b5446330a41eb208aea7acf63d827d26d`
- Starting tooling HEAD: `16e58b767a9c0e8f15fd2ff29ac0132277ba413a`
- Packaged tooling source: `03bf59c5bc71b06c19a43b5f376226c75c5a60d8`
- Packaged application source: `a3682fc44dd9e74ff96392ad99623474facf377f`
- Local prelaunch gate: exact approved package/identity/hashes, trusted host/key binding, managed state ACL chain, unused claim/outcome paths, no incomplete journal and no matching Spain SSH process.
- Execution-policy bypass was confined to child PowerShell processes. No user/machine execution-policy setting was changed.

## Terminal evidence

- Outcome: `C:\ProgramData\AMN2\phase16\readonly-preflight\outcomes\phase16-spain-preflight-20260827-026.json`
- Outcome SHA-256: `752ca5c954ce3092ac87a0df90a874f5f67bbaa3a628b82a264b75ed661feb80`
- Outcome bytes: `3636`
- Terminal claim SHA-256: `f61f627490616882160ff893c83b470b3a9d6763ac53c4faa5591983444c1d1f`
- Exact package-bound Python outcome contract validation: `pass`
- Canonical JSON byte equality: `pass`
- Exact checksum, claim-window, observation-inventory, safety and decision binding: `pass`
- Observation count: `23`
- Blocking observation count: `1`
- Terminal claim status: `completed`
- Terminal claim reason: `not_applicable`
- Incomplete transaction artifacts: `0`
- Recovery outcome artifacts for claim: `0`
- Owned transaction temporary residues: `0`
- Matching Spain SSH processes after completion: `0`
- Matching exact preflight runner processes after completion: `0`
- Raw remote output persisted: `false`
- The temporary future-claim file was removed after byte-level outcome validation and terminal lifecycle confirmation; the terminal claim and outcome remain retained.

`completed` confirms completed evidence collection, not a passing preflight.
The schema-valid decision remains `stop`, and the allowance is consumed `1/1`.

## Observation summary

- `stop`: `awg2_health`
- `present`: `application_state`, `database_state`
- `pass`: `architecture`, `backup_capability`, `container_capability`, `disk_space`, `firewall`, `os_compatibility`, `python_3_12`, `routes`, `service_capability`, `telegram_prerequisites`
- `free`: `bridge_amn2sp3br0`, `config_path`, `container_cidr_172_29_252_0_28`, `container_name`, `interface_awg3`, `service_name`, `state_root`, `udp_30002`, `vpn_cidr_10_212_13_0_24`
- `absent`: `recovery_markers_phase14_phase15_phase16`
- `unknown`: none

The only blocking observation is `awg2_health`; the other 22 observations are non-blocking.
The outcome does not disclose which owner-unit, container, interface, handshake-command/schema or handshake-freshness subcheck failed.
No narrower root cause is inferred from the observation digest or historical package-012/013 diagnostics.
The 600-second AWG2 freshness requirement is unchanged. This STOP does not establish that freshness, configuration quality, or the server network is the cause.

## Safety boundary

- Approved preflight runner invocations: `1`
- SSH transport attempts: `1`
- Transport carries the checksum-bound collector over stdin; no remote package upload or file creation was performed.
- Strict host-key checking and single SSH connection attempt remained enabled.
- Remote file written: `false`
- Live mutation: `false`
- Additional diagnostic or preflight retry: `false`
- Stage, install or rollback attempted: `false`
- AWG2 service/runtime/peer/config/firewall/route changes: `false`
- Pilot peer/config created or global issuance enabled: `false`
- Package 014 and package 015 contents changed: `false`
- New materialization, package verifier or test-suite run during this preflight turn: `0`
- Transaction `phase16-spain-stage-20260827-004` remains consumed and is not reused.

## Next exact diagnostic gate

Task 2 remains blocked; no stage authorization is emitted.
A separately approved single read-only AWG2 health diagnostic should classify owner, container, interface and handshake freshness without raw values, collector execution, server writes or preflight retry.
The following is a request for future authority; no diagnostic was executed in this turn:

```text
/APPROVE PHASE16 SPAIN READONLY_AWG2_HEALTH_DIAGNOSTIC_EGRESS TO_138.124.181.246 PACKAGE_phase16-awg3-family-3-1-spain-pilot-20260824-015 IDENTITY_7ceafccd337323b84c1de0cf57d949023bfe48365ce313e1d1d99a7afb937509 PREFLIGHT_OUTCOME_SHA256_752ca5c954ce3092ac87a0df90a874f5f67bbaa3a628b82a264b75ed661feb80 ONE_SSH_REMOTE_COMMAND_ATTEMPT COMMAND_ID_PHASE16_PACKAGE015_AWG2_HEALTH_STOP_V1 TIMEOUT_30S STRICT_HOST_KEY_CHECKING CAPTURE_NORMALIZED_AWG2_OWNER_CONTAINER_INTERFACE_HANDSHAKE_FRESHNESS_CLASS_ONLY NO_RAW_VALUES NO_RAW_PERSISTENCE NO_COLLECTOR NO_REMOTE_WRITE NO_PREFLIGHT_RETRY NO_STAGE NO_INSTALL AWG2_UNTOUCHED
```

Any new preflight after diagnosis needs a separate explicit scope decision and exact approval.
Controlled stage and the one-operator ARM/Windows AWG3.1 pilot remain gated on preflight PASS and their own approvals.
Task 4.5 AWG2/AWG3.1 A/B transport-quality comparison remains mandatory before Task 5 acceptance and Task 6 closeout.
