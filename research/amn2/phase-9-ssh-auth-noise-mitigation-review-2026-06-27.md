# AMN2 Phase 9 SSH auth-noise mitigation review

Дата: 2026-06-27.
Модель решения: `GPT-5.5`.
Run type: docs-only review.

## Input evidence

- `docs/AMN2_PRIVATE_RC_SSH_AUTH_NOISE_MITIGATION_REVIEW.ru.md`
- `docs/AMN2_PRIVATE_RC_SSH_SERVER_LOG_DIAGNOSTIC_RESULT.ru.md`
- `docs/AMN2_PRIVATE_RC_SSH_SINGLE_SESSION_DIAGNOSTIC_RESULT.ru.md`
- `docs/AMN2_PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE_RESULT.ru.md`
- `docs/AMN2_HELPER_SSH_TRANSPORT_HARDENING.ru.md`
- `docs/AMN2_PHASE_9_HARDENING_ENTRY_REVIEW.ru.md`

## Result

`AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW` completed as docs-only.

```text
selected_phase9_lane=HARDENING_PRODUCTIZATION
ssh_auth_noise_observed=true
ssh_auth_noise_execution_required_for_current_lane=false
ssh_auth_hardening_execution_approved=false
ssh_auth_hardening_future_exact_gate_required=true
current_safe_policy=no-mutation-short-ssh-key-based-operations
```

## Rationale

Phase 8 diagnostics showed heavy SSH auth-noise, but did not prove
`MaxStartups`, OOM, conntrack exhaustion, fatal sshd errors or AMN2 runtime
failure. Key-based access was later prepared, and the Telegram no-long-SSH
pattern passed without holding SSH open during the manual window.

Therefore, for Phase 9 hardening/productization, auth-noise mitigation is not
a current blocker and should not mutate SSH/firewall/auth settings without a
future exact gate plus provider-console/rollback boundary.

## Output artifact

- `docs/AMN2_SSH_AUTH_NOISE_MITIGATION_REVIEW.ru.md`

## Post-condition

No live/VPS/SSH/config/Telegram/public gate was opened. No `sshd_config`,
firewall, auth, user, key, service, provider, config delivery or peer mutation
was performed.
