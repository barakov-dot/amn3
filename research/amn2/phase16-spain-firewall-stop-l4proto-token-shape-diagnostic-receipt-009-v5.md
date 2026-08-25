# Phase 16 Spain firewall STOP L4 protocol token shape diagnostic receipt 009 V5

- Recorded: `2026-08-25T16:38:41Z`
- Command ID: `PHASE16_FIREWALL_STOP_L4PROTO_TOKEN_SHAPE_V5`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-009`
- Package identity: `2a4549c05daca9f3666ffe1babfa17851c93c59cc1b902efe9dca16002d9fe5d`
- Destination: `root@138.124.181.246`
- Bound preflight outcome SHA-256: `672a0037e0139f9c70a227fa7713d97dcc122a519ecaeeeebf02600d0d100184`
- Bound diagnostic V4 stdout SHA-256: `85d82743e7c352f986f3a0619a46b10e787d96644ff1ddb88364114cdd8b3303`
- SSH exit: `0`

## Diagnostic binding

- Ephemeral diagnostic program SHA-256: `1617731cca0fd1e82c4d9ea13b545425f210a4a041f214175f147557080f1ba7`
- Normalized stdout bytes: `378`
- Normalized stdout SHA-256: `379f2bdf5ce224f2761b88edaae61f951335abcc456263c2720fd84c312916d1`
- Empty stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Output schema: `amn2.phase16.firewall-stop-l4proto-token-shape.v5`
- Exact normalized output validation: `pass`

## Normalized result

- V4 other-string population: `52`
- Classified population: `52`
- Lowercase IANA-style token, length `1-16`: `52`
- Other lowercase token lengths: `0`
- Safe-token fallback: `0`
- Non-token string: `0`
- Non-string: `0`

All remaining `meta l4proto` values are bounded lowercase tokens matching `[a-z][a-z0-9+.-]{0,15}`. No token value was emitted. Combined with V3 and V4, this closes the root-cause investigation for all 68 nft `match` expressions rejected by package 009.

## Bounded local TDD contract

The evidence supports a new immutable package revision with only these parser extensions:

- admit `payload / protocol / ip / == / string` only when the right side is a bounded lowercase L4 protocol token;
- admit `meta / l4proto / == / string` only when the right side is a bounded lowercase IANA-style token of length `1-16`;
- admit exact `ct / state / in / array[string]` only with the finite connection-state allowlist;
- admit exact `ct / status / in / string` only with the finite connection-status allowlist;
- admit `meta / oifname / != / string` while preserving target-interface conflict detection;
- retain existing target UDP port, CIDR, and interface conflict checks;
- keep every unknown kind, selector, operator, value type, malformed token, extra key, and out-of-bound form fail closed;
- do not change AWG2 handshake freshness policy.

This evidence is sufficient to propose local TDD for package 010, but does not itself authorize source changes, package materialization, preflight retry, stage, install, pilot issuance, or AWG2 operations.

## Safety boundary

- Approved SSH diagnostic attempts: `1`
- Collector executions: `0`
- Remote file written: `false`
- Raw right values emitted: `false`
- Raw values emitted: `false`
- Raw output persisted: `false`
- Live mutation: `false`
- Diagnostic retry attempted: `false`
- Preflight retry attempted: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Matching Spain SSH processes after completion: `0`
- Temporary diagnostic program after completion: `absent`
- Package revision 009 changed: `false`

This diagnostic is terminal for the approved V5 attempt.
