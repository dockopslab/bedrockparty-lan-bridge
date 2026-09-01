# BedrockParty

BedrockParty publishes a **Bedrock Dedicated Server (BDS)** as a LAN world for Android and Nintendo Switch. BDS means *Bedrock Dedicated Server*: the standalone Minecraft Bedrock server application, which runs without a player hosting the world from the game.

> **NOT AN OFFICIAL MINECRAFT PRODUCT. NOT APPROVED BY OR ASSOCIATED WITH MOJANG OR MICROSOFT.**

BedrockParty is an independent interoperability project and is not affiliated with Mojang, Microsoft, or Nintendo. It is intended only for lawful use with genuine, lawfully acquired copies of Minecraft Bedrock and properly licensed hardware, software, and services. Read [Legal and responsible use](LEGAL.md) before deploying or redistributing it.

The project combines a transparent RakNet relay with a NetherNet/WebRTC bridge. The production deployment is `compose.yml` on Linux with Docker Engine and host networking. `compose.win.yml` provides a validated Docker Desktop alternative for Windows.

## Validated play scenario

The most complete physical test used **Minecraft Bedrock 1.26.45, protocol 2169** on the BDS, Nintendo Switch, and Android devices:

- Nintendo Switch with an active Nintendo Switch Online subscription. BedrockParty neither determines nor changes platform entitlement, account, or subscription requirements.
- LAN-only play with BDS identity verification disabled through `online-mode=false`; the bridge did not use Microsoft/Xbox authentication in this test.
- Two local split-screen players on the same Nintendo Switch.
- Simultaneous cooperative play with multiple Android participants and both local Switch players in the same world.

For Android compatibility, the RakNet relay still advertises the historical `1.26.32`/protocol `1001` discovery values. Those fields describe the relay advertisement and do not change the real `1.26.45` version negotiated with the BDS.

## What it provides

- Publishes the BDS as a LAN world named `BedrockParty`.
- Serves Android clients through RakNet on `UDP/19132`.
- Serves Nintendo Switch through NetherNet on `UDP/7551` and WebRTC/ICE on `UDP/50000`.
- Converts a Switch NetherNet session into a Bedrock/RakNet connection to the BDS.
- Preserves Bedrock subclient headers required for split-screen play.
- Supports a trusted-LAN BDS configured with `online-mode=false`; this changes local identity verification only and does not waive game ownership or platform requirements.
- Requires no alternate DNS, featured-server replacement, or Internet exposure.

## Architecture

```text
Android -- RakNet UDP/19132 ---------+
                                      +--> BDS UDP/19132
Switch  -- NetherNet UDP/7551 -------+
        -- WebRTC/ICE UDP/50000 -----+
```

The `proxy` service answers RakNet discovery and transparently relays Android datagrams. The `nethernet-bridge` service terminates ICE, DTLS, SCTP, and Bedrock over NetherNet, opens a RakNet session to the BDS, and relays serialized Bedrock packets without losing split-screen subclient identifiers.

## Validated compatibility

| Environment | Discovery | Join and play | Notes |
|---|:---:|:---:|---|
| Android / RakNet | Yes | Yes | Multiple devices tested cooperatively with Switch |
| Nintendo Switch | Yes | Yes | NetherNet, WebRTC, login, and spawn completed |
| Switch split-screen play | N/A | Yes | Two local players, including cooperative Android play |
| Linux / Docker Engine | Yes | Yes | Production deployment using host networking |
| Windows / Docker Desktop | Yes | Yes | Validated alternative using published UDP ports |

### Tested Minecraft versions

- **Nintendo Switch:** discovery, join, gameplay, and two local players were validated on `1.26.44-Switch`/protocol `2168` and `1.26.45`/protocol `2169`.
- **BDS:** Minecraft Bedrock `1.26.45`, protocol `2169`.
- **Android/RakNet:** discovery, join, and cooperative play were validated with physical Android devices on Minecraft Bedrock `1.26.45`.
- **Bridge:** `gophertunnel v1.61.0`, which implements Bedrock `1.26.45`/protocol `2169`.

Compatibility applies to the tested versions only. After updating Minecraft, the BDS, or gophertunnel, repeat discovery, join, gameplay, and split-screen validation.

## Releases and versioning

Source releases use `bedrock-<Minecraft version>-r<project revision>`. The Bedrock version states the compatibility target; the revision permits BedrockParty fixes without inventing a new game version.

