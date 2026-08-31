#!/usr/bin/env python3
"""Capture only UDP/19132 and UDP/19133 on Windows as a DLT_RAW PCAP."""

import argparse
import socket
import struct
import sys
import time
from pathlib import Path

BEDROCK_PORTS = {19132, 19133}
PCAP_GLOBAL_HEADER = struct.pack(
    "<IHHIIII",
    0xA1B2C3D4,
    2,
    4,
    0,
    0,
    65535,
    101,  # LINKTYPE_RAW: the packet starts with the IPv4 header.
)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interface", required=True, help="Local IPv4 address of the LAN interface")
    parser.add_argument("--output", required=True)
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--ip", action="append", default=[], help="Limit capture to a source/destination IPv4")
    parser.add_argument("--all-udp", action="store_true", help="Capture any UDP port within the IP filter")
    return parser.parse_args()


def is_selected_udp(packet, selected_ips, all_udp):
    if len(packet) < 28 or packet[0] >> 4 != 4 or packet[9] != socket.IPPROTO_UDP:
        return False
    header_length = (packet[0] & 0x0F) * 4
    if header_length < 20 or len(packet) < header_length + 8:
        return False
    source_ip = socket.inet_ntoa(packet[12:16])
    destination_ip = socket.inet_ntoa(packet[16:20])
    if selected_ips and source_ip not in selected_ips and destination_ip not in selected_ips:
        return False
    if all_udp:
        return True
    source_port, destination_port = struct.unpack("!HH", packet[header_length : header_length + 4])
    return source_port in BEDROCK_PORTS or destination_port in BEDROCK_PORTS


def main():
    args = parse_args()
    if args.duration <= 0:
        raise SystemExit("Duration must be positive")
    if args.all_udp and not args.ip:
        raise SystemExit("--all-udp requires at least one --ip filter")
    if not hasattr(socket, "SIO_RCVALL"):
        raise SystemExit("This tool requires Windows")

    output = Path(args.output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    capture = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
    capture.bind((args.interface, 0))
    capture.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
    capture.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
    capture.settimeout(0.5)

    packet_count = 0
    byte_count = 0
    deadline = time.monotonic() + args.duration
    try:
        with output.open("wb") as pcap:
            pcap.write(PCAP_GLOBAL_HEADER)
            while time.monotonic() < deadline:
                try:
                    packet = capture.recv(65535)
                except socket.timeout:
                    continue
                if not is_selected_udp(packet, set(args.ip), args.all_udp):
                    continue
                now = time.time()
                seconds = int(now)
                microseconds = int((now - seconds) * 1_000_000)
                pcap.write(struct.pack("<IIII", seconds, microseconds, len(packet), len(packet)))
                pcap.write(packet)
                packet_count += 1
                byte_count += len(packet)
    finally:
        capture.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)
        capture.close()

    print(f"PCAP: {output}")
    print(f"Bedrock packets: {packet_count}; IP bytes: {byte_count}")
    return 0 if packet_count else 2


if __name__ == "__main__":
    sys.exit(main())
