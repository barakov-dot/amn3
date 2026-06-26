# PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE_RUNBOOK

Дата: 2026-06-26.

Статус: `prepared-pending-provider-console-result-and-private-inputs`.

Назначение: подготовить key-based SSH access как дополнительный access path,
не отключая текущий password/root path и не выполняя SSH hardening.

Использовать только после:

```text
PRIVATE_RC_PROVIDER_CONSOLE_SSH_DIAGNOSTIC_GATE=passed_or_provider_console_available
```

## Stop-lines

Нельзя в этом gate:

- отключать password auth;
- отключать root login;
- менять SSH port;
- менять firewall/listener/TLS/proxy;
- удалять существующие authorized keys;
- перезапускать ssh/sshd;
- reboot/rebuild/restore/import;
- открывать public exposure;
- запускать Telegram polling;
- генерировать/deliver config;
- печатать private key/password/token/full authorized_keys.

## Local private key prep

Если отдельного ключа еще нет, оператор может локально создать новый ключ.
Private key остается только на локальной машине и не вставляется в чат.

```powershell
$KeyPath = "$env:USERPROFILE\.ssh\amn2_private_rc_operator_ed25519"
ssh-keygen.exe -t ed25519 -f $KeyPath -C "amn2-private-rc-operator" -N ""
ssh-keygen.exe -lf "$KeyPath.pub"
```

Если ключ уже есть:

```powershell
$KeyPath = "$env:USERPROFILE\.ssh\amn2_private_rc_operator_ed25519"
ssh-keygen.exe -lf "$KeyPath.pub"
Get-Content "$KeyPath.pub"
```

Публичный ключ можно вставить приватно в provider console. Private key нельзя
печатать или отправлять.

## Provider console append block

В provider console/VNC/serial на VPS выполнить только после explicit gate и
только если публичный ключ оператора готов. Блок попросит вставить public key
приватно в консоль и не выведет его обратно.

```bash
echo "PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE"
echo "target=89.185.80.166"
echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "opened_gate=PRIVATE_RC_SSH_KEY_BASED_ACCESS_PREP_GATE"
echo "scope=append-one-operator-public-key-no-hardening"
echo "disable_password_auth_performed=false"
echo "disable_root_login_performed=false"
echo "ssh_port_change_performed=false"
echo "firewall_change_performed=false"
echo "service_restart_performed=false"
echo "public_exposure_performed=false"
echo "secret_values_printed=false"

printf 'Paste OPERATOR PUBLIC ssh-ed25519 key, then Enter: '
IFS= read -r OPERATOR_PUBLIC_KEY
case "$OPERATOR_PUBLIC_KEY" in
  ssh-ed25519\ *|ssh-rsa\ *) echo "operator_public_key_shape=accepted" ;;
  *) echo "operator_public_key_shape=rejected"; echo "key_based_access_prep_status=failed_bad_public_key_shape"; exit 20 ;;
esac

mkdir -p /root/.ssh
chmod 700 /root/.ssh
touch /root/.ssh/authorized_keys
chmod 600 /root/.ssh/authorized_keys

KEY_FP="$(printf '%s\n' "$OPERATOR_PUBLIC_KEY" | ssh-keygen -lf - 2>/dev/null | awk '{print $2}' || true)"
echo "operator_public_key_fingerprint=${KEY_FP:-unavailable}"

if grep -Fqx "$OPERATOR_PUBLIC_KEY" /root/.ssh/authorized_keys; then
  echo "authorized_keys_append_count=0"
  echo "operator_public_key_already_present=true"
else
  printf '%s\n' "$OPERATOR_PUBLIC_KEY" >> /root/.ssh/authorized_keys
  echo "authorized_keys_append_count=1"
  echo "operator_public_key_already_present=false"
fi

echo "authorized_keys_path=/root/.ssh/authorized_keys"
echo "authorized_keys_mode=$(stat -c '%a' /root/.ssh/authorized_keys 2>/dev/null || echo unknown)"
echo "ssh_dir_mode=$(stat -c '%a' /root/.ssh 2>/dev/null || echo unknown)"
echo "authorized_keys_full_contents_printed=false"
echo "private_key_output_performed=false"
echo "password_auth_setting_changed=false"
echo "root_login_setting_changed=false"
echo "ssh_port_changed=false"
echo "firewall_changed=false"
echo "service_restart_performed=false"
echo "key_based_access_prep_status=operator_public_key_installed_or_already_present"
echo "secret_values_printed=false"
```

## Local key login test

После append block проверить с локальной машины:

```powershell
$KeyPath = "$env:USERPROFILE\.ssh\amn2_private_rc_operator_ed25519"
ssh.exe -i $KeyPath -o IdentitiesOnly=yes root@89.185.80.166 "echo key_login_test_status=passed; test -f /opt/amn2/.amn2_source_overlay_commit && tr -d '[:space:]' < /opt/amn2/.amn2_source_overlay_commit | sed 's/^/source_overlay_commit=/'"
```

Если SSH снова закрывается до вывода:

```text
key_login_test_status=blocked-by-ssh-transport
```

Не повторять больше одного раза без нового diagnostic decision.

## Safe summary to paste back

```text
key_based_access_prep_status=operator_public_key_installed_or_already_present|blocked
operator_public_key_fingerprint=<fingerprint_or_unavailable>
authorized_keys_append_count=0|1
key_login_test_status=passed|blocked-by-ssh-transport|failed
source_overlay_match=yes|not_checked|no
password_auth_setting_changed=false
root_login_setting_changed=false
ssh_port_changed=false
firewall_changed=false
service_restart_performed=false
secret_values_printed=false
exact_blocker=<none|safe_text>
```
