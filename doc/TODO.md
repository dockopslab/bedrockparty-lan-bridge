# TODO

## High priority

- [ ] Confirm visually that the main Switch player displays the local name already forwarded through `ThirdPartyName`.
- [ ] Verify that BDS `online-mode=false` persists after restarts and that `allow-list` does not block offline identities.
- [ ] Confirm that the unauthenticated BDS is not Internet-accessible and remains restricted to the LAN.

## Medium priority

- [ ] Persist the NetherNet TOFU identity securely if Switch requests trust after each recreation.
- [ ] Add automated concurrency and session-expiration tests.

## Low priority

- [ ] Create the public remote and validate deployment from a clean clone before tagging the first release.
- [ ] Obtain professional legal review before claiming legal certainty, monetizing, or marketing the project as a consumer service.
- [ ] Re-run dependency and final-image license scans whenever Go dependencies or container base images change.
- [ ] Evaluate IPv6/19133 only if new captures demonstrate a requirement.
- [ ] Pin base images by digest after defining an update policy.
- [ ] Evaluate per-player upstream authentication if online-mode BDS support is required.
- [ ] Add ICE-cause metrics and Wi-Fi correlation only if session loss recurs.

## Security checklist

- [x] Containers run without root.
- [x] No secrets or credentials exist in versioned image/configuration files.
- [x] Only `19132`, `7551`, and multiplexed `50000/udp` are exposed.
- [x] Logs rotate and contain no gameplay payloads.
- [x] Windows firewall limits all three ports to the LAN.
- [x] `.env` is ignored and absent from the public tree.
- [ ] Review base images regularly and rebuild for security fixes.

## Recently completed

- [x] Confirm GitHub Actions builds both images and verifies the packaged BedrockParty license and third-party NOTICE files.
- [x] Define the `bedrock-<version>-r<revision>` release scheme and prepare the English `bedrock-1.26.45-r1` notes.
- [x] Add the official Minecraft independence disclaimer, responsible-use conditions, and trademark notices.
- [x] Inventory Go dependency licenses and package exact license/NOTICE files in the runtime image.
- [x] Clarify that local BDS identity settings do not waive ownership, account, entitlement, subscription, or platform obligations.
- [x] Select and add the MIT License.
- [x] Sanitize real IP addresses, identifiers, names, and local paths.
- [x] Add CI, contribution guidance, security policy, and publishing procedure.
- [x] Consolidate `main` into one initial public commit and retain private history only in an ignored local bundle.
- [x] Validate Linux/Docker Engine host networking as production.
- [x] Validate Windows/Docker Desktop as an alternative.
- [x] Document AI-assisted development.
- [x] Document the full `1.26.45` cooperative scenario.
- [x] Upgrade to `gophertunnel v1.61.0` for protocol `2169`.
- [x] Validate Android discovery, join, and gameplay.
- [x] Validate Switch discovery, WebRTC, login, and gameplay.
- [x] Preserve split-screen subclient headers and validate two local players.
- [x] Validate mixed cooperative play with Android and Switch split-screen play.
- [x] Provide root `compose.yml`, `compose.win.yml`, and `.env.example`.
- [x] Separate production runtime from diagnostics and legacy material.
- [x] Harden containers with read-only root file systems, dropped capabilities, and `no-new-privileges`.
