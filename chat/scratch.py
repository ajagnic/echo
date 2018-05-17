'''
TCP SERVER SCRIPT WHICH MAINTAINS SOCKET CONNECTIONS AND THREADS OFF BY EVENT: NEW CONNECTION, NEW MESSAGE, OR CLOSED CONNECTION
'''
import socket
import queue
from threading import Thread
from select import select
from sys import argv

__author__ = 'Adrian Agnic'
__version__ = '0.0.1'


HOST = argv[1]
PORT = argv[2]
socket_list = []
message_pipeline = {}


def readable_socket_handler(readables_list, server_socket):
    for sock in readables_list:
        if sock is server_socket:
            # server socket readable means a new connection is pending
            new_connection, addr = sock.accept()
            print("server new connection")
            new_connection.setblocking(False)
            # build list of connections
            socket_list.append(new_connection)
            # init queues for msg data since await for writable state
            message_pipeline[new_connection] = queue.Queue()
        else:
            # client has sent message data
            client_message = sock.recv(1024)
            if client_message:
                for conn in message_pipeline.keys():
                    # check not sending back to origin
                    if conn is not sock:
                        message_pipeline[conn].put(client_message)
            else:
                # readable socket w/ no data is closed
                socket_list.remove(sock)
                del message_pipeline[sock]
                sock.close()


def main():
    # initialize a reusable, non-blocking IPv4/TCP socket on given host and port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.setblocking(False)
    server_socket.bind((str(HOST), int(PORT)))
    socket_list.append(server_socket)
    # backlog up to 5 connections if busy
    server_socket.listen(5)
    # monitor known sockets for events
    while True:
        read_sockets, write_sockets, error_sockets = select(socket_list, socket_list, socket_list)
        read_thread = Thread(target=readable_socket_handler, args=(read_sockets,server_socket))
        read_thread.start()
        for sock in write_sockets:
            # try advancing message queue of writable sockets
            try:
                next_msg = message_pipeline[sock].get_nowait()
            except queue.Empty:
                pass
            else:
                print(next_msg.decode())
                sock.send(next_msg)
        for sock in error_sockets:
            # remove all sockets in error
            socket_list.remove(sock)
            del message_pipeline[sock]
            sock.close()
        read_thread.join()



if __name__ == '__main__':
    main()
