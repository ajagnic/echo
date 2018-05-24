''' tests require Mserver running separately '''

import unittest
import socket


class test_mserver(unittest.TestCase):
    def setUp(self):
        self.test_socket = socket.socket()
    
    def test_connect(self):
        self.test_socket.connect(('127.0.0.1', 55555))

    def test_message_pipeline(self):
        producer_socket = socket.socket()
        producer_socket.connect(('127.0.0.1', 55555))
        self.test_connect()
        producer_socket.send("test".encode())
        origin = producer_socket.getsockname()
        test_recv_msg = f'{origin[0]}:{origin[1]}'
        received_msg = None
        while received_msg is None:
            received_msg = self.test_socket.recv(1024)
            decoded_msg = received_msg.decode()
            edited_msg = decoded_msg[0:len(test_recv_msg)]
        self.assertEqual(test_recv_msg, edited_msg)
        producer_socket.close()

    def tearDown(self):
        self.test_socket.close()
