# Spain preflight run 006 — sanitized failure evidence

## Результат

`spain-fresh-20260720-006` был запущен один раз с отдельной checksum-bound
approval и завершился fail-closed. Единственный разрешённый failure envelope:

```text
schema=amn2.spain-readonly-preflight-failure.v1
classification=transport
stage=unavailable
subreason=unavailable
exit_code=255
claim=present
success_evidence=absent
```

## Безопасностная интерпретация

Remote probe не вернул валидный stage envelope, поэтому этот результат не
утверждает состояние Spain OS, capacity, ports, services, Docker, systemd,
firewall, SSH policy, clock или unrelated service. Никакие raw OpenSSH
stdout/stderr, private target identifiers, credentials или configs не
сохранялись в Git. Install/restart/stop, Telegram, web и AWG actions не
выполнялись.

Run `006` consumed и не повторяется. Перед будущим `007` нужен отдельный
local-only transport diagnostic contract с allowlisted subreason и новой
single-use approval; blind remediation запрещён.
