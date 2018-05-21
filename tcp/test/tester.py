import socket
import threading
import time
import random


def run_client():
    sck = socket.socket()
    sck.connect(('127.0.0.1', 55555))
    time.sleep(1)
    for i in range(10):
        time.sleep(0.5)
        sck.send(('heres a random number: ' + str(random.random())).encode())
    sck.close()


t1 = threading.Thread(target=run_client)
t2 = threading.Thread(target=run_client)
t3 = threading.Thread(target=run_client)
t4 = threading.Thread(target=run_client)
t5 = threading.Thread(target=run_client)

t_list = [t1,t2,t3,t4,t5]

for t in t_list:
    t.start()
