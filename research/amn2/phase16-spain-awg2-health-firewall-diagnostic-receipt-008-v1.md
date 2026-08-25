# Phase 16 Spain AWG2 health and firewall diagnostic receipt 008 V1

- Recorded: `2026-08-25T11:11:05Z`
- Observed: `2026-08-25T11:10:17Z`
- Command ID: `PHASE16_AWG2_HEALTH_AND_FIREWALL_BLOCKERS_V1`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-008`
- Package identity: `e1cf967208467acebdfcaaac30557436855b75a92b5154ab41fc3429f747a7c3`
- Preflight outcome SHA-256: `7e4b6d08810b1f936b6fa65155c36654a67e623d52f8aa3ef593def98e4cc7a8`
- Destination: `root@138.124.181.246`
- SSH attempts: `1`
- Exit: `0`
- Normalized stdout SHA-256: `dbffa1c71645d633423d1e05c4d0bca9d0d15bc1142131bbe83028dd99a1e4c0`
- Normalized stdout bytes: `2336`
- Stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Stderr bytes: `0`

## AWG2 health classification

- Collector-equivalent state: `stop`
- Exact failure class: `handshake_freshness`
- Owner unit active and stable: `true`
- Container snapshot valid and stable: `true`
- Container restart count: `59`
- Interface `awgsp0` shape valid: `true`
- Handshake probe successful: `true`
- Handshake records valid: `true`
- Handshake record count: `7`
- Handshake age bucket: `stale_gt_600`
- Fresh handshake within 600 seconds: `false`

The AWG2 STOP is caused only by the collector's traffic-recency condition. The diagnostic did not observe an owner, container, interface, command, or handshake-schema failure. This evidence does not by itself authorize relaxing the policy or changing AWG2.

## Firewall classification

- Collector-equivalent state: `stop`
- Failure classes: `nft:schema_stop`, `iptables:schema_stop`
- Normalized target references to AWG3 interface, bridge, CIDRs, or UDP 30002: none in all three backends

### nft

- Probe: exit `0`, stderr empty, JSON valid, top-level shape valid
- Output bytes: `61189`
- Output SHA-256: `558b07109436a55b9241f6ddf974a2c0e452a475a4198958fc09cd7e707a88f4`
- Entry count: `271`
- Entry types: `chain`, `metainfo`, `rule`, `table`
- Unsupported expression kinds: `dnat`, `limit`, `masquerade`, `xt`
- Classification: `schema_stop`

### iptables

- Probe: exit `0`, stderr empty, canonical newline present
- Output bytes: `50`
- Output SHA-256: `b8ab12afc0969351ffbd28fa574cbb24c77b43b28adc0efc2acdb63cf4beb7cf`
- Lines: `1`
- Tables, commits, rules, and option kinds: `0`
- Classification: `schema_stop`

### iptables-legacy

- Probe: exit `0`, stderr empty
- Output bytes: `0`
- Output SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Classification: `pass`

The normalized evidence shows parser coverage blockers rather than an observed AWG3 resource reference. A safe nft parser change still requires bounded payload-shape evidence for the four unsupported expression kinds; their raw payloads were not captured.

## Safety boundary

- Collector execution: `false`
- Preflight retry: `false`
- Raw output persisted: `false`
- Remote file written: `false`
- Live mutation: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Matching Spain SSH processes after completion: `0`
- Package revision 008 changed: `false`

This receipt authorizes no local fix, further diagnostic egress, preflight retry, controlled stage, install, pilot issuance, or AWG2 operation.
