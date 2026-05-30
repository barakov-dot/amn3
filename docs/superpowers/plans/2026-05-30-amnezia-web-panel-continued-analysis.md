# Amnezia Web Panel Continued Analysis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Продолжить безопасный research-only анализ `PRVTPRO/Amnezia-Web-Panel` и подготовить материалы, которые можно использовать для отбора идей в `amn2` и будущий гибридный VPN-проект.

**Architecture:** Работа остается документационной: каждый слой анализа получает отдельный Markdown deep-dive в `research/upstreams/`, а итоговые идеи раскладываются по `ideas/`. Код upstream не копируется; фиксируются только выводы, риски, источники и самостоятельные production-требования.

**Tech Stack:** Markdown, GitHub connector, PowerShell, Git. Основной язык документов - русский, английский используется для имен файлов, API-терминов, endpoint names и upstream-ссылок.

---

## Scope

План продолжает уже выполненный анализ:

- базовая карточка: `research/upstreams/prvtpro-amnezia-web-panel.md`;
- auth/secrets deep-dive: `research/upstreams/prvtpro-amnezia-web-panel-auth-secrets.md`.

Следующие слои:

1. API surface и route guards.
2. Manager/SSH/protocol architecture.
3. Feature gap и очередь следующих решений.

## File Structure

- Create: `research/upstreams/prvtpro-amnezia-web-panel-api-surface.md`
  - Карта endpoint-групп, guards, ролей, public surfaces, risky operations и переносимых идей.
- Create: `research/upstreams/prvtpro-amnezia-web-panel-manager-architecture.md`
  - Разбор manager-подхода, SSH abstraction, protocol lifecycle, destructive operations и safe-design требований.
- Create: `research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md`
  - Таблица идей: что полезно для `amn2`, что только для гибрида, что заблокировано, что требует текущего контекста `amn2`.
- Modify: `research/upstreams/prvtpro-amnezia-web-panel.md`
  - Добавить ссылки на новые deep-dive документы и отметить закрытые пункты следующих шагов.
- Modify: `ideas/candidates-for-amn2.md`
  - Добавить только идеи, которые можно самостоятельно спроектировать для `amn2` после проверок.
- Modify: `ideas/candidates-for-hybrid.md`
  - Добавить идеи, слишком широкие для `amn2`, но полезные для будущего гибридного продукта.
- Modify: `ideas/rejected.md`
  - Добавить anti-patterns и blocked items.
- Modify: `ideas/add-to-skill.md`
  - Добавить чеклисты для будущего анализа API surface и manager architecture.
- Modify: `watch-notes/README.md`
  - Добавить ссылки на новые активные deep-dive материалы.

## Task 1: API Surface Deep-Dive

**Files:**
- Create: `research/upstreams/prvtpro-amnezia-web-panel-api-surface.md`
- Modify: `research/upstreams/prvtpro-amnezia-web-panel.md`
- Modify: `ideas/candidates-for-amn2.md`
- Modify: `ideas/candidates-for-hybrid.md`
- Modify: `ideas/rejected.md`
- Modify: `ideas/add-to-skill.md`
- Modify: `watch-notes/README.md`

- [ ] **Step 1: Gather upstream API evidence**

Use the GitHub connector to inspect `app.py` sections around:

- `OPENAPI_TAGS`;
- `/api/auth/*`;
- `/api/servers/*`;
- `/api/servers/{server_id}/install`;
- `/api/servers/{server_id}/clear`;
- `/api/servers/{server_id}/server_config`;
- `/api/servers/{server_id}/connections/*`;
- `/api/users/*`;
- `/api/my/*`;
- `/api/share/*`;
- `/api/settings/*`;
- `/api/settings/tokens/*`;
- backup/restore endpoints.

Expected evidence:

- endpoint groups from README/OpenAPI tags;
- auth guard type for each group;
- role boundary;
- risky operations;
- candidate ideas and rejected patterns.

- [ ] **Step 2: Write API surface deep-dive**

Create `research/upstreams/prvtpro-amnezia-web-panel-api-surface.md` with these sections:

```md
# PRVTPRO/Amnezia-Web-Panel: API surface и route guards

## Паспорт deep-dive

## Краткий вывод

## Endpoint groups

## Auth и role guards

## Public surfaces

## Risky operations

## Что полезно для `amn2`

## Что полезно для будущего гибридного проекта

## Что нельзя переносить как есть

## Test-plan идеи для будущего production-дизайна

## Источники
```

