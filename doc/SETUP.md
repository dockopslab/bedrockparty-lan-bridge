# Setup and operations

The main guide is [`../README.md`](../README.md). BDS means *Bedrock Dedicated Server*. Copy `.env.example` to `.env`, configure installation-specific values, and deploy production on Linux with `docker compose up --build -d`. The validated Windows alternative uses `docker compose -f compose.win.yml up --build -d`.

Physical compatibility was validated with Switch/BDS `1.26.44`/protocol `2168` and with Switch, Android, and BDS `1.26.45`/protocol `2169`. The current bridge uses `gophertunnel v1.61.0`. Discovery, login, gameplay, split-screen play, and mixed cooperative play are validated.

The tested Switch had an active Nintendo Switch Online subscription, but the connection is LAN-only and does not require Microsoft/Xbox accounts with `online-mode=false`. The test does not establish the Nintendo subscription as mandatory.

## Common ports and requirements

- BDS reachable at `BACKEND_IP:19132/udp` on the LAN.
- `19132/udp`: RakNet discovery and sessions.
- `7551/udp`: NetherNet LAN discovery and signaling.
- `50000/udp`: multiplexed NetherNet ICE/WebRTC.
- Every port restricted to the LAN and never exposed to the Internet.

## BDS requirements for account-free LAN play

Keep LAN play enabled and set:

```properties
online-mode=false
allow-list=false
```

Restart the BDS. Offline mode disables Microsoft/Xbox identity verification, not LAN multiplayer. It permits name impersonation, so the proxy and BDS must remain on a trusted LAN.

`allow-list=false` prevents an Xbox-identity allow list from blocking offline clients. If access control is required, design one suitable for local identities before re-enabling it.

### Authenticated alternative

A directly accessed BDS may use `online-mode=true` when every player is authenticated. The current bridge originates a new offline RakNet session and has no per-player Xbox `TokenSource`, so `online-mode=true` is not supported through the proxy.

## Linux production

Use a static address or DHCP reservation for the host or VM:

```bash
cp .env.example .env
sed -i 's/^NETHERNET_PUBLIC_IP=.*/NETHERNET_PUBLIC_IP=/' .env
docker compose up --build -d
docker compose ps
docker compose logs -f nethernet-bridge
```

Linux host networking needs no Docker port mapping or ICE candidate replacement. If UFW is active, adapt the subnet:

```bash
sudo ufw allow from 192.168.1.0/24 to any port 19132 proto udp
sudo ufw allow from 192.168.1.0/24 to any port 7551 proto udp
sudo ufw allow from 192.168.1.0/24 to any port 50000 proto udp
```

Use equivalent nftables or firewalld rules when appropriate. Check port ownership first with `ss -lunp`.

## Windows alternative

1. Find the host LAN address with `ipconfig`.
2. Copy `.env.example` to `.env` and assign that address to `NETHERNET_PUBLIC_IP`.
3. Install the LAN-scoped Windows Firewall rule as administrator.
4. Start the bridge-network Compose deployment.

```bat
copy .env.example .env
notepad .env
powershell -ExecutionPolicy Bypass -File proxy-bedrock\scripts\install-windows-firewall.ps1
docker compose -f compose.win.yml up --build -d
docker compose -f compose.win.yml ps
docker compose -f compose.win.yml logs -f nethernet-bridge
```

If DHCP changes the Windows host address, update `NETHERNET_PUBLIC_IP` and recreate `nethernet-bridge`.

## Diagnostics

```bash
docker compose ps
docker compose logs --tail 100 nethernet-bridge
python support/diagnostics/query-nethernet-discovery.py --target PROXY_LAN_IP
python support/diagnostics/query-bedrock-broadcast.py --target 192.168.1.255
```

Important log messages:

- `NetherNet client connected`: ICE/WebRTC completed.
- `connect to Bedrock backend`: WebRTC worked, but BDS/RakNet failed.
- `Bedrock session bridged`: login, spawn, and bidirectional relay completed.
- `NotAuthenticated`: verify effective BDS `online-mode=false` and restart the correct process.
- `ICE transport entered unrecoverable state`: the current UDP path was lost; reconnect and investigate Wi-Fi only if it recurs.

## Removal

Linux:

```bash
docker compose down
```

Windows:

```powershell
docker compose -f compose.win.yml down
powershell -ExecutionPolicy Bypass -File proxy-bedrock\scripts\remove-windows-firewall.ps1
```
