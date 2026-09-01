# BedrockParty project context

## Overview

BedrockParty publishes the BDS configured in `.env` as a LAN world. Android uses classic RakNet. Nintendo Switch discovers the world through NetherNet on `UDP/7551` and then establishes WebRTC over `UDP/50000`. The project requires no alternate DNS or featured-server replacement.

The root [`README.md`](../README.md) is the operational entry point. It covers BDS configuration, environment variables, firewall rules, Linux production, the Windows alternative, verification, troubleshooting, and links to technical documentation.

The maintainer developed the project in collaboration with AI agents. `CHANGELOG_AI.md` records that assistance; functional decisions and physical validation remain subject to human review and confirmation.

## Technology stack

- Python 3.13 without external runtime dependencies for RakNet discovery and relay.
- Go 1.25, `gophertunnel v1.61.0`, `go-nethernet v1.0.20`, and Pion WebRTC/ICE for Switch.
- Docker Compose with Linux host networking in production and published bridge ports on Windows.

## Repository structure

- `proxy-bedrock/bedrock-lan-proxy.py`: RakNet discovery and relay.
- `proxy-bedrock/nethernet-bridge/`: NetherNet signaling, WebRTC, and Bedrock proxy.
- `proxy-bedrock/scripts/`: health check and Windows Firewall management.
- `compose.yml`: default Linux production deployment.
- `compose.win.yml`: Windows Docker Desktop alternative.
- `.env.example`: sanitized configuration template.
- `.github/workflows/ci.yml`: tests, Compose validation, and image builds.
- `CHANGELOG.md`: public release history and compatibility contract.
- `LICENSE`, `LEGAL.md`, `THIRD_PARTY_NOTICES.md`, `CONTRIBUTING.md`, and `SECURITY.md`: public project policies and compliance material.
- `proxy-bedrock/third_party_licenses/`: exact dependency license and NOTICE files packaged in the NetherNet image.
- `support/`: diagnostics, tests, and legacy reference outside production.
- `doc/`: persistent technical memory.

## Execution flow

### Android / RakNet

1. The client queries `UDP/19132`.
2. The Python relay returns the historical Android-compatible advertisement.
3. Every non-discovery datagram is relayed transparently to the BDS through a per-client session.

### Switch / NetherNet

1. Switch queries `UDP/7551`; the bridge answers with encrypted ServerData v6.
2. The same port exchanges NetherNet SDP/ICE signaling.
3. ICE, DTLS, and SCTP use the multiplexed `UDP/50000` port.
4. gophertunnel accepts the self-signed LAN login and opens a RakNet connection to the BDS.
5. Serialized Bedrock packets are relayed in both directions without losing split-screen headers.

## Current validated state

On 2026-08-26, Switch `1.26.44`/protocol `2168` completed discovery, join, gameplay, and two-player split-screen play.

On 2026-08-31, BDS, Switch, and Android were updated to `1.26.45`/protocol `2169`. Android continued working because its relay is transparent. Switch initially failed because `gophertunnel v1.59.0` expected protocol `2168`. Updating to `v1.61.0` restored discovery, login, gameplay, split-screen play, and mixed cooperative play with multiple Android participants.

The tested Switch had an active Nintendo Switch Online subscription. BedrockParty neither determines nor changes account, entitlement, or subscription requirements. The validated path is LAN-only and uses `online-mode=false` for BDS identity handling; all players must still own a genuine copy and comply with the applicable platform terms.

Switch may omit the main player's `IdentityData.DisplayName` while retaining the local name in `ClientData.ThirdPartyName`. The deployed fallback validates and forwards that local name only for an offline identity without XUID. Logs confirmed the expected local name and a subsequent `Bedrock session bridged`.

Linux/Docker Engine with host networking is the physically validated production deployment. Windows/Docker Desktop remains a validated alternative.

Public source releases use `bedrock-<Minecraft version>-r<project revision>`. The first compatibility release is `bedrock-1.26.45-r1`; no prebuilt images are published by the current workflow.

## Known limitations

- Confirm that `online-mode=false` persists after every BDS restart.
- `server.properties` belongs to the external BDS and cannot be changed by the proxy.
- Online mode through the bridge is unsupported without per-player upstream Xbox authentication.
- The NetherNet TOFU identity is regenerated at bridge startup.
- On Windows, DHCP changes require updating `NETHERNET_PUBLIC_IP`.
- The RakNet relay retains the historical `1001 / 1.26.32` discovery advertisement.
- One isolated ICE transport loss was observed; the console renegotiated successfully without restarting containers. Add deeper instrumentation only if it recurs.

## Important commands

```bash
# Linux production
docker compose up --build -d
docker compose ps
docker compose logs -f nethernet-bridge
```

```bat
REM Windows alternative
docker compose -f compose.win.yml up --build -d
docker compose -f compose.win.yml ps
docker compose -f compose.win.yml logs -f nethernet-bridge
```
