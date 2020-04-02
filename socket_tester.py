from socket import *


test_socket = socket(AF_INET, SOCK_DGRAM)
test_socket.bind((gethostname(), 5002))
test_socket.sendto(bytes("Hello World", 'utf-8'), (gethostname(), 6110))
