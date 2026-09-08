# Стартовое сообщение для новой задачи — Phase 16

Это передача контекста на 2026-09-08, не второй execution plan и не новая
авторизация live-действий. Текст ниже можно передать новой задаче целиком.

## Продолжение, не перезапуск

Работай только над AMN3 / VPS-OPS-LAB. Передача подготовлена в worktree
`C:/Users/SooL/.codex/worktrees/7489/VPS-OPS-LAB`, исходный HEAD перед этой docs-only
синхронизацией — `d2383a9fcdff0942aa426790afc31d330f52ca95` (detached).
В начале проверь фактические HEAD, branch и scoped diff: этот SHA не является
командой checkout или deployed revision. Итоговый SHA docs-only commit передаётся
оператору отдельно; не переключайся на старый SHA ради совпадения с этим текстом.

Целевая ветка публикации: `codex/phase16-awg3-family-3-1-spain-pilot-016`,
origin `https://github.com/barakov-dot/amn3.git`. Последний push до данной правки
подтверждался в исходной задаче для `d2383a9`; локальный tracking ref может отставать.
Это историческое подтверждение, не новый remote readback или разрешение push.
Не начинай с основного checkout по умолчанию: ранее там обнаружен старый HEAD.

## Сначала прочитай актуальное

1. [AGENTS](../AGENTS.md) и [START_HERE](START_HERE.ru.md).
2. Только актуальную часть [плана Phase 16](superpowers/plans/2026-08-24-amn2-phase16-awg3-family-3-1-spain-pilot.md).
3. [Recovery-контракт v1](superpowers/specs/2026-09-08-phase16-controlled-stage-recovery-contract.ru.md)
   и [завершённый R1 review](../research/amn2/phase16-recovery-helper-compatibility-review-2026-09-08.md).
4. [Статус опубликованного комментария #3043](../research/amn2/phase16-windows-issue-3043-comment-2026-09-08.md).

Не перечитывай всю историю и не выполняй старые approvals. Если документы
противоречат последнему сообщению, укажи точное расхождение, не повторяй работу.

## Уже сделано — не повторять

- Три stage-защиты: `db9f4a0` (ownership staging), `e97eda2` (`rollback_failed`),
  `b6c5fd7` (`recovery_required`, без cleanup при неподтверждённом stage).
  Результаты прежних offline-проверок зафиксированы в плане. Код не развёрнут.
- Recovery-контракт согласован: `CONTRACT_APPROVED_NOT_IMPLEMENTED_NOT_EXECUTED`.
  Повторное согласование того же контракта не нужно; runner/recovery не реализованы.
- R1 чтение старых collector/driver завершено, хеши известны. Parser compatibility
  fix только предложен; нельзя объявлять его реализованным или начинать без scope.
- Комментарий #3043 опубликован вручную и проверен. Не отправлять снова;
  сходство с issue не доказывает root cause и публикация не закрывает Windows gate.
- Документационный аудит и первая оптимизация уже завершены. Не начинать их с нуля.

## Первый ход новой задачи: только delta-аудит для передачи

Оператор просил подготовить аудит имеющегося проекта и рекомендации по документации,
архитектуре, регламентам, skills/агентам. Это проверка оставшихся пробелов после
выполненной оптимизации, не повтор полного аудита и не разрешение произвольных правок.

Используй существующие [README](../README.md), [паспорт](PROJECT_PASSPORT.ru.md),
[архитектуру](ARCHITECTURE.ru.md), [CODE_MAP](CODE_MAP.ru.md),
[SKILLS_MAP](SKILLS_MAP.ru.md) и [историю оптимизации](SKILLS_AUDIT_HISTORY_2026-09-08.ru.md)
только по конкретному вопросу. Отделяй отсутствие документа от устаревшего раздела.
Схему production БД не выдумывай: неизвестный источник данных — ограничение,
а не основание обследовать другой проект или production.

Итог первого хода: короткий список только новых подтверждённых пробелов с путями,
влиянием и минимальной правкой; для уже сделанного — «сохранить, не повторять».
Если новых существенных пробелов нет, прямо сообщи это. Не создавай документы,
агентов или skills ради полноты списка. Затем предложи один ограниченный пакет
с реальной пользой и дождись выбора scope перед реализацией.

Личные `sdp-firebird`/`winui-app` переведены в explicit-only по прежнему отдельному
решению; это историческая запись, не просьба их менять. Superpowers toggle-пилот
не подтверждён как выполненный и не является обязательным следующим этапом.
Не трогай глобальные skills, plugin cache, память и другие проекты.

## Границы и приоритеты

Полный статус — в актуальном плане. Quality FAIL, strict A/B и iPhone/две сети
отложены оператором. Windows traffic FAIL; гипотеза отсутствующих маршрутов
отвергнута. DNS bridge STOP. Acceptance/integration/closeout не завершены.
Не проси снова iPhone/две сети и не повторяй Windows-тест без новой гипотезы
или значимого изменения официального клиента/engine и точного live approval.

`AWG2_UNTOUCHED`; package016 immutable; один peer только последовательно.
Не читать protected profiles/raw logs; не менять peers, freshness policy,
Telegram, основное application state и общую issuance. Никаких SSH/Spain egress,
signals/upload/stage/install/реальной генерации без соответствующего exact approval.
Опасные операции — checksum/state/rollback-bound. Исторические approvals не действуют заново.

Docs-only: readback, ссылки, diff/whitespace, отсутствие секретов; без pytest
и package materialization. Code fix: отдельный scope, TDD и один целевой набор.
Сохраняй чужие изменения; Windows ACL может давать ложные удаления. Только точный
staging, никогда `git add -A`. После материальных правок — проверенный локальный
commit и SHA; push только по отдельному exact HEAD/origin/ref approval,
`NO_FORCE NO_TAGS NO_OTHER_BRANCHES NO_PROTECTED_CONFIGS`.

Общайся кратко по-русски. После операционного прогона — полный вертикальный статус
Phase 16, следующий конкретный шаг, safety state и фактические model/effort
(если недоступны — так и укажи). Рекомендация модели не разрешает действий.
