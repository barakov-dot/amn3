# Spain safe failure-envelope rejection diagnostic — design

## Цель

Для нового single-use outcome `spain-fresh-20260721-008` сохранить безопасную
причину, по которой строгий parser отверг remote failure envelope, не сохраняя
raw OpenSSH output, private target, исходную строку envelope или неподтверждённый
remote stage.

## Контракт

- Валидный envelope продолжает обрабатываться существующим строгим parser.
- Если failure prefix присутствует, но parser возвращает `null`, runner создаёт
  failure evidence с `classification=envelope_rejected`, `stage=unavailable`,
  безопасным process exit `1..255` и одной allowlisted причиной.
- Allowlist причин: `prefix_count`, `shape`, `stage`, `exit`,
  `stage_exit_mapping`, `unavailable`.
- `prefix_count` означает, что prefixed-строка не единственная; `shape` — что
  единственная строка не соответствует exact schema; `stage` — что stage не
  разрешён; `exit` — что exit вне диапазона или не равен process exit;
  `stage_exit_mapping` — что известный stage использует неразрешённый для него
  код.
- Даже если stage или exit удалось разобрать, в rejection evidence stage
  остаётся `unavailable`; parsed values не переносятся в evidence.
- Raw output живёт только в памяти и обнуляется до сериализации evidence.
- Success parser, trust bundle, host-key pin, dedicated key, remote probe и
  read-only границы не меняются.

## Fail-closed границы

Нулевой/небезопасный process exit не сериализуется как envelope rejection.
Неоднозначность не раскрывает raw values. Outcome создаётся atomically и не
переиспользуется. Run 008 не запускается этой задачей и требует отдельной exact
checksum-bound approval.

## Acceptance

1. TDD покрывает все пять именованных rejection-причин и safe `unavailable`.
2. Валидный allowlisted envelope по-прежнему принимается прежним parser.
3. Unsafe/malformed варианты по-прежнему не становятся remote-probe evidence.
4. Focused и full test suites проходят.
5. Diff/security review подтверждает отсутствие secrets, raw persistence, SSH
   execution и изменений AWG/Telegram/unrelated service.
6. После commit/push публикуется отдельный literal approval только для run 008.

## Ограничение повторов

Run 008 — следующий диагностический запуск. Если он докажет конкретную локально
исправимую причину, допускается максимум один новый run 009 после отдельной
коррекции и approval. При повторной неудаче используется другой способ
диагностики/консоль провайдера; цепочка повторов не продолжается.
