# Phase 16 Spain read-only preflight STOP receipt 013 claim 022

- Recorded: `2026-08-26T15:45:47Z`
- Claim: `phase16-spain-preflight-20260826-022`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-013`
- Package identity: `9cca04dd98143ff8a2dd7877d882cd53eccd09e4638ac2307cd92d0e31b3441c`
- Destination approved: `root@138.124.181.246`
- Claim issued: `2026-08-26T15:42:31Z`
- Claim expires: `2026-08-26T15:47:31Z`
- Collector evidence started: `2026-08-26T15:42:31Z`
- Collector evidence ended: `2026-08-26T15:42:53Z`
- Runner exit: `0`
- Decision: `stop`
- Stop reasons: `observation_failed`
- Transport disposition: `read_only_completed`

## Checksum binding

- Manifest SHA-256: `a80cd8d651b80c0fa24bbe26da3c310a7823db368093d5cc7d9f4edbb864ed47`
- Collector SHA-256: `39da47ad8776d8c77198f306c387d26e43d70631b435a7fc50f909b855ce8a66`
- Preflight runner SHA-256: `27684b4bc33704d91f3ece34f195d1aa9aba6d6c5f811283323e3560575e366c`
- Ephemeral future-claim SHA-256: `82990c880c839aeb3c9c2e2a96a27e5f3de436abadb9db6cca45656d3239df10`
- Resource-plan SHA-256: `bf41fbcdcd7fe4f34cc5cfde125fe4ce6f36804bbe8ca3e426c5dccdb0203938`
- Application-stage SHA-256: `70042dc351c315fc842b2042eb984b3b7430b11e21610610471be143680905a4`
- AWG3.1-runtime-stage SHA-256: `9dd153aa350b65c737de770ae7697d2fc8c59a663c9b3553c388e7a25052e0a9`
- Stage-support SHA-256: `871d2e7ef3926723a35912947886828faeabb576ebfec6a5573064ae5b932098`
- Controlled-stage coordinator SHA-256: `02c9c3cdf5184b0d4ed5eb1dbb381634119ab0a0b4cf2c4a2adf7f54c7b2523d`
- Controlled-stage SSH runner SHA-256: `50c517f763303b9cdc5cd294fffafcf41c5121ebda74c250d55782bc625b6a8d`
- Canonical rollback-scope SHA-256: `c70437c363cc822b602d90902d095917041e78044bb299426d7fa01aa8f17d85`

Correction recorded after the transaction-002 local prelaunch STOP: the
previous value was inherited from package 012. The package-013 stage runner
computes the corrected value above because `application_release` is bound to
the package-013 ID. Package contents, manifest, and package identity were not
changed by this evidence correction.

## Terminal evidence

- Outcome: `C:\ProgramData\AMN2\phase16\readonly-preflight\outcomes\phase16-spain-preflight-20260826-022.json`
- Outcome SHA-256: `0ae0a1fd76de48935a0ad7b06f9961604ca49e8d1e65026a24210b45d06447ae`
- Terminal claim SHA-256: `4da2c6d6097cdf8371cf1e98b9813a5da6e15ac49cc4797f602786367672be8d`
- Exact package-bound Python contract validation: `pass`
- Canonical JSON byte equality: `pass`
- Exact decision binding: `pass`
- Observation count: `23`
- Terminal claim status: `completed`
- Incomplete transaction artifacts: `0`
- Recovery outcome artifacts for claim: `0`
- Temporary future-claim artifact present after completion: `false`
- Matching Spain SSH processes after completion: `0`
- Matching Phase 16 runner processes after completion: `0`
- Raw remote output persisted: `false`

## Observation summary

- `stop`: `awg2_health`
- `present`: `application_state`, `database_state`
- `pass`: `architecture`, `backup_capability`, `container_capability`, `disk_space`, `firewall`, `os_compatibility`, `python_3_12`, `routes`, `service_capability`, `telegram_prerequisites`
- `free`: `bridge_amn2sp3br0`, `config_path`, `container_cidr_172_29_252_0_28`, `container_name`, `interface_awg3`, `service_name`, `state_root`, `udp_30002`, `vpn_cidr_10_212_13_0_24`
- `absent`: `recovery_markers_phase14_phase15_phase16`
- Other `stop` or `unknown` observations: none

The normalized outcome identifies only the `awg2_health` observation as blocking. It does not expose which owner, container, interface, or handshake-freshness subcheck failed. The current AWG2 observation hash differs from both the prior package-012 STOP and PASS hashes, so no narrower root cause is asserted without a separately approved read-only diagnostic.

## Safety boundary and stage gate

- Approved package-013 preflight runner invocations: `1`
- SSH transport attempts: `1`
- Remote file written: `false`
- Live mutation: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Preflight retry attempted: `false`
- Stage authorization emitted: `false`
- Pilot peer/config created: `false`
- General AWG3 issuance enabled: `false`
- Package revision 013 changed: `false`

This schema-valid read-only outcome is terminal for the approved attempt. The preflight allowance is consumed `1/1`; no retry is permitted. Its outcome SHA-256 is evidence of the observed STOP state and is not a stage authorization. No diagnostic egress, server-side repair, controlled stage, install, pilot issuance, config creation, or AWG2 operation is authorized by this receipt. Any further diagnosis requires a separate exact package-, identity-, and outcome-bound read-only approval.
