"""
This is the COSC364 Assignment 1 RIP Routing source code

Author: Ryan Beaumont 31591316
Author: Kazu Burrows 11201655
"""

from socket import *
from os import _exit
from sys import argv
from random import uniform
from select import *
from time import *


LOCALHOST = gethostname()
CONFIG_FORMAT = "format should match:\n{Router_id}\ninput ports {input port}, {input port},...\noutput ports " \
                "{output port}-{metric}-{id},...\ntimer {unsolicited timer value}"
COMMAND_SIZE = 8
VERSION_SIZE = 8
MUST_BE_ZERO_16_SIZE = 16
MUST_BE_ZERO_32_SIZE = 32
ADDR_FAMILY_ID_SIZE = 16
ID_SIZE = 32
METRIC_SIZE = 32
# ----------------------------------------------------------------------------------------------------------------------


class RouterException(Exception):
    """
    A custom exception thrown for router related errors
    """
    pass

# ----------------------------------------------------------------------------------------------------------------------


# convert id from string to int
def convert_id(param_id):
    try:
        converted_id = int(param_id)
        if 1 <= converted_id <= 64000:
            return converted_id
        else:
            raise RouterException("Router id is out of range must be between 1 and 64000 inclusive")
    except RouterException:
        raise
    except Exception:
        raise RouterException("Error converting router id\n" + CONFIG_FORMAT)


# Return a list of input ports as integers
def convert_input(param_input_ports):
    port_list = []
    try:
        for port in param_input_ports:
            converted_port = int(port)

            if not (1024 <= converted_port <= 64000):
                raise RouterException("Input port out of range must be between 1024 and 64000 inclusive")

            if converted_port in port_list:
                raise RouterException("Input ports can only be used once")

            port_list.append(converted_port)

        return port_list

    except RouterException:
        raise
    except Exception:
        raise RouterException("Unable to convert input ports\n" + CONFIG_FORMAT)


# Return a list of output ports as integers
def convert_output(param_output_ports, input_ports):
    port_list = []
    try:
        for port in param_output_ports:

            port = port.split('-')
            router_port = int(port[0])
            router_metric = int(port[1])
            router_id = int(port[2])

            if not (1024 <= router_port <= 64000):
                raise RouterException("Output port out of range must be between 1024 and 64000 inclusive")

            if router_metric < 0 or router_metric > 16:
                raise RouterException("Route metric out of range must be between 1 and 16 inclusive")

            if not (1 <= router_id <= 64000):
                raise RouterException("Neighbour router ID out of range must be between 1 and 64000 inclusive")

            if router_port in input_ports:
                raise RouterException("Output port is also an input port")

            if router_port in [p[0] for p in port_list]:
                raise RouterException("Output ports can only be used once")

            port_tuple = tuple([router_port, router_metric, router_id])
            port_list.append(port_tuple)

        if len(port_list) != len(input_ports):
            raise RouterException("There are not the same number of input ports and output ports")

        return port_list
    except RouterException:
        raise
    except Exception:
        raise RouterException("Could not convert output ports\n" + CONFIG_FORMAT)

# Converts the timer value in the file to an integer
def convert_timer(timer):
    try:
        if 5 <= int(timer) <= 30:
            return int(timer)
        else:
            raise RouterException("Unsolicited timer value must be from 5 to 30")
    except RouterException:
        raise
    except Exception:
        raise RouterException("Invalid value for an unsolicited update in config file")


# Parses the given config file return router configuration information
def router_config(filename):
    try:
        file = open(filename, 'r')

        print("\'%s\' file exists" % filename)

    except Exception:
        raise RouterException("File not found")

    else:
        lines = file.readlines()

        i = 0
        while i < len(lines):  # filters out comments and new lines
            line = lines[i]

            if line == '\n':
                lines.pop(i)

            elif line[0] == "#":
                lines.pop(i)

            else:
                i += 1

        filtered_lines = [line[:-1] if line[-1] == "\n" else line for line in lines]

        try:
            router_id = convert_id(filtered_lines[0])
            input_ports = convert_input(filtered_lines[1][12:].split(", "))
            output_ports = convert_output(filtered_lines[2][13:].split(", "), input_ports)
            timer = convert_timer(filtered_lines[3][6:])
        except RouterException:
            raise
        except Exception:
            raise RouterException("Error with config file " + CONFIG_FORMAT)
        else:
            return router_id, input_ports, output_ports, timer

