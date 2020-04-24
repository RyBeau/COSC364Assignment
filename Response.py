import RoutingTable
import Format
import math
#For regular 30 second response and triggered updates messages


"""Form a response message packet and return a list of 'bytearray/s' s of packet back to the caller"""
class ResponseSend:
    
    command = 2
    version = 1
    must_be_zero = 0
    
    f = Format.Format()
    
    
    
    """Return a RTE in integer format"""
    def createRTE(self, ip_addr, metric):
        f = self.f
        
        # Get list of each element for packet, e.g addr_family_id_list = [0, 1] for address family id = 1
        addr_family_id_list = f.formatAddrFamilyID(2)
        must_be_zero16_list = f.formatMustBeZero16(0)
        ip_addr_list = f.formatIP(ip_addr)
        must_be_zero32_list = f.formatMustBeZero32(0)
        metric_list = f.formatMetric(metric)
        
        
        # Concatonate lists to a single list(The size of the list is constant)
        RTE_byte_list = (addr_family_id_list + 
                         must_be_zero16_list + 
                         ip_addr_list + 
                         must_be_zero32_list + 
                         must_be_zero32_list + 
                         metric_list)
        
        
        return RTE_byte_list




    """Add RTE in packet form to packet. Returns packet & packet index(to keep track of what bytes are occupied in packet('byteArray')"""
    def appendToPacket(self, packet, packet_index, RTE_byte_list):
        
        i = 0
        while i < len(RTE_byte_list):
            packet[packet_index] = RTE_byte_list[i]     # 'calculatePacketByteSize()' ensures no index range error
            
            packet_index += 1
            i += 1        
        
        return packet, packet_index
    
    
    
    
    
    """Calculate the size of packet depending on how many RTE's are in routing table, returns number of bytes"""
    def calculatePacketByteSize(self, expected_num_packets, current_num_packets, RTE_total):
        max_packet_byte_size = 504      # max number of bytes for a single packet
        packet_header_size = 4          # packet header size(number of bytes)
        RTE_size = 20                   # RTE size(number of bytes)
        
        packet_byte_size = packet_header_size + (RTE_total * RTE_size)
        
        if packet_byte_size > max_packet_byte_size:     # if true, means multiple packets will be generated
            return max_packet_byte_size
        
        
        return packet_byte_size
    
    
    
    
    
    # THIS WILL NOW ONLY BE FOR THE 30 SECOND UPDATE PACKET
    """Initial function to call. Returns a list of packet/s depending on how many RTE's are in routing table"""
    def makeUnsolictedUpdate(self):
        
        routingTable = RoutingTable.RoutingTable().table
        
        RTE_total = len(routingTable)         # Number of RTE's in 'RoutingTable' class
        
        num_packets = math.ceil(float(RTE_total)/ float(max_num_packet_RTE))        # Number of packet required to send all RTE's
        
        packet_list = []        # List of packet/s to return
        
        
        while len(packet_list) < num_packets:
            packet_byte_size = calculatePacketByteSize(num_packets, len(packet_list), RTE_total)
            
            packet = bytearray(packet_byte_size)
            
            #packet header
            packet[0] = self.command
            packet[1] = self.version
            packet[2] = self.must_be_zero
            packet[3] = self.must_be_zero
            
            
            packet_index = 4
            
            for ip_addr, metric, _ in routingTable.items():
                if (packet_index < packet_byte_size):       #when packet is at max size, break to start new packet
                    break
                
                RTE_byte_list = self.createRTE(ip_addr, metric)
                packet, packet_index = self.appendToPacket(packet, packet_index, RTE_byte_list)
                
                
                
            packet_list.append(packet)
        
        
        return packet_list
        
        
        
        
        
    
        
        
        
    #ONLY MAKES TRIGGERED UPDATES
    def makeTriggeredUpdate(self):
        
        routingTable = RoutingTable.RoutingTable().table
        
        RTE_list = []
        
        # Get RTE's that have 'c' flag
        for key, _, flag in routingTable.items():
            if (flag == "c"):
                RTE_list.append(key)
                
        
        RTE_total = len(RTE_list)
        num_packets = math.ceil(float(RTE_total)/ float(max_num_packet_RTE))        # Number of packet required to send all RTE's
        
        packet_list = []        # List of packet/s to return        
        
        
        
        while len(packet_list) < num_packets:
            packet_byte_size = calculatePacketByteSize(num_packets, len(packet_list), RTE_total)
            
            packet = bytearray(packet_byte_size)
        
            #packet header
            packet[0] = self.command
            packet[1] = self.version
            packet[2] = self.must_be_zero
            packet[3] = self.must_be_zero
            
            packet_index = 4
            
            for RTE in RTE_list:
                if (packet_index < packet_byte_size):       #when packet is at max size, break to start new packet
                    break                
                
                ip_addr = RTE
                metric = routingTable[RTE][0]
                
                RTE_byte_list = self.createRTE(ip_addr, metric)
                packet, packet_index = self.appendToPacket(packet, packet_index, RTE_byte_list)
                
                
            packet_list.append(packet)                
        
        
        return packet_list
        
        






"""Pass a message received by neighbour in bytearray form to 'readResponse' to decode the message to retrieve the RTE/s"""
class ResponseReceive():
    

    """Decode and return a single RTE from packet"""
    def decodeRTE(self, message, msg_index, f):
        
        i = msg_index
        
        #Decode Address family identification from RTE
        addr_family_id = f.format_recev_addr_family_id([message[i], message[i+1]])
        
        #Decode ip address from RTE
        ip_addr = f.format_recev_ip_addr([message[i+4], message[i+5], message[i+6], message[i+7]])
        
        #Decode metric from RTE
        metric = f.format_recev_metric([message[i+16], message[i+17], message[i+18], message[i+19]])
        
        
        return addr_family_id, ip_addr, metric
    
    
    
    
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
        
        
        recv_RTE_list = []                  # All RTE's in message that have been read
        
        i = 4                               # packet index(Before index 4 is the header)
        j = 0                               # RTE counter
        while j < RTE_count:
            
            #i is start of a RTE in packet
            #f is points to 'Format' class
            addr_family_id, ip_addr, metric = self.decodeRTE(message, i, f)
            
            RTE = (addr_family_id, ip_addr, metric)
            recv_RTE_list.append(RTE)
            
            
            i += 20                         # Increments by 20 since a RTE has a size of 20 bytes
            j += 1                          # Increment by 1 for every RTE in message read
            
        
        
        return recv_RTE_list                # return a list of RTE's in tuple(address-family-id, ip-address, metric)
    




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
