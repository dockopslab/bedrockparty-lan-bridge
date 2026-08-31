#!/usr/bin/env python3
"""Check that the relay forwards the RakNet session start to the backend."""

import argparse
import json
import socket
import struct
import sys

MAGIC = bytes.fromhex("00ffff00fefefefefdfdfdfd12345678")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True)
    parser.add_argument("--port", type=int, default=19132)
    parser.add_argument("--protocol", type=int, default=11)
    parser.add_argument("--mtu", type=int, default=1492)
    parser.add_argument("--timeout", type=float, default=2.0)
    return parser.parse_args()


def main():
    args = parse_args()
    if not 46 <= args.mtu <= 65535:
        raise SystemExit("MTU fuera de rango")

    # ID_OPEN_CONNECTION_REQUEST_1 + magic + RakNet protocol + padding.
    request = b"\x05" + MAGIC + bytes([args.protocol])
    request += b"\x00" * (args.mtu - 28 - len(request))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(args.timeout)
    sock.sendto(request, (args.target, args.port))
    try:
        response, source = sock.recvfrom(65535)
    except socket.timeout:
        print(json.dumps({"target": args.target, "result": "timeout"}))
        return 1

    result = {
        "target": args.target,
        "source_ip": source[0],
        "source_port": source[1],
        "request_length": len(request),
        "response_length": len(response),
        "packet_id": response[0] if response else None,
        "hex": response.hex(),
    }
    if len(response) >= 28 and response[0] == 0x06 and response[1:17] == MAGIC:
        result.update(
            result="open_connection_reply_1",
            server_guid=struct.unpack(">Q", response[17:25])[0],
            security=response[25],
            mtu=struct.unpack(">H", response[26:28])[0],
        )
        print(json.dumps(result))
        return 0

    result["result"] = "unexpected_response"
    print(json.dumps(result))
    return 1


if __name__ == "__main__":
    sys.exit(main())
