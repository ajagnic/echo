import socket
import threading
import time
import random


def message_dispatch(sock):
    for i in range(10):
        time.sleep(random.random())
        sock.send(("testing" + str(random.random())).encode())


sock = socket.socket()

sock.connect(("127.0.0.1", 6999))

print("connected")

sock_thread = threading.Thread(target=message_dispatch, args=(sock,))
sock_thread.start()

try:
    while True:
        msg = sock.recv(1024)
        if msg:
            print(msg.decode())
except KeyboardInterrupt:
    sock_thread.join()
    sock.close()
else:
    pass