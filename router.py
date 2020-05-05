"""
Router.py
This is the router class for the COSC364 Assignment.
Author: Ryan Beaumont
"""
from RoutingTable import *
from config import *
from Response import *
import Timer
from multiprocessing.pool import ThreadPool
from socket import *
from os import _exit
from sys import argv
from random import uniform
from select import *
from time import *



LOCALHOST = gethostname()

def kill_router(code):
    """This procedure shuts down the router/ ends the program"""
    _exit(code)


class Router:
    def __init__(self, router_id, input_ports, output_ports):
        """Initialises starting properties"""
        self.ripMaxLength = 520
        self.router_id = router_id
        self.input_ports = input_ports
        self.output_ports = self.initialise_output_ports(output_ports)
        self.links = self.initialise_links()
        self.router_sockets = self.create_sockets()
        self.routing_table = RoutingTable()
        self.unsolicited_delay = 10
        self.garbage_collection_delay = 4 * self.unsolicited_delay
        self.neighbour_death_delay = 6 * self.unsolicited_delay
        self.garbage_collection_time = float("inf")
        self.triggered_update = False
        self.unsolicited_time = None
        self.triggered_time = float("inf")
        self.update_unsolicited()

    def __str__(self):
        """This method returns a string detailing the input, output, socket and routing table of the router
        It is intended for debugging purposes"""
        return "Input Ports: {}\nOutput Ports: {}\nSockets: {}\nRouting Table: {}\n".format(self.input_ports,
                                                                                            self.output_ports,
                                                                                            self.router_sockets,
                                                                                            self.routing_table.table)

    def initialise_output_ports(self, output_ports):
        """
        Stores output ports as a (router_id, metric) pair in dict with key = port
        """
        initialised_ports = {}
        for port in output_ports:
            initialised_ports[port[0]] = [None, port[1]]
        return initialised_ports

    def initialise_links(self):
        """
        input port = key, (id, output_port, last_heard_from)
        """
        links = {}
        for port in self.input_ports:
            links[port] = []
        return links

    def add_link(self, input_port, id, output_port):
        """
        router link holds the id, output_port and last heard from time related to the input port key
        :param input_port: the input port that received the message
        :param id: id of the sending router
        :param output_port: output port router sent from
        """
        self.links[input_port] = [id, output_port, int(time())]
        self.output_ports[output_port][0] = id
        self.print_links()

    def update_last_heard(self, input_port):
        """
        Update the last heard from time for a neighbour
        :param input_port: the port of a receiving UDP socket.
        """
        self.links[input_port][2] = int(time())

    def start_garbage_timer(self):
        """
        Starts the garbage collection timer
        """
        if self.garbage_collection_time == float("inf"):
            self.garbage_collection_time = time() + self.garbage_collection_delay

    def check_neighbour_alive(self):
        """
        Check if any router links have exceeded neighbour_death_time
        """
        neighbour_died = False
        for key in self.links.keys():
            if len(self.links[key]) > 0 and self.links[key][2] != "d":
                current_time = int(time())
                if current_time - self.links[key][2] >= self.neighbour_death_delay:
                    self.routing_table.update_dead_link(self.links[key][0])
                    neighbour_died = True
                    self.links[key][2] = "d"
        if neighbour_died:
            self.start_garbage_timer()
            self.update_triggered()
            self.print_links()

    def check_garbage_collection(self):
        """Checks if it is time to execute garbage collection"""
        if self.garbage_collection_time is not None:
            current_time = int(time())
            if current_time >= self.garbage_collection_time:
                self.routing_table.garbage_collection()
                self.garbage_collection_time = float("inf")

    def create_sockets(self):
        """This method creates each of the UDP sockets for the input ports"""
        sockets = []
        try:
            for port in self.input_ports:
                sockets.append(socket(AF_INET, SOCK_DGRAM))
                sockets[-1].bind((LOCALHOST, port))
        except error:
            print("Error could not open sockets:", error)
            kill_router(1)
        else:
            print("Sockets created on ports: {}\n".format(self.input_ports))
            return sockets

    def send_message(self):
        """This method send a RIP messages down each of the routers links. If possible applying split horizon poison
        reverse to each of them"""
        response_encode = ResponseSend()
        link_keys = list(self.links.keys())
        for i in range(len(link_keys)):
            if len(self.links[link_keys[i]]) == 0:
                output_port_keys = list(self.output_ports.keys())
                rip_entries = self.routing_table.get_entries(self.router_id)
                address = (LOCALHOST, int(output_port_keys[i]))
            else:
                rip_entries = self.routing_table.get_entries(self.router_id, self.links[link_keys[i]][0])
                address = (LOCALHOST, self.links[link_keys[i]][1])
            rip_messages = response_encode.newMessage(self.router_id, rip_entries)
            try:
                for rip_message in rip_messages:
                    self.router_sockets[i].sendto(rip_message, address)
                self.triggered_update = False
                self.triggered_time = float("inf")
            except error:
                print("Could not send message:", error)

    def get_message(self, socket_number):
        """Gets the data received on a socket and the sending address"""
        try:
            message, address = self.router_sockets[socket_number].recvfrom(self.ripMaxLength)
        except error:
            print("Error Reading Socket:", error)
        else:
            return message, address

    def get_routing_table(self, neighbour_to_send_to):
        """This method will return the rip entries to be sent in a message using neighbourToSendTo to implement
        split horizon poison reverse"""
        self.routing_table.get_entries(self.router_id, neighbour_to_send_to)

    def update_routing_table(self, rip_entries, next_hop_router, output_port):
        """This method will send the ripEntries through to the routing table"""
        route_dead = self.routing_table.update(rip_entries, next_hop_router, self.output_ports[output_port][1])
        if route_dead:
            self.start_garbage_timer()
            self.update_triggered()

    def can_send_unsolicited(self):
        """Checks if the router can send an unsolicited message"""
        return time() >= self.unsolicited_time

    def update_unsolicited(self):
        """This method updates the timers for unsolicited messages"""
        self.unsolicited_time = time() + self.unsolicited_delay * uniform(0.8, 1.2)

    def can_send_triggered(self):
        """Checks if the router can send a triggered message"""
        if self.triggered_time != float("inf"):
            return self.triggered_update and time() >= self.triggered_time
        else:
            return False

    def update_triggered(self):
        """Updates the timers for triggered messages"""
        self.triggered_time = time() + uniform(1, 5)
        self.triggered_update = True

    def select_wait_time(self):
        """Calculates the next timeout period for the select call"""
        wait_time = min(self.unsolicited_time, self.garbage_collection_time, self.triggered_time) - time()
        if wait_time < 0:
            wait_time = 0
        return wait_time

    def print_links(self):
        """Prints the direct router links and information associated"""
        print("Direct Link Information:")
        print(self.links, "\n")


