''' Simple threaded TCP producer/consumer '''

__author__ = 'Adrian Agnic'
__version__ = '0.0.1'

import socket
import threading
import sys
import struct
import hashlib
from Crypto.Cipher import AES


host = str(sys.argv[1])
port = int(sys.argv[2])
__key = hashlib.sha256(str(sys.argv[3]).encode()).digest()

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect((host, port))

def receiver():
    bits = None
    while True:
        if bits is None:
            bits = client_sock.recv(24)
            unpacked_bits = struct.unpack('L 16s', bits)
            cipher = AES.new(__key, AES.MODE_CBC, unpacked_bits[1])
            msg = client_sock.recv(unpacked_bits[0])
            print(cipher.decrypt(msg))
            bits = None

t = threading.Thread(target=receiver)
t.daemon = True
t.start()

try:
    while True:
        msg = input()
        if msg:
            client_sock.send(msg.encode())
except KeyboardInterrupt:
    client_sock.close()