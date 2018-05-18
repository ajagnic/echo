''' TCP server which maintains client connections and dispatches message data. '''

__author__ = 'Adrian Agnic'
__version__ = '0.0.3'

import sys
import socket
import select
import threading
import queue
from .services.jenkins import Jenkins


_host = sys.argv[1]
_port = sys.argv[2]
_m_sock = None
_input = []
_output = []
_message_pipeline = {}
_lock = threading.Lock()
_jenkins = Jenkins()


def remove_client(sock):
    _jenkins.alert_removing_client(sock)
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
            new_connection, addr = conn.accept()
            new_connection.setblocking(False)
            _lock.acquire()
            _input.append(new_connection)
            _jenkins.alert_new_client(new_connection)
            # Create message pipeline for this client
            _message_pipeline[new_connection] = queue.Queue()
            _lock.release()
        else:
            # Client has sent data
            data = conn.recv(2048)
            if data:
                _lock.acquire()
                _jenkins.alert_new_message(conn)
                for sock in _message_pipeline.keys():
                    if sock not in _output:
                        _output.append(sock)
                    # Not sending message back to origin
                    if sock is not conn:
                        _message_pipeline[sock].put(data)
                _lock.release()
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
            _jenkins.alert_empty_queue(conn)
            if conn in _output:
                _output.remove(conn)
        else:
            conn.send(next_message)


def main():
    ''' Creates a reusable, non-blocking IPv4 TCP socket at given host/port.
    Monitors status of every client.
    Threads off processes to handle readable and writable sockets.
    Removes sockets in error.
    '''
    _m_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _m_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    _m_sock.setblocking(False)
    _m_sock.bind((str(_host), int(_port)))
    _jenkins.server_start_msg(_host, _port)
    _input.append(_m_sock)
    # Backlog up to 5 connections if busy
    _m_sock.listen(5)
    i = 0
    while i < 20:
        readables, writables, in_error = select.select(_input, _output, _input)
        if readables:
            dispatcher_thread = threading.Thread(target=dispatcher, args=(readables,))
            dispatcher_thread.start()
        if writables:
            pipeline_thread = threading.Thread(target=pipeline_feed, args=(writables,))
            pipeline_thread.start()
        for sock in in_error:
            remove_client(sock)
        try:
            dispatcher_thread.join()
            pipeline_thread.join()
        except:
            pass
        i = i + 1



if __name__ == '__main__':
    main()