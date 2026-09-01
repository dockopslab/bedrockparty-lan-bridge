# Release changelog

All notable public releases of BedrockParty are documented here. Release identifiers follow `bedrock-<Minecraft version>-r<project revision>` so compatibility is explicit while allowing BedrockParty-only fixes for the same game version.

## bedrock-1.26.45-r1 - 2026-09-01

First public source release of BedrockParty, targeting **Minecraft Bedrock 1.26.45** and **protocol 2169**.

### Validated compatibility

- Bedrock Dedicated Server 1.26.45 / protocol 2169.
- Minecraft Bedrock 1.26.45 on physical Android devices.
- Minecraft Bedrock 1.26.45 on Nintendo Switch.
- Nintendo Switch discovery, NetherNet/WebRTC connection, join, spawn, and gameplay.
- Two local Nintendo Switch players in split-screen mode.
- Cooperative play with multiple Android players and both local Switch players.
- Linux with Docker Engine as the production deployment.
- Windows with Docker Desktop as a validated alternative.

The tested Nintendo Switch had an active Nintendo Switch Online subscription. BedrockParty neither determines nor changes platform account, entitlement, or subscription requirements. Every participant must use a genuine, lawfully acquired copy of Minecraft and comply with all applicable terms.

### Included

- RakNet LAN discovery and transparent relay for Android.
- NetherNet/WebRTC-to-RakNet bridge for Nintendo Switch.
- Preservation of serialized Bedrock subclient headers for split-screen play.
- Root-level Linux and Windows Compose deployments.
- LAN-scoped firewall guidance and hardened, non-root containers.
- Minecraft independence disclaimer, responsible-use terms, trademark notices, and packaged third-party license notices.

### Important configuration

- The current bridge path requires a trusted-LAN BDS configured with `online-mode=false` and `allow-list=false`.
- These settings affect BDS identity verification only; they do not grant game ownership, accounts, subscriptions, entitlements, or authorization to access third-party services.
- The proxy and BDS ports must never be exposed to the Internet.

### Known limitations

- Compatibility is asserted only for the versions and scenarios listed above.
- `online-mode=true` is not supported through the bridge because it has no per-player upstream Xbox authentication.
- The NetherNet TOFU identity is regenerated at bridge startup.
- The Android discovery advertisement retains validated historical `1.26.32` / protocol `1001` text while the real session negotiates 1.26.45 / protocol 2169 with the BDS.
- This release publishes source archives only. It does not publish prebuilt container images.

See [`README.md`](README.md), [`LEGAL.md`](LEGAL.md), and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md) before deployment or redistribution.
