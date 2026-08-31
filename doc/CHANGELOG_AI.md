# AI-assisted change log

## 2026-08-31 - Convert all public documentation to English

### Changes

- Replaced every Spanish public document with an English version at the same path.
- Converted the root README, contribution guidance, public/internal security policies, production/support READMEs, technical memory, publishing guide, legacy notes, and environment-template comments.
- Preserved deployment procedures, compatibility evidence, error IDs, technical decisions, and AI-development disclosure.
- Recorded English as the public documentation language for broader accessibility.
- Kept local ignored `AGENTS.md` unchanged because it is not part of the public repository.
- Completed an editorial consistency pass across terminology, platform roles, authentication modes, version/protocol pairs, split-screen wording, and security language.

### Files changed

- `README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `.env.example`
- `proxy-bedrock/README.md`
- `support/README.md`, `support/diagnostics/CAPTURES.md`, `support/legacy/README.txt`
- Every Markdown document under `doc/`
- Public script comments, help text, diagnostic output, and bridge disconnect messages

### Validation

- Repository-wide Spanish-language scan excluding ignored local instructions/archive: no matches.
- Local Markdown-link validation: passed.
- Linux and Windows Compose validation with `.env.example`: passed.
- Python unit tests: 2 passed.
- Python compilation for runtime, diagnostics, and legacy tools: passed.
- Docker build: both images built; gophertunnel patch, Go tests, and bridge binary passed.
- Cross-document consistency scan: no conflicting platform roles, version/protocol pairs, authentication claims, or deprecated project names found.

### Remaining

- Create the public remote and validate deployment from a clean clone.

## 2026-08-31 - Prepare the public initial release

### Changes

- Added the MIT License under `BedrockParty contributors`.
- Removed the migrated initial brief from the public tree and retained it only in the ignored local archive.
- Replaced real IP addresses, stable identifiers, player names, and local paths with neutral examples.
- Expanded `.gitignore` for local configuration, captures, keys, logs, IDE files, bytecode, and private archives.
- Added contribution guidance, a public security policy, CI, and a publishing procedure.
- Consolidated experimental commits into one recoverable initial public commit.
- Documented isolated ICE loss and successful reconnection as `ERR-NETH-005`.
- Documented the complete Bedrock `1.26.45`/protocol `2169` physical scenario: active Nintendo Switch Online subscription, LAN without Microsoft/Xbox accounts, two local Switch players, and mixed Android/Switch cooperative play.
- Declared Linux/Docker Engine host networking as the validated production deployment and Windows Docker Desktop as a validated alternative.
- Added public disclosure of development in collaboration with AI agents.

### Files changed

- `.env.example`, `.gitattributes`, `.gitignore`, `LICENSE`
- `CONTRIBUTING.md`, `SECURITY.md`, `.github/workflows/ci.yml`, `README.md`
- Production and support documentation
- `doc/PROJECT_CONTEXT.md`, `doc/DECISIONS.md`, `doc/ERROR_HISTORY.md`
- `doc/SECURITY.md`, `doc/TODO.md`, `doc/COMMIT_HISTORY.md`, `doc/PUBLISHING.md`

### Validation

- Known operational-address, identifier, player-name, and local-path scan: clean.
- Common credential-pattern scan: clean.
- `.env`, `AGENTS.md`, captures, bytecode, and `support/local-archive/`: ignore rules verified.
- Linux and Windows Compose validation with `.env.example`: passed.
- Python unit tests: 2 passed.
- Python compilation: passed.
- Docker image build: both images built; gophertunnel patch, Go tests, and binary build passed.
- Linux/Docker Engine deployment: physically confirmed by the user as production.

### Remaining

- Create the public remote and validate a clean-clone deployment.

## 2026-08-31 - Support Minecraft Bedrock 1.26.45

### Changes

- Confirmed the updated BDS advertises `1.26.45`, protocol `2169`.
- Diagnosed Switch rejection: `RequestNetworkSettings: incompatible protocol version: expected 2168, got 2169`.
- Upgraded gophertunnel from `v1.59.0` to `v1.61.0` and regenerated `go.sum`.
- Updated the Dockerfile patch path and revalidated the offline Switch exception.
- Added a regression test that accepts an empty DisplayName only without XUID.
- Built and deployed only the updated NetherNet bridge.
- Validated gameplay and two-player split-screen play on Switch `1.26.45`.
- Added validated `ClientData.ThirdPartyName` fallback for the main offline player.

### Files changed

- `proxy-bedrock/Dockerfile.nethernet`
- `proxy-bedrock/nethernet-bridge/go.mod`, `go.sum`, `main.go`, `main_test.go`
- Root and production READMEs
- Project context, setup, decisions, errors, security, TODO, and this change log

### Validation

- Direct BDS query: `1.26.45`, protocol `2169`.
- Docker build: patch applied to `v1.61.0`, Go tests passed, binary built.
- Physical Switch: `NetherNet client connected`, `Bedrock session bridged`, gameplay, and two local players.
- Name fallback: `source=thirdPartyName` followed by a bridged session.

### Remaining

- Visually confirm the main player's displayed local name.

## 2026-08-26 - Standardize root Compose layout and naming

### Changes

- Renamed the default Linux file to `compose.yml` and the Windows file to `compose.win.yml`.
- Moved both Compose files and `.env.example` to the repository root.
- Updated every deployment, validation, operation, and removal command.
- Added `AGENTS.md` to `.gitignore`.
- Standardized public naming on `BedrockParty` and removed previous private naming.

### Files changed

- Root Compose and environment files
- `.gitignore`
- Root and production READMEs
- Project context, setup, architecture, decisions, errors, TODO, and change log

### Validation

- Both Compose configurations parsed successfully.
- Production Python compiled.
- Python codec tests passed.
- Documentation links resolved.
- Searches found no previous naming or obsolete Compose paths.

### Remaining

- None for repository layout.

## 2026-08-26 - Complete deployment and configuration guide

### Changes

- Rebuilt the root README as the complete operational entry point.
- Documented BDS, architecture, ports, environment variables, BDS `online-mode=false`, Linux/Windows deployment, firewall rules, verification, operation, troubleshooting, and security.
- Documented the tested Minecraft versions and clarified that the historical Android advertisement does not represent the backend version.
- Added `.env.example` for one-command deployment after configuration.

### Files changed

- `README.md`, `.env.example`
- Production README
- Project context, setup, TODO, and change log

### Validation

- Linux and Windows Compose parsing passed.
- Production Python compiled.
- Python tests passed.
- Markdown links resolved.

### Remaining

- None for initial documentation completeness.

## 2026-08-26 - Prepare the BedrockParty production package

### Changes

- Standardized runtime naming on `BedrockParty`.
- Separated production runtime from diagnostics, tests, captures, and legacy material.
- Removed capture dependencies and volumes from runtime images.
- Hardened containers with non-root users, dropped capabilities, read-only root file systems, and `no-new-privileges`.
- Added log rotation and a shared `.env.example`.
- Documented account-free LAN mode and authenticated-mode limitations.

### Files changed

- Compose files, Dockerfiles, runtime, and health check
- Production and support documentation
- Project context, architecture, setup, decisions, security, TODO, and change log

### Validation

- Python compilation and tests passed.
- Both Docker images built.
- Containers started with read-only root file systems and non-root users.
- RakNet remained healthy and NetherNet discovery returned the configured world.

### Remaining

- Persist the NetherNet TOFU identity.

## 2026-08-26 - Add offline LAN login compatibility and diagnose BDS rejection

### Changes

- Confirmed Switch physically completed discovery, ICE, DTLS, and SCTP.
- Added a narrow gophertunnel patch for a self-signed offline identity without XUID or DisplayName.
- Assigned a deterministic local name before outbound BDS login.
- Added structured packet-direction and backend-disconnect diagnostics without logging gameplay payloads.
- Diagnosed Bedrock reason `46`, `NotAuthenticated`, and documented the required BDS offline setting.
- Documented that a directly accessed BDS may use `online-mode=true`, but the current bridge lacks per-player upstream authentication.

### Files changed

- NetherNet bridge source, test, patch, module files, and Dockerfile
- Compose configuration
- README and persistent technical documentation

### Validation

- Patch applied successfully during Docker build.
- Go tests and binary build passed.
- Physical Switch login reached the BDS.
- With BDS `online-mode=false`, the session reached `Bedrock session bridged` and gameplay.

### Remaining

- Preserve the regression tests across gophertunnel upgrades.

## 2026-08-26 - Implement Switch NetherNet discovery and session bridge

### Changes

- Captured and decoded accepted NetherNet ServerData v6 discovery.
- Reproduced the advertisement and confirmed Switch displayed `BedrockParty`.
- Implemented SDP/ICE signaling and WebRTC-to-Bedrock/RakNet bridging in Go.
- Added a single multiplexed ICE port.
- Separated Windows Docker NAT configuration from Linux host networking.
- Added diagnostic queries and golden codec tests.

### Files changed

- Go bridge and Dockerfile
- Compose files and environment template
- NetherNet diagnostic tools and tests
- README and technical documentation

### Validation

- Python codec tests passed.
- NetherNet query decoded valid ServerData v6.
- Docker image built and listener started on `7551/udp`.
- Physical Switch discovery, ICE, DTLS, and SCTP completed.

### Remaining

- None for discovery/session implementation; later authentication and subclient fixes are recorded above.

## 2026-08-25 - Containerize and deploy the initial Bedrock relay

### Changes

- Inspected the reconstructed legacy proxy.
- Made listener, backend, advertisement, and timeout settings environment-driven.
- Added per-client session expiration and optional discovery logs.
- Added a health check and Docker image.
- Created Linux and Windows Compose variants.
- Added Windows Firewall installation/removal scripts.
- Added diagnostic tools and persistent project documentation.

### Files changed

- Python relay, Dockerfile, health check, and firewall scripts
- Compose and environment configuration
- Diagnostic tools and tests
- README and initial `doc/` files

### Validation

- Python compilation passed.
- Docker image built.
- Container became healthy.
- Broadcast query received proxy and BDS replies.
- RakNet open-connection probe matched backend behavior.
- Physical Android devices discovered, joined, and played through the container.

### Remaining

- Switch support was implemented in later entries.
