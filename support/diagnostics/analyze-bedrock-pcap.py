#!/usr/bin/env python3
"""Summarize UDP/RakNet flows and MCPE advertisements from a classic PCAP."""

import argparse
import collections
import hashlib
import ipaddress
import json
import struct
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("pcap")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--backend-ip", default="192.168.1.10")
    return parser.parse_args()


def iter_pcap(path):
    with Path(path).open("rb") as stream:
        header = stream.read(24)
        if len(header) != 24:
            raise ValueError("PCAP has an incomplete header")
        magic = header[:4]
        if magic == b"\xd4\xc3\xb2\xa1":
            endian = "<"
        elif magic == b"\xa1\xb2\xc3\xd4":
            endian = ">"
        else:
            raise ValueError("Unrecognized format; classic PCAP is required")
        _, _, _, _, _, linktype = struct.unpack(endian + "HHIIII", header[4:])
        while True:
            record = stream.read(16)
            if not record:
                break
            if len(record) != 16:
                raise ValueError("Truncated PCAP record")
            seconds, microseconds, captured_length, original_length = struct.unpack(
                endian + "IIII", record
            )
            packet = stream.read(captured_length)
            if len(packet) != captured_length:
                raise ValueError("Truncated PCAP packet")
            yield linktype, seconds + microseconds / 1_000_000, packet, original_length


def parse_udp(linktype, packet):
    if linktype == 1:
        if len(packet) < 14:
            return None
        ether_type = struct.unpack("!H", packet[12:14])[0]
        ip_offset = 14
        if ether_type == 0x8100 and len(packet) >= 18:
            ether_type = struct.unpack("!H", packet[16:18])[0]
            ip_offset = 18
        if ether_type != 0x0800:
            return None
    elif linktype == 101:
        ip_offset = 0
    else:
        raise ValueError(f"Unsupported link type: {linktype}")

    if len(packet) < ip_offset + 28 or packet[ip_offset] >> 4 != 4:
        return None
    ihl = (packet[ip_offset] & 0x0F) * 4
    if ihl < 20 or packet[ip_offset + 9] != 17:
        return None
    udp_offset = ip_offset + ihl
    if len(packet) < udp_offset + 8:
        return None
    source_ip = str(ipaddress.ip_address(packet[ip_offset + 12 : ip_offset + 16]))
    destination_ip = str(ipaddress.ip_address(packet[ip_offset + 16 : ip_offset + 20]))
    source_port, destination_port, udp_length = struct.unpack("!HHH", packet[udp_offset : udp_offset + 6])
    payload = packet[udp_offset + 8 : udp_offset + udp_length]
    return source_ip, source_port, destination_ip, destination_port, payload


def parse_pong(payload):
    if len(payload) < 35 or payload[0] != 0x1C:
        return None
    advertised_length = struct.unpack(">H", payload[33:35])[0]
    text_bytes = payload[35 : 35 + advertised_length]
    text = text_bytes.decode("utf-8", errors="replace")
    return {
        "ping_time": struct.unpack(">Q", payload[1:9])[0],
        "server_guid": struct.unpack(">Q", payload[9:17])[0],
        "magic": payload[17:33].hex(),
        "advertised_length": advertised_length,
        "payload": text,
        "fields": text.split(";"),
        "datagram_hex": payload.hex(),
    }


