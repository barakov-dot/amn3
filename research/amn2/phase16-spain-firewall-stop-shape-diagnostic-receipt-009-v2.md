# Phase 16 Spain firewall STOP shape diagnostic receipt 009 V2

- Recorded: `2026-08-25T15:32:55Z`
- Command ID: `PHASE16_FIREWALL_STOP_SHAPE_V2`
- Package: `phase16-awg3-family-3-1-spain-pilot-20260824-009`
- Package identity: `2a4549c05daca9f3666ffe1babfa17851c93c59cc1b902efe9dca16002d9fe5d`
- Destination: `root@138.124.181.246`
- Bound preflight outcome SHA-256: `672a0037e0139f9c70a227fa7713d97dcc122a519ecaeeeebf02600d0d100184`
- Bound diagnostic V1 stdout SHA-256: `c33af70389833140b3bed2a335e5486af6a506c330d235ba79dcf9f28b2a4dce`
- SSH exit: `0`

## Diagnostic binding

- Ephemeral diagnostic program SHA-256: `be9e9a3e2cf4b1ede6210965fa18462784dde3a148239b2c8ed31bfb029ffadf`
- Normalized stdout bytes: `3931`
- Normalized stdout SHA-256: `f18812daa9499c90bc0f9bf0a7a06b041c03d4c07613efeede54dc4d08aab3b3`
- Empty stderr SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- Output schema: `amn2.phase16.firewall-stop-shape.v2`
- Exact normalized output validation: `pass`

## First rejection locus

- Rule ordinal: `5`
- Expression ordinal: `13`
- Expression kind: `match`
- Rejection locus: `match_payload_field_class`
- Payload shape: `left.payload{field:string,protocol:string}`, `op:string`, `right:string`

Only structural key names, types, counts, and ordinals were captured. No selector values or rule values were emitted.

## Expression shape summary

- Total expressions: `649`
- Accepted by package 009 parser contract: `581`
- Rejected by package 009 parser contract: `68`
- Distinct structural shapes: `15`
- `accept(null)`: `107`
- `counter{bytes:int,packets:int}`: `187`
- `dnat{addr:string,family:string,port:int}`: `1`
- `drop(null)`: `10`
- `jump{target:string}`: `59`
- `limit{burst:int,per:string,rate:int}`: `13`
- `masquerade(null)`: `1`
- `match left.ct{key:string}, right:array[string]`: `2`
- `match left.ct{key:string}, right:string`: `1`
- `match left.meta{key:string}, right:string`: `68`
- `match left.payload{field:string,protocol:string}, right:int`: `40`
- `match left.payload{field:string,protocol:string}, right:prefix{addr:string,len:int}`: `21`
- `match left.payload{field:string,protocol:string}, right:string`: `17`
- `return(null)`: `5`
- `xt{name:string,type:string}`: `117`

The V2 evidence proves that the package 009 STOP occurs within nft `match` selector semantics, not in the previously admitted `dnat`, `limit`, `masquerade`, or `xt` forms. The first rejected selector is a payload-field class outside the package 009 allowlist. The ruleset also contains `ct` selectors and multiple `meta`/`payload` selector shapes. Because V2 intentionally omitted selector values, it does not establish which exact bounded selector enums and right-hand value classes are safe to admit. A parser change is therefore not authorized by this evidence alone.

The protected historical run009 evidence was checked locally. It retains the firewall hash and rule count but no structured nft snapshot, so it cannot supply the missing current selector classes without another bounded observation.

## Safety boundary

- Approved SSH diagnostic attempts: `1`
- Collector executions: `0`
- Remote file written: `false`
- Raw values emitted: `false`
- Raw output persisted: `false`
- Live mutation: `false`
- Preflight retry attempted: `false`
- Stage/install attempted: `false`
- AWG2 changed: `false`
- Matching Spain SSH processes after completion: `0`
- Temporary diagnostic program after completion: `absent`
- Package revision 009 changed: `false`

This diagnostic is terminal for the approved V2 attempt. It authorizes neither another diagnostic nor a parser change, preflight retry, controlled stage, install, pilot issuance, or AWG2 operation.
