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


host = str(sys.argv[1])
port = int(sys.argv[2])
__key = hashlib.sha256(str(sys.argv[3]).encode()).digest()

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_sock.setblocking(False)
server_sock.bind((host, port))
print(f'\nBinded socket object:\n{server_sock}\n\nOn HOST/PORT: {host}:{port}\n')

_i = [server_sock]
_o = []
_message_pipeline = {}


def remove_client(sock):
    try:
        _i.remove(sock)
        _o.remove(sock)
        sock.close()
    except:
        pass
    print('Client '+ _message_pipeline[sock]['addr'] +' was removed.')
    del _message_pipeline[sock]


def encryptor(bmsg):
    IV = Random.new().read(AES.block_size)
    cipher = AES.new(__key, AES.MODE_CBC, IV)
    if len(bmsg) % 16 != 0:
        pad_bmsg = bmsg + (' ' * ((16-len(bmsg))%16)).encode()
    else:
        pad_bmsg = bmsg
    return cipher.encrypt(pad_bmsg), IV   # return bmsg packed w/ IV, origin


def main():
    server_sock.listen(5)
    print('Awaiting clients.')
    try:
        while _i:
            incoming_data, open_buffers, bad_socks = select.select(_i, _o, _i)
            for sock in incoming_data:
                if sock is server_sock:
                    new_client, addr = sock.accept()
                    new_client.setblocking(False)
                    _i.append(new_client)
                    _message_pipeline[new_client] = {'q': queue.Queue(), 'addr': f'{addr[0]}:{addr[1]}'}
                    print(f'New client: {addr[0]}:{addr[1]}')
                else:
                    new_msg = sock.recv(2048)
                    if new_msg:
                        for client in _message_pipeline.keys():
                            if client not in _o:
                                _o.append(client)
                            if client is not sock:
                                _message_pipeline[client]['q'].put(new_msg)   # use structpack here for origin
                    else:
                        remove_client(sock)
            for sock in open_buffers:
                try:
                    queued_msg = _message_pipeline[sock]['q'].get_nowait()
                except queue.Empty:
                    _o.remove(sock)
                else:
                    sock.send(encryptor(queued_msg))
            for sock in bad_socks:
                remove_client(sock)
    except KeyboardInterrupt:
        server_sock.close()
        print('Server shutdown.')



if __name__ == '__main__':
    main()
else:
    server_sock.close()
