# POST-RELEASE Spain systemd MainPID fallback implementation evidence

Дата: 2026-07-20

Статус: local implementation verified; live preflight not run

## Authority и граница

- correction design: commit `9654d77`;
- implementation plan: commit `b8f8fff`;
- implementation approval:
  `APPROVE_WRITTEN_PHASE11_SPAIN_SYSTEMD_MAINPID_FALLBACK_CORRECTION_SPEC_9654D77`.

Authority разрешает локальную реализацию, тесты, review, docs/commit/push и
подготовку новой буквальной approval. Она не разрешает SSH, повтор старого run,
install, service mutation, Telegram action или AWG action.

## Реализованный контракт

Remote probe различает три состояния systemd unit:

- непустой `ControlGroup`: прежний строгий cgroup path;
- пустой `ControlGroup` и `MainPID=0`: явный
  `active_exited_no_live_process`, без ложных портов;
- пустой `ControlGroup` и `MainPID>0`: строгий v2/v1 procfs parser, canonical
  systemd unit-id binding и повторная проверка неизменности MainPID, process
  starttime и cgroup bytes.

Ошибки формата/диапазона, procfs read, cgroup parsing и identity/stability
закрываются sanitized exit `71..74`. Raw procfs, unit name, target и command
не попадают в failure evidence.

Runner повторно использует только protected trust bundle
`spain-fresh-20260720-001` из заранее подготовленной защищённой local copy под
`%LOCALAPPDATA%\AMN2`, но новый single-use claim и outcome может создать только
в `spain-fresh-20260720-002`. До любого trust read он проверяет owner,
current-user-only ACL и отсутствие reparse points всей private-artifact parent
chain. Existing outcome не удаляется и не перезаписывается; исходный workspace
trust bundle сохранён без удаления.

## Byte binding

```text
source_revision=55dc243b8e6c6bdb57f8301b56326e4cd4072d19
runner_sha256=ACA990D94D2730ADBE022F44A3EBFCD3ABD6FE14A598889244DD80038D60B76F
remote_probe_sha256=3C8B341EC813776733835D39193F451E4FC21665851E1DCDADEFE69AD9D9BA0D
immutable_trust_bundle=spain-fresh-20260720-001
new_outcome_run=spain-fresh-20260720-002
```

## TDD и проверки

```text
mainpid_resolver_red=observed
mainpid_resolver_green=pass
separate_outcome_run_red=observed
separate_outcome_run_green=pass
pid_identity_change_regression_red=observed
pid_identity_change_regression_green=pass
unrelated_cgroup_regression=pass
parent_chain_acl_reparse_regression_red=observed
parent_chain_acl_reparse_regression_green=pass
secure_local_trust_copy=verified|source_retained
focused_tests=24_passed
root_full_tests=200_passed
bash_parse=pass
powershell_parse=pass
git_diff_check=pass
security_initial_findings=pid_identity_and_workspace_trust_path_integrity|all_closed
security_fix_validation=closed
security_fixed_snapshot_independent_review=clean|reportable_findings_0
security_diff_coverage=remote_2_of_2|runner_2_of_2|deferred_0
new_lines_sensitive_pattern_scan=pass
```

## Live boundary

Runner не запускался с непустым approval, Spain после run `001` не
контактировалась, outcome directory `002` не создавался. Не выполнялись
install/update, start/stop/restart, firewall/Docker/systemd/config writes,
Telegram, unrelated-service или AWG actions.

Private target, login, SSH key, host-key line, raw diagnostics и конфиги не
добавлялись в Git/evidence. `docs/CLIENT_RELEASE_MONITOR_BASELINE.ru.md` не
изменялся.

## LocalAppData binding correction и run 003

Literal run `002` остановился до outcome claim и до SSH, потому что перенесённый
`target.env` всё ещё ссылался на старый workspace key path. Approval `002`
считается consumed и не повторялся.

По отдельному authority атомарно изменена только строка `SSH_KEY_PATH`; old
binding сохранён как protected backup. Target, user и expected host pin
сравнены до/после, а SHA-256 private/public key и known-hosts bytes подтверждены
неизменными без публикации значений. Полная owner/ACL/no-reparse chain,
binding, Ed25519 pair и independent host pin прошли локальную проверку без SSH.

```text
run_002=fail_closed_before_outcome_and_ssh|approval_consumed
binding_correction=ssh_key_path_only|verified
binding_backup=protected|retained
next_outcome_run=spain-fresh-20260720-003|absent
runner_sha256=A27CC666EF47D6AF5983217169CFB3002F41E5A70DAF625EE3A422DAFB59FAEE
remote_probe_sha256=3C8B341EC813776733835D39193F451E4FC21665851E1DCDADEFE69AD9D9BA0D
focused_tests=24_passed
root_full_tests=200_passed
security_review=independent_diff_clean|reportable_findings_0|stale_run_fail_closed
ssh=false
telegram=false
awg=untouched
```
