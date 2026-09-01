# Error and regression history

## Purpose and scope

This file records reusable defects, diagnoses, mitigations, and regression lessons. Commit auditing belongs in [`COMMIT_HISTORY.md`](COMMIT_HISTORY.md), open work in [`TODO.md`](TODO.md), and security controls in [`SECURITY.md`](SECURITY.md).

## How to use this file

Search by stable ID or affected surface. Update an existing record when the same root cause recurs. Keep implementation status separate from validation status, and never mark an issue resolved without appropriate tests or physical-device evidence.

## Status taxonomy

- `Resolved in code`: correction implemented and validated within its stated scope.
- `Mitigated`: risk reduced but not eliminated.
- `Partial`: only part of the problem is solved.
- `Open`: cause or solution remains unknown.
- `Superseded`: a later design removed the issue.

Stable IDs use `ERR-<AREA>-<NUMBER>`.

## Quick index

| ID | Problem | Severity | Status |
|---|---|---:|---|
| ERR-CONFIG-001 | A hard-coded address prevented deployment on another host | High | Resolved in code |
| ERR-DISC-001 | Switch did not display the RakNet proxy | High | Resolved in code |
| ERR-NETH-001 | Switch discovered the proxy but BDS rejected offline login | High | Resolved in code |
| ERR-NETH-002 | Adding a split-screen player disconnected the main player | High | Resolved in code |
| ERR-NETH-003 | Updated Switch failed on incompatible Bedrock protocol | High | Resolved in code |
| ERR-NETH-004 | Main player appeared as `Switch…` | Low | Resolved in code |
| ERR-NETH-005 | An active Switch session lost ICE transport | Medium | Mitigated |
| ERR-NET-001 | Mobile devices could not reach UDP/19132 | High | Resolved in code |

## Configuration

### ERR-CONFIG-001 - Process fails away from the originally encoded address

- Related evidence: initial `bedrock-lan-proxy.py` and legacy backup.
- Severity/status: high; `Resolved in code`.
- Surface: UDP bind and Docker deployment.
- Symptom: `LISTEN_IP` defaulted to an address not owned by the current host.
- Root cause: the reconstructed legacy service was tied to one machine.
- Correction: default listener `0.0.0.0`; Compose publishes or exposes the host port.
- Current evidence: healthy container and successful LAN pong.
- Remaining risk: another process may already own `19132`.
- Prevention/test: validate Compose, check port ownership, start the service, and query discovery.
- TODO: no issue-specific work remains.

## Discovery and NetherNet

### ERR-DISC-001 - Nintendo Switch does not show BedrockParty through RakNet

- Related evidence: Android discovery worked while Switch showed only Android-hosted worlds.
- Severity/status: high; `Resolved in code` for discovery.
- Surface: Switch LAN discovery.
- Symptom: Switch ignored the valid RakNet advertisement on `19132`.
- Root cause: Switch `1.26.44` discovers LAN worlds through encrypted NetherNet ServerData v6 on `7551`, not classic RakNet pong.
- Correction: implement the NetherNet advertisement using fields derived from accepted Android-hosted worlds.
- Current evidence: Switch displayed `BedrockParty`; decoded response used transport `2` and connection type `4`.
- Remaining risk: session establishment is covered separately by ERR-NETH-001.
- Prevention/test: query `7551`, preserve the nonce, and validate on physical Switch hardware.
- TODO: no discovery-only work remains.

### ERR-NETH-001 - Switch discovers the proxy but BDS rejects offline login

