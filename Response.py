#import RoutingTable
import Format
import math
#For regular 30 second response and triggered updates messages


class ResponseSend():
    
    command = 2
    version = 1    
    
    
    
    
    
    """RTE_list = [(destination_id, metric)]"""
    def newMessage(self, local_router_id, RTE_list):
        f = Format.Format()
        local_router_id_bytes = f.formatLocalID(local_router_id)        
    
    
        max_RTE_in_message = 25                                                     # Max number of RTE's that can fit in a single message
        RTE_count = len(RTE_list)                                               # Number of RTE's in routing table
        message_count = 1 + (RTE_count // max_RTE_in_message)                       # Number of messages required to send entire routing table
        
        if RTE_count == 0:
            # Do something
            pass
    
    
    
        list_of_messages = []                                                       # Contains message/s in bytearray form that will be returned to the caller    
        
        
        
        while len(list_of_messages) < message_count:                                # Loop until all messages have been created
            message_byte_size, RTE_count = self.calculateMessageByteSize(RTE_count)        # Size of message in bytes
            
            message = bytearray(message_byte_size)
            
            # Message header
            message[0] = self.command
            message[1] = self.version
            
            message[2] = local_router_id_bytes[0]
            message[3] = local_router_id_bytes[1]
            
            
            message_index = 4                                                       # Begin at index 4 of message since first 3 index's are the message header
            
            
            for destination_id, metric in RTE_list:
                if (message_index >= message_byte_size):                            # If message_index is out of range in message(bytearray) size
                    break                                                           # then break loop to start a new message
            
                
                RTE = self.encodeRTE(destination_id, metric)                               # Format the RTE to be appended to the message(bytearray) which is done on the next line
                message, message_index = self.addToMessage(message, message_index, RTE)
    
    
            # end of for loop
            list_of_messages.append(message)                                        # Append message(bytearray) to list_of_messages after message is encoded


        #end of while loop
        return list_of_messages    
    
    
    
    
    
    
    
    #"""30 second unsolicited message. Returns message/s of the entire routing table"""
    #def unsolictedMessage(self, local_router_id):
        #f = Format.Format()
        #local_router_id_bytes = f.formatLocalID(local_router_id)
        
        #routingTable = RoutingTable.RoutingTable().table                            # The routing table(dictionary)
        ##routingTable = {1234: (1, 2, 12, "c"), 5678: (5, 6, 1, "c")}
        
        #max_RTE_in_message = 25                                                     # Max number of RTE's that can fit in a single message
        #RTE_count = len(routingTable)                                               # Number of RTE's in routing table
        #message_count = 1 + (RTE_count // max_RTE_in_message)                       # Number of messages required to send entire routing table
        
        #if RTE_count == 0:
            ## Do something
            #pass
    
    
    
        #list_of_messages = []                                                       # Contains message/s in bytearray form that will be returned to the caller
        
        
        
        
        #while len(list_of_messages) < message_count:                                # Loop until all messages have been created
            #message_byte_size, RTE_count = self.calculateMessageByteSize(RTE_count)        # Size of message in bytes
            
            #message = bytearray(message_byte_size)
            
            ## Message header
            #message[0] = self.command
            #message[1] = self.version
            
            #message[2] = local_router_id_bytes[0]
            #message[3] = local_router_id_bytes[1]
            
            
            #message_index = 4                                                       # Begin at index 4 of message since first 3 index's are the message header
            
            
            #for router_id in routingTable:
                #metric = routingTable[router_id][2]
                
                #if (message_index >= message_byte_size):                            # If message_index is out of range in message(bytearray) size
                    #break                                                           # then break loop to start a new message
            
                
                #RTE = self.encodeRTE(router_id, metric)                               # Format the RTE to be appended to the message(bytearray) which is done on the next line
                #message, message_index = self.addToMessage(message, message_index, RTE)
    
    
            ## end of for loop
            #list_of_messages.append(message)                                        # Append message(bytearray) to list_of_messages after message is encoded


        ##end of while loop
        #return list_of_messages





    #"""Make a triggered message/s. Param flagged_RTE_list is a list of flagged("c") keys. Returns message/s in a list"""
    #def triggerdMessage(self, local_router_id, flagged_RTE_list):
        #f = Format.Format()
        #local_router_id_bytes = f.formatLocalID(local_router_id)
        
        #routingTable = RoutingTable.RoutingTable().table
        ##routingTable = {1234: (1, 2, 3, "c"), 5678: (5, 6, 7, "c")}                # just a test routing table
        
        
        #max_RTE_in_message = 25                                                     # Max number of RTE's that can fit in a single message
        #RTE_count = len(routingTable)                                               # Number of RTE's in routing table
        #message_count = 1 + (RTE_count // max_RTE_in_message)                       # Number of messages required to send entire routing table
        
        #list_of_messages = []                                                       # Contains message/s in bytearray form that will be returned to the caller
        

        
        #while len(list_of_messages) < message_count:                                # Loop until all messages have been created
            #message_byte_size, RTE_count = self.calculateMessageByteSize(RTE_count)        # Size of message in bytes
            
            #message = bytearray(message_byte_size)
            
            ## Message header
            #message[0] = self.command
            #message[1] = self.version
            
            #message[2] = local_router_id_bytes[0]
            #message[3] = local_router_id_bytes[1]
            
            
            #message_index = 4                                                       # Begin at index 4 of message since first 3 index's are the message header
            
            #for router_id in flagged_RTE_list:
                #metric = routingTable[router_id][2]
                
                #if (message_index >= message_byte_size):                            # If message_index is out of range in message(bytearray) size
                    #break                                                           # then break loop to start a new message
                
                
                #RTE = self.encodeRTE(router_id, metric)                               # Format the RTE to be appended to the message(bytearray) which is done on the next line
                #message, message_index = self.addToMessage(message, message_index, RTE)
                
            
            ## end of for loop
            #list_of_messages.append(message)                                        # Append message(bytearray) to list_of_messages after message is encoded


        ##end of while loop
        #return list_of_messages            
        
        
    



    """
    
    HELPER FUNCTIONS BELOW
    
    """


    """Calculate the size of message depending on how many RTE's are in the routing table, returns number of bytes"""
    def calculateMessageByteSize(self, RTE_count):
        max_message_byte_size = 504                                                 # Max number of bytes for a single message
        message_header_size = 4                                                     # Message header size(number of bytes)
        RTE_size = 20                                                               # Single RTE size(number of bytes)
        
        message_byte_size = message_header_size + (RTE_count * RTE_size)
        
        if message_byte_size > max_message_byte_size:                               # If RTE count > 25, 
            return max_message_byte_size, RTE_count-25                              # then return max message byte size and RTE_count - 25(since 25 are going to be sent)
        
        
        return message_byte_size, 0                                                 # Else, return calculated message byte size and 0(since there will be no remaining RTE's to send after)
    
    
    
    
    
    
    """Encode a single RTE, formatted to be added to the message"""
    def encodeRTE(self, router_id, metric):
        f = Format.Format()
        
        # Each property is returned in a list, each value in the list represents a byte in the message(bytearray). e.g [1, 2], i=index(byte) in message, message[i] = 1 and message[i+1] = 2
        addr_family_id_list = f.formatAddrFamilyID(2)                               # Format addres-family-id property. Param is the property value to be formatted
        must_be_zero16_list = f.formatMustBeZero16(0)                               # Format must-be-zero(16 bits) property. Param is the property value to be formatted
        ip_addr_list = f.formatID(router_id)                                          # Format ip-address property. Param is the property value to be formatted
        must_be_zero32_list = f.formatMustBeZero32(0)                               # Format must-be-zero(32 bits) property. Param is the property value to be formatted
        metric_list = f.formatMetric(metric)                                        # Format metric property. Param is the property value to be formatted
        
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
        
        i = 0                                                                       # Index for RTE, since RTE is a list, each value in the list represents a byte in the message(bytearray)
        while i < len(RTE):
            message[message_index] = RTE[i]                                         # Append RTE property value to message
            
            message_index += 1
            i += 1
        
        return message, message_index
        
        






"""Pass a message received by neighbour in bytearray form to 'readResponse' to decode the message to retrieve the RTE/s"""
class ResponseReceive():
    

    """Decode and return a single RTE from packet"""
    def decodeRTE(self, message, msg_index, f):
        
        i = msg_index
        
        #Decode Address family identification from RTE
        addr_family_id = f.format_recev_addr_family_id([message[i], message[i+1]])
        
        #Decode ip address from RTE
        router_id = f.format_recev_id([message[i+4], message[i+5], message[i+6], message[i+7]])
        
        #Decode metric from RTE
        metric = f.format_recev_metric([message[i+16], message[i+17], message[i+18], message[i+19]])
        
        
        return addr_family_id, router_id, metric
    
    
    
    
    # GUESSING THAT MESSAGE IS A 'BYTEARRAY'
    """Read and extract the entire Response message"""
    def readResponse(self, message):
        
        
        packet_size = len(message) - 4      # Packet size minus the header(4 bytes)
        RTE_size = 20                       # Each RTE is 20 bytes
        
        
        try:                                # Get number of RTE's in packet
            RTE_count = int(packet_size / RTE_size)
        
        except:
            # Do something
            pass
        
        
        
        
        f = Format.Format()
        
        version = message[0]
        command = message[1]
        advertising_router_id = f.format_recev_advertising_id([message[2], message[3]])
        
        
        
        recv_RTE_list = []                  # All RTE's in message that have been read
        
        i = 4                               # packet index(Before index 4 is the header)
        j = 0                               # RTE counter
        while j < RTE_count:
            
            #i is start of a RTE in packet
            #f is points to 'Format' class
            addr_family_id, router_id, metric = self.decodeRTE(message, i, f)
            
            RTE = (addr_family_id, router_id, metric)
            recv_RTE_list.append(RTE)
            
            
            i += 20                         # Increments by 20 since a RTE has a size of 20 bytes
            j += 1                          # Increment by 1 for every RTE in message read
            
        
        
        return advertising_router_id, recv_RTE_list                # return a list of RTE's in tuple(address-family-id, ip-address, metric) and the advertising router's id
    




##Just tests

#r = ResponseReceive()

#routingTable = []

##Header
#command = int('00000010', 2)
#version = int('00000001', 2)
#zero1_16_1 = int('00000000', 2)
#zero1_16_2 = int('00000000', 2)

##RTE
#addr_family_id_1 = int('00000000', 2)
#addr_family_id_2 = int('00000010', 2)
#zero2_16_1 = int('00000000', 2)
#zero2_16_2 = int('00000000', 2)

#ip1 = int('11001010', 2)
#ip2 = int('00100100', 2)
#ip3 = int('10110011', 2)
#ip4 = int('01010001', 2)

#zero1_32_1 = int('00000000', 2)
#zero1_32_2 = int('00000000', 2)
#zero1_32_3 = int('00000000', 2)
#zero1_32_4 = int('00000000', 2)

#zero2_32_1 = int('00000000', 2)
#zero2_32_2 = int('00000000', 2)
#zero2_32_3 = int('00000000', 2)
#zero2_32_4 = int('00000000', 2)

#metric_1 = int('00000000', 2)
#metric_2 = int('00000000', 2)
#metric_3 = int('00000000', 2)
#metric_4 = int('00000001', 2)



#packet = bytearray(44)


#packet[0] = command
#packet[1] = version
#packet[2] = zero1_16_1
#packet[3] = zero1_16_2
#packet[4] = addr_family_id_1
#packet[5] = addr_family_id_2
#packet[6] = zero2_16_1
#packet[7] = zero2_16_2
#packet[8] = ip1
#packet[9] = ip2
#packet[10] = ip3
#packet[11] = ip4
#packet[12] = zero1_32_1
#packet[13] = zero1_32_2
#packet[14] = zero1_32_3
#packet[15] = zero1_32_4
#packet[16] = zero2_32_1
#packet[17] = zero2_32_2
#packet[18] = zero2_32_3
#packet[19] = zero2_32_4
#packet[20] = metric_1
#packet[21] = metric_2
#packet[22] = metric_3
#packet[23] = metric_4

##Header
#command = int('00000010', 2)
#version = int('00000001', 2)
#zero1_16_1 = int('00000000', 2)
#zero1_16_2 = int('00000000', 2)

##RTE
#addr_family_id_1 = int('00000000', 2)
#addr_family_id_2 = int('00000011', 2)
#zero2_16_1 = int('00000000', 2)
#zero2_16_2 = int('00000000', 2)

#ip1 = int('11001011', 2)
#ip2 = int('00100100', 2)
#ip3 = int('10110011', 2)
#ip4 = int('01010011', 2)

#zero1_32_1 = int('00000000', 2)
#zero1_32_2 = int('00000000', 2)
#zero1_32_3 = int('00000000', 2)
#zero1_32_4 = int('00000000', 2)

#zero2_32_1 = int('00000000', 2)
#zero2_32_2 = int('00000000', 2)
#zero2_32_3 = int('00000000', 2)
#zero2_32_4 = int('00000000', 2)

#metric_1 = int('00000000', 2)
#metric_2 = int('00000000', 2)
#metric_3 = int('00000000', 2)
#metric_4 = int('00000011', 2)

#packet[24] = addr_family_id_1
#packet[25] = addr_family_id_2
#packet[26] = zero2_16_1
#packet[27] = zero2_16_2
#packet[28] = ip1
#packet[29] = ip2
#packet[30] = ip3
#packet[31] = ip4
#packet[32] = zero1_32_1
#packet[33] = zero1_32_2
#packet[34] = zero1_32_3
#packet[35] = zero1_32_4
#packet[36] = zero2_32_1
#packet[37] = zero2_32_2
#packet[38] = zero2_32_3
#packet[39] = zero2_32_4
#packet[40] = metric_1
#packet[41] = metric_2
#packet[42] = metric_3
#packet[43] = metric_4


#print(r.readResponse(packet))



## test unsolicited message
#s = ResponseSend()
#print(s.unsolictedMessage())


## test triggered message
#s = ResponseSend()
#print(s.triggerdMessage([1234, 5678]))


## test reading received message
#r = ResponseReceive()
#a = r.readResponse(bytearray(b'\x02\x01\x00\x00\x00\x02\x00\x00\x00\x00\x04\xd2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x02\x00\x00\x00\x00\x16.\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07'))
#print(a)



