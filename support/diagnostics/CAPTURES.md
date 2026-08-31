# Local captures

Packet captures, ETL traces, JSONL samples, and temporary decoded output are local diagnostic artifacts. They must not be committed.

Store them under `support/local-archive/` or another ignored directory. Before sharing any capture:

1. Confirm that it contains no credentials or authentication material.
2. Remove player names, UUIDs, XUIDs, device identifiers, and real network addresses.
3. Limit the capture to the minimum traffic required to reproduce the issue.
4. Document the Minecraft version, protocol, test topology, and expected result separately.

The repository intentionally contains only diagnostic scripts and synthetic test data.
