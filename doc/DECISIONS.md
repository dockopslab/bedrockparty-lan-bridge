# Technical decisions

## 2026-09-01 - Publish source releases from validated tags

### Context

Creating releases manually would separate publication from the checks that establish build and packaging quality.

### Decision

Make CI reusable and trigger a dedicated release workflow from immutable `bedrock-*-r*` tags. The release job depends on CI success, extracts the matching English `CHANGELOG.md` section, and creates the GitHub Release with the repository token.

### Rationale

The tag, validation result, release notes, and source archives remain reproducible and linked to one commit without handling personal credentials or storing Docker images.

### Consequences

Tag pushes are the publication authority and require `contents: write` only in the release job. A malformed tag or missing changelog section fails safely before a release is created.

## 2026-09-01 - Version releases by Bedrock compatibility target

### Context

The bridge is protocol-sensitive and may require a new gophertunnel version or patch adjustment after a Bedrock update. A project-only correction may also be needed without a new Minecraft release.

### Decision

Use immutable source-release tags formatted as `bedrock-<Minecraft version>-r<project revision>`, beginning with `bedrock-1.26.45-r1` for protocol `2169`.

### Rationale

The tag identifies the tested game/BDS target while the independent revision avoids conflating BedrockParty fixes with official Minecraft versions.

### Consequences

Every compatibility release must document the protocol, dependency versions, tested devices, deployment environments, and limitations. The current release process publishes source archives, not container images.

## 2026-08-31 - Present local identity support as interoperability, not entitlement avoidance

### Context

The tested bridge uses BDS `online-mode=false`, and earlier documentation described the outcome mainly as play without Microsoft/Xbox accounts. That wording could incorrectly suggest that the project grants access or removes third-party licensing and platform obligations.

### Decision

Describe `online-mode=false` strictly as a trusted-LAN BDS identity setting. Require genuine game copies and compliance with all applicable account, subscription, entitlement, and platform terms. Add a prominent Minecraft independence disclaimer, trademark notices, responsible-use guidance, and a generated third-party license inventory.

### Rationale

The proxy performs protocol interoperability and local relaying; it does not provide software licenses, credentials, subscriptions, entitlements, or authorization to use third-party services.

### Consequences

Documentation must not market the project as an authentication or subscription bypass. Dependency and container-image licensing must be re-audited before each distributable release, and legal certainty still requires professional review.

## 2026-08-31 - Prepare a sanitized MIT-licensed initial publication

### Context

Development and diagnostics occurred on a real LAN. The private history contained operational addresses, stable identifiers, local player names, and initial material that was unnecessary for public operation.

### Decision

Publish only the sanitized final tree under the MIT License with `BedrockParty contributors` as the copyright holder. Consolidate experimental history into one initial public commit and retain a recoverable copy only in an ignored local bundle. Add CI, contribution guidance, a security policy, and a publishing guide.

### Rationale

This reduces accidental disclosure, provides a clear contributor baseline, and preserves local recovery without transferring private history.

### Consequences

Only `main` may be pushed publicly. Do not use `git push --all` or distribute `support/local-archive/`. Every installation must replace the examples in `.env.example`.

AI-agent collaboration is disclosed in the README and `CHANGELOG_AI.md`; it does not remove the requirement for human review and physical validation. Public documentation is maintained in English for broader accessibility.

## 2026-08-31 - Upgrade the bridge to Bedrock protocol 2169

### Context

After BDS and clients moved to Bedrock `1.26.45`, Android continued working through the transparent relay, but Switch failed during `RequestNetworkSettings`. Logs showed `expected 2168, got 2169` because the bridge used `gophertunnel v1.59.0`.

### Decision

Upgrade to `gophertunnel v1.61.0`, which declares Minecraft `1.26.45` and protocol `2169`. Reapply the narrowly scoped offline identity patch and test both offline acceptance and online rejection.

### Rationale

The bridge terminates and originates Bedrock, so it must support the exact protocol used by client and BDS. The Android relay does not decode the protocol and did not require this upgrade.

### Consequences

Every Bedrock protocol update requires checking gophertunnel support, applying the patch, running tests, and repeating physical Switch gameplay and split-screen validation. `ThirdPartyName` remains an unsigned offline-LAN fallback only.

## 2026-08-26 - Keep operational Compose files at the repository root

### Context

Deployment commands previously required entering an internal directory, and platform-specific filenames were inconsistent.

### Decision

Use `compose.yml` as the default Linux production deployment and `compose.win.yml` for Docker Desktop. Keep `.env.example` at the root and use `proxy-bedrock/` only as build context.

### Rationale

Root-level standard names make `docker compose up --build -d` the Linux production command while preserving explicit Windows behavior.

### Consequences

Documentation and automation must execute Compose from the root. Linux and Windows networking differences remain explicit.

## 2026-08-26 - Create a production BedrockParty distribution

### Context

The runtime directory accumulated captures, backups, prototypes, and legacy material during Switch research.

### Decision

Keep only production runtime in `proxy-bedrock/`; move diagnostics, tests, captures, and legacy deployment material under `support/`. Standardize names on `BedrockParty`, provide a configurable environment template, and harden containers.

### Rationale

A public deployment package must be understandable, reproducible, and free from experimental artifacts.

### Consequences

