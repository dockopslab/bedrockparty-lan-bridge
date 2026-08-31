"""Minimal codec for NetherNet LAN discovery packets."""

import hashlib
import hmac
import struct

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

KEY = hashlib.sha256(struct.pack("<Q", 0xDEADBEEF)).digest()


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


def write_varuint(value):
    encoded = bytearray()
    while value >= 0x80:
        encoded.append((value & 0x7F) | 0x80)
        value >>= 7
    encoded.append(value)
    return bytes(encoded)


def write_varint(value):
    unsigned = (value << 1) if value >= 0 else ~(value << 1)
    return write_varuint(unsigned & 0xFFFFFFFF)


def write_string(value):
    encoded = value.encode("utf-8")
    return write_varuint(len(encoded)) + encoded


def encode_server_data(
    server_name,
    level_name,
    game_type,
    player_count,
    max_player_count,
    editor_world,
    hardcore,
    accepts_online_auth,
    accepts_self_signed_auth,
    nonce,
    transport_layer=2,
    connection_type=4,
):
    return b"".join(
        (
            b"\x06",
            write_string(server_name),
            write_string(level_name),
            write_varint(game_type),
            struct.pack("<ii", player_count, max_player_count),
            bytes(
                (
                    bool(editor_world),
                    bool(hardcore),
                    bool(accepts_online_auth),
                    bool(accepts_self_signed_auth),
                )
            ),
            write_string(nonce),
            write_varint(transport_layer),
            write_varint(connection_type),
        )
    )


def encode_response(sender_id, server_data):
    application_data = server_data.hex().encode("ascii")
    response_data = struct.pack("<I", len(application_data)) + application_data
    return encode_packet(1, sender_id, response_data)
