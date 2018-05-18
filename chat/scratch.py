import socket
import threading

sck = socket.socket()

sck.bind(('127.0.0.1', 8888))

sck.listen(5)

print(sck)

def handle(sock):
    while True:
        msg = sock.recv(1024)
        if msg:
            print(msg.decode())

while True:
    conn, addr = sck.accept()
    print(addr)
    t = threading.Thread(target=handle, args=(conn,))
    t.start()
    print('threaded')
