# AMN3 / VPN Ops Lab

Приватный штаб проекта для параллельного развития `amn2`, будущих VPN-продуктов и Local Amnezia Agent.

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

Этот репозиторий не является production-кодом.

Код из внешних проектов не копируется без проверки лицензии.

Основной подход: изучать идеи, адаптировать архитектурно и реализовывать своими изменениями с тестами.

Если лицензия проекта неясна, несовместима или требует copyleft-обязательств, идея не переносится в `amn2` как код. Допускается только анализ концепции и самостоятельное проектирование.

## Язык документов

Markdown-документы, README, спецификации, заметки и исследовательские карточки в этом проекте готовятся в первую очередь на русском языке.

Английский используется вторым слоем для имен файлов, технических терминов, ссылок, лицензий и названий внешних проектов.

## Структура

```text
research/
  amn2/
  upstreams/
ideas/
watch-notes/
prototypes/
```

`research/amn2/` - read-only inventory текущего production-направления `amn2` для проверки применимости идей из lab.

`research/upstreams/` - карточки анализа внешних проектов.

`ideas/` - отбор идей по направлениям: `amn2`, будущий гибридный проект, общий Codex skill, отклоненные идеи.

`watch-notes/` - периодические наблюдения за upstream-проектами, релизами и security-relevant изменениями.

`prototypes/` - собственные эксперименты и проверки гипотез без копирования внешнего кода.

## Phase 9 progress harness

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

## Design specs и transfer gate

Foundational design specs для будущей оценки переноса в `amn2` собраны в [Design Specs Index + `amn2` Transfer Checklist](docs/superpowers/specs/2026-05-30-design-specs-index-amn2-transfer-checklist.md).

Этот index не разрешает автоматический перенос функций. Он нужен, чтобы перед работой в основном Amneziya/`amn2` проверить лицензию, пользу, риски, архитектурную совместимость, тестовый план и recovery-модель.