The document must state `GPL-3.0` and `research-only`.

- [ ] **Step 3: Update idea files from API analysis**

Add candidate ideas to `ideas/candidates-for-amn2.md` only when they are independent design ideas, for example:

- route guard matrix;
- endpoint risk classification;
- separate public/user/admin API surfaces;
- destructive operation test plan.

Add hybrid-only ideas to `ideas/candidates-for-hybrid.md`, for example:

- full multi-surface operator API;
- API docs as product surface;
- integration-friendly external API.

Add rejected patterns to `ideas/rejected.md`, for example:

- raw config editing without validation/audit;
- destructive API endpoints without dry-run;
- mixed auth guard policy without endpoint matrix.

- [ ] **Step 4: Verify Task 1**

Run:

```powershell
Select-String -Path '*.md','research\**\*.md','ideas\*.md','watch-notes\*.md','prototypes\*.md','docs\superpowers\plans\*.md','docs\superpowers\specs\*.md' -Pattern 'T[O]DO|T[B]D|PLACE[H]OLDER'
```

Expected: no matches.

Run:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' -c safe.directory='C:/Users/SooL/Documents/VPS-OPS-LAB' diff --check
```

Expected: exit code 0.

- [ ] **Step 5: Commit Task 1**

Stage the files changed in Task 1 and commit:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' -c safe.directory='C:/Users/SooL/Documents/VPS-OPS-LAB' add research/upstreams/prvtpro-amnezia-web-panel-api-surface.md research/upstreams/prvtpro-amnezia-web-panel.md ideas/candidates-for-amn2.md ideas/candidates-for-hybrid.md ideas/rejected.md ideas/add-to-skill.md watch-notes/README.md
& 'C:\Program Files\Git\cmd\git.exe' -c safe.directory='C:/Users/SooL/Documents/VPS-OPS-LAB' -c user.name='Codex' -c user.email='codex@local' commit -m 'Add Amnezia API surface analysis'
```

Expected: one commit with API surface analysis.

## Task 2: Manager Architecture Deep-Dive

**Files:**
- Create: `research/upstreams/prvtpro-amnezia-web-panel-manager-architecture.md`
- Modify: `research/upstreams/prvtpro-amnezia-web-panel.md`
- Modify: `ideas/candidates-for-amn2.md`
- Modify: `ideas/candidates-for-hybrid.md`
- Modify: `ideas/rejected.md`
- Modify: `ideas/add-to-skill.md`
- Modify: `watch-notes/README.md`

- [ ] **Step 1: Gather upstream manager evidence**

Use the GitHub connector to inspect:

- `managers/ssh_manager.py`;
- `managers/awg_manager.py`;
- `managers/wireguard_manager.py`;
- `managers/xray_manager.py`;
- `managers/telemt_manager.py`;
- `managers/dns_manager.py`;
- `managers/adguard_manager.py`;
- `managers/socks5_manager.py`;
- relevant `app.py` lifecycle endpoints.

Expected evidence:

- shared SSH abstraction;
- per-protocol manager responsibilities;
- install/status/add/remove/toggle/config patterns;
- destructive operations;
- logging and command execution risks.

- [ ] **Step 2: Write manager architecture deep-dive**

Create `research/upstreams/prvtpro-amnezia-web-panel-manager-architecture.md` with these sections:

```md
# PRVTPRO/Amnezia-Web-Panel: manager architecture

## Паспорт deep-dive

## Краткий вывод

## Общая модель

## SSH abstraction

## Protocol managers

## Lifecycle operations

## Destructive operations

## Что полезно для `amn2`

## Что полезно для будущего гибридного проекта

## Что нельзя переносить как есть

## Test-plan идеи для будущего production-дизайна

## Источники
```

The document must state `GPL-3.0` and `research-only`.

- [ ] **Step 3: Update idea files from manager analysis**

Add `amn2` candidates such as:

- command execution contract;
- dry-run-first protocol operations;
- audit event model;
- manager interface checklist.

Add hybrid candidates such as:

- plugin-like protocol managers;
- attach existing server reconciliation flow;
- protocol capability registry.

Add rejected patterns such as:

- shell command construction with unsanitized runtime values;
- destructive cleanup without preview;
- host key auto-trust for production.

- [ ] **Step 4: Verify Task 2**

Run the same forbidden-marker scan and `git diff --check` from Task 1.

Expected: no forbidden-marker matches and exit code 0.

- [ ] **Step 5: Commit Task 2**

