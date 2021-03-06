''' A non-blocking, encrypted TCP echo server. 
Script requires passing of two parameters:
*   str: filepath of config file
*   str: password used by clients for decryption
'''

__author__ = 'Adrian Agnic'
__version__ = '0.0.5'

import sys
import socket
import struct
import select
import queue
import hashlib
import configparser
from Crypto.Cipher import AES
from Crypto import Random


def remove_client(sock):
    addr = sock.getpeername()
    try:
        _i.remove(sock)
        _o.remove(sock)
        sock.close()
    except:
        pass
    del _message_pipeline[sock]
    print(f'Client {addr[0]}:{addr[1]} was removed.')


def encryptor(bmsg):
    ''' Pad message to atleast 16 bytes and encrypt with salt.
    :return[0]: length of message, salt for decryption
    :return[1]: encrypted message data
    '''
    if len(bmsg) % 16 != 0:
        pad_bmsg = bmsg + (' ' * ((16-len(bmsg))%16)).encode()
    else:
        pad_bmsg = bmsg
    IV = Random.new().read(AES.block_size)
    meta_bundle = (len(pad_bmsg), IV)
    cipher = AES.new(__key, AES.MODE_CBC, IV)
    bits = struct.pack('L 16s', *meta_bundle)
    return bits, cipher.encrypt(pad_bmsg)


def main():
    server_sock.bind((cfg['Host'], int(cfg['Port'])))
    server_sock.listen(int(cfg['Backlog']))
    print('\nAwaiting clients.')
    try:
        while _i:
            incoming_data, open_buffers, bad_socks = select.select(_i, _o, _i)
            for sock in incoming_data:
                if sock is server_sock:
                    # new connection pending
                    new_client, addr = sock.accept()
                    new_client.setblocking(False)
                    _i.append(new_client)
                    _message_pipeline[new_client] = queue.Queue()
                    print(f'New client: {addr[0]}:{addr[1]}')
                else:
                    new_msg = sock.recv(int(cfg['BufferSize']))
                    if new_msg:
                        for client in _message_pipeline.keys():
                            if client not in _o:
                                _o.append(client)
                            if client is not sock:
                                _message_pipeline[client].put(new_msg)
                    else:
                        remove_client(sock)
            for sock in open_buffers:
                try:
                    queued_msg = _message_pipeline[sock].get_nowait()
                except queue.Empty:
                    _o.remove(sock)
                else:
                    msg_pack = encryptor(queued_msg)
                    sock.sendall(msg_pack[0])   # expect 24 bytes
                    sock.sendall(msg_pack[1])   # expect msg_pack[0][0] bytes
            for sock in bad_socks:
                remove_client(sock)
    except KeyboardInterrupt:
        server_sock.close()
        print('Server shutdown.')



if __name__ == '__main__':
    parser = configparser.ConfigParser()
    try:
        parser.read(sys.argv[1])
        cfg = parser['TCP']   # NOTE TODO revise for udp
        __key = hashlib.sha256(sys.argv[2].encode()).digest()
    except:
        parser.read('example_config.ini')
        cfg = parser['DEFAULT']
        print('No config file found. Values defaulted\n')
        for k in cfg: print(k,cfg[k])
        __key = hashlib.sha256(sys.argv[1].encode()).digest()

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# move to try for udp
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.setblocking(False)

    _i = [server_sock]
    _o = []
    _message_pipeline = {}

    main()
