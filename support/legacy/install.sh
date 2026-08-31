#!/usr/bin/env bash
set -euo pipefail

install -m 0755 bedrock-lan-proxy.py /opt/bedrock-lan-proxy.py
install -m 0644 bedrockparty-proxy.env /etc/bedrockparty-proxy.env
install -m 0644 bedrockparty-proxy.service /etc/systemd/system/bedrockparty-proxy.service
install -m 0755 query-bedrock-broadcast.py /opt/query-bedrock-broadcast.py

systemctl daemon-reload
systemctl enable --now bedrockparty-proxy.service
systemctl --no-pager --full status bedrockparty-proxy.service
