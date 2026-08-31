#!/usr/bin/env python3
"""Query Minecraft Bedrock LAN advertisements through RakNet."""

import argparse
import json
import secrets
import socket
import struct
import sys
import time

MAGIC = bytes.fromhex("00ffff00fefefefefdfdfdfd12345678")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="192.168.1.255")
    parser.add_argument("--port", type=int, default=19132)
    parser.add_argument("--packet-id", type=lambda value: int(value, 0), choices=(0x01, 0x02), default=0x01)
    parser.add_argument("--timeout", type=float, default=2.0)
    parser.add_argument("--first", action="store_true", help="Stop after the first response")
    parser.add_argument("--json", action="store_true", help="Emit JSON Lines with bytes and fields")
    parser.add_argument("--require-response", action="store_true")
    return parser.parse_args()


def parse_pong(data, addr):
    result = {
        "source_ip": addr[0],
        "source_port": addr[1],
        "length": len(data),
        "packet_id": data[0] if data else None,
        "hex": data.hex(),
    }
    if len(data) < 35 or data[0] != 0x1C:
        return result

    text_length = struct.unpack(">H", data[33:35])[0]
    payload_bytes = data[35 : 35 + text_length]
    payload = payload_bytes.decode("utf-8", errors="replace")
    result.update(
        ping_time=struct.unpack(">Q", data[1:9])[0],
        server_guid=struct.unpack(">Q", data[9:17])[0],
        magic=data[17:33].hex(),
        advertised_length=text_length,
        payload=payload,
        fields=payload.split(";"),
    )
    return result


def main():
    args = parse_args()
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(args.timeout)
    sock.bind(("", 0))

    stamp = int(time.time() * 1000) & 0xFFFFFFFFFFFFFFFF
    ping = bytes([args.packet_id]) + struct.pack(">Q", stamp) + MAGIC + struct.pack(">Q", secrets.randbits(64))
    if not args.json:
        print(
            f"Looking for Bedrock responses on {args.target}:{args.port} "
            f"using ping 0x{args.packet_id:02x}..."
        )
    sock.sendto(ping, (args.target, args.port))

    seen = set()
    while True:
        try:
            data, addr = sock.recvfrom(65535)
        except socket.timeout:
            break
        if addr in seen:
            continue
        seen.add(addr)
        result = parse_pong(data, addr)
        result.update(
            query_target=args.target,
            query_port=args.port,
            query_packet_id=args.packet_id,
        )
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        elif result.get("payload") is not None:
            print(f"{addr} -> {result['payload']}")
            print(f"  bytes={result['length']} guid={result['server_guid']} hex={result['hex']}")
            for index, field in enumerate(result["fields"]):
                print(f"  [{index:02}] {field}")
        else:
            packet_id = result["packet_id"]
            label = "empty" if packet_id is None else f"0x{packet_id:02x}"
            print(f"{addr} -> RakNet packet id={label} len={result['length']}")
        if args.first:
            break

    if not args.json:
        print(f"Done. Unique responses: {len(seen)}")
    if args.require_response and not seen:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