def process_received(router, socket):
    """
    This function processes the data received from neighbour routing tables
    :param router: the router class instance
    :param socket: socket that has data ready to receive
    """
    response_decode = ResponseReceive()
    message, address = router.get_message(router.router_sockets.index(socket))
    advertising_router_id, rip_entries = response_decode.readResponse(message)
    if advertising_router_id is not None:
        recv_sock_port = socket.getsockname()[1]
        if len(router.links[recv_sock_port]) == 0:
            router.add_link(recv_sock_port, advertising_router_id, address[1])
        route_dead = router.update_routing_table(rip_entries, advertising_router_id, address[1])
        router.update_last_heard(recv_sock_port)
        if route_dead:
            router.start_garbage_timer()
            router.update_triggered()



def main():
    # Initialisation of classes
    filename = argv[1]
    router_id, input_ports, output_ports = router_config(filename)
    router = Router(router_id, input_ports, output_ports)

    while True:
        ready_sockets, _, _ = select(router.router_sockets, [], [], router.select_wait_time())
        # Process any sockets with received RIP messages
        if len(ready_sockets) > 0:
            for ready_socket in ready_sockets:
                process_received(router, ready_socket)
        # Check if any links are dead
        router.check_neighbour_alive()
        # Check garbage collection
        router.check_garbage_collection()

        if router.can_send_unsolicited():
            if router.triggered_update:
                print("Sent Unsolicited Instead of Triggered\n")
            else:
                print("Sent Unsolicited\n")
            router.send_message()
            router.update_unsolicited()

        elif router.can_send_triggered():
            router.send_message()
            router.update_unsolicited()
            print("Sent Triggered\n")

main()
