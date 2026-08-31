#!/usr/bin/env python3
import socket
import struct
import time
import secrets

BROADCAST = '192.168.1.255'
PORT = 19132
MAGIC = bytes.fromhex('00ffff00fefefefefdfdfdfd12345678')

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.settimeout(2.0)
sock.bind(('', 0))

stamp = int(time.time() * 1000) & 0xffffffffffffffff
client_guid = secrets.randbits(63)
ping = b'\x01' + struct.pack('>Q', stamp) + MAGIC + struct.pack('>Q', client_guid)

print(f'Looking for Bedrock responses on {BROADCAST}:{PORT}...')
sock.sendto(ping, (BROADCAST, PORT))

seen = set()
while True:
    try:
        data, addr = sock.recvfrom(65535)
    except socket.timeout:
        break
    if addr in seen:
        continue
    seen.add(addr)
    if not data or data[0] != 0x1c:
        print(f'{addr} -> RakNet packet id=0x{data[0]:02x} len={len(data)}')
        continue
    # pong = id(1) + pingtime(8) + guid(8) + magic(16) + strlen(2) + text
    if len(data) < 35:
        print(f'{addr} -> PONG demasiado corto ({len(data)} bytes)')
        continue
    strlen = struct.unpack('>H', data[33:35])[0]
    text = data[35:35+strlen].decode('utf-8', errors='replace')
    print(f'{addr} -> {text}')
print('Fin.')