- Related evidence: Switch `InitialConnection-95` and `InitialConnection-122`, signaling logs, and BDS response.
- Severity/status: high; `Resolved in code`, validated with physical gameplay.
- Surface: signaling, ICE/WebRTC, Bedrock login, and BDS bridge.
- Symptom: early prototypes produced no SDP/ICE session; later builds reached the BDS but were rejected.
- Root cause: two successive blockers: missing WebRTC session handling, then a self-signed Switch identity without a verified name reaching an online-mode BDS.
- Correction: Go bridge using go-nethernet, Pion, and gophertunnel; exact ServerData v6; one ICE port; narrow offline identity handling; BDS `online-mode=false`.
- Current evidence: ICE/DTLS/SCTP completed, `Bedrock session bridged` appeared, and gameplay traffic remained bidirectional.
- Remaining risk: confirm BDS `online-mode=false` after restarts; protect the unauthenticated LAN boundary.
- Prevention/test: verify three firewall ports, effective BDS settings, `NetherNet client connected`, and `Bedrock session bridged`.
- TODO: high-priority BDS configuration checks remain in `TODO.md`.

### ERR-NETH-002 - Adding a split-screen player disconnects the main player

- Related evidence: physical Switch test and BDS disconnect reason `44`, `LoggedInOtherLocation`.
- Severity/status: high; `Resolved in code`, validated on physical Switch.
- Surface: Bedrock subclients after spawn.
- Symptom: main player could play, but adding the second local player closed the session.
- Root cause: `ReadPacket`/`WritePacket` recreated packet headers and reset `SenderSubClient` and `TargetSubClient` to zero.
- Correction: relay serialized packet bytes with `ReadBytes`/`Write`.
- Current evidence: two local players joined and played simultaneously.
- Remaining risk: the solution assumes matching Bedrock versions on both sides.
- Prevention/test: join with the main player, add the second local player, and keep both active for several minutes after every protocol update.
- TODO: retain this regression test for future versions.

### ERR-NETH-003 - Updated Switch fails during RequestNetworkSettings

- Related evidence: physical test on 2026-08-31, direct BDS query, and bridge logs.
- Severity/status: high; `Resolved in code`, physically validated.
- Surface: Bedrock version negotiation.
- Symptom: Android joined the updated BDS, but Switch failed immediately.
- Root cause: Switch/BDS used `1.26.45` protocol `2169`; `gophertunnel v1.59.0` expected `2168`.
- Correction: upgrade to `gophertunnel v1.61.0`, regenerate dependencies, reapply the offline patch, and add identity regression tests.
- Current evidence: the previous `expected 2168, got 2169` failure disappeared; build/tests passed and physical connection reached `Bedrock session bridged`.
- Remaining risk: every future Minecraft update may require another gophertunnel version.
- Prevention/test: compare BDS protocol with `protocol.CurrentProtocol`, then repeat join and split-screen tests.
- TODO: future-version validation only.

### ERR-NETH-004 - Main player appears as `Switch…`

- Related evidence: two-player Switch `1.26.45` test and offline-name logs.
- Severity/status: low; `Resolved in code`, deployed and log-validated; visual UI confirmation remains.
- Surface: main-player name forwarded to the offline BDS.
- Symptom: the second subplayer retained the Nintendo name, while the main player received a deterministic `Switch…` name.
- Root cause: main login omitted `IdentityData.DisplayName` and XUID but included the local name only in unsigned `ClientData.ThirdPartyName`.
- Correction: trim and validate `ThirdPartyName` only for an identity without XUID or DisplayName; retain deterministic fallback for missing/invalid values.
- Current evidence: unit tests cover valid, trimmed, empty, invalid, and online-XUID cases; physical logs showed `source=thirdPartyName` followed by `Bedrock session bridged`.
- Remaining risk: `ThirdPartyName` is not signed and may be forged.
- Prevention/test: compare log-assigned and in-game names; never use this fallback for an online identity.
- TODO: visual confirmation remains in `TODO.md`.

### ERR-NETH-005 - Active Switch session loses ICE transport

