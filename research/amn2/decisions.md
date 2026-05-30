# `amn2`: decision log

## 2026-05-30 - Web-admin 2FA paused

Решение: поставить 2FA для web-admin на паузу.

Статус: `paused`.

Что это значит:

- не писать implementation plan для 2FA сейчас;
- не менять production-код `amn2` под TOTP/MFA;
- сохранить auth/route/secret inventories как контекст на будущее;
- вернуться к вопросу только после отдельного решения о необходимости этой доработки.

Почему так:

- текущие inventories показали, что 2FA технически применима, но это не значит, что она нужна прямо сейчас;
- перед 2FA все равно потребуется выбор actor model и recovery model;
- ближайшая работа lab может дать больше пользы через config delivery, remote operations, route policy и secret handling без добавления нового login flow.

Когда вернуться к обсуждению:

- web-admin планируется открывать шире, чем локальный/закрытый operator access;
- появляются несколько операторов с разным уровнем доверия;
- появляется требование security hardening перед production rollout;
- обнаруживается риск password-only admin access;
- нужен отдельный compliance/security milestone.

Следующий фокус lab: продолжать inventory и transfer-gate работу без предположения, что 2FA будет первой production-доработкой.
