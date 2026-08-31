#!/usr/bin/env python3
"""Minimal healthcheck for the local RakNet advertisement."""

import argparse
import secrets
import socket
import struct
import sys
import time

MAGIC = bytes.fromhex("00ffff00fefefefefdfdfdfd12345678")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=19132)
    parser.add_argument("--timeout", type=float, default=1.0)
    args = parser.parse_args()

    stamp = int(time.time() * 1000) & 0xFFFFFFFFFFFFFFFF
    ping = b"\x01" + struct.pack(">Q", stamp) + MAGIC + struct.pack(">Q", secrets.randbits(64))
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(args.timeout)
        sock.sendto(ping, (args.target, args.port))
        try:
            response, _ = sock.recvfrom(65535)
        except socket.timeout:
            return 1
    return 0 if len(response) >= 35 and response[0] == 0x1C else 1


if __name__ == "__main__":
    sys.exit(main())
