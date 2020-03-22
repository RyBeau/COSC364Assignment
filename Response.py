#import RoutingTable
import Format
import math
#For unsolicited response and triggered updates caused by route change

#Receiving responses, so reading, validating, and returning data to caller class

"""Form a response message packet and return a 'bytearray' of packet back to the caller"""
class ResponseSend:
    
    command = 2
    version = 1
    must_be_zero = 0
    
    f = Format.Format()
    
    """Return a RTE in integer format"""
    def createRTE(self, r_table_RTE):
        f = self.f
        
        # Get list of each element for packet, e.g addr_family_id_list = [0, 1] for address family id = 1
        addr_family_id_list = f.formatAddrFamilyID(RTE[])
        must_be_zero16_list = f.formatMustBeZero16(0)
        ip_addr_list = f.formatIP(RTE[])
        must_be_zero32_list = f.formatMustBeZero32(0)
        metric_list = f.formatMetric(RTE[])
        
        
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
    
    
    
    """Initial function to call. Returns a list of packet/s depending on how many RTE's are in routing table"""
    def makeResonse(self):
        #RTE_total = number of RTE's in 'RoutingTable' class
        #routingTable = copy routing table form 'Routing Table' class
        
        num_packets = math.ceil(float(RTE_total)/ float(max_num_packet_RTE))        # Number of packet required to send all RTE's
        
        packet_list = []        # List of packet/s to return
        
        
        R_Table_index = 0          # indexing 'routingTable' list
        while len(packet_list) < num_packets:
            packet_byte_size = calculatePacketByteSize(num_packets, len(packet_list), RTE_total)
            
            packet = bytearray(packet_byte_size)
            
            #packet header
            packet[0] = self.command
            packet[1] = self.version
            packet[2] = self.must_be_zero
            packet[3] = self.must_be_zero
            
            
            packet_index = 4
            while packet_index < packet_byte_size:
                RTE = routingTable[R_Table_index]
                
                RTE_byte_list = self.createRTE(RTE)
                packet, packet_index = self.appendToPacket(packet, packet_index, RTE_byte_list)
                
                R_Table_index += 1
                
                
            packet_list.append(packet)
        
        
        return packet_list
        
        



"""Deal with handling a recieved packet. Returns a list of RTE's"""
class ResponseReceive:
    
    received_RTEs = []
    
    
    """Add RTE into 'received_RTEs' list"""
    def append_RTE(self, my_Addr_family_id, my_temp_ip_addr, my_metric):
        
        my_RTE = tuple([my_Addr_family_id, my_temp_ip_addr, my_metric])
        
        self.received_RTEs.append(my_RTE)
        
    
    
    """Read and extract the entire Response message"""
    def readResponse(self, myPacket):
        packet_size = len(myPacket) - 4
        
        #get number of RTE's in packet
        try:
            RTE_total = int(packet_size / 20)
        
        except:
            return "Response packet has missing data."
        
        
        command = myPacket[0]
        version = myPacket[1]
        
        
        #pointer to 'Format' class
        f = Format.Format()
        
        
        #RTE's begin at index 4 of 'myPacket'
        i = 4   # packet index
        j = 0   # RTE count
        while j < RTE_total:
            
            #i is start of a RTE in packet
            #f is points to 'Format' class
            addr_family_id, ip_addr, metric = self.getRTE(myPacket, i, f)
            
            self.append_RTE(addr_family_id, ip_addr, metric)
            
            
            i = 24      # set i to 24 for the next RTE in packet
            j += 1
            
        
        #return a list of RTE's
        return self.received_RTEs
    
    
    
    """Decode and return a single RTE from packet"""
    def getRTE(self, myPacket, RTE_index, f):
        
        i = RTE_index
        
        #Decode Address family identification from RTE
        addr_family_id = f.format_recev_addr_family_id([myPacket[i], myPacket[i+1]])
        
        #Decode ip address from RTE
        ip_addr = f.format_recev_ip_addr([myPacket[i+4], myPacket[i+5], myPacket[i+6], myPacket[i+7]])
        
        #Decode metric from RTE
        metric = f.format_recev_metric([myPacket[i+16], myPacket[i+17], myPacket[i+18], myPacket[i+19]])
        
        
        return addr_family_id, ip_addr, metric
    


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
