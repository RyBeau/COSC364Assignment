"""
Router.py
This is the router class for the COSC364 Assignment.
Author: Ryan Beaumont
"""
from RoutingTable import *
from config import *
from Response import *
from socket import *
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
        self.output_ports = self.initialise_output_ports(output_ports)
        self.links = self.initialise_links()
        self.router_sockets = self.create_sockets()
        self.routing_table = RoutingTable.RoutingTable()

    def __str__(self):
        """This method returns a string detailing the input, output, socket and routing table of the router
        It is intended for debugging purposes"""
        return "Input Ports: {}\nOutput Ports: {}\nSockets: {}\nRouting Table: {}\n".format(self.input_ports,
                                                                                            self.output_ports,
                                                                                            self.router_sockets,
                                                                                            self.routing_table.table)

    def initialise_output_ports(self, output_ports):
        """
        Stores output ports as a (id, metric) pair in dict with key = port
        """
        initialised_ports = {}
        for port in output_ports:
            initialised_ports[port[0]] = (port[2], port[1])
        return initialised_ports

    def initialise_links(self):
        links = {}
        for port in self.input_ports:
            links[port] = [None, None]
        return links

    def add_link(self, input_port, id, output_port):
        self.links[input_port] = (id, output_port)

    def create_sockets(self):
        """This method creates each of the UDP for the input ports"""
        sockets = []
        try:
            for port in self.input_ports:
                sockets.append(socket(AF_INET, SOCK_DGRAM))
                sockets[-1].bind((LOCALHOST, port))
                sockets[-1].settimeout(5)
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
            self.router_sockets[port_to_use].sendto(message, address)
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
        self.routing_table.get_entries(neighbour_to_send_to)

    def update_routing_table(self, rip_entries):
        """This method will send the ripEntries through to the routing table"""
        self.routing_table.update(rip_entries)

def main():
    filename = argv[1]
    router_id, input_ports, output_ports = router_config(filename)
    router = Router(router_id, input_ports, output_ports)
    print(router.output_ports)
    response_decode = ResponseReceive()
    while True:
        ready_sockets, _, timed_out = select(router.router_sockets, [], router.router_sockets)
        if len(ready_sockets) > 0:
            for ready_socket in ready_sockets:
                message, address = router.get_message(router.router_sockets.index(ready_socket))
                rip_entries = response_decode.readResponse(message)
                if router.links[ready_socket.getsockname()[1]] is None:
                    router.add_link(ready_socket.getsockname()[1], None, address[1])
                router.update_routing_table(rip_entries)
                print(router.routing_table)
                print(router.links)
        if timed_out > 0:
            for timed_out_socket in timed_out:
                print(timed_out_socket.getsockname()[1])


main()

"""
Routing Loop Planning
get filename
read file
create router
start timers
select
on read ready
    getMessage
    decode message
    update routing table
    if link invalid send update
on socket timeout
    update routing table
    configure message
    send update
"""