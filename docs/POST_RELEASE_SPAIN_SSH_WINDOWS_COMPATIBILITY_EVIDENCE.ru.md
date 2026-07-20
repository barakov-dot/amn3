# Spain SSH onboarding: Windows OpenSSH compatibility evidence

Дата: 2026-07-20
Статус: trust state локально подготовлен; Spain network contact не выполнялся

## Причина коррекции

Первый запуск реального локального `prepare-key` остановился fail-closed:
Windows PowerShell 5.1 не передал `ssh-keygen` пустое значение после `-N`.
После точной коррекции генерация сработала, но строгая проверка пары также
закрылась на том, что Windows OpenSSH добавляет public comment к выводу
`ssh-keygen -y`. Parser теперь допускает только необязательный однострочный
comment, продолжая сравнивать точный Ed25519 base64 key material.

## TDD и verification

```text
red_real_windows_keygen=option_requires_an_argument_N
red_native_public_output=optional_comment_rejected
green_real_windows_keygen=pass
spain_focused_tests=22_passed
root_full_tests=185_passed
powershell_parse=pass
diff_check=pass
added_line_secret_scan=pass
```

Добавлен integration regression test с системным
`C:\Windows\System32\OpenSSH\ssh-keygen.exe` и изолированным временным
artifact root. Он не устанавливает сеть и не читает private key material.

## Immutable local evidence

```text
amn2_source=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
spain_onboarding_sha256=EB725B63723949D6EFF71C691C31695FBEDA44B555F6F3591C6E426263E3DCD2
spain_readonly_runner_sha256=0F27113DEA48F8F4443CDCA6628F5D6527E7036F407447B6288595AD0FCCF5AC
spain_remote_probe_sha256=5485260DF91713B742E45793C079F6A18BC1B83D54AF72556EB8E6A3CC0AB345
dedicated_key_run_id=spain-fresh-20260720-001
dedicated_public_key_fingerprint=SHA256:22zMZFDsPF5SrU5tiF7k27aWvXEMmXwyjqw+CSyYqns
security_scan=2071578_b7eaf7d_20260720T055655Z
security_coverage=4_of_4_complete
security_reportable_findings=0
```

Runner перепривязан к текущему AMN2 source; approval со старым source
`51fd...` больше не соответствует runner bytes и не может быть принят.

## Provider-console trust checkpoint

Оператор отдельно подтвердил установку dedicated public key и передал только
безопасные public host-key evidence. Локальная проверка зафиксировала:

```text
private_target_binding=prepared|four_line_schema|acl_current_user_only
known_hosts_spain=created_once|fingerprint_exact_match|acl_current_user_only
dedicated_key_pair=exact_ed25519_material_match
preflight_evidence=absent
network_contact=false
```

Target address, login и raw host-key line остаются только в Git-ignored private
artifacts и не записываются в status/evidence.

## Live boundary

- Private key находится только в ACL-protected и Git-ignored artifact root.
- Public key установлен оператором вручную через provider console.
- Private target binding и `known_hosts_spain` созданы локально только после
  независимого точного совпадения provider-console fingerprint.
- SSH/read-only preflight всё ещё запрещён до отдельного literal approval.
- Unrelated Spain service, production bot/web/database и AWG не контактировались
  и не изменялись.
- `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` не затронут.
