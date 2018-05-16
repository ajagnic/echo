'''
TCP SERVER WHICH MAINTAINS SOCKET CONNECTIONS AND THREADS OFF BY EVENT: NEW CONNECTION, NEW MESSAGE, OR CLOSED CONNECTION
'''
import socket
from threading import Thread
from select import select
from sys import argv

__author__ = 'Adrian Agnic'
__version__ = '0.0.1'


#MAIN
#initialize a reusable, non-blocking IPv4/TCP socket on given host and port
HOST = argv[1]
PORT = argv[2]
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.setblocking(False)
