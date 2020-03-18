"""
Router.py
This is the router class for the COSC364 Assignment.
Author: Ryan Beaumont
"""
from RoutingTable import *
from socket import*
from os import _exit


def kill_router(code):
    """This procedure shuts down the router/ ends the program"""
    _exit(code)


class Router:
    def __init__(self, inputPorts, outputPorts):
        """Initialises starting properties"""
        self.adHeaderLength = 20
        self.ripMaxLength = 520
        self.inputPorts = inputPorts
        self.outputPorts = outputPorts
        self.routerSockets = self.create_sockets()
        self.routingTable = RoutingTable()

    def create_sockets(self):
        """This method creates each of the UDP for the input ports"""
        sockets = []
        try:
            for port in self.inputPorts:
                sockets.append(socket(AF_INET, SOCK_DGRAM))
                sockets[-1].bind((gethostname(), port))
        except:
            print("Error could not open sockets")
            kill_router(1)
        else:
            print("Sockets created on ports: {}".format(self.inputPorts))
            return sockets

    def send_message(self, message, address):
        """This method send a RIP message to the given address using the first socket
        in routerSockets"""
        try:
            self.routerSockets[0].sendTo(address, message)
        except:
            print("Could not send message")

    def get_message(self, socketNumber):
        """Gets the data received on a socket and the sending address"""
        try:
            message, address = self.routerSockets[socketNumber].recvfrom(self.ripMaxLength)
        except:
            print("Socket Timed Out")
        else:
            return message, address

    def get_routing_table(self, neighbourToSendTo):
        """This method will return the rip entries to be sent in a message using neighbourToSendTo to implement
        split horizon poison reverse"""
        pass

    def update_routing_table(self, ripEntries):
        """This method will send the ripEntries through to the routing table"""
        pass


if __name__ == "__main__":
    testInputPorts = [30, 2000, 5000]
    testOutputPorts = [4000]
    router = Router(testInputPorts, testOutputPorts)
