#!/usr/bin/env python3
import os
import socket
import struct
import threading
import time
import secrets

LISTEN_IP = os.getenv('LISTEN_IP', '0.0.0.0')
LISTEN_PORT = int(os.getenv('LISTEN_PORT', '19132'))
BACKEND_IP = os.getenv('BACKEND_IP', '127.0.0.1')
BACKEND_PORT = int(os.getenv('BACKEND_PORT', '19132'))
MOTD = os.getenv('MOTD', 'BedrockParty')
SUB_MOTD = os.getenv('SUB_MOTD', 'BedrockParty')
PROTOCOL = os.getenv('PROTOCOL', '1001')
VERSION = os.getenv('VERSION', '1.26.32')
PLAYERS = os.getenv('PLAYERS', '0')
MAX_PLAYERS = os.getenv('MAX_PLAYERS', '10')
GAMEMODE = os.getenv('GAMEMODE', 'Survival')
GAMEMODE_NUM = os.getenv('GAMEMODE_NUM', '1')
IPV6_PORT = os.getenv('IPV6_PORT', '19133')
EXTRA_FIELDS = os.getenv('EXTRA_FIELDS', '0;1;0')
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '60'))
LOG_DISCOVERY = os.getenv('LOG_DISCOVERY', 'false').lower() in ('1', 'true', 'yes', 'on')

RAKNET_MAGIC = bytes.fromhex('00ffff00fefefefefdfdfdfd12345678')
SERVER_GUID = int(os.getenv('SERVER_GUID', str(secrets.randbits(63))))

sessions = {}
sessions_lock = threading.Lock()
main_sock = None


def advertisement():
    fields = [
        'MCPE', MOTD, PROTOCOL, VERSION, PLAYERS, MAX_PLAYERS,
        str(SERVER_GUID), SUB_MOTD, GAMEMODE, GAMEMODE_NUM,
        str(LISTEN_PORT), str(IPV6_PORT)
    ]
    base = ';'.join(fields)
    if EXTRA_FIELDS:
        base += ';' + EXTRA_FIELDS.strip(';')
    return (base + ';').encode('utf-8')


def make_pong(data: bytes) -> bytes:
    # RakNet ID_UNCONNECTED_PONG (0x1c)
    # Echo the 8-byte ping time from the request when available.
    if len(data) >= 9:
        ping_time = data[1:9]
    else:
        ping_time = struct.pack('>Q', int(time.time() * 1000) & 0xffffffffffffffff)
    ad = advertisement()
    return (
        b'\x1c' + ping_time + struct.pack('>Q', SERVER_GUID) +
        RAKNET_MAGIC + struct.pack('>H', len(ad)) + ad
    )


def backend_reader(client_addr, backend_sock):
    global main_sock
    try:
        while True:
            backend_sock.settimeout(SESSION_TIMEOUT)
            try:
                payload = backend_sock.recv(65535)
            except socket.timeout:
                break
            if not payload:
                break
            main_sock.sendto(payload, client_addr)
    except OSError:
        pass
    finally:
        with sessions_lock:
            current = sessions.get(client_addr)
            if current is backend_sock:
                sessions.pop(client_addr, None)
        try:
            backend_sock.close()
        except OSError:
            pass


def get_backend_session(client_addr):
    with sessions_lock:
        sock = sessions.get(client_addr)
        if sock is not None:
            return sock
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect((BACKEND_IP, BACKEND_PORT))
        sessions[client_addr] = sock
        threading.Thread(
            target=backend_reader,
            args=(client_addr, sock),
            daemon=True,
            name=f'backend-{client_addr[0]}:{client_addr[1]}'
        ).start()
        return sock


def main():
    global main_sock
    main_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    main_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    main_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    main_sock.bind((LISTEN_IP, LISTEN_PORT))

    print('BedrockParty LAN proxy', flush=True)
    print(f'  listen : {LISTEN_IP}:{LISTEN_PORT}/udp', flush=True)
    print(f'  backend: {BACKEND_IP}:{BACKEND_PORT}/udp', flush=True)
    print(f'  advert : {advertisement().decode()}', flush=True)
    print(f'  guid   : {SERVER_GUID}', flush=True)

    while True:
        data, client_addr = main_sock.recvfrom(65535)
        if not data:
            continue

        packet_id = data[0]

        # Standard RakNet LAN discovery pings. Answer locally instead of
        # forwarding them to the dedicated server so the proxy owns the LAN ad.
        if packet_id in (0x01, 0x02):
            try:
                if LOG_DISCOVERY:
                    print(
                        f'DISCOVERY id=0x{packet_id:02x} from '
                        f'{client_addr[0]}:{client_addr[1]} bytes={len(data)}',
                        flush=True
                    )
                main_sock.sendto(make_pong(data), client_addr)
            except OSError as exc:
                print(f'PONG error to {client_addr}: {exc}', flush=True)
            continue

        # Everything else is proxied to the real BDS using a per-client UDP
        # socket so replies can be mapped back to the originating client.
        try:
            backend = get_backend_session(client_addr)
            backend.send(data)
        except OSError as exc:
            print(f'Proxy error {client_addr} -> {BACKEND_IP}:{BACKEND_PORT}: {exc}', flush=True)
            with sessions_lock:
                old = sessions.pop(client_addr, None)
            if old:
                try:
                    old.close()
                except OSError:
                    pass


if __name__ == '__main__':
    main()
