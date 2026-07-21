# Phase 12 Spain: conflict-free fresh install package design

Дата: 2026-07-21
Статус: обязательная корректировка design после независимого GPT-5.6 SOL review
Scope: только подготовка checksum-bound install package; без SSH и без Spain mutation

## 1. Цель текущего gate

Подготовить воспроизводимый пакет fresh install AMN2 для Spain, который:

- устанавливает чистую БД без USA users/configs/peers;
- не изменяет и не удаляет USA production/rollback contour;
- не занимает уже занятые TCP 22/53/443/8080/10050 и UDP 53/443;
- не останавливает AWG ради тестов или peer lifecycle;
- не изменяет существующий посторонний Spain-сервис;
- до первого live write повторно доказывает read-only preconditions;
- после установки и после rollback доказывает сохранность исходного Spain fingerprint;
- не включает bot и remote VPS writes до отдельного issuance gate.

Текущий gate не выдаёт клиентские конфиги и не включает бот. Он создаёт только чистый server runtime с нулём peers и локальный web listener.

## 2. Исправление контракта fingerprint equality

Run 009 содержит 148 systemd unit fingerprints. Установка собственных unit'ов и собственных firewall rules неизбежно меняет полный набор наблюдений. Поэтому проверка определяется формально.

### 2.1 Baseline projection equality

Для каждого из 148 baseline entries после установки обязаны совпасть:

- `kind`;
- `name_sha256`;
- `image_or_unit_sha256`;
- `active_state`;
- `restart_count`;
- `bound_port_set`;
- `unit_content_status`;
- `bound_port_status`.

Ни один baseline entry нельзя исключать по имени нового сервиса, эвристике или регулярному выражению. Массив baseline канонизируется и связывается checksum'ом.

### 2.2 Closed AMN2-owned delta

Допускаются только объекты, перечисленные в package manifest и mutation ledger:

- выбранные AMN2 systemd units;
- AMN2 service user/group;
- install/config/state/runtime directories;
- AMN2 Docker daemon/socket/data root;
- один AMN2 container, image, network и bridge;
- один AWG interface и его адрес;
- loopback web listener;
- один UDP AWG listener;
- точно описанные AMN2-owned nftables additions.

Любой новый объект вне closed delta означает verification failure и запускает rollback.

### 2.3 Firewall equality

Run 009 связывает только исторические `backend=nft`, raw SHA-256
`35ED9383AE9E73268E3D1AB7F57612BC60EA59C0531D6A96372E5F3731883D00` и
`rule_count=129`; structured snapshot в evidence отсутствует. Поэтому package не
выдаёт исторический raw hash за восстановимую semantic equality. Первый отдельный
live read-only receipt сохраняет две последовательные canonical structured
observations, удаляет только volatile counters/handles и требует их стабильного
semantic digest. Именно этот current digest связывается вторым exact install
approval и повторно проверяется непосредственно перед первой mutation.

До mutation сохраняются canonical nftables snapshot и semantic hash. После установки verifier:

1. выделяет только additions, созданные package-owned table/chain/set по manifest;
2. удаляет эту точную проекцию из наблюдения;
3. проверяет наличие и неизменность всех pre-existing rules;
4. отклоняет любое изменение или дополнительное правило вне owned delta.

Rollback удаляет только ledger-recorded owned additions и требует буквального восстановления baseline firewall projection.

Raw nft text/hash сохраняется только как forensic observation и не заменяет
semantic projection: меняющиеся counters не могут ни разрешить mutation, ни
создать ложный rollback mismatch.

## 3. Ресурсный план

Кандидаты считаются зарезервированными только после live read-only precondition check:

| Ресурс | Кандидат |
|---|---|
| install root | `/opt/amn2-spain` |
| config root | `/etc/amn2-spain` |
| state root | `/var/lib/amn2-spain` |
| service user/group | `amn2-spain` |
| web unit | `amn2-spain-web.service` |
| bot unit | `amn2-spain-bot.service` (installed, disabled and stopped) |
| Docker unit | `amn2-spain-docker.service` |
| host network unit | `amn2-spain-network.service` |
| Docker socket | `/run/amn2-spain-docker/docker.sock` |
| Docker data root | `/var/lib/amn2-spain-docker` |
| image | checksum-bound AMN2 Spain AWG image |
| container | `amn2-spain-awg` |
| Docker network | `amn2-spain-net` |
| bridge | `amn2spbr0` |
| AWG interface | `awgsp0` |
| web listener | `127.0.0.1:3031` |
| AWG listener | `UDP/30001` |
| Docker CIDR candidate | `172.29.251.0/28` |
| container IP candidate | `172.29.251.2` |
| VPN CIDR candidate | `10.212.12.0/24` |
| server VPN address candidate | `10.212.12.1/24` |
| host VPN route | `10.212.12.0/24 via 172.29.251.2 dev amn2spbr0` |
| nft namespace | `inet amn2_spain` |

