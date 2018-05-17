'''
TCP SERVER SCRIPT WHICH MAINTAINS SOCKET CONNECTIONS AND THREADS OFF BY EVENT: NEW CONNECTION, NEW MESSAGE, OR CLOSED CONNECTION
'''
import socket
from threading import Thread
from select import select
from sys import argv
from queue import Queue

__author__ = 'Adrian Agnic'
__version__ = '0.0.1'


def main():
    HOST = argv[1]
    PORT = argv[2]
    sel_inputs = []
    sel_outputs = []
    message_pipeline = {}
    # initialize a reusable, non-blocking IPv4/TCP socket on given host and port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setblocking(False)
    server_socket.bind((str(HOST), int(PORT)))
    # backlog up to 5 connections if busy
    server_socket.listen(5)
    # monitor known sockets for events
    while True: # NOTE TODO: ~~~~~~~~CHECK THREADING FOR EACH LIST LOOP~~~~~~~~~
        read_sockets, write_sockets, error_sockets = select(sel_inputs, sel_outputs, sel_inputs)
        for sock in read_sockets:
            if sock is server_socket:
                # server socket readable means a new connection is pending
                new_connection, addr = sock.accept()
                new_connection.setblocking(False)
                # build list of connections
                sel_inputs.append(new_connection)
                # init queues for msg data since await for writable state
                message_pipeline[new_connection] = Queue()
            else:
                # client has sent messge data
                client_message = sock.recv(1024)
                if client_message:
                    for conn in message_pipeline.keys():
                        # check not sending back to origin
                        if conn is not sock:
                            message_pipeline[conn].put(client_message)
                else:
                    # readable socket w/ no data is closed
                    if sock in sel_outputs:
                        sel_outputs.remove(sock)
                    if sock in sel_inputs:
                        sel_inputs.remove(sock)
                    del message_pipeline[sock]
                    sock.close()


if __name__ == '__main__':
    main()