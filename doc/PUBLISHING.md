# Repository publishing

## State

The public tree is prepared on `main` as one sanitized initial commit. The experimental history is retained only in a local ignored bundle and must never be uploaded.

## Pre-publish checklist

1. Confirm that `git status --short` is empty.
2. Confirm that `.env`, `AGENTS.md`, `support/local-archive/`, packet captures, and bytecode are ignored.
3. Search for real addresses, identifiers, names, routes, and credentials.
4. Run Python tests, validate both Compose files, and build both images.
5. Verify that the README states the supported Bedrock version and Linux production deployment.
6. Confirm that no private remote is configured.

## Create the public repository

Create an empty repository without platform-generated README, license, or ignore files. Then:

```bash
git remote add origin PUBLIC_REPOSITORY_URL
git remote -v
git log --oneline --decorate
git push -u origin main
```

Never use `git push --all` and never publish the private-history bundle.

## Recommended hosting settings

- Enable dependency analysis and security alerts.
- Enable private vulnerability reporting.
- Protect `main` and require `CI / validate`.
- Delay package or image publication until a versioning policy is defined.

## First release

After validating deployment from a clean clone, create a semantic-version tag and release notes that state:

- supported Minecraft Bedrock version and protocol;
- validated operating systems and physical devices;
- LAN authentication and TOFU limitations;
- required BDS `server.properties` settings.