Ни один кандидат нельзя создавать, если read-only observation показывает конфликт имени, пути, UID/GID, port, address, route, interface или CIDR overlap.

## 4. Live preconditions до первого write

Run 009 не содержит distro release, architecture, Python version, free bytes/inodes,
MemAvailable, routes и addresses. Эти значения нельзя подставить из локальных
предположений. Поэтому live boundary разделён на два exact approvals:

1. **resource-confirmation approval** разрешает только checksum-bound read-only
   collector по закреплённому SSH target; upload/install/write запрещены;
2. **install approval** выдаётся только после сохранения, проверки, commit/push и
   origin readback canonical resource-confirmation receipt. Он связывает точные
   observed values и прежние package hashes.

Read-only collector имеет отдельные script/runner hashes и не содержит mutation mode.
Install executor не принимает observation, не связанный вторым approval.

Read-only означает отсутствие remote filesystem writes, включая скрытые temporary
files и Python bytecode. Collector передаёт программы и bounded data только через
pipes/in-memory arguments, не использует heredoc/here-string/temp files, запускает
Python isolated с `-I -B`, не вызывает Docker CLI (socket activation считается
mutation) и создаёт protected local evidence с private ACL уже в момент создания.

Remote executor сначала работает только в режиме `precondition`. Он обязан проверить и записать evidence:

- evidence run 009 имеет SHA-256 `8D8A4E155B30C4B72C564056C71B159E222C53E3BDC60018C3F6099C1979E1A8`;
- текущая baseline projection равна run 009;
- OS family/release, architecture и kernel совместимы с bound binaries/images;
- версия Python совместима с wheelhouse;
- свободны disk bytes, inodes и available memory с заданным запасом;
- отсутствуют Docker и package-owned resources;
- отсутствуют пересечения interface/address/route/CIDR;
- свободны `127.0.0.1:3031` и `UDP/30001`;
- nftables backend и исходные rules соответствуют bound baseline;
- все package member hashes и manifest signature/checksum корректны.

Любое расхождение завершает executor до mutation. Precondition evidence имеет собственный canonical SHA-256 и входит в exact live approval receipt.

## 5. Воспроизводимый package contract

Package archive включает только перечисленные manifest entries:

- runtime-only archive авторитетного AMN2 source;
- external canonical Git tree inventory: path/mode/blob OID каждого runtime member,
  проверяемый повторным вычислением Git blob IDs из archive bytes;
- Linux x86_64 CPython wheelhouse и hash-locked requirements;
- checksum-bound Docker runtime bundle;
- exact Docker archive digest и per-binary ELF/hash inventory;
- checksum-bound AWG image archive, raw OCI index/platform/config blobs и их
  index/platform/config/layer/diff-ID cross-binding;
- systemd units и environment templates;
- server config template без secrets;
- installer, verifier и rollback scripts;
- immutable resource plan;
- run 009 baseline reference и canonical fingerprint array;
- provenance receipt и полный SHA-256 inventory.

Запрещены network downloads на Spain во время install. Запрещены floating tags, `latest`, package-manager updates и непроверенные curl-pipelines.

Archive SHA не может включать сам себя. Поэтому exact approval связывает отдельно:

- package archive SHA-256;
- remote executor SHA-256;
- manifest/resource-plan SHA-256;
- source commit и runtime archive SHA-256;
- Docker bundle SHA-256;
- AWG image index/platform/config digests и image archive SHA-256;
- wheel lock and wheelhouse inventory SHA-256;
- run 009 evidence SHA-256;
- canonical fingerprint-array SHA-256.

Filename, tag, declared version или provenance JSON сами по себе не доказывают
содержимое. Verifier отклоняет duplicate/special archive members, неполный Git tree,
Docker binary drift и docker-save, который нельзя связать с приложенными raw OCI
manifest blobs.

## 6. Bootstrap, install state machine и rollback

