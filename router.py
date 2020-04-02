"""
Router.py
This is the router class for the COSC364 Assignment.
Author: Ryan Beaumont
"""
from RoutingTable import *
from socket import*
from os import _exit
from config import *
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

    def send_message(self, message, address):
        """This method send a RIP message to the given address using the first socket
        in routerSockets"""
        try:
            self.router_sockets[0].sendTo(address, message)
        except:
            print("Could not send message")

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
        pass


def main():
    filename = input("Enter the config filename: ")
    router_id, input_ports, output_ports = router_config(filename)
    router = Router(router_id, input_ports, output_ports)
    print(router)
    while True:
        ready_sockets, _, _ = select(router.router_sockets, [], [])
        for ready_socket in ready_sockets:
            message, address = router.get_message(router.router_sockets.index(ready_socket))
            print(message)
            print(address)


main()
