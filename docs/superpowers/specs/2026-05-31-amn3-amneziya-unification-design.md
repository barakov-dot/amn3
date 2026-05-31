# AMN3 / Amneziya Unification: design spec

## Назначение

Этот документ фиксирует рабочую модель объединения проекта AMN3/VPS Ops Lab с production-проектом Amneziya/`amn2`.

Главная цель: перестать терять решения между чатами, upstream-анализом и production-кодом. AMN3 становится приватным штабом проекта, а `amn2` остается репозиторием production-реализации.

Документ не является implementation plan. Он описывает правила движения информации, решений и кода между AMN3, чатами Codex и `amn2`.

## Роли Репозиториев

### AMN3

GitHub:

```text
https://github.com/barakov-dot/amn3.git
```

Роль: coordination and knowledge base.

AMN3 хранит:

- выводы из чатов;
- upstream-анализ;
- internal inventory текущего `amn2`;
- design specs;
- implementation plans;
- transfer decisions;
- ссылки на branches, commits и PR в `amn2`;
- skill-кандидаты и правила будущих чатов.

AMN3 не хранит:

- production secrets;
- `.env`;
- приватные ключи;
- клиентские VPN-конфиги;
- полный production-код `amn2`, если это не короткий фрагмент для объяснения решения.

### Amneziya / `amn2`

GitHub:

```text
https://github.com/barakov-dot/amn2.git
```

Роль: production application.

`amn2` хранит:

- Telegram bot;
- web admin panel;
- server/VPS runtime code;
- database/repository layer;
- VPN config generation and delivery;
- Local Amnezia Agent implementation;
- tests and production docs.

`amn2` не должен становиться местом хаотичного research. Любая крупная идея сначала проходит через AMN3 как design/plan/transfer decision.

## Источники Наработок

AMN3 должен учитывать три типа источников:

1. Внешние upstream-проекты:
   - `PRVTPRO/Amnezia-Web-Panel`;
   - `kyoresuas/amnezia-api`;
   - `wg-easy/wg-easy`;
   - будущие VPN/admin/API проекты.

2. Внутренний production-контекст `amn2`:
   - код и тесты в `C:\Users\SooL\Documents\Amneziya`;
   - docs/handoff внутри `amn2`;
   - live VPS retest результаты;
   - реальные ограничения Docker/AmneziaWG runtime.

3. Локальные Codex-чаты:
   - main coordination chats;
   - deep-dive chats;
   - task/review sessions;
   - VPS-test chats.

Внутренний контекст `amn2` является таким же важным источником, как upstream-analysis. Если AMN3 предлагает перенос идеи, он обязан сравнить ее с тем, что уже сделано в `amn2`.

## Transfer Flow

Каждая идея или наработка проходит такой путь:

1. Capture in AMN3:
   - откуда идея;
   - какую проблему решает;
   - какие файлы/чаты/commits подтверждают контекст.

2. Inventory check:
   - есть ли это уже в `amn2`;
   - какие текущие boundaries, tests и risks;
   - не конфликтует ли идея с существующей моделью.

3. Design gate:
   - license/source verdict;
   - product value;
   - risk class;
   - architecture fit;
   - secret/audit/recovery implications.

4. Implementation plan:
   - только после design approval;
   - с TDD steps;
   - с точными файлами;
   - с verification commands.

5. `amn2` branch:
   - код меняется только в `amn2`;
   - branch naming: `codex/<feature>`;
   - commits маленькие и проверяемые;
   - PR base выбирается по текущему stacked flow.

6. Return to AMN3:
   - зафиксировать branch/commit/PR;
   - записать test evidence;
   - обновить project status;
   - обновить transfer backlog.

## Chat Protocol

Каждый важный чат должен завершаться одним из артефактов в AMN3:

- `docs/PROJECT_STATUS_CURRENT.ru.md` - текущий общий snapshot;
- `docs/PROJECT_CONTEXT_IMPORT.ru.md` - большой context import для новых чатов;
- `docs/NEXT_CHAT_*.ru.md` - handoff в конкретный следующий чат;
- `research/upstreams/*.md` - upstream карточка;
- `research/amn2/*.md` - read-only inventory production-контекста;
- `docs/superpowers/specs/*.md` - validated design specs;
- `docs/superpowers/plans/*.md` - implementation plans.

Новый чат не должен начинать с нуля. Он должен получить ссылку на AMN3 snapshot и работать от текущего состояния.

## AMNEZIYA Наработки Как First-Class Input

Под "наработками AMNEZIYA" считаются не только новые идеи, но и уже сделанные production-срезы:

- VPS retest bundle;
- server health and readiness;
- peer sync;
- Docker runtime apply/revoke;
- config defaults through `.env`;
- verified email gate for config delivery;
- admin audit and redaction;
- device disable/enable flows;
- Local Amnezia Agent first slice.

AMN3 должен вести для них:

- current status;
- какие tests покрывают поведение;
- какие риски остались;
- какие upstream-идеи с ними связаны;
- что можно переносить дальше;
- что нельзя трогать без отдельного gate.

## Правило Не-Дублирования

AMN3 не дублирует production-код `amn2`.

AMN3 хранит:

- ссылки на commits;
- summary поведения;
- route/API/risk maps;
- design rationale;
- test evidence.

Если нужно объяснить production-code decision, допускается короткий path-level reference, например:

```text
amn2: app/agent/api.py
amn2: tests/agent/test_api.py
```

Но код не копируется целиком.

## GitHub И Приватность

Оба репозитория приватные:

- AMN3: project brain;
- `amn2`: production code.

Если GitHub connector не видит приватные репозитории, источником правды остаются:

- локальные checkout;
- `git status`;
- `git log`;
- pushed branches;
- manual PR URLs.

Когда GitHub connector или `gh` будет настроен, PR/issues можно вести напрямую из Codex. До этого PR создаются вручную через GitHub URL, а AMN3 хранит ссылку и статус.

## Conflict Policy

Если AMN3 и `amn2` расходятся:

1. Для production behavior верить `amn2` tests/code.
2. Для принятого решения верить последнему AMN3 status/spec, если он ссылается на commit/branch.
3. Если AMN3 устарел, сначала обновить AMN3 snapshot, потом продолжать работу.
4. Если `amn2` изменился без AMN3 update, создать AMN3 capture entry до следующего feature plan.

## First Operational Backlog

Ближайшие действия после этого spec:

1. Открыть stacked PR `codex/local-agent-first-slice` -> `codex-vps-test-prep`.
2. После merge PR обновить AMN3 status with PR/merge result.
3. Создать AMN3 transfer backlog для AMNEZIYA-наработок:
   - VPS retest;
   - config defaults;
   - Local Agent;
   - Docker runtime peer operations;
   - verified config delivery.
4. Перед следующим implementation slice создать отдельный design/plan:
   - Local Agent feature flag/settings;
   - real read-only runtime detection;
   - secure token provisioning.

## Self-Review

Scope:

- Документ описывает governance/workflow, не production implementation.
- AMN3 и `amn2` roles разделены.
- AMNEZIYA-наработки включены как first-class source.

Security:

- Secrets не переносятся в AMN3.
- Production code не дублируется в AMN3.
- GitHub connector limitations названы явно.

Operational clarity:

- Есть transfer flow.
- Есть chat protocol.
- Есть conflict policy.
- Есть first operational backlog.

Open dependency:

- Для полной автоматизации PR нужен доступ GitHub connector к приватным repo или установленный `gh`.
