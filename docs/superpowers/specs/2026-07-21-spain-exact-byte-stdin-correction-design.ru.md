# Spain exact-byte stdin correction — design

## Проблема и причина

PowerShell object pipeline сериализовал LF-terminated probe как string и добавил
Windows CRLF. Дополнительный CR стал удалённой Bash-строкой. Probe-файл сам
LF-only; серверное окружение причиной не является.

## Решение

- читать bounded bytes из того же открытого stream, по которому проверен SHA;
- валидировать bytes как strict UTF-8, но передавать исходный byte array;
- запускать только pinned absolute OpenSSH через `ProcessStartInfo`;
- экранировать каждый аргумент по Windows CreateProcess quoting rules;
- писать bytes напрямую в `StandardInput.BaseStream` и закрывать stdin;
- читать stdout/stderr асинхронно только в память и передавать существующим
  sanitized parsers;
- очищать probe byte array сразу после process boundary.

## Acceptance

Локальный child-process regression получает `41 0A` ровно как `410A`; quoting
tests покрывают пробелы, кавычки, trailing backslash и empty value. Старый
`$RemoteText | & $SshExe` отсутствует. Все scoped/full tests проходят.

## Live boundary

Коррекция только готовит финальный run 009. SSH не выполняется без новой exact
approval. При любом результате run 009 новых attempts нет.
