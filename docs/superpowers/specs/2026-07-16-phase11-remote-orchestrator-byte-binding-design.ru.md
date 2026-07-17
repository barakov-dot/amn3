# Phase 11 Remote Orchestrator Same-Bytes Binding Design

## Контекст

Phase 11 runner уже проверяет точную approval-фразу, SHA-256 overlay-пакета,
выделенный SSH key и pinned known-host. Для `preflight`, `postflight` и
`apply` он при этом только проверяет существование
`phase11_0b858c5_combined_remote_rollout.sh`, затем повторно читает текущий
текст файла и передаёт его в `root@$target bash -s`.

Security scan `750fd1c_20260716T151551Z` подтвердил Medium/P2 finding
`transport-unbound-remote-orchestrator`: review и exact approval не закрепляют
байты наиболее привилегированного локального input.

## Цель и security invariant

Runner обязан прочитать remote orchestrator ровно один раз как `byte[]`,
проверить SHA-256 этого массива против reviewed digest
`A41C000C8C15E0A4D4E2DE0CC35CB84A27EF73CCA00B69EB04FD4971FC64EF72`
и передать в SSH standard input тот же массив без повторного чтения пути или
текстового перекодирования.

Любое несовпадение должно завершать локальный запуск до `ssh.exe`. Текущие
exact approval, package SHA, host-key pinning, режимы, output sanitization,
regular-bot disabled и AWG untouched остаются без ослабления.

## Рассмотренные варианты

### 1. Same-bytes SHA-256 binding — выбран

`[IO.File]::ReadAllBytes()` создаёт один массив. `SHA256.Create()` и
`BitConverter` вычисляют uppercase hex, совместимый с текущими receipt.
`Invoke-CapturedProcess` принимает необязательный `byte[]` и пишет его через
`StandardInput.BaseStream`. Это минимальная полная граница и не требует нового
формата артефакта.

### 2. Git blob binding — отклонён для этого fix

Runner мог бы читать blob из index/commit, но это добавило бы зависимость от
Git runtime и усложнило бы связь с уже подготовленным working-tree gate.
Проверка только clean tree также не доказывает, что hash проверен над теми же
байтами, которые ушли в stdin.

### 3. Reviewed operation manifest — отложен

Manifest лучше масштабируется на несколько privileged inputs и независимую
подпись, но требует schema/canonicalization/key-custody lifecycle. Для одного
runner это непропорционально; hardening portfolio сохраняет вариант как
следующий архитектурный уровень.

## Архитектура и data flow

Для `upload` остаётся существующий package-only путь. Для остальных режимов:

1. exact approval проходит ordinal equality;
2. локальные key, known-host и remote-script paths проверяются;
3. upload branch возвращается до remote-orchestrator execution path;
4. remote script один раз читается в `$remoteScriptBytes`;
5. SHA-256 считается над `$remoteScriptBytes` и ordinally сравнивается с
   `$expectedRemoteScriptSha`;
6. mismatch бросает `Remote rollout script SHA-256 mismatch`;
7. verified `$remoteScriptBytes` передаётся в
   `Invoke-CapturedProcess -StandardInputBytes`;
8. helper пишет этот массив через `StandardInput.BaseStream`, flush/close и
   сохраняет существующую обработку stdout/stderr/exit code.

## Совместимость и error handling

- Используются API .NET, доступные в Windows PowerShell и PowerShell 7:
  `ReadAllBytes`, `SHA256.Create`, `ComputeHash`, `BitConverter` и
  `Stream.BaseStream.Write`.
- `upload` не получает нового remote-script hash requirement: он не выполняет
  orchestrator и сохраняет текущую package-only семантику.
- Empty byte input просто закрывает stdin; текущие SCP/SSH chmod calls не
  меняются.
- Hash mismatch не раскрывает содержимое, target или secret и происходит до
  transport process.
- Текстовый `StandardInputText` удаляется, чтобы не осталось альтернативного
  unbound пути к тому же root sink.

## Тестовая стратегия

TDD начинается с двух failing static regression tests:

1. expected remote SHA обязан совпадать с `SHA256(REMOTE.read_bytes())`, а
   ordinal mismatch guard обязан предшествовать созданию SSH args;
2. один и тот же `$remoteScriptBytes` обязан участвовать в `ComputeHash`,
   `BaseStream.Write` и final invocation; повторный `Get-Content` и
   `StandardInputText` запрещены.

После GREEN выполняются focused/full pytest, PowerShell parser, Bash syntax,
`git diff --check`, original source/control/sink retrace и повторный scoped
security diff scan. Live SSH/VPS, Telegram, provider, database и AWG не входят
в проверку fix.

## Acceptance criteria

- Reviewed SHA remote script закреплён в runner и совпадает с текущими байтами.
- Hash и transport используют один `byte[]` без повторного чтения пути.
- Mismatch fail-closed расположен до первого non-upload transport call.
- Existing approval/package/host/output/bot/AWG tests остаются зелёными.
- Повторный security scan закрывает P2 или возвращает конкретный новый blocker.
- Status/evidence отражают новые runner hash, test receipts и новый approval
  gate; старое approval не переиспользуется.

## Вне scope

Production rollout, SSH upload/apply, Telegram profile, provider mutation,
schema mutation, bot activation, AWG restart/configuration и изменение
`docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md`.
