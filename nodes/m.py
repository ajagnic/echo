import socket
import threading
import sys

__author__ = 'Adrian Agnic'
__version__ = '0.0.1'


HOST = sys.argv[1]
PORT = sys.argv[2]
M_SCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
M_SCK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
CONNS = []
IP_LIST = []

def echo(con):
    print('::THREAD...::')
    while True:
        msg = con.recv(1024)
        if msg is None:
            print('::EXITING::')
            break
        print(f'::MSG:: {msg.decode()}')
        for client in CONNS:
            client.send(msg)

def listen():
    M_SCK.bind((str(HOST), int(PORT)))
    M_SCK.listen(5)
    print('::BINDED, LISTENING...::')
    while True:
        conn, addr = M_SCK.accept()
        print(f'::CONNECTION::...{addr[0]}:{addr[1]}')
        CONNS.append(conn)
        IP_LIST.append(addr)
        t = threading.Thread(target=echo, args=(conn,))
        t.start()


if __name__ == '__main__':
    listen()