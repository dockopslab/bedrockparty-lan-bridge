# BedrockParty production package

BedrockParty publishes a Bedrock Dedicated Server (BDS) as a LAN world for Android and Nintendo Switch. BDS means *Bedrock Dedicated Server*, the standalone Minecraft Bedrock server. The production deployment uses Docker Engine on Linux; Docker Desktop on Windows is a validated alternative.

> **NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.**

This independent interoperability project is intended only for lawful use with genuine, lawfully acquired game copies and properly licensed hardware, software, and services. See [`../LEGAL.md`](../LEGAL.md).

The Compose files and `.env.example` live at the repository root. Run all commands from that directory. The complete user guide is [`../README.md`](../README.md).

## Production architecture

```text
Android -- RakNet UDP/19132 ---------+
                                      +--> Bedrock Dedicated Server
Switch  -- NetherNet UDP/7551 -------+
        -- WebRTC/ICE UDP/50000 -----+
```

This directory contains only runtime code, Dockerfiles, the health check, and firewall scripts. Diagnostics, protocol experiments, tests, and the pre-Docker deployment live in [`../support/`](../support/README.md). Go tests remain beside the package because they run during the image build, but they are not copied into the final image.

## Validated state

- Android discovers `BedrockParty`, joins the BDS, and supports gameplay.
- Nintendo Switch discovers the world, completes NetherNet/WebRTC, joins, and plays.
- Two local players can play simultaneously in split-screen mode on one Switch.
- Cooperative play was validated with multiple Android devices and both local Switch players.
- The tested Switch had an active Nintendo Switch Online subscription. The bridge does not determine or change platform entitlement, account, or subscription requirements.
- The validated LAN scenario used `online-mode=false`, so the BDS did not verify Microsoft/Xbox identities through the bridge.
- Linux/Docker Engine with host networking is the physically validated production deployment.
- Docker Desktop on Windows is a validated alternative with LAN-scoped UDP ports.
- Full validation covers `1.26.44-Switch`/protocol `2168` and Switch, Android, and BDS `1.26.45`/protocol `2169`.
- The current bridge uses `gophertunnel v1.61.0`.
- The Android relay keeps the historical `1.26.32`/protocol `1001` discovery text; it does not represent the actual client or BDS version.

## Requirements

- Docker Engine with Compose on Linux, or Docker Desktop with Linux containers on Windows.
- Proxy, clients, and BDS on the same trusted LAN.
- The BDS reachable through UDP from the proxy host.
- Free `19132`, `7551`, and `50000/udp` ports.
- `online-mode=false` on the trusted-LAN BDS for the currently supported local identity flow.

## Initial configuration

Linux:

```bash
cp .env.example .env
nano .env
```

Windows:

```bat
copy .env.example .env
notepad .env
```

Always review `BACKEND_IP`, `NETHERNET_PUBLIC_IP`, `SERVER_GUID`, and `NETHERNET_SERVER_ID`. Both identifiers must be equal and remain stable. The local `.env` file is excluded from Git.

## Production deployment on Linux

Leave `NETHERNET_PUBLIC_IP` empty and run:

```bash
docker compose up --build -d
```

Linux uses `network_mode: host`. The bridge sees the VM interfaces directly, so Docker NAT and ICE candidate replacement are unnecessary. Restrict `19132`, `7551`, and `50000/udp` to the LAN in UFW, nftables, or firewalld.

## Alternative deployment on Windows

Run PowerShell as administrator once, adjusting the subnet, and then deploy:

```powershell
powershell -ExecutionPolicy Bypass -File proxy-bedrock\scripts\install-windows-firewall.ps1 -LanSubnet 192.168.1.0/24
```

```bat
docker compose -f compose.win.yml up --build -d
```

Compose publishes `19132`, `7551`, and `50000/UDP`. Set `NETHERNET_PUBLIC_IP` to the current Docker host LAN address so Pion advertises it instead of the container's `172.x` bridge address.

The firewall rule covers both Public and Private profiles but accepts traffic only from the selected LAN subnet.

## Important variables

| Variable | Example | Purpose |
|---|---:|---|
| `LISTEN_PORT` | `19132` | Published and listened UDP port |
| `BACKEND_IP` | `192.168.1.10` | Real BDS LAN address |
| `BACKEND_PORT` | `19132` | BDS UDP port |
| `MOTD` / `SUB_MOTD` | `BedrockParty` | RakNet advertisement |
| `PROTOCOL` / `VERSION` | `1001` / `1.26.32` | Historical Android discovery values |
| `SERVER_GUID` | stable value | RakNet advertisement identity |
| `NETHERNET_PORT` | `7551` | Switch discovery and signaling |
| `NETHERNET_LEVEL_NAME` | `BedrockParty` | World name shown on Switch |
| `NETHERNET_PUBLIC_IP` | host LAN IP | Docker Desktop only; empty on Linux |
| `NETHERNET_ICE_PORT` | `50000` | Multiplexed WebRTC port |
| `LOG_LEVEL` | `INFO` | Bridge log level |

`IPV6_PORT=19133` is currently only an advertisement field. This release listens on IPv4 `19132` and does not implement an IPv6 socket.

## BDS authentication modes

For the currently supported trusted-LAN identity flow, keep LAN play enabled and configure:

```properties
online-mode=false
allow-list=false
```

Restart the BDS. This setting affects BDS identity verification only; it does not grant a game license or waive platform, account, subscription, or entitlement requirements. Every player must use a genuine, lawfully acquired copy of Minecraft. Offline mode permits name impersonation, so neither the BDS nor proxy may be exposed to the Internet.

A directly accessed BDS may use `online-mode=true` when all players authenticate. The current bridge terminates NetherNet and originates a new offline RakNet session. It has no per-player Xbox `TokenSource`, so `online-mode=true` is not supported through this bridge.

## Operations

```bash
docker compose ps
docker compose logs --tail 100
docker compose up --build -d
```

On Windows, add `-f compose.win.yml` after `docker compose`.

A successful Switch join produces:

```text
NetherNet client connected
Bedrock session bridged
```

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

## Security

- Never forward `19132`, `7551`, or `50000/udp` on the router.
- Limit the firewall to the real LAN subnet.
- Keep `.env` out of Git.
- Use `online-mode=false` only on a trusted LAN.
- Both containers run without root, capabilities, or writable root file systems.

## Validation summary

- Android: discovery, join, gameplay, and cooperative play.
- Nintendo Switch: discovery, ICE/DTLS/SCTP, join, gameplay, and two-player split-screen play.
- Linux/Docker Engine: validated production deployment with host networking.
- Windows/Docker Desktop: validated alternative with LAN ICE candidate publication.