# ----------------------------------------------------------------------------------------------------------------------


class Format:
    """
        This class is responsible for the formatting of the fields within the RIP Response Message
    """

    # Return command as 8 bits
    def formatCommand(self, myCommand):
        command_bit = bin(myCommand)[2:]
        command_bit = self.bitSizeCorrection(command_bit, COMMAND_SIZE)

        return command_bit

    # Return version as 8 bits
    def formatVersion(self, myVersion):
        version_bit = bin(myVersion)[2:]
        version_bit = self.bitSizeCorrection(version_bit, VERSION_SIZE)

        return version_bit

    # Return must be zero as 8 bit int list
    def formatMustBeZero16(self, myMustZero):
        must_zero_bit = bin(myMustZero)[2:]
        must_zero_bit = self.bitSizeCorrection(must_zero_bit, MUST_BE_ZERO_16_SIZE)

        must_zero_list = []

        must_zero_list.append(int(must_zero_bit[:8], 2))
        must_zero_list.append(int(must_zero_bit[8:], 2))

        return must_zero_list

    # Return address family identifier as 8 bit int list
    def formatAddrFamilyID(self, myAddrFamilyID):
        addr_fimily_id_bit = bin(myAddrFamilyID)[2:]
        addr_fimily_id_bit = self.bitSizeCorrection(addr_fimily_id_bit, ADDR_FAMILY_ID_SIZE)

        addr_fimily_id_list = []

        addr_fimily_id_list.append(int(addr_fimily_id_bit[:8], 2))
        addr_fimily_id_list.append(int(addr_fimily_id_bit[8:], 2))

        return addr_fimily_id_list

    # Return ip address as 8 bit int list
    def formatID(self, myId):
        id_bit = bin(myId)[2:]
        id_bit = self.bitSizeCorrection(id_bit, ID_SIZE)

        id_list = []

        id_list.append(int(id_bit[:8], 2))
        id_list.append(int(id_bit[8:16], 2))
        id_list.append(int(id_bit[16:24], 2))
        id_list.append(int(id_bit[24:], 2))

        return id_list

    def formatLocalID(self, myId):
        id_bit = bin(myId)[2:]
        id_bit = self.bitSizeCorrection(id_bit, 16)

        id_list = []

        id_list.append(int(id_bit[:8], 2))
        id_list.append(int(id_bit[8:], 2))

        return id_list

    # Return must be zero as 8 bit int list
    def formatMustBeZero32(self, myMustZero):
        must_zero_bit = bin(myMustZero)[2:]
        must_zero_bit = self.bitSizeCorrection(must_zero_bit, MUST_BE_ZERO_32_SIZE)

        must_zero_list = []

        must_zero_list.append(int(must_zero_bit[:8], 2))
        must_zero_list.append(int(must_zero_bit[8:16], 2))
        must_zero_list.append(int(must_zero_bit[16:24], 2))
        must_zero_list.append(int(must_zero_bit[24:], 2))

        return must_zero_list

    # Return metric as 8 bit int list
    def formatMetric(self, myMetric):
        metric_bit = bin(myMetric)[2:]
        metric_bit = self.bitSizeCorrection(metric_bit, METRIC_SIZE)

        metric_list = []

        metric_list.append(int(metric_bit[:8], 2))
        metric_list.append(int(metric_bit[8:16], 2))
        metric_list.append(int(metric_bit[16:24], 2))
        metric_list.append(int(metric_bit[24:], 2))

        return metric_list

    def format_recev_addr_family_id(self, byte_list):
        addr_family_id = ''

        addr_family_id += self.bitSizeCorrection(bin(byte_list[0])[2:], 8)
        addr_family_id += self.bitSizeCorrection(bin(byte_list[1])[2:], 8)

        addr_family_id = int(addr_family_id, 2)

        if (addr_family_id < 1) or (addr_family_id > 15):
            print("Address family id value is out of the expected range.")
            return None

        return addr_family_id

    def format_recev_id(self, byte_list):
        router_id = ""

        router_id += self.bitSizeCorrection(bin(byte_list[0])[2:], 8)
        router_id += self.bitSizeCorrection(bin(byte_list[1])[2:], 8)
        router_id += self.bitSizeCorrection(bin(byte_list[2])[2:], 8)
        router_id += self.bitSizeCorrection(bin(byte_list[3])[2:], 8)

        router_id = int(router_id, 2)

        if (router_id < 1) or (router_id > 64000):
            print("Router id value is out of the expected range.")
            return None

        return router_id

    def format_recev_advertising_id(self, byte_list):
        router_id = ""

        router_id += self.bitSizeCorrection(bin(byte_list[0])[2:], 8)
        router_id += self.bitSizeCorrection(bin(byte_list[1])[2:], 8)

        router_id = int(router_id, 2)

        if (router_id < 1) or (router_id > 64000):
            print("Advertising router id value is out of the expected range.")
            return None

        return router_id

    def format_recev_metric(self, byte_list):
        metric = ''

        metric += self.bitSizeCorrection(bin(byte_list[0])[2:], 8)
        metric += self.bitSizeCorrection(bin(byte_list[1])[2:], 8)
        metric += self.bitSizeCorrection(bin(byte_list[2])[2:], 8)
        metric += self.bitSizeCorrection(bin(byte_list[3])[2:], 8)

        metric = int(metric, 2)

        if (metric < 0) or (metric > 16):
            print("Metric value is out of the expected range.")
            return None

        return metric

    def bitSizeCorrection(self, myBits, size):
        myBits = myBits

        # maybe make a check it 'myBits' is larger than wanted 'size'
        # don't think it is needed

        i = 0

        while len(myBits) < size:
            myBits = '0' + myBits

        # this returns '0011' not '0b0011'
        return myBits

