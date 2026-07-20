# Phase 11 Spain render-stage subreason diagnostic — дизайн

## Контекст и решение

Одноразовый read-only запуск `spain-fresh-20260720-005` дошёл до удалённого
`render` stage и завершился с `exit=127`. Существующий envelope намеренно
сохраняет только stage/exit; он не выводит stdout, stderr, имя команды,
private target, unit/PID/path/socket values или конфигурации. Поэтому новый
outcome `006` нельзя создавать до отдельной локальной коррекции диагностики.

Выбран минимальный подход: непосредственно перед JSON rendering remote probe
проверяет наличие только команд, которые уже используются render-путями.
Проверка сопоставляет отсутствие каждой команды с фиксированным exit code,
а PowerShell runner переводит только эти exact пары `render/exit` в безопасный
subreason. В evidence остаются только `classification`, `stage`, `subreason`,
`exit_code` и уже существующие checksum/source bindings.

## Allowlist-контракт

| Пара `render/exit` | Безопасный `subreason` | Назначение |
| --- | --- | --- |
| `81` | `sha256sum` | хеширование redacted identifiers |
| `82` | `cut` | выделение hex digest |
| `83` | `tr` | нормализация safe atom |
| `84` | `awk` | нормализация published port set |
| `85` | `sort` | детерминированная сортировка port set |
| `86` | `paste` | компактная сериализация port set |

Команда проверяется через shell builtin `command -v` без печати результата.
Неизвестный exit, отсутствующая/дублированная envelope line, смешанный output
или ошибка вне шести пар не получают подпричину и закрывают gate fail-closed.

## Границы

- Нет SSH, Spain VPS mutation, install, restart, stop, config/secret delivery,
  Telegram action или AWG action.
- Не изменяются trust bundle `spain-fresh-20260720-001`, ключ, host pin или
  уже использованный outcome `005`.
- Новый runner будет связан с `spain-fresh-20260720-006` и потребует новую
  checksum-bound literal approval; эта спецификация не даёт live authority.
- `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` вне scope.

## Проверяемое поведение

1. До rendering probe вызывает allowlisted dependency checks с кодами `81–86`.
2. Runner принимает только exact `render/81..86` и пишет только соответствующий
   subreason; raw command name/remote output в evidence не попадает.
3. Проверки checksum binding, single-use claim и прочих failure stages не
   ослабляются.
4. TDD содержит RED test для mapping и статической placement-проверки, затем
   scoped и полный suites, diff/security review и origin readback.