Package staging само является первой live mutation и поэтому не может выполняться
executor'ом, уже лежащим внутри package. Отдельный checksum-bound bootstrap
executor получает по stdin exact approval binding, выполняет последний critical
read-only recheck, под global lock атомарно записывает retained one-time
authorization tombstone и только затем принимает package bytes. Tombstone входит
в объявленный audit delta, переживает rollback и не позволяет повторно использовать
nonce даже после неудачной установки.

Стадии имеют monotonic journal и fsync'ed mutation ledger:

1. `authorization_validated` (read-only);
2. `critical_recheck_passed` (read-only, под lock);
3. `authorization_consumed` (retained tombstone, первый write);
4. `package_staged`;
5. `package_verified_remote` (same open descriptor/immutable bytes);
6. `identity_created`;
7. `filesystem_staged`;
8. `secrets_configs_rendered`;
9. `clean_db_initialized`;
10. `units_installed`;
11. `docker_started`;
12. `awg_image_loaded`;
13. `network_container_started`;
14. `host_network_applied`;
15. `web_started` (bot остаётся static/inactive);
16. `postinstall_verified`.

До `authorization_consumed` mutation запрещена. Для каждого mutation object ledger
сначала fsync'ит `intent` с ожидаемой semantic identity, затем выполняет bounded
operation и fsync'ит `committed`. Rollback/recovery обязаны reconcile и committed,
и незавершённый intent: crash между syscall и journal append не может оставить
неучтённый объект. Все filesystem операции используют no-follow ancestor walk;
command argv закрыты, без shell, с timeout/output bounds. Предсуществующий объект
никогда не присваивается AMN2 и не удаляется.

Создание fixed service identity меняет глобальные passwd/group/shadow databases.
Это явно объявленный semantic identity-db delta, а не обещание byte-equality этих
файлов. Rollback удаляет только exact UID/GID/name при совпадении ledger identity;
любая drift вызывает fail-closed manual recovery. Альтернатива DynamicUser должна
быть принята отдельно, если live OS не позволяет безопасный fixed identity.

Rollback считается успешным только если:

- AMN2-owned delta отсутствует;
- все 148 baseline entries равны;
- firewall projection равна;
- исходные listeners/routes/addresses равны;
- посторонний Spain-сервис имеет тот же canonical receipt.

## 7. Runtime safety на install gate

- AWG разрешено запустить один раз как часть install; тесты не должны его останавливать или перезапускать.
- БД создаётся пустой; старые USA records отсутствуют.
- `VPS_APPLY_ENABLED=false`.
- bot unit installed, но disabled/stopped.
- web слушает только `127.0.0.1:3031`.
- web bootstrap secrets генерируются локально на Spain, права `0600`, значения не попадают в logs/evidence.
- конфиг AWG не содержит peers.

### 7.1 Dedicated runtime topology

Spain не получает system-wide package-manager Docker. Exact static Docker bundle
разворачивается под `/opt/amn2-spain/docker` и запускается отдельным unit с:

- socket `/run/amn2-spain-docker/docker.sock`;
- data root `/var/lib/amn2-spain-docker`;
- default bridge disabled;
- automatic Docker iptables/ip-masquerade/ip-forward mutations disabled;
- dedicated exec root и pid file;
- единственным package-owned image/container/network.

Daemon запускается только с exact dedicated socket/data/exec/pid paths и
`--bridge=none --iptables=false --ip6tables=false --ip-forward=false
--ip-masq=false --userland-proxy=false`. Built-in/default Docker bridge или
Docker-owned firewall delta являются verification failure.

AWG запускается непосредственно из checksum-bound
`amneziavpn/amneziawg-go@sha256:3c78...` platform image; derived floating build
не используется. Package-owned start script и server config монтируются каталогом,
чтобы последующий broker мог выполнять atomic same-directory replace.

User-defined bridge `amn2spbr0` использует `172.29.251.0/28`; container получает
`172.29.251.2`. Поскольку Docker firewall automation отключена, UDP/30001 DNAT,
bridge forward и outbound NAT задаются только в sealed nft namespace
`inet amn2_spain`: отдельные base chains `prerouting`/`dstnat`,
`forward`/`filter` и `postrouting`/`srcnat` с exact rules. Host route
`10.212.12.0/24 via 172.29.251.2 dev amn2spbr0` также package-owned. Resource confirmation обязан доказать, что foreign base-chain
policies/rules не перекроют этот закрытый contour; иначе install остаётся NO-GO.
Запрещено вставлять AMN2 rules в существующие foreign tables/chains. IPv4
forwarding сохраняется как explicit ledger mutation с предыдущим значением и exact
rollback.

