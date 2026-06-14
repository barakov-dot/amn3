# AMN2 Phase 7 Release Candidate Plan

Дата: 2026-06-14.

Phase name: `Phase 7: Release Candidate Readiness / Clean Installer RC`.

Status: `pre-release / release-candidate readiness`.

Default lane: `local-only/docs/tests/security/package-preflight`.

This phase does not open public launch, production mutation, config delivery,
write API, destructive install, live package apply or Telegram identity changes.

## Source Of Truth

```text
AMN2 current local head: b121865 Add multi instance conflict model
AMN2 known-good VPS-smoked/package head: 0de7a77 Polish fresh installer preflight planning
Current disposable VPS: 89.185.80.166
Known-good evidence: research/amn2/phase-6-live-update-smoke-0de7a77-2026-06-14.md
```

## Critical Gated / Deferred

- `P7-C001` Live package/apply/smoke gate for current AMN2 head.
  Importance: critical gated. Carried from Phase 6 closeout. Gate: live VPS
  package/apply/smoke. Purpose: update disposable VPS from `0de7a77` to a named
  current head only after local package build/preflight. Not active by default.

- `P7-C002` Public exposure gate.
  Importance: critical gated. Carried from Phase 6 `P6-C001`. Gate: public
  exposure. Covers domain, HTTPS, reverse proxy, public web/admin, public API,
  firewall/listener changes and public docs/OpenAPI publication.

- `P7-C003` Config delivery gate.
  Importance: critical gated. Carried from Phase 6 `P6-C002`. Gate: config
  delivery. Covers `.conf`, QR, `vpn://`, tokenized public redeem, Telegram real
  config send and self-service download.

- `P7-C004` Destructive clean installer execution gate.
  Importance: critical gated. Carried from Phase 6 `P6-C007` and earlier
  `VPS-REBUILD-001`. Gate: destructive. Covers wipe, rebuild, reinstall,
  cleanup and provider-side destructive actions.

- `P7-C005` Write API / install mutation gate.
  Importance: critical gated. Carried from Phase 6 `P6-C003`, Local Agent
  write/config routes and production peer/user mutation. Gate: write API /
  production mutation.

- `P7-C006` Backup/restore/import gate.
  Importance: critical gated. Carried from Phase 6 `P6-C004`. Gate:
  backup/restore/import. Covers encrypted backup, restore preview/apply,
  archive import and disaster recovery drill.

- `P7-C007` Telegram identity/profile/media mutation gate.
  Importance: critical gated. Carried from Phase 6. Gate: Telegram identity.
  Covers Telegram API token use, live bot send for identity work, profile icon
  apply and bot profile/media mutations.

## Very Important

- `P7-I001` Current-head release-candidate package/preflight for `b121865`.
  Importance: very important. Gate: local-only/package-preflight. Build or
  prepare a local package/preflight evidence path for `b121865`; do not apply to
  VPS; do not rewrite `0de7a77` known-good evidence.

- `P7-I002` Clean installer RC acceptance checklist.
  Importance: very important. Gate: local-only/docs/tests. Convert the
  fresh-installer backlog into a release-candidate acceptance checklist:
  answers, preflight, package, smoke evidence, secret handoff, rollback and stop
  lines.

- `P7-I003` Installer secret/input contract hardening.
  Importance: very important. Gate: local-only/security/tests. Ensure installer
  answers, generated plans and evidence cannot contain raw `.env`, Telegram
  tokens, client configs, QR payloads, private keys, PSK or `vpn://`.

## Important

- `P7-M001` Known-good snapshot/runbook alignment.
  Importance: important. Gate: local-only/docs/tests. Keep `0de7a77` as the
  known-good VPS snapshot and document how future heads relate to it.

- `P7-M002` Package asset/runbook path verification integration.
  Importance: important. Gate: local-only/package-preflight. Carry forward
  `FI-M004` into a concrete RC package checklist.

- `P7-M003` Multi-instance/IPAM model incorporation.
  Importance: important. Gate: local-only/docs/tests. Carry forward `P6-M005`
  into installer RC decisions without enabling live multi-instance apply.

## Normal

- `P7-N001` Automation intake for Phase 7.
  Importance: normal. Gate: local-only/docs. Ensure upstream-refresh automation
  outputs are classified as release-candidate candidates, not automatic product
  changes.
  Automation IDs retained and updated for Phase 7 context:
  `prvtpro-weekly-upstream-refresh`,
  `weekly-kyoresuas-upstream-refresh`,
  `amnezia-weekly-upstream-refresh`.

- `P7-N002` API/docs taxonomy RC drift check.
  Importance: normal. Gate: local-only/docs/tests. Carry forward `P6-N005` route
  order guard into the RC checklist.

- `P7-N003` Client compatibility watch refresh.
  Importance: normal/watch-only. Gate: local-only/docs. Keep DefaultVPN and
  AmneziaWG iOS/Android guidance current without config delivery.

## Simple

- `P7-S001` Next-chat and status hygiene.
  Importance: simple. Gate: docs-only. Keep handoff/status/backlog synchronized
  after each Phase 7 task.

- `P7-S002` Release notes skeleton.
  Importance: simple. Gate: docs-only. Prepare a changelog/release-note skeleton
  for the eventual RC without declaring a release.

## Cosmetic

- `P7-X001` Operator copy polish for clean installer.
  Importance: cosmetic. Gate: local-only/docs/tests. Keep Russian-first prompts
  concise and safe.

## Watch-Only

- Amnezia/DefaultVPN/AmneziaWG client releases.
  Importance: watch-only. Gate: watch-only. Use only as client compatibility
  signals.

- PRVTPRO/KYORESUAS upstream changes.
  Importance: watch-only/research. Gate: GPL/upstream-copy forbidden where
  applicable. Use only ideas/signals/links unless a local AMN2 candidate is
  explicitly accepted.

## Recommended First Step

```text
P7-I001 + P7-M001 together as local-only package/test readiness:
- build or prepare local package/preflight evidence for b121865;
- preserve 0de7a77 as known-good VPS-smoked baseline;
- do not apply to VPS;
- do not restart services;
- do not open public/config/write/destructive gates.
```

Alternative single:

```text
P7-I002 Clean installer RC acceptance checklist
```

Alternative triple:

```text
P7-I001 + P7-M001 + P7-I002
```

## Access Requirements

No additional access is required for default Phase 7 work.

Ask the operator only when needed:

- VPS/SSH/PowerShell access for `P7-C001` or `P7-C004`;
- provider console access for destructive rebuild/reinstall;
- DNS/domain/TLS credentials for `P7-C002`;
- payment provider credentials for commercial/payment work;
- Telegram token/profile access for `P7-C007`.

## Stop Lines

Stop immediately and ask for a named gate if a task would:

- run SSH or live VPS commands;
- upload/apply a package to VPS;
- stop/restart/deploy services;
- open public `3030`, `3040`, `80`, `443`, domain, HTTPS or reverse proxy;
- emit `.conf`, QR, `vpn://`, config body or client secret;
- enable write API, Local Agent mutation, backup/import/reboot or peer/user
  mutation;
- delete, wipe, rebuild or reinstall a VPS;
- use Telegram tokens, live bot send or Telegram identity/profile mutation;
- publish secret-bearing evidence;
- copy upstream/GPL implementation code.
