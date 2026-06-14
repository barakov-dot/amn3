# AMN2 After Phase 6 Next-Chat Handoff And Live Gate Checklist 0de7a77

Дата: 2026-06-14.

Статус: docs-only/local-only handoff refresh completed.

## Scope

This slice refreshes the next-chat handoff and grooms the future live gate
checklist for AMN2 `0de7a77`.

It does not open the live gate and does not run live apply/smoke.

## Current State

```text
AMN2 current head: 0de7a77 Polish fresh installer preflight planning
AMN2 latest package-ready head: 0de7a77
AMN2 latest VPS-smoked head: c46f664
AMN3 latest package evidence: research/amn2/after-phase-6-package-preflight-0de7a77-2026-06-14.md
package status: package-ready-not-vps-smoked
```

## Candidate Package

```text
package: dist/amn2-vps-update-and-smoke-kit-0de7a77.zip
package_sha256: 7B6DA000DAA39DD15A4DB7C3691D0B0C24EAA20ACB1C428150C6961B01E6F85B
source_zip: dist/amn2-codex-vps-test-prep-0de7a77-source.zip
source_zip_sha256: B8D0E7E2A40051AB38EDF09947977DFE5F7197CEEEE87D1523734D3C1C505295
```

## Future Named Gate Phrase

The future live gate remains closed unless the operator sends this exact named
gate phrase:

```text
Открываю P6-C010 live apply/smoke gate для 0de7a77 на текущем disposable VPS 89.185.80.166.
```

## Checklist

Before any future live command:

- confirm target `89.185.80.166` is still the intended disposable VPS;
- confirm local AMN2 head is `0de7a77`;
- confirm local AMN3 package evidence is present;
- verify package SHA256 and source SHA256;
- record stop criteria;
- keep smoke loopback-only;
- keep `VPS_APPLY_ENABLED=false`;
- confirm no public/config/write/destructive gate is being opened.

Stop criteria:

- checksum mismatch;
- package extract missing one of the five expected files;
- source overlay apply failure;
- web/bot runtime cannot be verified inside the named gate;
- listener drift exposes public web/API ports unexpectedly;
- loopback API smoke fails auth/listener/audit checks;
- secret-bearing evidence appears.

## Forbidden Without Separate Gates

- public exposure;
- config delivery, `.conf`, QR, `vpn://`;
- write API;
- Local Agent mutation;
- backup/import/reboot;
- production peer/user mutation;
- destructive provider/VPS action;
- Telegram token use, live bot send or identity/profile mutation;
- secret-bearing evidence publication;
- upstream/GPL implementation copy.

## Verification

This docs-only slice should be verified with:

```text
python -m unittest tests.test_markdown_hygiene
git diff --check
```

No AMN2 code changed in this slice.

## Next

Gated option:

```text
P6-C010 live apply/smoke for 0de7a77
```

Only after the exact named gate phrase above.

Local-only option:

```text
Pause here and keep 0de7a77 package-ready-not-vps-smoked.
```
