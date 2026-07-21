# Spain read-only preflight run 009 — success evidence

## Result

Outcome `spain-fresh-20260721-009` выполнен ровно один раз и прошёл. Approval
consumed. Claim и sanitized success evidence присутствуют; failure evidence
отсутствует.

```text
schema=amn2.spain-readonly-preflight.v1
mode=preflight
evidence_sha256=8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8
runner_sha256=26ED19344B9E7F56069BFEBAC9864BB5779B413767312B4AAB411B7DBF859D76
remote_probe_sha256=228E53330DF694F18BBA6C2F13A7837C7F0B5F2A0D5D4757A134E126FB18945D
source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
```

## Sanitized readiness facts

- Linux, 1 logical CPU, 984564 KiB memory, 10479628288 root-disk bytes;
- Docker absent; systemd present;
- firewall backend nft, 129 rules;
- occupied ports: TCP 22/53/443/8080/10050, UDP 53/443;
- unrelated-service fingerprint contains 148 normalized entries and becomes the
  immutable before-snapshot for Phase 12 equality checks.

## Negative guarantees

No install, restart, stop, config write, Telegram call or AWG mutation occurred.
The unrelated Spain service and USA production contour were untouched. Raw
inventory is retained only in protected local artifacts and is not committed.

## Decision

Read-only preflight gate passed. Separate Phase 12 install/package/rollback
approval is still mandatory.