- Related evidence: bridge logs and immediate physical reconnection on 2026-08-31.
- Severity/status: medium; `Mitigated`, not reproduced.
- Surface: ICE/WebRTC transport after a successful bridge.
- Symptom: gameplay stopped and the listener logged `ICE transport entered unrecoverable state: failed`, followed by session closure.
- Root cause: undetermined. Logs prove loss of the ICE/UDP path but cannot distinguish Wi-Fi interruption, console sleep, network change, or prolonged packet loss.
- Mitigation: close the invalid session cleanly and accept a fresh negotiation.
- Current evidence: about 20 seconds later a new connection completed `Bedrock session bridged`; containers remained running and RakNet stayed healthy.
- Remaining risk: unstable Wi-Fi may interrupt future sessions.
- Prevention/test: maintain stable coverage, avoid console sleep, correlate repeats with access-point events, and instrument further only if recurrent.
- TODO: conditional instrumentation is recorded in `TODO.md`.

## Network

### ERR-NET-001 - Proxy works locally but no mobile device sees it

- Related evidence: networking decision and physical Android tests.
- Severity/status: high; `Resolved in code` for validated environments.
- Surface: Docker Desktop, Wi-Fi, and UDP publication.
- Symptom: local query and health check passed, but no mobile ping reached the process.
- Root cause: Wi-Fi was classified as Public while the firewall rule covered only Private.
- Correction: publish `19132:19132/udp` and allow required UDP ports from the LAN subnet on both Public and Private profiles.
- Current evidence: multiple Android devices discovered the world; gameplay through the relay succeeded.
- Remaining risk: other hosts and firewall products may behave differently.
- Prevention/test: compare the active profile with the rule and repeat discovery from a physical device.
- TODO: no host-specific work remains.

## Evidence coverage matrix

| Evidence | CONFIG-001 | DISC-001 | NETH-001 | NETH-002 | NETH-003 | NETH-004 | NETH-005 | NET-001 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Initial untracked files | Yes | Yes | N/A | N/A | N/A | N/A | N/A | Yes |
| RakNet LAN query | Yes | Partial | N/A | N/A | N/A | N/A | N/A | Yes |
| Android NetherNet golden samples | N/A | Yes | Partial | N/A | N/A | N/A | N/A | N/A |
| Switch InitialConnection tests | N/A | Yes | Yes | N/A | N/A | N/A | N/A | N/A |
| Go bridge and ServerData query | N/A | Yes | Partial | N/A | Partial | N/A | Partial | N/A |
| BDS NotAuthenticated diagnosis | N/A | N/A | Yes | N/A | N/A | N/A | N/A | N/A |
| Split-screen disconnect test | N/A | N/A | Yes | Yes | N/A | Partial | N/A | N/A |
| Protocol 2169 update | N/A | N/A | N/A | N/A | Yes | Partial | N/A | N/A |
| Two-player name test | N/A | N/A | N/A | Yes | Yes | Yes | N/A | N/A |
| ICE loss and reconnection | N/A | N/A | Partial | N/A | N/A | N/A | Yes | N/A |

## Regression-prevention playbook

1. Confirm no active configuration hard-codes a real proxy address.
2. Compile Python, run tests, and validate both Compose files.
3. Build both images and confirm the gophertunnel patch applies.
4. Start containers and wait for a healthy RakNet relay.
5. Query discovery from another physical machine when possible.
6. Validate Android before changing advertisement behavior.
7. Validate Switch discovery on `7551` separately from ICE on `50000`.
8. On Docker Desktop, confirm ICE advertises the host LAN address rather than `172.x`.
9. On Linux host networking, keep address replacement empty.
10. Change one variable at a time and record the result.
11. For the local unauthenticated identity flow, verify BDS `online-mode=false`, require legitimate game copies, and prevent Internet exposure.
12. Always test split-screen subclient headers, not only the main player.
13. After a Minecraft update, compare BDS protocol with gophertunnel support first.
14. Use `ThirdPartyName` only as a validated no-XUID fallback.
15. For isolated ICE loss, verify reconnection before adding complexity; instrument only recurrent failures.
