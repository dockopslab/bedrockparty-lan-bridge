BedrockParty legacy deployment
==============================

This directory preserves the pre-Docker systemd deployment as a historical
reference:

  LAN clients -> 192.168.1.20:19132/UDP -> 192.168.1.10:19132/UDP

Files:

  bedrockparty-proxy.env      Example environment file
  bedrockparty-proxy.service  systemd unit
  install.sh                  Legacy installer
  query-bedrock-broadcast.py  Basic RakNet discovery query

Do not deploy this service alongside Docker. Both implementations bind the
same UDP port and will conflict.

The values in this directory are documentation examples, not production
defaults. The supported deployment is compose.yml on Linux. Use
compose.win.yml only for the documented Docker Desktop alternative.

Refer to ../../README.md for current installation, security, and validation
instructions.
