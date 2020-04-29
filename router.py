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
from select import *
from time import *


LOCALHOST = gethostname()
print(LOCALHOST)

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
        self.routing_table = RoutingTable()
        self.neighbour_death_time = 30
        self.garbage_collection_time = 20
        self.start_garbage_collection_time = None
        self.triggered_update = False

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
        if self.start_garbage_collection_time is None:
            self.start_garbage_collection_time = int(time())

    def check_neighbour_alive(self):
        """
        Check if any router links have exceeded neighbour_death_time
        """
        neighbour_died = False
        for key in self.links.keys():
            if len(self.links[key]) > 0 and self.links[key][2] != "d":
                current_time = int(time())
                if current_time -self.links[key][2] >= self.neighbour_death_time:
                    self.routing_table.update_dead_link(self.links[key][0])
                    neighbour_died = True
                    self.links[key][2] = "d"
                    print("Router {} died".format(self.links[key][0]))
        if neighbour_died:
            self.start_garbage_timer()
            self.triggered_update = True
            print("Routing Table After Death:")
            print(self.routing_table)

    def check_garbage_collection(self):
        if self.start_garbage_collection_time is not None:
            current_time = int(time())
            if current_time - self.start_garbage_collection_time >= self.garbage_collection_time:
                self.routing_table.garbage_collection()
                self.start_garbage_collection_time = None
                print("Garbage Collection Completed")

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
            print("Sockets created on ports: {}".format(self.input_ports))
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
            except error:
                print("Could not send message:", error)
        print("Sent RIP Messages")

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
        self.routing_table.update(rip_entries, next_hop_router, self.output_ports[output_port][1])


def process_received(router, socket):
    """
    This function processes the data received from neighbour routing tables
    :param router: the router class instance
    :param socket: socket that has data ready to receive
    """
    response_decode = ResponseReceive()
    message, address = router.get_message(router.router_sockets.index(socket))
    advertising_router_id, rip_entries = response_decode.readResponse(message)
    recv_sock_port = socket.getsockname()[1]
    if len(router.links[recv_sock_port]) == 0:
        router.add_link(recv_sock_port, advertising_router_id, address[1])
    route_dead = router.update_routing_table(rip_entries, advertising_router_id, address[1])
    router.update_last_heard(recv_sock_port)
    print(router.routing_table)
    if route_dead:
        router.start_garbage_timer()
        router.triggered_update = True



def main():
    # Initialisation of classes
    filename = argv[1]
    router_id, input_ports, output_ports = router_config(filename)
    router = Router(router_id, input_ports, output_ports)
    start_time = int(time())

    # For Timer
    timer = Timer.Timer()
    can_send_unsolicited = False
    can_send_triggered = False
    
    pool = ThreadPool(processes=1)
    async_unsolicited_result = pool.apply_async(timer.unsolisotedMessageTimer)
    async_triggered_result = pool.apply_async(timer.triggeredMessageTimer)
    # End of for Timer

    # First message to initialise with neighbours
    router.send_message()
    while True:
        ready_sockets, _, _ = select(router.router_sockets, [], [], 5.0)
        # Process any sockets with received RIP messages
        if len(ready_sockets) > 0:
            for ready_socket in ready_sockets:
                process_received(router, ready_socket)
                print(router.links)
        # Check if any links are dead
        router.check_neighbour_alive()
        # Check garbage collection
        router.check_garbage_collection()
        """
        if int(time()) - start_time >= 10:
            router.send_message()
            start_time = int(time())
        """

        # For Timer
        can_send_unsolicited = async_unsolicited_result.get()
        can_send_triggered = async_triggered_result.get()
        
        if can_send_unsolicited:
            # Send unsolicited message by calling Response.unsolictedMessage()
            router.send_message()
            can_send_unsolicited = False
            async_unsolicited_result = pool.apply_async(timer.unsolisotedMessageTimer)

        if can_send_triggered:
            # Check for flagged RTE's if true then
            # Send unsolicited message by calling Response.triggerdMessage(list of flagged RTE's in routing table)
            router.send_message()
            # After making a triggered message set these 2 variables below else don't
            can_send_triggered = False
            async_triggered_result = pool.apply_async(timer.triggeredMessageTimer)
            
            pass
        # End of for Timer


main()
