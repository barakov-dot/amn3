# Spain preflight run 007 — fail-closed evidence

## Доказанный результат

```text
outcome=spain-fresh-20260720-007
classification=envelope_rejected
failure_prefix=present
strict_parser=rejected
claim=present
failure_evidence=absent
success_evidence=absent
raw_output_persisted=false
```

Runner остановился на сообщении `malformed failure envelope`. Точная remote
stage/exit pair не сохранялась и поэтому не утверждается. Локальный synthetic
test с exact `AMN2_SPAIN_PREFLIGHT_FAILURE_V1`, stage и matching exit прошёл,
что исключает только воспроизводимый generic PowerShell string/cast failure.

## Границы

Run `007` consumed и не повторяется. Install, restart, stop, config/secret,
Telegram, web и AWG actions не выполнялись. Unrelated Spain service не
изменялся. Следующий SSH возможен только после отдельного safe envelope
rejection diagnostic contract, нового outcome и новой literal approval.