The current release is [`bedrock-1.26.45-r1`](https://github.com/dockopslab/bedrockparty-lan-bridge/releases/tag/bedrock-1.26.45-r1), targeting protocol `2169`. A tag-triggered workflow validates and publishes each GitHub Release. Releases contain source archives only; deployment builds the images locally with Docker Compose.

See the [release changelog](CHANGELOG.md) for validated scenarios, limitations, and upgrade notes. A new Bedrock version is not declared compatible until Compose validation, tests, image builds, and applicable physical-device checks have completed.

## Requirements

- A Bedrock Dedicated Server reachable on the LAN.
- Docker Engine with Compose on Linux, or Docker Desktop with Linux containers on Windows.
- The proxy host, BDS, and players on the same trusted local network.
- Free `UDP/19132`, `UDP/7551`, and `UDP/50000` ports on the proxy host.
- Firewall rules that allow those ports only from the LAN subnet.

## Repository layout

```text
compose.yml                production deployment for Linux / host network
compose.win.yml            Docker Desktop deployment for Windows
.env.example               shared configuration template
proxy-bedrock/             production source and Docker build context
  nethernet-bridge/        Go NetherNet/WebRTC -> RakNet bridge
  scripts/                 health check and Windows Firewall scripts
support/                   diagnostics, tests, and legacy reference
doc/                       architecture, decisions, history, and operations
.github/workflows/ci.yml   tests, Compose validation, and image builds
```

Runtime files are at the repository root so deployment does not require changing directories. `support/` is not copied into either production image.

## Configure the BDS

### Trusted-LAN BDS identity mode

Keep LAN play enabled and set the BDS `server.properties` file to:

```properties
online-mode=false
allow-list=false
```

Restart the BDS after editing the file. `online-mode=false` disables BDS online identity verification, not LAN multiplayer. It does not grant a Minecraft license or bypass any platform, account, subscription, or entitlement requirement. Every player must use a genuine, lawfully acquired copy of Minecraft and comply with the applicable terms. Because names are no longer verified, the BDS and proxy must remain on a trusted LAN and must never be exposed to the Internet.

### Play with Microsoft/Xbox accounts

A directly accessed BDS can use `online-mode=true` when every player is authenticated. The current bridge does not retain or acquire a separate upstream Xbox credential for each player, so `online-mode=true` is not currently supported through BedrockParty.

## Configure `.env`

On Linux:

```bash
cp .env.example .env
nano .env
```

On Windows from `cmd.exe`:

```bat
copy .env.example .env
notepad .env
```

Review every installation-specific value:

| Variable | Example | Purpose |
|---|---|---|
| `LISTEN_PORT` | `19132` | Published RakNet port |
| `BACKEND_IP` | `192.168.1.10` | BDS LAN IPv4 address |
| `BACKEND_PORT` | `19132` | BDS UDP port |
| `MOTD` / `SUB_MOTD` | `BedrockParty` | RakNet advertisement names |
| `PROTOCOL` / `VERSION` | `1001` / `1.26.32` | Historical Android discovery advertisement |
| `PLAYERS` / `MAX_PLAYERS` | `0` / `10` | Advertised occupancy |
| `GAMEMODE` / `GAMEMODE_NUM` | `Survival` / `1` | Advertised game mode |
| `IPV6_PORT` | `19133` | IPv6 field in the RakNet advertisement |
| `EXTRA_FIELDS` | `0;1;0` | Validated trailing RakNet fields |
| `SERVER_GUID` | uint64 | Stable RakNet advertisement identity |
| `SESSION_TIMEOUT` | `60` | Idle Android relay timeout in seconds |
| `LOG_DISCOVERY` | `false` | Detailed RakNet discovery logs |
| `NETHERNET_PORT` | `7551` | Switch discovery and signaling |
| `NETHERNET_SERVER_ID` | same uint64 | Stable NetherNet identity |
| `NETHERNET_SERVER_NAME` | `BedrockParty` | Server name shown on Switch |
| `NETHERNET_LEVEL_NAME` | `BedrockParty` | World name shown on Switch |
| `NETHERNET_GAME_TYPE` | `0` | Advertised Switch game type |
| `NETHERNET_PUBLIC_IP` | proxy LAN IP | Required on Docker Desktop; empty on Linux |
| `NETHERNET_ICE_PORT` | `50000` | Multiplexed WebRTC/ICE UDP port |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARN`, or `ERROR` |

`SERVER_GUID` and `NETHERNET_SERVER_ID` must be equal, unique to the installation, and stable across restarts. Generate a value with:

```bash
python -c "import secrets; print(secrets.randbits(63))"
```

## Production deployment on Linux

The Linux host or VM should use a static address or DHCP reservation. Leave this value empty:

```dotenv
NETHERNET_PUBLIC_IP=
```

Deploy from the repository root:

```bash
docker compose up --build -d
```

`compose.yml` uses `network_mode: host`, so Docker does not perform port NAT and ICE does not require candidate-address replacement.

Example UFW rules, adjusted to the real LAN subnet:

```bash
sudo ufw allow from 192.168.1.0/24 to any port 19132 proto udp
sudo ufw allow from 192.168.1.0/24 to any port 7551 proto udp
sudo ufw allow from 192.168.1.0/24 to any port 50000 proto udp
```

Use equivalent LAN-scoped rules for nftables or firewalld.

## Alternative deployment on Windows

### 1. Identify the host address

Run `ipconfig` and assign the Docker host LAN IPv4 address to `NETHERNET_PUBLIC_IP`. The bridge publishes that address as its ICE candidate instead of the container's private `172.x` address.

### 2. Install the firewall rule

Run PowerShell as administrator, adjusting the subnet:

```powershell
powershell -ExecutionPolicy Bypass -File proxy-bedrock\scripts\install-windows-firewall.ps1 -LanSubnet 192.168.1.0/24
```

The rule allows only `UDP/19132`, `UDP/7551`, and `UDP/50000` from the selected subnet on both Public and Private profiles.

### 3. Deploy

```bat
docker compose -f compose.win.yml up --build -d
```

## Verification

Linux:

```bash
docker compose ps
docker compose logs --tail 100
```

Windows:

```bat
docker compose -f compose.win.yml ps
docker compose -f compose.win.yml logs --tail 100
```

Expected state:

- `proxy`: `Up` and `healthy`.
- `nethernet-bridge`: `Up`.
- RakNet log: an `MCPE;BedrockParty;...` advertisement.
- NetherNet log: `BedrockParty NetherNet bridge ready`.
- Switch join: `NetherNet client connected`.
- Completed spawn: `Bedrock session bridged`.

Optional diagnostic tools live in [`support/diagnostics/`](support/diagnostics/):

```bat
python -m pip install -r support\requirements.txt
python support\diagnostics\query-bedrock-broadcast.py --target PROXY_IP --first --require-response
python support\diagnostics\query-nethernet-discovery.py --target PROXY_IP
```

## Routine operation

The examples below use the default Linux production Compose file. On Windows, add `-f compose.win.yml` after `docker compose`.

```bash
docker compose up --build -d
docker compose logs -f
docker compose restart
docker compose stop
docker compose down
```

Remove the Windows Firewall rule with:

```powershell
powershell -ExecutionPolicy Bypass -File proxy-bedrock\scripts\remove-windows-firewall.ps1
```

## Troubleshooting

### The world is not visible

- Confirm both containers are running.
- Confirm the active Windows network profile is covered by the firewall rule.
- Confirm the rule uses the correct LAN subnet.
- Check that no other process owns `19132`, `7551`, or `50000/udp`.
- On Windows, confirm `NETHERNET_PUBLIC_IP` matches the current host LAN address.

### Switch sees the world but cannot join

- Look for `NetherNet client connected`.
- If it is absent, inspect `UDP/50000` and `NETHERNET_PUBLIC_IP`.
- If the backend returns `NotAuthenticated`, verify `online-mode=false` and restart the BDS.
- Confirm `BACKEND_IP:BACKEND_PORT` is reachable from Docker.
- If an active session reports `ICE transport entered unrecoverable state`, reconnect. An isolated case normally indicates a temporary UDP path loss; repeated failures require checking Wi-Fi coverage, console sleep, and access-point events.

### Android cannot see the world

- Inspect `UDP/19132` and the host firewall profile.
- Confirm the `proxy` service is healthy.
- Compare the configured `MOTD`, `PROTOCOL`, and `VERSION` with the validated advertisement.

### TOFU prompt after recreating the bridge

The bridge currently generates a NetherNet identity at startup. A console may request trust confirmation after container recreation. Persisting this identity is tracked as a future improvement.

## Security

- Never forward `19132`, `7551`, or `50000/udp` on the router.
- Restrict firewall access to the LAN subnet.
- Never commit `.env`, packet captures, real addresses, player names, UUIDs, XUIDs, or credentials.
- Both containers run as UID/GID `65532`, with read-only root file systems, all capabilities removed, and `no-new-privileges`.
- Logs rotate across three 10 MB files and do not record gameplay payloads.
- Rebuild images regularly to receive base-image security updates.

## Project documentation

- [Project context](doc/PROJECT_CONTEXT.md)
- [Release changelog](CHANGELOG.md)
- [Architecture](doc/ARCHITECTURE.md)
- [Setup and operations](doc/SETUP.md)
- [Technical decisions](doc/DECISIONS.md)
- [Error history and regression playbook](doc/ERROR_HISTORY.md)
- [Security controls](doc/SECURITY.md)
- [Open work](doc/TODO.md)
- [AI-assisted change log](doc/CHANGELOG_AI.md)
- [Commit-history audit](doc/COMMIT_HISTORY.md)
- [Publishing guide](doc/PUBLISHING.md)
- [Production package](proxy-bedrock/README.md)
- [Support material](support/README.md)
- [Contributing](CONTRIBUTING.md)
- [Public security policy](SECURITY.md)
- [Legal and responsible use](LEGAL.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)

## AI development transparency

BedrockParty was developed by its maintainer in collaboration with artificial-intelligence agents. The agents contributed to protocol analysis, implementation, diagnosis, testing, and documentation; the maintainer directed and confirmed functional decisions and physical-device validation.

AI-assisted work is recorded in [`doc/CHANGELOG_AI.md`](doc/CHANGELOG_AI.md). AI assistance does not replace human review or deployment validation.

## License

Original BedrockParty code is distributed under the [MIT License](LICENSE). Third-party components retain their own licenses; see [Third-party notices](THIRD_PARTY_NOTICES.md). Minecraft, Microsoft, Xbox, Mojang, Nintendo, Nintendo Switch, and related marks belong to their respective owners and are used only to describe compatibility. See [Legal and responsible use](LEGAL.md).

## Project status

The Linux production deployment and the Windows Docker Desktop alternative have both been validated. The public tree contains a license, CI, contribution guidance, security policies, and sanitized examples.