The build context is smaller, images contain no capture tools, and diagnostic workflows remain available outside production.

## 2026-08-25 - Preserve the working legacy relay behavior

### Context

The reconstructed Python proxy already worked for Android. Changing networking and protocol behavior simultaneously would obscure regressions.

### Decision

Containerize the existing per-client UDP relay first. Restrict initial changes to configuration, observability, tooling, and packaging.

### Rationale

This created a stable Android baseline before investigating Switch-specific differences.

### Consequences

The relay intentionally does not interpret RakNet state; complete behavior must be tested from a real client.

## 2026-08-25 - Use Linux host networking and Windows published ports

### Context

Docker Desktop does not give Linux containers direct layer-2 identity on the physical Wi-Fi network, while native Linux can expose host interfaces directly.

### Decision

Use `network_mode: host` in production on Linux. Keep a separate Windows Compose file with published UDP ports and ICE candidate address replacement.

### Rationale

Both environments passed physical tests. Host networking avoids NAT and candidate rewriting on Linux; Docker Desktop requires bridge publication.

### Consequences

The host address is visible to clients, and only one process may bind each UDP port. Linux is the production target; Windows remains a validated alternative.

## 2026-08-25 - Keep the historical Android advertisement

### Context

The legacy relay advertised `1001 / 1.26.32` and already worked with Android, while the real BDS version differed.

### Decision

Keep those values configurable and retain them as defaults until a controlled Android discovery change is validated.

### Rationale

Changing a working advertisement without evidence would add risk unrelated to Switch support.

### Consequences

Documentation must clearly distinguish the RakNet discovery text from the actual client/BDS protocol version.

## 2026-08-25 - Restrict firewall rules to the LAN on both profiles

### Context

Local health checks worked, but mobile devices could not reach the proxy because the Wi-Fi connection was classified as Public while the rule covered only Private.

### Decision

Allow the required UDP ports from the configured LAN subnet on both Public and Private Windows profiles.

### Rationale

The profile label should not break LAN discovery, but the rule must remain source-restricted.

### Consequences

The script requires administrative privileges and a correct subnet. The ports remain inaccessible from outside that LAN.

## 2026-08-26 - Separate classic RakNet from NetherNet

### Context

Android discovered the RakNet relay on `19132`, while Switch discovered Android-hosted worlds through NetherNet on `7551`.

### Decision

Keep the Python RakNet relay unchanged and add a separate Go NetherNet/WebRTC bridge.

### Rationale

RakNet and NetherNet use different discovery and session transports. A dedicated bridge avoids destabilizing Android.

### Consequences

The deployment has two services and three UDP ports. Switch uses `7551` and `50000`; Android remains on `19132`.

## 2026-08-26 - Multiplex ICE through one UDP port

### Context

Dynamic ICE ports complicate Docker publication and firewall scope.

### Decision

Use Pion `UDPMux` and bind all ICE sessions to `NETHERNET_ICE_PORT`, default `50000/udp`.

### Rationale

One explicit port is easier to secure, publish, and migrate.

### Consequences

The port must be free. On Windows, `NETHERNET_PUBLIC_IP` replaces the container address; Linux host networking requires no replacement.

## 2026-08-26 - Keep Windows and Linux networking explicit

### Context

The validated Windows host used Docker Desktop NAT, while production Linux uses native host networking.

### Decision

Maintain two small Compose files sharing the same environment variables instead of hiding platform differences in scripts.

### Rationale

Explicit platform configuration is easier to audit and troubleshoot than conditional networking logic.

### Consequences

Windows uses published ports and a configured public LAN candidate. Linux uses host networking and an empty `NETHERNET_PUBLIC_IP`.

## 2026-08-26 - Narrowly accept an empty offline Switch identity

### Context

Switch sent a self-signed LAN chain without XUID or `DisplayName`. gophertunnel rejected it before the bridge could connect to the BDS.

### Decision

Patch gophertunnel during the image build to permit an empty name only when XUID is also empty. Before outbound login, validate `ThirdPartyName` or generate a deterministic local fallback.

### Rationale

This reproduces observed LAN behavior while preserving validation for online identities.

### Consequences

The exception is deliberately offline-only and version-sensitive. Every gophertunnel upgrade must reapply and test the patch.

## 2026-08-26 - Require `online-mode=false` only on the trusted-LAN BDS

### Context

The BDS rejected the forwarded offline login with Bedrock reason `46`, `NotAuthenticated`.

### Decision

Keep LAN play enabled but use `online-mode=false` and `allow-list=false` for the trusted-LAN BDS.

### Rationale

The current bridge cannot create an independently authenticated Xbox session for each player.

### Consequences

Names can be impersonated. Proxy and BDS must never be exposed to the Internet. Supporting `online-mode=true` requires a separate upstream-authentication design.

## 2026-08-26 - Relay serialized gameplay packets

### Context

The main player worked, but adding a second local player caused `DisconnectReasonLoggedInOtherLocation`. Decode/re-encode relay logic lost subclient header fields.

### Decision

After login and spawn, relay serialized Bedrock bytes with `ReadBytes` and `Write`.

### Rationale

This preserves `SenderSubClient` and `TargetSubClient` across NetherNet and RakNet.

### Consequences

Both sides must negotiate the same Bedrock packet format. Split-screen must be repeated after every protocol upgrade.
