# Phase 16 Spain read-only preflight STOP receipt 008 claim 016

- Recorded: `2026-08-25T11:01:14Z`
- Claim: `phase16-spain-preflight-20260825-016`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-008`
- Package identity: `e1cf967208467acebdfcaaac30557436855b75a92b5154ab41fc3429f747a7c3`
- Destination: `root@138.124.181.246`
- Claim issued: `2026-08-25T10:57:32Z`
- Started: `2026-08-25T10:57:33Z`
- Ended: `2026-08-25T10:57:40Z`
- Runner exit: `0`
- Decision: `stop`
- Stop reasons: `observation_failed`, `resource_conflict`
- Transport disposition: `read_only_completed`

## Checksum binding

- Manifest SHA-256: `065d3369b8dd11783572365f06f84c6ec3ed207e71c758dea2f1d57a02baf24e`
- Collector SHA-256: `b2e112eec77a3a6c272be8d79c7fd010a8f54ad1f6d833002f76d1fcfba03ada`
- Runner SHA-256: `dfc47725248376a0c3e816a9e8681385c615cf3a713ef7cba079fbfbd8d32828`
- Ephemeral future-claim SHA-256: `12c7b0f8db0dd0f0a16059a6d1bc05897dd00c7be35525ec2139cbab50bf1999`
- Pinned host key: `SHA256:XVFOmBAXMHYlngo9+x7lGAJbzlOqiMiG/6/4qhRC4HU`

## Terminal evidence

- Outcome: `C:\ProgramData\AMN2\phase16\readonly-preflight\outcomes\phase16-spain-preflight-20260825-016.json`
- Outcome SHA-256: `7e4b6d08810b1f936b6fa65155c36654a67e623d52f8aa3ef593def98e4cc7a8`
- Terminal claim SHA-256: `6a25808aea03c91acde02e46d6a81ac961a07f32721127ff66777b8b357092a6`
- Canonical terminal evidence validation: `pass`
- Exact terminal evidence properties: `pass`
- Exact observation names and shape: `pass`
- Observation count: `23`
- Terminal claim status: `completed`
- Incomplete transaction artifacts: `0`
- Recovery outcome artifacts: `0`
- Temporary claim artifacts: `0`
- Matching Spain SSH processes after completion: `0`
- Matching Phase 16 runner processes after completion: `0`
- Persistent claim lock: present as expected audit/serialization state
- Raw remote output persisted: `false`

## Blocking observations

- `awg2_health`: `stop`
- `firewall`: `stop`

The evidence records `architecture`, `backup_capability`, `container_capability`, `disk_space`, `os_compatibility`, `python_3_12`, `routes`, `service_capability`, and `telegram_prerequisites` as `pass`. The intended bridge, config path, container CIDR, container name, AWG3 interface, service name, state root, UDP port, and VPN CIDR are `free`; Phase 14/15/16 recovery markers are `absent`. `application_state` and `database_state` are `present`. Passing and free observations do not override either blocking observation.

No observed state SHA-256 or stage authorization is emitted for a STOP decision.

## Safety boundary

- Approved claim-016 runner invocations: `1`
- SSH transport attempts: `1`
- Remote file written: `false`
- Live mutation: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Retry attempted: `false`
- Diagnostic egress attempted: `false`
- Stage authorization emitted: `false`
- Package revision 008 changed: `false`

This schema-valid read-only outcome is terminal for the approved attempt. Its outcome SHA-256 is evidence of the observed STOP state and is not a stage authorization. No diagnostic egress, server-side repair, controlled stage, install, pilot issuance, or AWG2 operation is authorized by this receipt.