Stage the files changed in Task 2 and commit:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' -c safe.directory='C:/Users/SooL/Documents/VPS-OPS-LAB' add research/upstreams/prvtpro-amnezia-web-panel-manager-architecture.md research/upstreams/prvtpro-amnezia-web-panel.md ideas/candidates-for-amn2.md ideas/candidates-for-hybrid.md ideas/rejected.md ideas/add-to-skill.md watch-notes/README.md
& 'C:\Program Files\Git\cmd\git.exe' -c safe.directory='C:/Users/SooL/Documents/VPS-OPS-LAB' -c user.name='Codex' -c user.email='codex@local' commit -m 'Add Amnezia manager architecture analysis'
```

Expected: one commit with manager architecture analysis.

## Task 3: Feature Gap And Decision Queue

**Files:**
- Create: `research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md`
- Modify: `research/upstreams/prvtpro-amnezia-web-panel.md`
- Modify: `ideas/candidates-for-amn2.md`
- Modify: `ideas/candidates-for-hybrid.md`
- Modify: `ideas/rejected.md`
- Modify: `watch-notes/README.md`

- [ ] **Step 1: Build feature gap without assuming current `amn2` internals**

Because this repository does not contain `amn2`, classify each item as one of:

- `candidate-for-amn2-review`;
- `hybrid-only`;
- `blocked-by-license-or-risk`;
- `needs-amn2-context`;
- `rejected-for-production`.

Expected feature areas:

- bootstrap/auth;
- users/roles;
- API tokens;
- self-service;
- public sharing;
- Telegram delivery;
- backup/restore;
- multi-protocol orchestration;
- SSH/sudo command execution;
- API docs and endpoint taxonomy;
- status polling and health checks.

- [ ] **Step 2: Write feature gap document**

Create `research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md` with a Markdown table:

```md
# PRVTPRO/Amnezia-Web-Panel: feature gap для `amn2` и гибрида

## Паспорт

## Как читать таблицу

| Область | Upstream идея | Для `amn2` | Для гибрида | License/risk verdict | Следующий шаг |
| --- | --- | --- | --- | --- | --- |

## Кандидаты ближайшего проектирования

## Заблокировано или отклонено

## Что требует контекста `amn2`

## Источники
```

The document must state that `amn2` context is not present in this repository, so final gap verdicts require reviewing `amn2`.

- [ ] **Step 3: Update upstream card and watch notes**

Update `research/upstreams/prvtpro-amnezia-web-panel.md`:

- link API surface deep-dive;
- link manager architecture deep-dive;
- link feature gap;
- mark API surface and manager architecture as completed first-pass.

Update `watch-notes/README.md` with the feature gap document.

- [ ] **Step 4: Verify Task 3**

Run the same forbidden-marker scan and `git diff --check` from Task 1.

Expected: no forbidden-marker matches and exit code 0.

- [ ] **Step 5: Commit Task 3**

Stage the files changed in Task 3 and commit:

```powershell
& 'C:\Program Files\Git\cmd\git.exe' -c safe.directory='C:/Users/SooL/Documents/VPS-OPS-LAB' add research/upstreams/prvtpro-amnezia-web-panel-feature-gap.md research/upstreams/prvtpro-amnezia-web-panel.md ideas/candidates-for-amn2.md ideas/candidates-for-hybrid.md ideas/rejected.md watch-notes/README.md
& 'C:\Program Files\Git\cmd\git.exe' -c safe.directory='C:/Users/SooL/Documents/VPS-OPS-LAB' -c user.name='Codex' -c user.email='codex@local' commit -m 'Add Amnezia feature gap analysis'
```

Expected: one commit with feature gap analysis.

## Final Verification

- [ ] Run forbidden-marker scan across Markdown files.
- [ ] Run `git status --short --branch`.
- [ ] Run `git log -4 --oneline --decorate`.
- [ ] Confirm the final working tree is clean.
- [ ] Summarize:
  - created files;
  - updated idea queues;
  - rejected patterns;
  - next recommended analysis target.

## Self-Review

Spec coverage:

- Continue upstream analysis: covered by Tasks 1-3.
- Prepare a plan: this document is the plan.
- Start execution: begin with Task 1 after saving this plan.
- Keep docs Russian-first: all deliverables are Russian-first.
- Keep license safety: every new deep-dive must state GPL-3.0 and `research-only`.

Forbidden-marker scan target: no unfinished-work markers should remain in the plan or produced Markdown.
