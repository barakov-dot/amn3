# Spain read-only preflight run 008 — fail-closed evidence

## Outcome

`spain-fresh-20260721-008` запущен ровно один раз. Claim создан. Success и
sanitized failure evidence не созданы, поскольку Windows PowerShell превратил
native stderr в terminating error непосредственно на process invocation.

## Доказанная причина

- reviewed remote probe: `434 LF`, `0 CRLF`, последний byte `0A`;
- remote Bash сообщил отдельный carriage return на следующей строке;
- передача выполнялась как один PowerShell string через native object pipeline;
- следовательно, CR был добавлен локальной stdin serialization boundary, а не
  содержался в probe и не был создан Spain VPS.

## Инварианты

Install/restart/stop/config actions не выполнялись. Telegram, production AWG и
посторонний Spain service не изменялись. Raw output не сохранялся в artifact.
Run 008 consumed и не повторяется.

## Следствие

Разрешён один финальный outcome 009 после exact-byte transport correction,
tests, security review, commit/push и отдельной literal approval. После 009
новых attempts в этой цепочке нет.
