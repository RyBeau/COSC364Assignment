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
from time import *


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
            initialised_ports[port[0]] = [None, port[1]]
        return initialised_ports

    def initialise_links(self):
        """
        input port = key, (id, output_port)
        """
        links = {}
        for port in self.input_ports:
            links[port] = None
        return links

    def add_link(self, input_port, id, output_port):
        self.links[input_port] = (id, output_port)
        self.output_ports[output_port][0] = id

    def create_sockets(self):
        """This method creates each of the UDP for the input ports"""
        sockets = []
        setdefaulttimeout(5)
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

    def update_routing_table(self, rip_entries, link_metric):
        """This method will send the ripEntries through to the routing table"""
        self.routing_table.update(rip_entries, link_metric)

def main():
    filename = argv[1]
    router_id, input_ports, output_ports = router_config(filename)
    router = Router(router_id, input_ports, output_ports)
    response_encode = ResponseSend()
    response_decode = ResponseReceive()
    start_time = int(time())
    triggered_response_time = 10
    
    
    # For Timer
    import Timer
    from multiprocessing.pool import ThreadPool
    timer = Timer.Timer()
    
    can_send_unsolicited = False
    can_send_triggered = False
    
    pool = ThreadPool(processes=1)
    async_unsolicited_result = pool.apply_async(timer.unsolisotedMessageTimer)
    async_triggered_result = pool.apply_async(timer.triggeredMessageTimer)
    # End of for Timer
    
    
    while True:
        ready_sockets, _, _ = select(router.router_sockets, [], [], 5.0)
        if len(ready_sockets) > 0:
            for ready_socket in ready_sockets:
                message, address = router.get_message(router.router_sockets.index(ready_socket))
                rip_entries = response_decode.readResponse(message)
                if router.links[ready_socket.getsockname()[1]] is None:
                    router.add_link(ready_socket.getsockname()[1], None, address[1])
                router.update_routing_table(rip_entries, router.output_ports[address[1]][1])
                print(router.routing_table)
        elif False:
            for timed_out_socket in timed_out:
                timed_out_port = timed_out_socket.getsockname()[1]
                if router.output_ports[timed_out_port][[0]] is not None:
                    router.routing_table.update_dead_link()
                    #Start garbage timer
        elif time() - start_time >= triggered_response_time:
            print("Send Update")
            start_time = time()
        print("Hello World")
        
        
        
        
        # For Timer
        can_send_unsolicited = async_unsolicited_result.get()
        can_send_triggered = async_triggered_result.get()
        
        if (can_send_unsolicited == True):
            # Send unsolicited message by calling Response.unsolictedMessage()
            
            can_send_unsolicited = False
            async_unsolicited_result = pool.apply_async(timer.unsolisotedMessageTimer)
            
        
        if (can_send_triggered == True):
            # Check for flagged RTE's if true then
            # Send unsolicited message by calling Response.triggerdMessage(list of flagged RTE's in routing table)
            
            
            # After making a triggered message set these 2 variables below else don't
            #can_send_triggered = False
            #async_triggered_result = pool.apply_async(timer.triggeredMessageTimer)
            
            pass
        # End of for Timer

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