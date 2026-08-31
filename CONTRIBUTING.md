# Contributing to BedrockParty

Thank you for helping improve BedrockParty. Open an issue before starting a substantial feature or behavioral change. Small, self-contained fixes may be submitted directly.

## Development setup

1. Copy `.env.example` to `.env` and replace all example addresses and identifiers.
2. Run the Python tests:

   ```bash
   python -m unittest discover -s support/tests -v
   ```

3. Validate both deployment definitions:

   ```bash
   docker compose config --quiet
   docker compose -f compose.win.yml config --quiet
   ```

4. Build the production images:

   ```bash
   docker compose -f compose.win.yml build
   ```

## Pull requests

- Keep changes small and focused.
- Use Conventional Commits.
- Add tests when behavior changes.
- Update `README.md` and `doc/` when configuration, architecture, compatibility, or risks change.
- Never include `.env`, packet captures, player names, UUIDs, XUIDs, real network addresses, or credentials.
- State which Minecraft Bedrock, BDS, operating-system, and physical-device versions were tested.

AI-assisted contributions are welcome when the contributor reviews the result, runs the applicable validation, and accepts responsibility for the change. Disclose material use of AI agents in the pull request and update `doc/CHANGELOG_AI.md` when appropriate.

## Security

Do not disclose vulnerabilities or private data in a public issue. Follow [SECURITY.md](SECURITY.md).
