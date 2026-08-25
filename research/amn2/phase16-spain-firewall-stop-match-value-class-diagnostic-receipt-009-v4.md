# Phase 16 Spain firewall STOP match value class diagnostic receipt 009 V4

- Recorded: `2026-08-25T16:29:19Z`
- Command ID: `PHASE16_FIREWALL_STOP_MATCH_VALUE_CLASS_V4`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-009`
- Package identity: `2a4549c05daca9f3666ffe1babfa17851c93c59cc1b902efe9dca16002d9fe5d`
- Destination: `root@138.124.181.246`
- Bound preflight outcome SHA-256: `672a0037e0139f9c70a227fa7713d97dcc122a519ecaeeeebf02600d0d100184`
- Bound diagnostic V3 stdout SHA-256: `0ffff73e7f300f6f32ee4c05714f2bd2a853bab510e577bcee4ee9c807b43063`
- SSH exit: `0`

## Diagnostic binding

- Ephemeral diagnostic program SHA-256: `523f68e1eee00aaab02e8b118298b6720c0282da6e6c4826d7fa42df6814e931`
- Normalized stdout bytes: `549`
- Normalized stdout SHA-256: `85d82743e7c352f986f3a0619a46b10e787d96644ff1ddb88364114cdd8b3303`
- Empty stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Output schema: `amn2.phase16.firewall-stop-match-value-class.v4`
- Exact normalized output validation: `pass`

## Normalized result

### `meta l4proto`

- Total: `54`
- Named finite allowlist: `2`
- Decimal unsigned 8-bit string: `0`
- Other string: `52`
- Non-string: `0`

### `ct status`

- Total: `1`
- Finite allowlist: `1`
- Other string: `0`
- Non-string: `0`

The `ct status` contract is fully classified. The V4 hypothesis that the 52 remaining `meta l4proto` strings were bounded decimal protocol numbers was falsified. They are strings outside the narrow finite named allowlist used by V4. Their values were not emitted, so V4 does not prove whether they are syntactically bounded IANA-style protocol tokens or another string form.

One final token-shape observation is required before local TDD: classify only those 52 strings as lowercase IANA-style name tokens, bounded safe tokens, or non-token strings, with length buckets and counts only. No string value needs to be emitted. Until that evidence exists, no parser change or package 010 is authorized by this receipt.

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

This diagnostic is terminal for the approved V4 attempt. It authorizes neither another diagnostic nor a parser change, preflight retry, controlled stage, install, pilot issuance, or AWG2 operation.
