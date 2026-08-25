# Phase 16 Spain read-only preflight STOP receipt 009 claim 017

- Recorded: `2026-08-25T13:52:38Z`
- Claim: `phase16-spain-preflight-20260825-017`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-009`
- Package identity: `2a4549c05daca9f3666ffe1babfa17851c93c59cc1b902efe9dca16002d9fe5d`
- Destination: `root@138.124.181.246`
- Claim issued: `2026-08-25T13:46:53Z`
- Started: `2026-08-25T13:48:12Z`
- Ended: `2026-08-25T13:48:28Z`
- Runner exit: `0`
- Decision: `stop`
- Stop reasons: `resource_conflict`
- Transport disposition: `read_only_completed`

## Checksum binding

- Manifest SHA-256: `084302df340f4741109103dc7baf94601dd24163406d002b82756fde8d9c80c1`
- Collector SHA-256: `80b3347b8787ca1490b40f1763ccff01fb4428233ca4f240c068fd02e35cef15`
- Runner SHA-256: `f0d0843c05c341b340dce8721d30f55380b6a8493aff70da7013185875301fbf`
- Ephemeral future-claim SHA-256: `6249be4c2529dd94eef512dcf80de47d5dc00c6bb0dcfc9de21b89f8b9c666cd`
- Pinned host key: `SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU`

## Terminal evidence

- Outcome: `C:\ProgramData\AMN2\phase16\readonly-preflight\outcomes\phase16-spain-preflight-20260825-017.json`
- Outcome SHA-256: `672a0037e0139f9c70a227fa7713d97dcc122a519ecaeeeebf02600d0d100184`
- Terminal claim SHA-256: `d590cca20d1f7951c41d4a7f6df1561385e2d8448fb0be57acade9a62d9dc1f3`
- Canonical terminal evidence validation: `pass`
- Exact terminal evidence properties: `pass`
- Exact observation names and shape: `pass`
- Observation count: `23`
- Terminal claim status: `completed`
- Incomplete transaction artifacts: `0`
- Recovery outcome artifacts for claim: `0`
- Temporary claim artifacts: `0`
- Matching Spain SSH processes after completion: `0`
- Matching Phase 16 runner processes after completion: `0`
- Persistent claim lock: present as expected audit/serialization state
- Raw remote output persisted: `false`

## Blocking observation

- `firewall`: `stop`

The evidence records `architecture`, `awg2_health`, `backup_capability`, `container_capability`, `disk_space`, `os_compatibility`, `python_3_12`, `routes`, `service_capability`, and `telegram_prerequisites` as `pass`. The intended bridge, config path, container CIDR, container name, AWG3 interface, service name, state root, UDP port, and VPN CIDR are `free`; Phase 14/15/16 recovery markers are `absent`. `application_state` and `database_state` are `present`. The passing AWG2 health observation is consistent with the operator-generated traffic, but does not override the firewall blocker.

No observed state SHA-256 or stage authorization is emitted for a STOP decision.

## Safety boundary

- Approved claim-017 runner invocations: `1`
- SSH transport attempts: `1`
- Remote file written: `false`
- Live mutation: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Retry attempted: `false`
- Diagnostic egress attempted: `false`
- Stage authorization emitted: `false`
- Package revision 009 changed: `false`

This schema-valid read-only outcome is terminal for the approved attempt. Its outcome SHA-256 is evidence of the observed STOP state and is not a stage authorization. No diagnostic egress, server-side repair, controlled stage, install, pilot issuance, or AWG2 operation is authorized by this receipt.
