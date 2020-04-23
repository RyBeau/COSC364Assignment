"""
Router.py
This is the router class for the COSC364 Assignment.
Author: Ryan Beaumont
"""
from RoutingTable import *
from config import *
from socket import*
from os import _exit
from sys import argv
from select import *


LOCALHOST = gethostname()


def kill_router(code):
    """This procedure shuts down the router/ ends the program"""
    _exit(code)


class Router:
    def __init__(self, router_id, input_ports, output_ports):
        """Initialises starting properties"""
        self.adHeaderLength = 20
        self.ripMaxLength = 520
        self.router_id = router_id
        self.input_ports = input_ports
        self.output_ports = output_ports
        self.router_sockets = self.create_sockets()
        self.routing_table = RoutingTable()

    def __str__(self):
        """This method returns a string detailing the input, output, socket and routing table of the router
        It is intended for debugging purposes"""
        return "Input Ports: {}\nOutput Ports: {}\nSockets: {}\nRouting Table: {}\n".format(self.input_ports,
                                                                                            self.output_ports,
                                                                                            self.router_sockets,
                                                                                            self.routing_table.table)

    def create_sockets(self):
        """This method creates each of the UDP for the input ports"""
        sockets = []
        try:
            for port in self.input_ports:
                sockets.append(socket(AF_INET, SOCK_DGRAM))
                sockets[-1].bind((LOCALHOST, port))
        except:
            print("Error could not open sockets")
            kill_router(1)
        else:
            print("Sockets created on ports: {}".format(self.input_ports))
            return sockets

    def send_message(self, message, address, port_to_use):
        """This method send a RIP message to the given address using the first socket
        in routerSockets"""
        try:
            message_bytes = message[0] << 16 | message[1]
            message_bytes = message_bytes.to_bytes(3, byteorder="big")
            self.router_sockets[port_to_use].sendto(message_bytes, address)
        except error:
            print("Could not send message", error)

    def get_message(self, socket_number):
        """Gets the data received on a socket and the sending address"""
        try:
            message, address = self.router_sockets[socket_number].recvfrom(self.ripMaxLength)
        except:
            print("Socket Timed Out")
        else:
            return message, address

    def get_routing_table(self, neighbour_to_send_to):
        """This method will return the rip entries to be sent in a message using neighbourToSendTo to implement
        split horizon poison reverse"""
        pass

    def update_routing_table(self, rip_entries):
        """This method will send the ripEntries through to the routing table"""
        self.routing_table.update(rip_entries)


def main():
    filename = argv[1]
    router_id, input_ports, output_ports = router_config(filename)
    router = Router(router_id, input_ports, output_ports)
    while True:
        ready_sockets, _, _ = select(router.router_sockets, [], [], 3.0)
        if len(ready_sockets) > 0:
            for ready_socket in ready_sockets:
                message, _ = router.get_message(router.router_sockets.index(ready_socket))
                message = int.from_bytes(message, "big")
                return_port = int((2**16-1) & message)
                sending_router = int(message >> 16)
                router.update_routing_table([(return_port, sending_router)])
                print(router.routing_table)
        else:
            for i in range(0, len(router.output_ports)):
                message = [router.router_id, router.input_ports[i]]
                router.send_message(message, (LOCALHOST, router.output_ports[i][0]), i)


main()
