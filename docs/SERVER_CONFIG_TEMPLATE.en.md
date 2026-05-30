# Server Configuration Template

## Purpose

VPS data must be universal and replaceable. To connect a new server, the administrator fills in the server configuration, then provisioning can deploy AmneziaWG 2.0 on a new Debian VPS.

Secrets are not stored in the repository. Documentation and examples use placeholders only.

Provisioning must support two modes:

- `non-interactive` - reads a prepared `servers.yml`;
- `interactive` - asks for missing values and creates or updates `servers.yml`.

## Example `servers.yml`

Starter examples are available at:

- `deploy/examples/servers.host_systemd.example.yml`;
- `deploy/examples/servers.docker.example.yml`.

```yaml
servers:
  - name: "debian-vps-1"
    enabled: true
    location: "default"

    ssh:
      host: "CHANGE_ME_SERVER_IP_OR_DOMAIN"
      port: 22
      user: "CHANGE_ME_SSH_USER"
      auth:
        type: "key"
        private_key_path: "CHANGE_ME_PATH_TO_PRIVATE_KEY"

    vpn:
      endpoint_host: "CHANGE_ME_PUBLIC_IP_OR_DOMAIN"
      port: "auto"
      port_min: 30001
      port_max: 65535
      interface: "awg0"
      network_cidr: "10.8.0.0/24"
      server_address: "10.8.0.1/24"
      dns: "1.1.1.1"
      allowed_ips: "0.0.0.0/0"
      server_public_key: "CHANGE_ME_AWG_SERVER_PUBLIC_KEY"
      max_devices: 254

    firewall:
      provider: "ufw"
      open_vpn_port: true

    runtime:
      type: "host_systemd"
      service_name: "awg-quick@awg0"
```

## Multiple Servers

Add another item to `servers`.

```yaml
servers:
  - name: "debian-vps-1"
    location: "nl"
    vpn:
      network_cidr: "10.8.0.0/24"

  - name: "debian-vps-2"
    location: "de"
    vpn:
      network_cidr: "10.9.0.0/24"
```

Pools of different servers must not overlap.

## Pool Expansion

If more than 255 devices are expected on one server, choose a larger network in advance.

```yaml
vpn:
  network_cidr: "10.8.0.0/16"
  server_address: "10.8.0.1/16"
  max_devices: 65000
```

The MVP may start with `10.8.0.0/24`, but IPAM must work with CIDR, not with a fixed last octet.

## Environment Variables

```env
ACCESS_MODE=free_test
FREE_TEST_REQUIRES_APPROVAL=true
DEFAULT_PLAN_DAYS=7
MAX_DEVICES_PER_USER=5
CLIENT_DNS=1.1.1.1
CLIENT_ALLOWED_IPS=0.0.0.0/0
EXPIRATION_NOTICE_DAYS=7,5,3,1
VPN_PORT_MIN=30001
VPN_PORT_MAX=65535
VPN_SERVER_RUNTIME=host_systemd
```

## Values to Fill Later

- `ssh.host`;
- `ssh.port`;
- `ssh.user`;
- `ssh.auth.private_key_path` or another access method;
- `vpn.endpoint_host`;
- `vpn.server_public_key`;
- Telegram bot token;
- Telegram admin IDs.

If `ssh.auth.type: password` is selected, do not store the password in `servers.yml`. Store it only in `.env`:

```env
VPS_SSH_PASSWORD=CHANGE_ME_REAL_SSH_PASSWORD
```

Non-interactive password auth requires `sshpass` on the server running the bot/web panel. SSH key auth remains the preferred production option.

## Interactive Wizard

If `servers.yml` is missing or still contains `CHANGE_ME_*`, the setup script must offer interactive mode.

Minimum questions:

1. Server name.
2. Location or short server label.
3. SSH host/IP.
4. SSH port.
5. SSH user.
6. SSH access type: key or password.
7. SSH private key path if key access is selected.
8. Public endpoint for clients.
9. VPN UDP port: auto or manual.
10. VPN CIDR.
11. Server VPN address.
12. DNS.
13. Allowed IPs.
14. Whether to open the port in `ufw`.

After answers, the wizard must show a secret-free summary, request confirmation, save config, and run provisioning or show the provisioning command.

## Docker Runtime For The First VPS Test

If AmneziaWG already runs in a Docker container and is not managed through host `systemd`, set the runtime in `servers.yml` to `docker` and provide the container name:

```yaml
runtime:
  type: "docker"
  container_name: "amnezia-awg"
```

Docker runtime currently supports safe read-only checks only:

- Docker availability on the VPS;
- running container lookup by `container_name`;
- `awg` availability inside the container;
- `docker exec <container_name> awg show <interface>`;
- UDP port visibility through host `ss -lun`.

`apply-peer`, `revoke-peer`, and live `collect-traffic` intentionally do not change a Docker server yet and return a clear `not implemented yet` message. This stays blocked until the persistent AmneziaWG config path inside the container and the safe peer reload flow are confirmed.
