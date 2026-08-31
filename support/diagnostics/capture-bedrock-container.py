#!/usr/bin/env python3
"""Capture only UDP/19132 and UDP/19133 from a Linux interface into PCAP."""

import argparse
import socket
import struct
import sys
import time
from pathlib import Path

BEDROCK_PORTS = {19132, 19133}
ETH_P_ALL = 0x0003
PCAP_GLOBAL_HEADER = struct.pack("<IHHIIII", 0xA1B2C3D4, 2, 4, 0, 0, 65535, 1)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interface", default="eth0")
    parser.add_argument("--output", required=True)
    parser.add_argument("--duration", type=float, default=30.0)
    return parser.parse_args()


def is_bedrock_udp(frame):
    if len(frame) < 42:
        return False
    ether_type = struct.unpack("!H", frame[12:14])[0]
    ip_offset = 14
    if ether_type == 0x8100 and len(frame) >= 46:
        ether_type = struct.unpack("!H", frame[16:18])[0]
        ip_offset = 18
    if ether_type != 0x0800 or frame[ip_offset] >> 4 != 4:
        return False
    header_length = (frame[ip_offset] & 0x0F) * 4
    if frame[ip_offset + 9] != socket.IPPROTO_UDP:
        return False
    udp_offset = ip_offset + header_length
    if header_length < 20 or len(frame) < udp_offset + 8:
        return False
    source_port, destination_port = struct.unpack("!HH", frame[udp_offset : udp_offset + 4])
    return source_port in BEDROCK_PORTS or destination_port in BEDROCK_PORTS


def main():
    args = parse_args()
    if args.duration <= 0:
        raise SystemExit("Duration must be positive")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    capture = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.htons(ETH_P_ALL))
    capture.bind((args.interface, 0))
    capture.settimeout(0.5)

    packet_count = 0
    byte_count = 0
    deadline = time.monotonic() + args.duration
    try:
        with output.open("wb") as pcap:
            pcap.write(PCAP_GLOBAL_HEADER)
            while time.monotonic() < deadline:
                try:
                    frame = capture.recv(65535)
                except socket.timeout:
                    continue
                if not is_bedrock_udp(frame):
                    continue
                now = time.time()
                seconds = int(now)
                microseconds = int((now - seconds) * 1_000_000)
                pcap.write(struct.pack("<IIII", seconds, microseconds, len(frame), len(frame)))
                pcap.write(frame)
                packet_count += 1
                byte_count += len(frame)
    finally:
        capture.close()

    print(f"PCAP: {output}")
    print(f"Bedrock packets: {packet_count}; Ethernet bytes: {byte_count}")
    return 0 if packet_count else 2


if __name__ == "__main__":
    sys.exit(main())