# ----------------------------------------------------------------------------------------------------------------------


class ResponseSend:
    """
    This class is responsible for the formation of the RIP Response Message
    """

    command = 2
    version = 1

    """RTE_list = [(destination_id, metric)]"""

    def newMessage(self, local_router_id, RTE_list):
        f = Format()
        local_router_id_bytes = f.formatLocalID(local_router_id)

        max_RTE_in_message = 25  # Max number of RTE's that can fit in a single message
        RTE_count = len(RTE_list)  # Number of RTE's in routing table
        message_count = 1 + (
                RTE_count // max_RTE_in_message)  # Number of messages required to send entire routing table

        if RTE_count == 0:
            # Do something
            pass

        list_of_messages = []  # Contains message/s in bytearray form that will be returned to the caller

        while len(list_of_messages) < message_count:  # Loop until all messages have been created
            message_byte_size, RTE_count = self.calculateMessageByteSize(RTE_count)  # Size of message in bytes

            message = bytearray(message_byte_size)

            # Message header
            message[0] = self.command
            message[1] = self.version

            message[2] = local_router_id_bytes[0]
            message[3] = local_router_id_bytes[1]

            message_index = 4  # Begin at index 4 of message since first 3 index's are the message header

            for destination_id, metric in RTE_list:
                if (message_index >= message_byte_size):  # If message_index is out of range in message(bytearray) size
                    break  # then break loop to start a new message

                RTE = self.encodeRTE(destination_id,
                                     metric)  # Format the RTE to be appended to the message(bytearray) which is done on the next line
                message, message_index = self.addToMessage(message, message_index, RTE)

            # end of for loop
            list_of_messages.append(message)  # Append message(bytearray) to list_of_messages after message is encoded

        # end of while loop
        return list_of_messages

    """

    HELPER FUNCTIONS BELOW

    """

    """Calculate the size of message depending on how many RTE's are in the routing table, returns number of bytes"""

    def calculateMessageByteSize(self, RTE_count):
        max_message_byte_size = 504  # Max number of bytes for a single message
        message_header_size = 4  # Message header size(number of bytes)
        RTE_size = 20  # Single RTE size(number of bytes)

        message_byte_size = message_header_size + (RTE_count * RTE_size)

        if message_byte_size > max_message_byte_size:  # If RTE count > 25,
            return max_message_byte_size, RTE_count - 25  # then return max message byte size and RTE_count - 25(since 25 are going to be sent)

        return message_byte_size, 0  # Else, return calculated message byte size and 0(since there will be no remaining RTE's to send after)

    """Encode a single RTE, formatted to be added to the message"""

    def encodeRTE(self, router_id, metric):
        f = Format()

        # Each property is returned in a list, each value in the list represents a byte in the message(bytearray). e.g [1, 2], i=index(byte) in message, message[i] = 1 and message[i+1] = 2
        addr_family_id_list = f.formatAddrFamilyID(
            2)  # Format addres-family-id property. Param is the property value to be formatted
        must_be_zero16_list = f.formatMustBeZero16(
            0)  # Format must-be-zero(16 bits) property. Param is the property value to be formatted
        ip_addr_list = f.formatID(router_id)  # Format ip-address property. Param is the property value to be formatted
        must_be_zero32_list = f.formatMustBeZero32(
            0)  # Format must-be-zero(32 bits) property. Param is the property value to be formatted
        metric_list = f.formatMetric(metric)  # Format metric property. Param is the property value to be formatted

        # Concatonate property lists to a single list
        RTE = (addr_family_id_list +
               must_be_zero16_list +
               ip_addr_list +
               must_be_zero32_list +
               must_be_zero32_list +
               metric_list)

        return RTE

    """Append RTE to message(bytearray) and return new message(with appended RTE) and message_index(next index free space in message for the next RTE to begin at)"""

    def addToMessage(self, message, message_index, RTE):

        i = 0  # Index for RTE, since RTE is a list, each value in the list represents a byte in the message(bytearray)
        while i < len(RTE):
            message[message_index] = RTE[i]  # Append RTE property value to message

            message_index += 1
            i += 1

        return message, message_index


"""Pass a message received by neighbour in bytearray form to 'readResponse' to decode the message to retrieve the RTE/s"""


class ResponseReceive:
    """
    This class is responsible for decoding a receive RIP Response Message
    """

    """Decode and return a single RTE from packet"""

    def decodeRTE(self, message, msg_index, f):

        i = msg_index

        # Decode Address family identification from RTE
        addr_family_id = f.format_recev_addr_family_id([message[i], message[i + 1]])

        # Decode ip address from RTE
        router_id = f.format_recev_id([message[i + 4], message[i + 5], message[i + 6], message[i + 7]])

        # Decode metric from RTE
        metric = f.format_recev_metric([message[i + 16], message[i + 17], message[i + 18], message[i + 19]])

        return addr_family_id, router_id, metric

    # GUESSING THAT MESSAGE IS A 'BYTEARRAY'
    """Read and extract the entire Response message"""

    def readResponse(self, message):

        message_size = len(message) - 4  # Message size minus the header(4 bytes)
        RTE_size = 20  # Each RTE is 20 bytes

        try:  # Get number of RTE's in message
            RTE_count = int(message_size / RTE_size)

        except:
            print(
                "The message size is inconsistant to what was expected.\nThe packet may have good RTE's but at least one would have missing information.")
            return None, []

        f = Format()

        command = message[0]
        version = message[1]
        advertising_router_id = f.format_recev_advertising_id(
            [message[2], message[3]])  # Do some checks on the formati side as well

        if command != 2:
            print("Unexpected command value in header of message.")
            return None, []

        if version != 1:
            print("Unexpected version value in header of message.")
            return None, []

        if advertising_router_id is None:
            return None, []

        recv_RTE_list = []  # All RTE's in message that have been read

        i = 4  # packet index(Before index 4 is the header)
        j = 0  # RTE counter
        while j < RTE_count:

            # i is start of a RTE in packet
            # f is points to 'Format' class
            addr_family_id, router_id, metric = self.decodeRTE(message, i, f)

            if addr_family_id is None:
                return None, []

            if router_id is None:
                return None, []

            if metric is None:
                return None, []

            RTE = (addr_family_id, router_id, metric)
            recv_RTE_list.append(RTE)

            i += 20  # Increments by 20 since a RTE has a size of 20 bytes
            j += 1  # Increment by 1 for every RTE in message read

        return advertising_router_id, recv_RTE_list  # return a list of RTE's in tuple(address-family-id, ip-address, metric) and the advertising router's id


# ----------------------------------------------------------------------------------------------------------------------


class RoutingTable:
    """
    This class is the routing table, it is responsible for storing and maintaining the routes the router knows
    """

    def __init__(self):
        """Initialise starting properties
        Table entry format (destination_id, next_hop_routerID, metric, flag)
        flag
        "a" alive link
        "d" for dead link
        """
        self.table = {}

    def __str__(self):
        """Print format for the Routing Table class"""
        table_string = ""
        for key in self.table.keys():
            table_string += "{}: Next Hop ID {}, Metric: {}, Flag {}\n".format(key, self.table[key][1], self.table[key][2], self.table[key][3])
        return "Routing Table\n" + table_string

    def display_table_changes(self, route_dead, table_changed, change_cause):
        """Prints out the routing table if a change has occurred"""
        if route_dead:
            print("Route Has Died")
        if table_changed:
            print("Change Caused By: " + change_cause)
            print(self)

    def update(self, rip_entries, next_hop_id, link_metric):
        """
        Expected RIP entry format
        (addr_family, destination_id, metric)
        """
        route_dead = False
        table_changed = False
        for entry in rip_entries:
            if str(entry[1]) not in self.table.keys():
                if (entry[2] + link_metric) < 16:
                    self.table[str(entry[1])] = (entry[1], next_hop_id, entry[2] + link_metric, "a")
                    table_changed = True
            elif self.table[str(entry[1])][2] > entry[2] + link_metric:
                self.table[str(entry[1])] = (entry[1], next_hop_id, entry[2] + link_metric, "a")
                table_changed = True
            elif self.table[str(entry[1])][1] == next_hop_id and entry[2] + link_metric != self.table[str(entry[1])][2] \
                    and entry[2] + link_metric < 16:
                self.table[str(entry[1])] = (entry[1], next_hop_id, entry[2] + link_metric, "a")
                table_changed = True
            elif self.table[str(entry[1])][1] == next_hop_id and entry[2] + link_metric >= 16 \
                    and self.table[str(entry[1])][3] != "d":
                self.table[str(entry[1])] = (entry[1], next_hop_id, 16, "d")
                table_changed = True
                route_dead = True
        self.display_table_changes(route_dead, table_changed, str(next_hop_id))
        return route_dead

    def get_entries(self, sending_router_id, receiving_neighbour=None):
        """
        receiving_neighbour, ID of router to apply split horizon poisoned reverse for.
        return entry format (destination_id, metric)
        return entry type list
        Default parameter for initial message sending for unknown links
        """
        rip_entries = [(sending_router_id, 0)]
        if receiving_neighbour is not None:
            for entry in self.table.values():
                if entry[0] != receiving_neighbour:
                    if entry[1] == receiving_neighbour:
                        rip_entries.append((entry[0], 16))
                    else:
                        rip_entries.append((entry[0], entry[2]))
        return rip_entries

    def update_dead_link(self, neighbour_id):
        """
        Updates router entries on death of a neighbour
        """
        for entry in self.table.values():
            if entry[1] == neighbour_id:
                self.table[str(entry[0])] = (entry[0], entry[1], 16, "d")
        self.display_table_changes(True, True, "Neighbour {} died". format(neighbour_id))

    def garbage_collection(self):
        """
        Removes any links marked for garbage collection
        """
        keys = list(self.table.keys())
        for key in keys:
            if self.table[key][3] == "d":
                del self.table[key]
        print("Garbage Collection Completed")
        print(self)

# ----------------------------------------------------------------------------------------------------------------------


def kill_router(code):
    """This procedure shuts down the router/ ends the program"""
    _exit(code)


class Router:
    """
    This is the main controlling class. It is the router itself
    """
    def __init__(self, router_id, input_ports, output_ports, timer):
        """Initialises starting properties"""
        self.ripMaxLength = 520
        self.router_id = router_id
        self.input_ports = input_ports
        self.output_ports = self.initialise_output_ports(output_ports)
        self.links = self.initialise_links()
        self.router_sockets = self.create_sockets()
        self.routing_table = RoutingTable()
        self.unsolicited_delay = timer
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
    """
    This is the mainloop for the program
    """
    # Initialisation of classes
    filename = argv[1]
    try:
        router_id, input_ports, output_ports, timer = router_config(filename)
    except Exception as e:
        print(e)
        kill_router(1)
    else:
        router = Router(router_id, input_ports, output_ports, timer)

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
