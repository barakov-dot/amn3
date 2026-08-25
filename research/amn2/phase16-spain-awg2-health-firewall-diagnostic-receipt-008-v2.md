# Phase 16 Spain firewall shape diagnostic receipt 008 V2

- Recorded: `2026-08-25T11:18:04Z`
- Observed: `2026-08-25T11:17:18Z`
- Command ID: `PHASE16_AWG2_HEALTH_AND_FIREWALL_BLOCKERS_V2`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-008`
- Package identity: `e1cf967208467acebdfcaaac30557436855b75a92b5154ab41fc3429f747a7c3`
- Preflight outcome SHA-256: `7e4b6d08810b1f936b6fa65155c36654a67e623d52f8aa3ef593def98e4cc7a8`
- Diagnostic V1 stdout SHA-256: `dbffa1c71645d633423d1e05c4d0bca9d0d15bc1142131bbe83028dd99a1e4c0`
- Destination: `root@138.124.181.246`
- SSH attempts: `1`
- Exit: `0`
- Normalized stdout SHA-256: `e192f9b9f86177961644a186d2ae6a02eed10edb23831d071ef0195a4a12a05d`
- Normalized stdout bytes: `1284`
- Stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Stderr bytes: `0`

## nft observed payload shapes

The nft probe exited `0` with empty stderr. Its JSON and exact top-level shape were valid. The normalized nft output was `61189` bytes with SHA-256 `ddf093edd65fb677f4e857d4e40a3f19aff9ff66ee2a958bca1246edc942ae39`.

- `dnat`: count `1`, payload type `object`
  - `addr:string`
  - `family:string`
  - `port:int`
- `limit`: count `13`, payload type `object`
  - `burst:int`
  - `per:string`
  - `rate:int`
- `masquerade`: count `1`, payload type `null`
- `xt`: count `117`, payload type `object`
  - `name:string`
  - `type:string`

No payload values were captured. V1 already recorded no normalized references to AWG3 interface `awg3`, bridge `amn2sp3br0`, CIDRs `10.212.13.0/24` and `172.29.252.0/28`, or UDP `30002`.

These exact key/type shapes are sufficient for a bounded fail-closed parser extension: reject missing, extra, malformed, wrong-type, out-of-range, or unknown expression shapes; preserve target address, network, interface, and port conflict detection.

## iptables single-line classification

- Probe: exit `0`, stderr empty
- Output bytes: `50`
- Output SHA-256: `b8ab12afc0969351ffbd28fa574cbb24c77b43b28adc0efc2acdb63cf4beb7cf`
- Line count: `1`
- Line length without LF: `49`
- Printable ASCII: `true`
- Begins with comment marker: `true`
- Normalized class: `other_comment`

No line value was captured. Combined with V1 evidence of zero tables, commits, rules, option kinds, and target references, this supports admitting only successful comment-only iptables output as no conflict while keeping every non-comment, malformed, stderr, nonzero, or conflicting form fail-closed.

## Resulting bounded local contract

- Extend nft parsing only for the four exact observed key/type shapes.
- Continue checking `dnat` address and port fields against Phase 16 target resources.
- Treat `limit`, exact null `masquerade`, and bounded exact `xt{name,type}` as non-resource expressions after validation.
- Admit successful printable comment-only iptables output as no conflict.
- Keep unknown nft/iptables forms fail-closed.
- Do not relax AWG2 handshake freshness. A real AWG2 client handshake is required before the next preflight.

## Safety boundary

- Collector execution: `false`
- Preflight retry: `false`
- Raw values captured: `false`
- Raw output persisted: `false`
- Remote file written: `false`
- Live mutation: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Matching Spain SSH processes after completion: `0`
- Package revision 008 changed: `false`

This receipt authorizes no code change, package materialization, further egress, preflight retry, controlled stage, install, pilot issuance, or AWG2 operation.
