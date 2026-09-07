# Начать здесь — AMN3 / VPS-OPS-LAB

Обновлено: 2026-09-07. Это навигация по текущей работе, не второй execution plan
и не подтверждение состояния сервера. Scope текущего документационного пакета —
только этот репозиторий; другие проекты и глобальные skills не изменяются.

## Короткий маршрут

1. [Правила работы](../AGENTS.md): разрешения, проверки, секреты, Git и отчётность.
2. [Паспорт](PROJECT_PASSPORT.ru.md): назначение, ответственность и границы системы.
3. [Актуальный план Phase 16](superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md):
   читать верхний раздел «Актуальный порядок и gates», далее — только нужную задачу.
4. [Карта skills](SKILLS_MAP.ru.md): выбирать по задаче, не читать всё заранее.
5. Для работы с инструментами: [архитектура](ARCHITECTURE.ru.md) и
   [карта кода/проверок](CODE_MAP.ru.md). Это статический обзор, не live acceptance.

## Текущая работа и источники состояния

Активное направление — Phase 16 Spain AWG3.1. Единственный подробный execution
status и очередь gates находятся в плане выше. Windows и quality acceptance не
закрыты; iPhone/две сети/A/B отложены оператором. Не запрашивать их повторно
и не запускать прежние диагностики при подготовке документации.

| Состояние | Где проверять | Граница утверждения |
| --- | --- | --- |
| Local source / HEAD | Локальные git HEAD, branch/detached state и diff | Не равно package/deployed revision; SHA в истории может быть старым |
| Package / stage / install | Exact manifest и receipt конкретного gate, только в scope задачи | Наличие package016 не доказывает завершённую интеграцию; пакет immutable |
| Runtime / клиент | Датированный receipt; новый readback только по точному approval | Исторический PASS не является текущим мониторингом |
| Acceptance | Активный план и согласованные критерии v1 | Connectivity не равно quality; согласование критериев не равно PASS или live approval |

Минимальный runtime и Android/iPhone connectivity подтверждались ранее. Это не
закрывает интеграцию приложения и Phase 16. Локальный DNS-fix и документационный
пакет не меняют live-профили. Последний deployed HEAD в этом docs-only пакете
не устанавливался; не подменять его локальным git HEAD.

## Документы по вопросу

| Вопрос | Источник |
| --- | --- |
| Контракт Phase 16 | [Design](superpowers/specs/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot-design.ru.md) |
| Минимальный пилот и исторические наблюдения | [Pilot](PHASE16_MINIMAL_AWG31_PILOT.ru.md) |
| Обязательный quality gate | [Task 4.5](../research/amn2/phase16-spain-transport-quality-ab-gate-2026-08-26.md) |
| Согласованные численные критерии | [Acceptance v1](PHASE16_ACCEPTANCE_CRITERIA_DRAFT.ru.md), `CRITERIA_APPROVED_NOT_EXECUTED` |
| Локальный DNS-fix и выполненные проверки | [Receipt](../research/amn2/phase16-local-dns-generator-two-ipv4-compatibility-2026-09-05.md) |
| Передача секретов | [Протокол](AMN2_SECRET_HANDOFF_PROTOCOL.ru.md); сам документ не разрешает передачу |
| Базовые решения и transfer checklist | [Design index](superpowers/specs/2026-05-30-design-specs-index-amn2-transfer-checklist.md), [decision log](../research/amn2/decisions.md); учитывать даты |

## История, не стартовая инструкция

[PROJECT_STATUS_CURRENT](PROJECT_STATUS_CURRENT.ru.md) и
[PROJECT_CONTEXT_IMPORT](PROJECT_CONTEXT_IMPORT.ru.md) сохранены по старым путям,
чтобы не ломать ссылки. После новых предупреждений их прежнее содержимое остаётся
историей. Слова «текущий», старые GO/approvals и next-step внутри истории действуют
только в контексте той даты, а не как команда новой задаче.

Старые runbooks, templates и Phase 9 harness не являются обязательным процессом
для Phase 16 или docs-only задач. При противоречии не запускать команду: проверить
дату, scope и активный план; для нового риска/неясного разрешения обратиться к оператору.

## Как поддерживать этот вход

Менять ссылку на активный план при смене фазы; обновлять маршрут при переносе
канонического документа. Не копировать сюда полный статус или журнал прогонов.
Выполненные проверки фиксируются в соответствующем receipt/commit; новый receipt
ради одной навигационной правки не нужен. Архитектурный обзор и code map подготовлены
по локальным инструментам; production-архитектура AMN2 и ER-схема БД не обследованы.
