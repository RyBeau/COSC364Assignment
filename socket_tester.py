from socket import *
from time import sleep

test_socket = socket(AF_INET, SOCK_DGRAM)
test_socket.bind((gethostname(), 5002))
while True:
    test_socket.sendto(bytes("Hello World 1", 'utf-8'), (gethostname(), 6110))
    sleep(1)
    test_socket.sendto(bytes("Hello World 2", 'utf-8'), (gethostname(), 6201))
    sleep(1)
    test_socket.sendto(bytes("Hello World 3", 'utf-8'), (gethostname(), 7345))
    sleep(1)