Nft table, route и sysctl должны переживать reboot через
`amn2-spain-network.service` с idempotent boot-id-aware apply/verify и CAS rollback.
Без этого unit install остаётся NO-GO: работающий до первого reboot contour не
считается production install.

AWG config создаётся на Spain: X25519 keypair генерируется authoritative AMN2
key API после offline import smoke; private key не покидает host, public key
записывается в generated `servers.yml`, peers отсутствуют. Clean DB создаётся через
AMN2 schema, затем проверяются `integrity_check=ok`, пустой `foreign_key_check`,
включённый `foreign_keys` и нулевые counts всех application-data tables, включая
users/devices/servers/admin issuance. Default plans/server не seed'ятся.

AWG container использует exact config image digest, package-owned PID 1 start
script (`awg-quick up`, health verify, TERM trap/down, wait), read-only rootfs,
`CAP_DROP=ALL`, только `NET_ADMIN`, `/dev/net/tun`, writable `/run` tmpfs,
read-only config bind, fixed bridge IP и restart policy. Tests никогда не вызывают
`docker restart`.

Web unit запускает `/usr/bin/python3 -m app.cli web serve --host 127.0.0.1
--port 3031`. Python dependencies разворачиваются offline в private site-packages
из hash-bound wheels без pip/venv/network. Bot unit использует `-m app.main`, но не
имеет enable marker/WantedBy и остаётся stopped. Required secrets для загрузки
Settings/web генерируются локально, права `0600`, значения не выводятся; временный
web password уничтожается и будет заменён отдельным operator credential gate.

## 8. No-restart Docker peer lifecycle

Перед включением issuance gate текущий `docker restart` должен быть заменён внутри
typed AF_UNIX broker. Попытка реализовать transaction цепочкой независимых SSH
commands отклонена: она не даёт общей lock/CAS scope и может затереть concurrent
success. Install gate сохраняет authoritative source
`55dc243b8e6c6bdb57f8301b56326e4cd4072d19`, `VPS_APPLY_ENABLED=false` и
stopped/disabled bot; peer write path на этом gate недостижим и AWG не
останавливается тестами.

Apply transaction:

1. прочитать persistent config;
2. проверить network и отсутствие IP/key collision;
3. подготовить новый config;
4. атомарно записать его через temporary file, permissions, fsync и rename;
5. выполнить live `awg set <interface> peer ...` внутри exact container; PSK передать только через stdin-backed `0600` temporary file;
6. проверить `awg show <interface> dump` на exact key/allowed IP;
7. при live/verify failure атомарно вернуть исходный config и удалить partially applied live peer;
8. никогда не вызывать `docker restart`.

Revoke transaction аналогично удаляет peer live через `awg set ... remove`, проверяет отсутствие и при ошибке восстанавливает persistent config. Сообщение об ошибке должно различать clean rollback и partial rollback failure; secrets всегда redacted.

## 9. Отдельный issuance gate

Install gate не разрешает ambient SSH bot write path. Перед включением bot/VPS writes нужен root-owned typed broker по AF_UNIX:

- closed operations: `status`, `list_ips`, `apply_peer`, `revoke_peer`;
- exact container/interface/config binding;
- peer inputs валидируются как typed data;
- отсутствует arbitrary command/shell surface;
- socket ACL разрешает только AMN2 service identity;
- durable config, live apply, verify и compensation выполняются broker'ом;
- отдельные security review, tests, commit/push и exact live approval.

До принятия этого gate `VPS_APPLY_ENABLED` остаётся `false`, bot остаётся stopped/disabled, список получателей у оператора не запрашивается.

## 10. Acceptance текущего package gate

Перед запросом exact read-only resource-confirmation approval должны быть готовы:

- все artifacts и checksums;
- offline clean-room package verification;
- unit/integration tests install verifier и rollback;
- scoped и full AMN2 tests;
- diff review и security review без незакрытых high/critical findings;
- synced status/evidence docs;
- commits pushed и origin readback равен локальным commits;
- один точный read-only approval text с bound collector/runner/package hashes и host scope.

Перед запросом exact install approval дополнительно должны быть готовы:

- protected resource-confirmation evidence и canonical receipt;
- current baseline fingerprint equality с run 009;
- observed distro/arch/Python/capacity/routes/addresses и conflict-free resources;
- docs/status sync, commit/push и origin readback этого receipt;
- exact install approval text с mutation scope и rollback rule.

До первого approval запрещён SSH. До второго approval запрещены upload, package
install и любые Spain mutations.
