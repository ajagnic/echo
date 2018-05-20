''' tbd '''

__author__ = 'Adrian Agnic'
__version__ = '0.0.1'

import socket
import select
import queue

_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
_server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
_server_sock.setblocking(False)
_server_sock.bind(('127.0.0.1', 8888))

_i = [_server_sock]
_o = []
_message_pipeline = {}


def remove_client(sock):
    try:
        _i.remove(sock)
        _o.remove(sock)
        sock.close()
    except:
        pass
    del _message_pipeline[sock]


def main():
    _server_sock.listen(5)
    while _i:
        incoming_data, open_buffers, bad_socks = select.select(_i, _o, _i)
        for sock in incoming_data:
            if sock is _server_sock:
                # new connection pending
                new_client, addr = sock.accept()
                new_client.setblocking(False)
                _i.append(new_client)
                _message_pipeline[new_client] = queue.Queue()
            else:
                # incoming message data
                new_msg = sock.recv(2048)
                if new_msg:
                    for client in _message_pipeline.keys():
                        if client not in _o:
                            _o.append(client)
                        if client is not sock:
                            _message_pipeline[client].put(new_msg)
                else:
                    # closed connection
                    remove_client(sock)
        for sock in open_buffers:
            # progress pipeline
            try:
                queued_msg = _message_pipeline[sock].get_nowait()
            except queue.Empty:
                _o.remove(sock)
            else:
                sock.send(queued_msg)
        for sock in bad_socks:
            remove_client(sock)



if __name__ == '__main__':
    main()
else:
    _server_sock.close()