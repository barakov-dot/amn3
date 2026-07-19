# Локальный SSH onboarding для Spain

Этот шаг создаёт отдельный ключ и private binding для Spain. Скрипт выполняет
только локальные операции и не устанавливает SSH-соединение с VPS. Артефакты
хранятся в игнорируемом каталоге
`private-artifacts/post-release/spain-migration/<run_id>/` с ACL только для
текущего пользователя Windows.

## Локальные режимы

Запускайте `scripts/vps/post_release_spain_ssh_onboarding.ps1` с одним и тем же
`-RunId`:

1. `prepare-key` — создать отдельный Ed25519-ключ Spain.
2. `write-binding` — скрыто ввести host, login и независимо полученный SHA-256
   fingerprint. Значения не печатаются; `target.env` содержит ровно четыре поля.
3. `print-public-key` — показать только публичный ключ.
4. `verify-pin` — скрыто ввести полученную out-of-band строку публичного host key,
   локально вычислить fingerprint и записать `known_hosts_spain` только при точном
   совпадении с pin из binding.

## Единственное интерактивное действие на сервере

Оператор один раз открывает provider console (web/VNC) либо вручную использует
интерактивный системный OpenSSH. Он добавляет результат `print-public-key` в
`~/.ssh/authorized_keys` разрешённой учётной записи Spain. Скрипт этого не делает.

Fingerprint host key получают через доверенный provider console/out-of-band
канал и проверяют независимо до `verify-pin`. Trust state USA или другого VPS не
переносится. Автоматическое принятие неизвестного ключа и сетевое сканирование
ключей не являются подтверждением identity.

После режима `verify-pin` должны существовать отдельные файлы
`id_ed25519_spain`, `target.env` и `known_hosts_spain`. До этого состояния любые
автоматизированные preflight или deployment для Spain запрещены.
