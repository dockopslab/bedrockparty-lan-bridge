# Security Policy

## Supported versions

BedrockParty follows the Minecraft Bedrock protocol version documented in the README. Only the latest revision of the main branch receives security fixes.

## Reporting a vulnerability

Use **Report a vulnerability** in the repository's **Security** tab when private vulnerability reporting is enabled. Otherwise, contact the maintainer privately before opening a public issue.

Do not publicly attach packet captures, `.env` files, player names, UUIDs, XUIDs, real network addresses, or credentials. Include only the minimum reproduction steps and affected versions.

## Trust boundary

Unauthenticated LAN mode permits name impersonation. The proxy and BDS must remain on a trusted local network, and their UDP ports must never be exposed to the Internet. See [`doc/SECURITY.md`](doc/SECURITY.md) for technical controls.
