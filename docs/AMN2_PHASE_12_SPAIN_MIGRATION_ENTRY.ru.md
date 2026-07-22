# AMN2 Phase 12 — Spain Migration Entry

## Current operational override — 2026-07-22

Install boundary использует executor-embedded in-memory collector, run009
baseline и resource plan: remote precondition receipt, baseline и collector не
загружаются отдельными файлами. Foreign-service equality действует как
`dynamic_persistent_v1`: persistent identities обязаны совпасть; volatile
identities только записываются. Spain foreign service не останавливается и не
изменяется. Тихая SCP upload v4 завершилась с remote hash equality, но executor
fail-closed до tombstone/state machine на инвертированном time-gate
authorization/receipt; AMN2 services не запускались. Текущие v5 локальные
artifacts до commit/push: package
`324A6845F8B702AABF8C9CBADC38E66CCC6BE12AAE1DE6AA035F2394996E3426`, executor
`58648073D5E5001AF5736C15C633E9754D8E3C0460F373078374A36DD71BCBE7`.
Исправление допускает approval до выпуска in-memory receipt при сохранении
строгого expiry/binding контроля.
Policy receipt фиксирует `persistent_equal` и числа volatile entries до/после;
полностью volatile membership допустим, но любое изменение stable fields
persistent identity остаётся fail-closed. Volatile fields persistent identity:
`bound_port_set`, `restart_count`.
Firewall equality использует approved semantic rebaseline `nft`, rule count
`129`, SHA-256 `FB8E1D41F6F4F0EBCEB7C89D65E4E5E440E0AC0A4E780B4F638F96CEE1B9A682`;
raw counter hash не является equality gate.

До exact checksum-bound install approval любые Spain upload/install/mutation
запрещены. USA остаётся rollback contour.

## Objective

Deploy a fresh AMN2 production contour on the separate Spain VPS, accept it
with disposable lifecycle evidence, switch the existing private Telegram bot
disabled-first, and issue only new operator-requested configurations. Existing
USA configs/users/peers are not migrated and are not deleted by Codex.

## Authoritative baseline

```text
phase11=completed-controlled-private-release
spain_preflight_009=passed|consumed|never_repeat
spain_evidence_sha256=8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8
amn2_source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
usa_production_overlay=0b858c5cdbc5b565cc265966a2edfe2d339d65e0
docs_branch=codex-spark-phase9-docs-sync
spain_docker=absent
occupied_ports=tcp_22_53_443_8080_10050|udp_53_443
unrelated_fingerprint_entries=148
```

## Migration contract

1. Fresh install, clean DB. Do not restore USA DB, peers, configs or secrets as
   production state.
2. Preserve the unrelated Spain service byte-for-byte/state-for-state where
   applicable; its normalized fingerprint must equal the run-009 snapshot after
   install, acceptance and cutover.
3. Select new conflict-free container/unit names, Docker network, VPN subnet,
   AWG port and loopback web port. Do not bind TCP/UDP 53/443, TCP 8080/10050,
   or SSH 22.
4. Docker installation is a separate explicit mutation inside the install gate.
5. USA remains live rollback contour until Spain disposable acceptance, bot
   cutover and first real batch are accepted. Never stop/mutate USA AWG for
   testing.
6. Bot cutover is disabled-first with one polling owner, exact identity,
   webhook/backlog checks, rollback watchdog and independent postflight.
7. New configs use `NEOBYATNAYA.NET — recipient — slot/device`. Device may be
   unknown at issuance. Multiple active unassigned slots per recipient are
   allowed; default expiry is indefinite unless operator explicitly supplies
   an expiry.
8. Operator sends one batch message listing recipients and quantities; AMN2
   creates separate peers/passports/receipts. Operator distributes configs
   manually. Disable/revoke remains per slot and per recipient.

## Exact gate sequence

```text
P0 INSTALL_DESIGN_AND_PACKAGE
P0 INSTALL_SNAPSHOT_APPLY_VERIFY_OR_ROLLBACK
P0 DISPOSABLE_CREATE_IMPORT_CONNECT_DISABLE_REVOKE_CLEANUP
P0 DISABLED_FIRST_TELEGRAM_BOT_CUTOVER
P0 FIRST_REAL_OPERATOR_BATCH_ISSUANCE
P1 60_MINUTE_STABILITY_AND_FINAL_ACCEPTANCE
```

Every live mutation requires its own checksum-bound literal approval. Never
reuse Phase 11 approvals.

## Exit to Phase 13

Phase 12 closes only after Spain services are healthy, web remains loopback or
private-only, DB integrity/FK pass, one bot instance is stable, AWG lifecycle
acceptance passes, real batch receipts exist, unrelated fingerprint is equal,
and USA rollback/retirement decision is separately documented.
