import unittest
import socket

class test_mserver(unittest.TestCase):
    def setUp(self):
        self.test_socket = socket.socket()

    def test_connect(self):
        self.test_socket.connect(('127.0.0.1', 8888))

    def tearDown(self):
        self.test_socket.close()
