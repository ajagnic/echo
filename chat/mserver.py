__author__ = 'Adrian Agnic'
__version__ = '0.0.1'

import socket
import select


_host = '127.0.0.1'
_port = 8888
_message_pipeline = {}
_input = []
_output = []

_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
_server_socket.setblocking(False)
_server_socket.bind((str(_host), int(_port)))
_input.append(_server_socket)


def main():
    _server_socket.listen(5)



if __name__ == '__main__':
    main()
else:
    _server_socket.close()