''' A non-blocking TCP echo server script. 
Script requires passing of three parameters:
*   str: hostname for server
*   int: port number to bind to
*   str: password required for new clients
'''

__author__ = 'Adrian Agnic'
__version__ = '0.0.5'

import socket
import select
import queue
import sys
import hashlib
from Crypto.Cipher import AES
from Crypto import Random


_host = str(sys.argv[1])
_port = int(sys.argv[2])
try:
    __key = str(sys.argv[3]).encode()
except:
    print('Provide a server connection password.')
    sys.exit()

_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
_server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
_server_sock.setblocking(False)
_server_sock.bind((_host, _port))
print(f'Binded socket object:\n{_server_sock}\n\nOn HOST/PORT: {_host}:{_port}\n')

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
    print(f'Client {_message_pipeline[sock][1]} removed.')
    del _message_pipeline[sock]


def encryptor(bmsg):
    salt = Random.new().read(AES.block_size)
    cipher = AES.new(__key, AES.MODE_CFB, salt)
    return cipher.encrypt(bmsg)


def main():
    _server_sock.listen(5)
    print('Awaiting clients.')
    try:
        while _i:
            incoming_data, open_buffers, bad_socks = select.select(_i, _o, _i)
            for sock in incoming_data:
                if sock is _server_sock:
                    # new connection pending
                    new_client, addr = sock.accept()
                    new_client.setblocking(False)
                    _i.append(new_client)
                    _message_pipeline[new_client] = (queue.Queue(), f'{addr[0]}:{addr[1]}')
                else:
                    # incoming message data
                    new_msg = sock.recv(2048)
                    if new_msg:
                        for client in _message_pipeline.keys():
                            if client not in _o:
                                _o.append(client)
                            if client is not sock:
                                origin = _message_pipeline[sock][1]+'\n'
                                _message_pipeline[client][0].put(origin.encode())   # NOTE TODO handle differently
                                _message_pipeline[client][0].put(new_msg)
                    else:
                        # closed connection
                        remove_client(sock)
            for sock in open_buffers:
                # progress pipeline
                try:
                    queued_msg = _message_pipeline[sock][0].get_nowait()
                except queue.Empty:
                    _o.remove(sock)
                else:
                    sock.send(encryptor(queued_msg))
            for sock in bad_socks:
                remove_client(sock)
    except KeyboardInterrupt:
        _server_sock.close()
        print('Server shutdown.')



if __name__ == '__main__':
    main()
else:
    _server_sock.close()
