#!/usr/bin/env python3
"""Anuncia BedrockParty como mundo LAN NetherNet en UDP/7551."""

import os
import secrets
import socket

from nethernet_codec import decode_packet, encode_response, encode_server_data

LISTEN_IP = os.getenv("NETHERNET_LISTEN_IP", "0.0.0.0")
LISTEN_PORT = int(os.getenv("NETHERNET_PORT", "7551"))
SERVER_ID = int(os.getenv("NETHERNET_SERVER_ID", os.getenv("SERVER_GUID", "1234567890123456789")))
SERVER_NAME = os.getenv("NETHERNET_SERVER_NAME", "BedrockParty")
LEVEL_NAME = os.getenv("NETHERNET_LEVEL_NAME", "BedrockParty")
GAME_TYPE = int(os.getenv("NETHERNET_GAME_TYPE", "0"))
PLAYER_COUNT = int(os.getenv("PLAYERS", "0"))
MAX_PLAYER_COUNT = int(os.getenv("MAX_PLAYERS", "10"))
NONCE = os.getenv("NETHERNET_NONCE") or secrets.token_hex(8)


def main():
    server_data = encode_server_data(
        server_name=SERVER_NAME,
        level_name=LEVEL_NAME,
        game_type=GAME_TYPE,
        player_count=PLAYER_COUNT,
        max_player_count=MAX_PLAYER_COUNT,
        editor_world=False,
        hardcore=False,
        accepts_online_auth=True,
        accepts_self_signed_auth=True,
        nonce=NONCE,
        transport_layer=2,
        connection_type=4,
    )
    response = encode_response(SERVER_ID, server_data)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind((LISTEN_IP, LISTEN_PORT))
    print("BedrockParty NetherNet LAN discovery", flush=True)
    print(f"  listen : {LISTEN_IP}:{LISTEN_PORT}/udp", flush=True)
    print(f"  world  : {LEVEL_NAME} / {SERVER_NAME}", flush=True)
    print(f"  id     : {SERVER_ID}", flush=True)
    print(f"  nonce  : {NONCE}", flush=True)

    while True:
        datagram, address = sock.recvfrom(65535)
        try:
            packet_id, sender_id, data = decode_packet(datagram)
        except ValueError as exc:
            print(f"NETHERNET invalid from {address[0]}:{address[1]}: {exc}", flush=True)
            continue
        if sender_id == SERVER_ID:
            continue
        if packet_id == 0:
            sock.sendto(response, address)
            print(
                f"NETHERNET discovery from {address[0]}:{address[1]} "
                f"sender={sender_id} response_bytes={len(response)}",
                flush=True,
            )
        elif packet_id == 2:
            print(
                f"NETHERNET signaling from {address[0]}:{address[1]} "
                f"sender={sender_id} bytes={len(data)} (session bridge pending)",
                flush=True,
            )


if __name__ == "__main__":
    main()
