#!/usr/bin/env python3
"""Query and decode NetherNet LAN discovery on UDP/7551."""

import argparse
import hashlib
import hmac
import json
import secrets
import socket
import struct
import time

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

APPLICATION_ID = 0xDEADBEEF
KEY = hashlib.sha256(struct.pack("<Q", APPLICATION_ID)).digest()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", default="192.168.1.255")
    parser.add_argument("--port", type=int, default=7551)
    parser.add_argument("--source-port", type=int, default=0)
    parser.add_argument("--timeout", type=float, default=3.0)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def encode_packet(packet_id, sender_id, data=b""):
    body = struct.pack("<HQ", packet_id, sender_id) + (b"\x00" * 8) + data
    payload = struct.pack("<H", len(body) + 2) + body
    padder = padding.PKCS7(128).padder()
    padded = padder.update(payload) + padder.finalize()
    encryptor = Cipher(algorithms.AES(KEY), modes.ECB()).encryptor()
    ciphertext = encryptor.update(padded) + encryptor.finalize()
    return hmac.new(KEY, payload, hashlib.sha256).digest() + ciphertext


def decode_packet(datagram):
    if len(datagram) < 48 or (len(datagram) - 32) % 16:
        raise ValueError("invalid encrypted length")
    decryptor = Cipher(algorithms.AES(KEY), modes.ECB()).decryptor()
    padded = decryptor.update(datagram[32:]) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    payload = unpadder.update(padded) + unpadder.finalize()
    expected = hmac.new(KEY, payload, hashlib.sha256).digest()
    if not hmac.compare_digest(datagram[:32], expected):
        raise ValueError("invalid HMAC")
    declared_length = struct.unpack("<H", payload[:2])[0]
    if declared_length != len(payload):
        raise ValueError(f"declared length {declared_length}, actual {len(payload)}")
    packet_id, sender_id = struct.unpack("<HQ", payload[2:12])
    return packet_id, sender_id, payload[20:]


def read_varuint(data, offset):
    value = 0
    for shift in range(0, 35, 7):
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, offset
    raise ValueError("invalid varuint32")


def read_varint(data, offset):
    value, offset = read_varuint(data, offset)
    decoded = value >> 1
    if value & 1:
        decoded = ~decoded
    return decoded, offset


def read_string(data, offset):
    length, offset = read_varuint(data, offset)
    end = offset + length
    if end > len(data):
        raise ValueError("cadena truncada")
    return data[offset:end].decode("utf-8", errors="replace"), end


def decode_server_data(data):
    offset = 0
    version = data[offset]
    offset += 1
    server_name, offset = read_string(data, offset)
    level_name, offset = read_string(data, offset)
    game_type, offset = read_varint(data, offset)
    player_count, max_player_count = struct.unpack("<ii", data[offset : offset + 8])
    offset += 8
    editor_world = bool(data[offset])
    offset += 1
    result = {
        "version": version,
        "server_name": server_name,
        "level_name": level_name,
        "game_type": game_type,
        "player_count": player_count,
        "max_player_count": max_player_count,
        "editor_world": editor_world,
    }
    if version >= 6:
        result["hardcore"] = bool(data[offset])
        result["accepts_online_auth"] = bool(data[offset + 1])
        result["accepts_self_signed_auth"] = bool(data[offset + 2])
        offset += 3
        result["nonce"], offset = read_string(data, offset)
    result["transport_layer"], offset = read_varint(data, offset)
    if offset < len(data):
        result["connection_type"], offset = read_varint(data, offset)
    result["remaining_hex"] = data[offset:].hex()
    return result


def decode_response_data(data):
    if len(data) < 4:
        raise ValueError("truncated response")
    text_length = struct.unpack("<I", data[:4])[0]
    text = data[4 : 4 + text_length]
    application_data = bytes.fromhex(text.decode("ascii"))
    return application_data, decode_server_data(application_data)


def main():
    args = parse_args()
    sender_id = secrets.randbits(64)
    request = encode_packet(0, sender_id)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", args.source_port))
    sock.settimeout(args.timeout)
    sock.sendto(request, (args.target, args.port))
    deadline = time.monotonic() + args.timeout
    responses = 0
    while time.monotonic() < deadline:
        try:
            datagram, address = sock.recvfrom(65535)
        except socket.timeout:
            break
        try:
            packet_id, response_sender_id, data = decode_packet(datagram)
            result = {
                "source_ip": address[0],
                "source_port": address[1],
                "length": len(datagram),
                "datagram_hex": datagram.hex(),
                "packet_id": packet_id,
                "sender_id": response_sender_id,
                "request_sender_id": sender_id,
            }
            if packet_id == 1:
                application_data, server_data = decode_response_data(data)
                result["application_data_hex"] = application_data.hex()
                result["server_data"] = server_data
            else:
                result["data_hex"] = data.hex()
        except (ValueError, IndexError) as exc:
            result = {
                "source_ip": address[0],
                "source_port": address[1],
                "length": len(datagram),
                "datagram_hex": datagram.hex(),
                "error": str(exc),
            }
        responses += 1
        if args.json:
            print(json.dumps(result, ensure_ascii=False))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.json:
        print(f"Responses: {responses}")
    return 0 if responses else 2


if __name__ == "__main__":
    raise SystemExit(main())
