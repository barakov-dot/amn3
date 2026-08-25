# Phase 16 Spain read-only preflight STOP receipt 010 claim 018

- Recorded: `2026-08-25T17:20:46Z`
- Claim: `phase16-spain-preflight-20260825-018`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-010`
- Package identity: `0d9367c120b98d85981a8ad591870f84d5ff6544f5c1168d833f3e53a7e4d658`
- Destination: `root@138.124.181.246`
- Claim issued: `2026-08-25T17:15:23Z`
- Runner started: `2026-08-25T17:16:55Z`
- Collector evidence started: `2026-08-25T17:16:56Z`
- Collector evidence ended: `2026-08-25T17:17:03Z`
- Runner exit: `0`
- Decision: `stop`
- Stop reasons: `observation_failed`, `resource_conflict`
- Transport disposition: `read_only_completed`

## Checksum binding

- Manifest SHA-256: `e79ce27b34d175495ff3f5eebb3e19b1a2cbe6c51c47493fab01113fe2a63805`
- Collector SHA-256: `da54841074b70b1cdd0c2704ceefa23b81a79cae6c26e70722b7371e728efc45`
- Runner SHA-256: `70cb93f165bb4578ee8d5de3bd4cc71b8b54ed66bce34352fc074aff1468742c`
- Ephemeral future-claim SHA-256: `4bbda668b7376a03e2d54fe93fe06f59e96e3385492fa6ccbe280b184daaf4a0`
- Pinned host key: `SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU`

## Terminal evidence

- Outcome: `C:\ProgramData\AMN2\phase16\readonly-preflight\outcomes\phase16-spain-preflight-20260825-018.json`
- Outcome SHA-256: `4622f3b6d6d4726ff93377f7127db48d84785dd3bc9e8d7b8471db4ec59a8636`
- Terminal claim SHA-256: `50ddc0a72d484bb985527affb5fbcbdd6813d75c3f9a8e5c0d69be8682970a62`
- Canonical terminal evidence validation: `pass`
- Exact terminal evidence properties: `pass`
- Exact observation names, order, states, and shape: `pass`
- Observation count: `23`
- Terminal claim status: `completed`
- Incomplete transaction artifacts: `0`
- Recovery outcome artifacts for claim: `0`
- Temporary claim artifacts: `0`
- Matching Spain SSH processes after completion: `0`
- Matching Phase 16 runner processes after completion: `0`
- Persistent claim lock: present as expected audit/serialization state
- Raw remote output persisted: `false`

## Blocking observations

- `awg2_health`: `stop`
- `firewall`: `stop`

The evidence records `architecture`, `backup_capability`, `container_capability`, `disk_space`, `os_compatibility`, `python_3_12`, `routes`, `service_capability`, and `telegram_prerequisites` as `pass`. The intended bridge, config path, container CIDR, container name, AWG3 interface, service name, state root, UDP port, and VPN CIDR are `free`; Phase 14/15/16 recovery markers are `absent`; `application_state` and `database_state` are `present`.

No observed-state SHA-256 or stage authorization is emitted for a STOP decision. The normalized outcome does not expose the underlying raw AWG2-health or firewall values; classifying either remaining blocker requires a separately checksum-bound read-only diagnostic approval.

## Safety boundary

- Approved package-010 runner invocations: `1`
- SSH transport attempts: `1`
- Remote file written: `false`
- Live mutation: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Retry attempted: `false`
- Diagnostic egress attempted: `false`
- Stage authorization emitted: `false`
- Package revision 010 changed: `false`

This schema-valid read-only outcome is terminal for the approved attempt. Its outcome SHA-256 is evidence of the observed STOP state and is not a stage authorization. No diagnostic egress, server-side repair, controlled stage, install, pilot issuance, config creation, or AWG2 operation is authorized by this receipt.
