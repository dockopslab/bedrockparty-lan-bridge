# Support material

This directory is not part of the production deployment and is not copied into the Docker images.

- `diagnostics/`: queries, analyzers, and capture tools for future regressions.
- `tests/`: tests for the codecs used during NetherNet development.
- `legacy/`: the pre-Docker systemd deployment, retained only as a reference.
- `local-archive/`: recoverable local captures and backups, excluded from Git and never distributed.

The maintained runtime lives exclusively in [`../proxy-bedrock/`](../proxy-bedrock/README.md). Do not run the legacy service alongside Docker because both deployments compete for the same UDP ports.

Run the development tests with:

```bash
python -m pip install -r support/requirements.txt
python -m unittest discover -s support/tests -v
```
