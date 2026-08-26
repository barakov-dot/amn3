# Phase 16 Spain AWG2 health diagnostic receipt 013 V1

- Recorded: `2026-08-26T16:02:41Z`
- Command ID: `PHASE16_PACKAGE013_AWG2_HEALTH_STOP_V1`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-013`
- Package identity: `9cca04dd98143ff8a2dd7877d882cd53eccd09e4638ac2307cd92d0e31b3441c`
- Preflight outcome SHA-256: `0ae0a1fd76de48935a0ad7b06f9961604ca49e8d1e65026a24210b45d06447ae`
- Destination: `root@138.124.181.246`
- SSH attempts: `1`
- Exit: `0`
- Diagnostic program SHA-256: `d441a8e26ea7b22e5bb6174422f00faf1fc88fa47803cf8099fd54e0cb3890b6`
- Normalized stdout SHA-256: `b95b6edafbdcd1b7255fdccdc1ebe1906feca24d992585da1126e0a87bc8e27c`
- Normalized stdout bytes: `585`
- Stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Stderr bytes: `0`
- Normalized schema validation: `pass`

## AWG2 health classification

- Collector-equivalent state: `stop`
- Exact failure class: `handshake_freshness`
- Owner unit state: `pass`
- Owner unit stability: `pass`
- Container shape: `pass`
- Container stability: `pass`
- Interface `awgsp0` shape: `pass`
- Handshake command: `pass`
- Handshake record schema: `pass`
- Handshake freshness class: `stale_gt_600`

The package-013 preflight STOP is caused only by the unchanged 600-second AWG2 traffic-recency condition. The diagnostic observed no owner-unit, owner-stability, container-shape, container-stability, interface, handshake-command, framing, or handshake-schema failure. No AWG2 freshness-policy change or local code correction is justified by this evidence.

## Safety boundary

- Collector execution: `false`
- Preflight retry: `false`
- Raw values captured in normalized output: `false`
- Raw output persisted: `false`
- Remote file written: `false`
- Live mutation: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Matching Spain SSH processes after completion: `0`
- Matching diagnostic processes after completion: `0`
- Package revision 013 changed: `false`

The approved diagnostic allowance is consumed `1/1`. This receipt authorizes no further diagnostic egress, preflight retry, controlled stage, install, pilot issuance, config creation, or AWG2 operation. To obtain a fresh AWG2 observation, the operator must first generate real traffic through an existing Spain AWG2 client configuration. Because the Phase 16 preflight allowance is already consumed, one new preflight requires a separate explicit `/GO` scope decision followed by a new exact checksum-bound `/APPROVE`.
