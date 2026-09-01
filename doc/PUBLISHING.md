# Repository publishing

## State

The public tree is prepared on `main` as one sanitized initial commit. The experimental history is retained only in a local ignored bundle and must never be uploaded.

## Pre-publish checklist

1. Confirm that `git status --short` is empty.
2. Confirm that `.env`, `AGENTS.md`, `support/local-archive/`, packet captures, and bytecode are ignored.
3. Search for real addresses, identifiers, names, routes, and credentials.
4. Run Python tests, validate both Compose files, and build both images.
5. Verify that the README states the supported Bedrock version and Linux production deployment.
6. Confirm that the prominent independence disclaimer, `LEGAL.md`, and trademark notices are present.
7. Regenerate the Go license inventory, compare it with `THIRD_PARTY_NOTICES.md`, and confirm the exact license files are present in the NetherNet image.
8. Scan the final images for package licenses and vulnerabilities, including Python and Alpine components.
9. Confirm that no private remote is configured.

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

After validating deployment from a clean clone, create a compatibility tag using:

```text
bedrock-<Minecraft version>-r<BedrockParty revision>
```

Example: `bedrock-1.26.45-r1`. Increment `r2`, `r3`, and so on for project-only fixes that retain the same Bedrock compatibility target. Release notes must state:

- supported Minecraft Bedrock version and protocol;
- validated operating systems and physical devices;
- LAN authentication and TOFU limitations;
- required BDS `server.properties` settings.
- legitimate-copy and platform-terms requirements;
- links to the legal guidance and third-party notices.

The initial release process publishes GitHub source archives only. Do not imply that container images are available unless a separate registry publication workflow has completed successfully.

## Automated release publication

`.github/workflows/release.yml` publishes a GitHub Release when a tag matching `bedrock-*-r*` is pushed. It calls the reusable CI workflow first, so Compose validation, tests, image builds, and packaged-license checks must all succeed before publication.

The release job extracts the matching section from `CHANGELOG.md`, uses it as the English release notes, and lets GitHub attach its standard source archives. It does not upload or retain the temporary Docker images.

Create and publish an annotated tag only after the target commit is ready:

```bash
git tag -a bedrock-1.26.45-r1 -m "BedrockParty for Bedrock 1.26.45 - revision 1"
git push origin bedrock-1.26.45-r1
```

Never reuse or move a published release tag. Corrections for the same Bedrock target use the next revision, such as `r2`.
