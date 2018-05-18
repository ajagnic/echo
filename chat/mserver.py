''' TCP server which maintains client connections and dispatches message data. '''

__author__ = 'Adrian Agnic'
__version__ = '0.0.3'

import sys
import socket
import select
import threading
import queue


_host = sys.argv[1]
_port = sys.argv[2]
_m_sock = None
_message_pipeline = {}
_input = []
_output = []


def initialize_server_socket():
    ''' Creates an IPv4 TCP socket at given host/port.
    Socket is non-blocking and address is reusable.
    '''
    _m_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _m_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    _m_sock.setblocking(False)
    _m_sock.bind((str(_host), int(_port)))
    _input.append(_m_sock)


def remove_client(sock):
    try:
        _input.remove(sock)
        _output.remove(sock)
    except:
        pass
    del _message_pipeline[sock]
    sock.close()


def dispatcher(readables):
    ''' Maintains readable sockets
    Registers new clients and dispatches messages to pipeline.
    '''
    for conn in readables:
        if conn is _m_sock:
            # Server socket readable means a connection is pending.
            new_connection, addr = conn.accept()   # NOTE USE ADDR
            new_connection.setblocking(False)
            _input.append(new_connection)
            # Create message pipeline for this client
            _message_pipeline[new_connection] = queue.Queue()
        else:
            # Client has sent data
            data = conn.recv(2048)
            if data:
                for sock in _message_pipeline.keys():
                    if sock not in _output:
                        _output.append(sock)
                    # Not sending message back to origin
                    if sock is not conn:
                        _message_pipeline[sock].put(data)
            else:
                # Readable socket with no data is closed.
                remove_client(conn)


def pipeline_feed(writables):
    ''' Maintains writable sockets 
    Attempts to progress queue for each client.
    '''
    for conn in writables:
        try:
            next_message = _message_pipeline[conn].get_nowait()
        except queue.Empty:
            if conn in _output:
                _output.remove(conn)
        else:
            conn.send(next_message)


def main():
    ''' Monitors status of every socket.
    Threads off processes to handle readable and writable sockets.
    Removes sockets in error.
    '''
    initialize_server_socket()
    # Backlog up to 5 connections if busy
    _m_sock.listen(5)
    while True:
        readables, writables, in_error = select.select(_input, _output, _input)
        dispatcher_thread = threading.Thread(target=dispatcher, args=(readables,))
        dispatcher_thread.start()
        pipeline_thread = threading.Thread(target=pipeline_feed, args=(writables,))
        pipeline_thread.start()
        for sock in in_error:
            remove_client(sock)
        dispatcher_thread.join()
        pipeline_thread.join()



if __name__ == '__main__':
    main()