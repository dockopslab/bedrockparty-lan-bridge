# Architecture

The public project and distribution name is `BedrockParty`.

## Topology

```text
Android -- RakNet UDP/19132 --> Python relay -----------+
                                                        +--> BDS LAN UDP/19132
Switch -- discovery/signaling UDP/7551 --> Go bridge   |
       -- WebRTC ICE UDP/50000 ----------> Go bridge ---+
```

The Go bridge terminates WebRTC and inbound Bedrock, then creates a Bedrock-over-RakNet connection to the BDS. Blindly forwarding `7551` to `19132` cannot work because they are different transports.

## RakNet relay

`bedrock-lan-proxy.py` answers `0x01/0x02` pings with a local `0x1c` advertisement and relays every other datagram through a per-client UDP session. This is the validated Android path. It does not implement IPv6/19133 or interpret RakNet session state.

## NetherNet bridge

`nethernet-bridge/main.go` uses the `go-nethernet` LAN listener, Pion for ICE/DTLS/SCTP, and `gophertunnel` for Bedrock login and packets. A wrapper suppresses periodic gophertunnel RakNet `PongData` so the exact NetherNet ServerData v6 advertisement is preserved, including its nonce and `transport_layer=2`.

Switch may send a self-signed LAN identity without XUID or `DisplayName`. The image applies a minimal, versioned gophertunnel patch that accepts only that offline case. Before the outbound login, the bridge trims and validates `ClientData.ThirdPartyName`. If it is absent or invalid, the bridge creates a deterministic `Switch…` fallback of at most 14 characters. This fallback never applies to an identity with an XUID.

All ICE sessions share `UDP/50000` through `UDPMux`, reducing the firewall surface and simplifying Docker networking.

After login and spawn, the relay uses `ReadBytes`/`Write` on serialized Bedrock packets. This preserves `SenderSubClient` and `TargetSubClient`, which are required for multiple local players on one Switch. Decoding and rewriting packets with `ReadPacket`/`WritePacket` previously reset those fields to zero.

## Linux production networking

`compose.yml` uses `network_mode: host`. Processes see the Linux host interfaces directly, no Docker port NAT is involved, and `NETHERNET_PUBLIC_IP` remains empty. The Linux firewall must allow only `UDP/19132`, `7551`, and `50000` from the LAN.

## Windows alternative

`compose.win.yml` publishes the three UDP ports through Docker Desktop bridge networking. Because ICE candidates originate inside Docker's `172.x` network, Pion replaces the address with `NETHERNET_PUBLIC_IP`, the Windows host LAN IPv4 address.

## Production/support separation

The root contains both Compose files and the public environment template. `proxy-bedrock/` contains production runtime and Dockerfiles. `support/` contains protocol tests, diagnostics, and the legacy deployment and is excluded from both image contexts.

Final images run as UID/GID `65532`, use read-only root file systems, drop every capability, and enable `no-new-privileges`.

## Validation boundary

Android gameplay, Switch WebRTC/login/spawn, two-player split-screen play, mixed Android/Switch cooperative play, Linux production, and the Windows alternative are physically validated. The proxy cannot replace Microsoft/Xbox authentication required by a BDS using `online-mode=true`.
