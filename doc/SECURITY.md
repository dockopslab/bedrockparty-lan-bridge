# Security controls

## Scope

The proxy exposes RakNet and NetherNet/WebRTC only on a private LAN and relays traffic to a BDS. It stores no accounts, passwords, or tokens. The listener accepts self-signed LAN authentication, so it must never be exposed to the Internet.

## Implemented controls

- Both images run as UID/GID `65532`, without root.
- Both services drop all capabilities, enable `no-new-privileges`, and use read-only root file systems.
- NetherNet dependencies are version-locked in `go.mod`.
- Only `UDP/19132`, `UDP/7551`, and multiplexed ICE `UDP/50000` are exposed.
- `.env`, packet captures, traces, decoded samples, private keys, and local archives are ignored.
- Windows Firewall rules restrict the three ports to the configured LAN subnet on Public and Private profiles.
- Logs rotate across three 10 MB files and do not record gameplay payloads.
- Compose requires `BACKEND_IP`, `SERVER_GUID`, and `NETHERNET_SERVER_ID`.
- The public tree contains only documentation addresses and sample identifiers.
- CI has read-only repository-content permission.

## Risks and operating rules

- Never forward proxy or BDS ports on the router.
- Review and sanitize packet captures before sharing them.
- Never run the legacy service and Docker deployment on the same host.
- On Windows, verify that `NETHERNET_PUBLIC_IP` is a LAN address.
- On Linux host networking, leave `NETHERNET_PUBLIC_IP` empty unless real NAT exists.
- Treat names, UUIDs, XUIDs, and device identifiers as private information.
- Rebuild images regularly to receive base-image fixes.
- For the supported local identity flow, keep LAN play enabled and use `online-mode=false`. This setting affects BDS identity verification only; it grants no license or entitlement and permits name impersonation, so it is acceptable only on a trusted LAN.
- A directly accessed BDS may use `online-mode=true` for authenticated players. The current bridge has no per-player upstream Microsoft/Xbox authentication and must not be used with `online-mode=true`.
- Do not present or use the proxy as a means to evade game ownership, accounts, subscriptions, access controls, or platform terms.
- The gophertunnel patch accepts an empty `DisplayName` only when XUID is also empty.
- `ClientData.ThirdPartyName` is unsigned. The bridge may use it only for an offline identity without XUID and only after offline-name validation.

## Review

- Owner: project maintainer.
- Last review: 2026-08-31.
- Next review: before changing authentication, identity handling, exposed ports, or base images.
