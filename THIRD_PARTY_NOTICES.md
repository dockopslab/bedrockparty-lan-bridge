# Third-party notices

BedrockParty is licensed under the repository's [`LICENSE`](LICENSE). That license applies only to original BedrockParty material. Third-party components remain copyrighted by their respective owners and are distributed under their own licenses.

The Go inventory below was generated on 2026-08-31 from the package actually compiled by `proxy-bedrock/nethernet-bridge/go.mod`, using `go-licenses v2.0.1`. Exact license and NOTICE files are stored in [`proxy-bedrock/third_party_licenses/`](proxy-bedrock/third_party_licenses/) and copied into the NetherNet runtime image at `/usr/share/licenses/bedrockparty/third-party/`.

## Direct Go dependencies

| Component | Version | License |
|---|---:|---|
| `github.com/df-mc/go-nethernet` | `v1.0.20` | MIT |
| `github.com/pion/ice/v4` | `v4.2.7` | MIT |
| `github.com/pion/webrtc/v4` | `v4.2.16-0.20260627075746-7a223a6f4d4f` | MIT |
| `github.com/sandertv/gophertunnel` | `v1.61.0` | MIT |

BedrockParty applies the source patch in `proxy-bedrock/nethernet-bridge/patches/` to the downloaded gophertunnel source during the image build. The modified dependency remains subject to gophertunnel's MIT license; the project does not claim ownership of upstream code.

## Transitive Go dependencies

| Component | Version | License identified by the audit |
|---|---:|---|
| `github.com/andreburgaud/crypt2go` | `v1.8.0` | BSD-3-Clause |
| `github.com/coder/websocket` | `v1.8.14` | ISC |
| `github.com/coreos/go-oidc/v3` | `v3.17.0` | Apache-2.0; NOTICE included |
| `github.com/df-mc/go-playfab/v2` | `v2.0.2` | MIT |
| `github.com/df-mc/go-xsapi/v2` | `v2.0.3` | MIT |
| `github.com/df-mc/jsonc` | `v1.0.5` | MIT |
| `github.com/go-gl/mathgl` | `v1.1.0` | BSD-3-Clause |
| `github.com/go-jose/go-jose/v4` | `v4.1.4` | Apache-2.0; bundled JSON package under BSD-3-Clause |
| `github.com/google/uuid` | `v1.6.0` | BSD-3-Clause |
| `github.com/klauspost/compress` | `v1.18.1` | Multiple notices: MIT, Apache-2.0, and BSD-3-Clause |
| `github.com/pion/datachannel` | `v1.6.2` | MIT |
| `github.com/pion/dtls/v3` | `v3.1.4` | MIT |
| `github.com/pion/interceptor` | `v0.1.45` | MIT |
| `github.com/pion/logging` | `v0.2.4` | MIT |
| `github.com/pion/mdns/v2` | `v2.1.0` | MIT |
| `github.com/pion/randutil` | `v0.1.0` | MIT |
| `github.com/pion/rtcp` | `v1.2.16` | MIT |
| `github.com/pion/rtp` | `v1.10.2` | MIT |
| `github.com/pion/sctp` | `v1.10.2` | MIT |
| `github.com/pion/sdp/v3` | `v3.0.19` | MIT |
| `github.com/pion/srtp/v3` | `v3.0.12` | MIT |
| `github.com/pion/stun/v3` | `v3.1.6` | MIT |
| `github.com/pion/transport/v4` | `v4.0.2` | MIT |
| `github.com/pion/turn/v5` | `v5.0.10` | MIT |
| `github.com/sandertv/go-raknet` | pseudo-version at `0d1fd09e2cf6` | MIT |
| `github.com/wlynxg/anet` | `v0.0.5` | BSD-3-Clause |
| `golang.org/x/crypto` | `v0.48.0` | BSD-3-Clause |
| `golang.org/x/exp` | `v0.0.0-20240909161429-701f63a606c0` | BSD-3-Clause |
| `golang.org/x/image` | `v0.21.0` | BSD-3-Clause |
| `golang.org/x/net` | `v0.50.0` | BSD-3-Clause |
| `golang.org/x/oauth2` | `v0.36.0` | BSD-3-Clause |
| `golang.org/x/sys` | `v0.41.0` | BSD-3-Clause |
| `golang.org/x/text` | `v0.34.0` | BSD-3-Clause |
| `golang.org/x/time` | `v0.14.0` | BSD-3-Clause |

## Container base images

- `python:3.13-alpine` supplies the Python runtime and Alpine userland for the RakNet image.
- `golang:1.25-alpine` is used only as a build stage for the NetherNet binary.
- `alpine:3.22` supplies the NetherNet runtime userland.

These images contain separately licensed operating-system and language components. Their package-level notices remain governed by the image publishers and installed packages. Redistributors of built container images must retain the notices included in the image layers and perform a fresh image/software-composition audit for the exact image digests they publish.

## Maintaining this inventory

Whenever `go.mod`, `go.sum`, a base image, or the Docker build changes:

1. Regenerate the Go report and `proxy-bedrock/third_party_licenses/` from the compiled package.
2. Review multi-license results and every included `NOTICE` file.
3. Update the versions and license classifications above.
4. Scan the final images before publishing binaries or container images.

This inventory is a compliance aid, not legal advice and not a warranty that every possible obligation has been identified.
