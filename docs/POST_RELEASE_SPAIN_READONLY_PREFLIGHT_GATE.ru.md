# Spain read-only preflight gate

## Статус

Этот gate реализует только checksum-bound read-only инвентаризацию Spain VPS. В рамках подготовки Task 8 он не выполнялся: SSH-соединение с Spain/VPS не устанавливалось, Telegram API не вызывался, установка и любые live-изменения не производились.

Runner допускает единственный режим `preflight` и до обращения к private artifacts требует полного точного approval. Approval привязан к SHA-256 удалённого probe и исходному AMN2 head. Текст approval для будущего запуска берётся только из отдельно проверенного runner после локальной проверки и отдельного решения оператора; частичное совпадение, шаблон или approval другого gate не подходят.

## Повторное использование trust state Task 7

Gate не создаёт второй SSH-контур. Он потребляет уже подготовленные Task 7 artifacts в игнорируемом каталоге:

```text
private-artifacts/post-release/spain-migration/<run_id>/target.env
private-artifacts/post-release/spain-migration/<run_id>/id_ed25519_spain
private-artifacts/post-release/spain-migration/<run_id>/id_ed25519_spain.pub
private-artifacts/post-release/spain-migration/<run_id>/known_hosts_spain
```

Перед SSH runner проверяет защищённые ACL, точную четырёхстрочную схему binding, соответствие `SSH_KEY_PATH` dedicated key, совпадение private/public Ed25519 пары и независимый fingerprint `known_hosts_spain`. Ambient SSH config отключён через `-F none`; обязательны batch mode, только dedicated identity и strict host-key checking.

## Состав evidence

Удалённый probe формирует нормализованный JSON `amn2.spain-readonly-preflight.v1`:

- ОС и kernel без hostname или target address;
- CPU, RAM и ёмкость корневого диска;
- listening sockets только как protocol/scope/port, без адреса;
- безопасные состояния Docker и systemd с хешированными именами;
- digest и количество отображаемых firewall rules без раскрытия адресов;
- allowlist безопасных значений эффективной SSH policy;
- UTC clock и наличие фиксированного набора пакетов;
- `unrelated_service_fingerprint` из kind, name hash, image/unit hash, active state, restart count и bound-port set.

Evidence не содержит environment, config bodies, command line, IP/host, ключи, учётные данные или Telegram-значения. После проверки JSON runner сохраняет только redacted evidence как `preflight-evidence.json` в том же private run directory.

## Граница безопасности

Probe не устанавливает и не обновляет пакеты, не пишет удалённые файлы, не изменяет firewall, Docker или systemd, не запускает и не останавливает сервисы. Он не изменяет AWG, AMN2, Telegram и посторонний сервис. Fingerprint предназначен для последующего точного сравнения до и после отдельно разрешённых этапов.

Наличие этого кода не является live-authority. Будущий оператор сначала проверяет repository head, SHA runner/probe и Task 7 trust artifacts, затем получает отдельное точное approval и только после этого вручную запускает gate. В этой задаче такой запуск запрещён и не выполнялся.
