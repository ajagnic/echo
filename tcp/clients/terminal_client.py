''' Simple threaded TCP producer/consumer '''

__author__ = 'Adrian Agnic'
__version__ = '0.0.1'

import socket
import threading
import sys


host = str(sys.argv[1])
port = int(sys.argv[2])

client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_sock.connect((host, port))

def receiver():
    while True:
        recv_msg = client_sock.recv(2048)
        if recv_msg:
            print(recv_msg.decode())

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