def main():
    args = parse_args()
    flows = collections.defaultdict(lambda: {"count": 0, "bytes": 0, "min": None, "max": 0, "first": None, "last": None})
    advertisements = []
    relay_payloads = {
        "client_to_proxy": [],
        "proxy_to_backend": [],
        "backend_to_proxy": [],
        "proxy_to_client": [],
    }
    total_packets = 0
    total_bytes = 0
    first_timestamp = None
    last_timestamp = None

    for linktype, timestamp, packet, _ in iter_pcap(args.pcap):
        parsed = parse_udp(linktype, packet)
        if parsed is None:
            continue
        source_ip, source_port, destination_ip, destination_port, payload = parsed
        packet_id = payload[0] if payload else None
        key = (source_ip, source_port, destination_ip, destination_port, packet_id)
        item = flows[key]
        item["count"] += 1
        item["bytes"] += len(payload)
        item["min"] = len(payload) if item["min"] is None else min(item["min"], len(payload))
        item["max"] = max(item["max"], len(payload))
        item["first"] = timestamp if item["first"] is None else item["first"]
        item["last"] = timestamp
        total_packets += 1
        total_bytes += len(payload)
        first_timestamp = timestamp if first_timestamp is None else first_timestamp
        last_timestamp = timestamp
        pong = parse_pong(payload)
        if pong:
            pong.update(source=f"{source_ip}:{source_port}", destination=f"{destination_ip}:{destination_port}", timestamp=timestamp)
            if not any(existing["datagram_hex"] == pong["datagram_hex"] for existing in advertisements):
                advertisements.append(pong)
        if packet_id not in (0x01, 0x02, 0x1C):
            digest = hashlib.sha256(payload).hexdigest()
            if destination_ip == args.backend_ip and destination_port == 19132:
                relay_payloads["proxy_to_backend"].append(digest)
            elif source_ip == args.backend_ip and source_port == 19132:
                relay_payloads["backend_to_proxy"].append(digest)
            elif destination_port == 19132:
                relay_payloads["client_to_proxy"].append(digest)
            elif source_port == 19132:
                relay_payloads["proxy_to_client"].append(digest)

    flow_rows = []
    for key, item in sorted(flows.items(), key=lambda pair: (-pair[1]["count"], pair[0])):
        source_ip, source_port, destination_ip, destination_port, packet_id = key
        flow_rows.append(
            {
                "source": f"{source_ip}:{source_port}",
                "destination": f"{destination_ip}:{destination_port}",
                "packet_id": packet_id,
                **item,
            }
        )
    relay_comparison = {
        "client_to_backend": {
            "input_packets": len(relay_payloads["client_to_proxy"]),
            "output_packets": len(relay_payloads["proxy_to_backend"]),
            "payload_multiset_equal": collections.Counter(relay_payloads["client_to_proxy"])
            == collections.Counter(relay_payloads["proxy_to_backend"]),
        },
        "backend_to_client": {
            "input_packets": len(relay_payloads["backend_to_proxy"]),
            "output_packets": len(relay_payloads["proxy_to_client"]),
            "payload_multiset_equal": collections.Counter(relay_payloads["backend_to_proxy"])
            == collections.Counter(relay_payloads["proxy_to_client"]),
        },
    }
    result = {
        "file": str(Path(args.pcap).resolve()),
        "packets": total_packets,
        "payload_bytes": total_bytes,
        "duration_seconds": 0 if first_timestamp is None else round(last_timestamp - first_timestamp, 6),
        "flows": flow_rows,
        "advertisements": advertisements,
        "relay_comparison": relay_comparison,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"PCAP: {result['file']}")
        print(f"UDP Bedrock: {total_packets} packets, {total_bytes} payload bytes, {result['duration_seconds']} s")
        print("Flows by ID (sorted by count):")
        for row in flow_rows:
            packet_id = "empty" if row["packet_id"] is None else f"0x{row['packet_id']:02x}"
            print(
                f"  {row['source']} -> {row['destination']} id={packet_id} "
                f"count={row['count']} bytes={row['bytes']} size={row['min']}..{row['max']}"
            )
        print(f"Unique advertisements: {len(advertisements)}")
        for advertisement in advertisements:
            print(f"  {advertisement['source']} -> {advertisement['destination']}")
            print(f"  payload={advertisement['payload']}")
            print(f"  hex={advertisement['datagram_hex']}")
            for index, field in enumerate(advertisement["fields"]):
                print(f"    [{index:02}] {field}")
        print("Byte-for-byte relay comparison (SHA-256 per payload):")
        for direction, comparison in relay_comparison.items():
            print(
                f"  {direction}: in={comparison['input_packets']} "
                f"out={comparison['output_packets']} equal={comparison['payload_multiset_equal']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
