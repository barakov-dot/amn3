# AMN3 / VPN Ops Lab

Приватный штаб проекта для параллельного развития `amn2`, будущих VPN-продуктов и Local Amnezia Agent.

## Начать работу

[Актуальный вход](docs/START_HERE.ru.md) → [паспорт проекта](docs/PROJECT_PASSPORT.ru.md)
и [правила AGENTS.md](AGENTS.md). Текущий Phase 16 execution plan указан во входе;
старые GO и «текущие» статусы внутри истории не являются командами к повторению.

[Карта skills](docs/SKILLS_MAP.ru.md) описывает применимость навыков к этому проекту,
не меняя личные skills и плагины. Другие проекты не входят в текущий scope.

GitHub:

```text
https://github.com/barakov-dot/amn3.git
```

## Цели

- анализировать похожие GitHub-проекты;
- проверять лицензии и ограничения заимствования;
- сравнивать архитектуру, функции, UX и production-подходы;
- вести feature gap между внешними проектами и `amn2`;
- отбирать идеи для переноса в `amn2`;
- отбирать идеи для будущего гибридного проекта;
- фиксировать выводы, которые стоит добавить в общий Codex skill.

## Главное правило

AMN3 остается coordination/knowledge-направлением.

`amn2` остается production-направлением.

`vpn-ops-lab`/AMN3 остается исследовательской лабораторией, design registry и transfer gate.

Функции переходят из `vpn-ops-lab` в `amn2` только после проверки:

- совместимости лицензии;
- практической пользы;
- operational- и security-рисков;
- архитектурной совместимости;
- тестового плана.

Пока идея не прошла эти проверки, она остается исследовательским кандидатом.

## Связь с Amneziya / `amn2`

Production-репозиторий:

```text
https://github.com/barakov-dot/amn2.git
```

AMN3 хранит решения, статусы, upstream-анализ, implementation plans и ссылки на ветки/commits/PR в `amn2`.

`amn2` хранит production-код, tests и runtime-документы.

Наработки из `amn2` являются обязательным контекстом для новых решений AMN3. Перед переносом любой идеи из upstream или чатов нужно проверить, не решена ли эта задача уже в `amn2`, и не конфликтует ли она с текущими runtime/security constraints.

Рабочая модель объединения описана в [AMN3 / Amneziya Unification design](docs/superpowers/specs/2026-05-31-amn3-amneziya-unification-design.md).

## Правила безопасности

Этот репозиторий не является основным production-приложением AMN2, но содержит
операционные scripts, tests и package snapshots. Их запуск может менять систему
и требует проверки scope/разрешений по [AGENTS.md](AGENTS.md).

Код из внешних проектов не копируется без проверки лицензии.

Основной подход: изучать идеи, адаптировать архитектурно и реализовывать своими изменениями с тестами.

Если лицензия проекта неясна, несовместима или требует copyleft-обязательств, идея не переносится в `amn2` как код. Допускается только анализ концепции и самостоятельное проектирование.

## Язык документов

Markdown-документы, README, спецификации, заметки и исследовательские карточки в этом проекте готовятся в первую очередь на русском языке.

Английский используется вторым слоем для имен файлов, технических терминов, ссылок, лицензий и названий внешних проектов.

## Структура

```text
AGENTS.md
docs/
  START_HERE.ru.md
  PROJECT_PASSPORT.ru.md
  SKILLS_MAP.ru.md
  superpowers/{specs,plans}/
research/
  amn2/
  upstreams/
scripts/
  vps/
tests/
packaging/
ideas/
watch-notes/
prototypes/
```

`research/amn2/` - датированные inventory, решения и evidence по `amn2`; проверять дату и scope, не считать все записи текущим runtime-состоянием.

`scripts/`, `tests/`, `packaging/` - инструменты, их проверки, контракты и
версионированные пакеты. Наличие файла не разрешает его исполнение или deployment.

`research/upstreams/` - карточки анализа внешних проектов.

`ideas/` - отбор идей по направлениям: `amn2`, будущий гибридный проект, общий Codex skill, отклоненные идеи.

`watch-notes/` - периодические наблюдения за upstream-проектами, релизами и security-relevant изменениями.

`prototypes/` - собственные эксперименты и проверки гипотез без копирования внешнего кода.

## Исторический Phase 9 progress harness

Только для соответствующих задач Phase 9. Не запускать как обязательную проверку
Phase 16, документационного пакета или нового входа в проект.

<details>
<summary>Сохранённые примеры Phase 9</summary>

Перед очередной операторской командой Phase 9 можно прогонять локальный guard, чтобы не возвращаться в цикл `CONFIRM_HOLD_STATE` / `AWAIT_OPERATOR_EXACT_CMD` вместо реального product-work:

```powershell
python scripts/phase9_progress_harness.py --next-command "КОДЕКС SPARK → START_CONFIG_SHARE_RESTORE_SCHEMA_INDEX_DECLARATION_CONTRACT_SLICE → RUN_SCOPED_TESTS_FOR_SELECTED_SLICE" --require-product-step
```

Если команда состоит только из hold/await шагов, harness должен вернуть `FAIL`.

Перед закрытием product slice можно требовать, чтобы diff содержал product-area изменения (`app/`, `scripts/`, `tests/`), а не только docs-sync:

```powershell
python scripts/phase9_progress_harness.py --require-product-diff
```

Если product slice выполняется в отдельном AMN2 worktree:

```powershell
python scripts/phase9_progress_harness.py --repo-root worktrees/amn2-public-config-delivery-policy-contract --require-product-diff
```

</details>

## Design specs и transfer gate

Foundational design specs для будущей оценки переноса в `amn2` собраны в [Design Specs Index + `amn2` Transfer Checklist](docs/superpowers/specs/2026-05-30-design-specs-index-amn2-transfer-checklist.md).

Этот index не разрешает автоматический перенос функций. Он нужен, чтобы перед работой в основном Amneziya/`amn2` проверить лицензию, пользу, риски, архитектурную совместимость, тестовый план и recovery-модель.
