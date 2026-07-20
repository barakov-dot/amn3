# Spain preflight run 005 failure evidence

Дата: 2026-07-20.

Run `spain-fresh-20260720-005` был выполнен ровно один раз после exact
checksum-bound approval. Gate был read-only: install/restart/stop/config
mutation, Telegram action, AWG mutation и blind remediation не выполнялись.

```text
schema=amn2.spain-readonly-preflight-failure.v1
classification=remote_probe
stage=render
subreason=unavailable
exit_code=127
runner_sha256=B42EEE2ED6D63DDC81BCDAF337B9A1581757C8B1E5B1475FACFF69322DD75C82
remote_probe_sha256=B45764A57E4258C8DD1AFC1570FE5F4359C755C146449225EAC0B74044E3F3F1
source_revision=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
claim=present
failure_evidence=present|sanitized
success_evidence=absent
approval=consumed|never_repeat
```

Локальный review reviewed remote probe показал, что `render` stage формирует
redacted JSON через shell helpers and external commands. Текущий sanitized
failure envelope не раскрывает raw stdout/stderr, target, unit/PID/FD/path,
socket values, keys, host pin bytes, configs или secret-bearing payloads.

Следующий шаг: отдельный локальный render-stage subreason diagnostic contract,
который классифицирует allowlisted render dependency failures без raw values.
После TDD correction нужен новый outcome run `spain-fresh-20260720-006`, новый
runner/probe SHA, commit/push/origin readback и новая exact single-use read-only
approval. Fresh Spain install и Phase12 migration gate остаются закрытыми до
успешного нового preflight.
