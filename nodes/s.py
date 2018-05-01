''' client for producing/consuming messages to tcp server '''
import socket
import threading
import sys

__author__ = 'Adrian Agnic'
__version__ = '0.0.1'


REM_HOST = sys.argv[1]
REM_PORT = sys.argv[2]
S_SCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
S_SCK.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

def response_handler():
    while True:
        msg = S_SCK.recv(1024)
        if msg is not None:
            print(f"::MSG:: {msg.decode('utf-8')}")

def chat():
    S_SCK.connect((str(REM_HOST), int(REM_PORT)))
    print('::CONNECTED::')
    t = threading.Thread(target=response_handler)
    t.start()
    while True:
        msg = input()
        S_SCK.send(msg.encode('utf-8'))


if __name__ == '__main__':
    chat()