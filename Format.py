COMMAND_SIZE = 8
VERSION_SIZE = 8
MUST_BE_ZERO_16_SIZE = 16
MUST_BE_ZERO_32_SIZE = 32
ADDR_FAMILY_ID_SIZE = 16
IP_SIZE = 32
METRIC_SIZE = 32

'''Format integer values to bits in string. Use "Format" class before concatenating a 32 bit line for "bytes()" representation.'''

class Format:
    
    #Return command as 8 bits
    def formatCommand(self, myCommand):
        command_bit = bin(myCommand)[2:]
        command_bit = self.bitSizeCorrection(command_bit, COMMAND_SIZE)
        
        return command_bit
        
    
    
    #Return version as 8 bits
    def formatVersion(self, myVersion):
        version_bit = bin(myVersion)[2:]
        version_bit = self.bitSizeCorrection(version_bit, VERSION_SIZE)
        
        return version_bit
    
    
    #Return must be zero as 16 bits
    def formatMustBeZero16(self, myMustZero):
        must_zero_bit = bin(myMustZero)[2:]
        must_zero_bit = self.bitSizeCorrection(must_zero_bit, MUST_BE_ZERO_16_SIZE)
        
        return must_zero_bit
    
    
    #Return address family identifier as 16 bits
    def formatAddrFamilyID(self, myAddrFamilyID):
        addr_fimily_id_bit = bin(myAddrFamilyID)[2:]
        addr_fimily_id_bit = self.bitSizeCorrection(addr_fimily_id_bit, ADDR_FAMILY_ID_SIZE)
        
        return addr_fimily_id_bit
    
    
    #Return ip address as 32 bits
    def formatIP(self, myIp):
        ip_bit = bin(myIp)[2:]
        ip_bit = self.bitSizeCorrection(ip_bit, IP_SIZE)
        
        return ip_bit
    
    
    #Return must be zero as 32 bits
    def formatMustBeZero32(self, myMustZero):
        must_zero_bit = bin(myMustZero)[2:]
        must_zero_bit = self.bitSizeCorrection(must_zero_bit, MUST_BE_ZERO_32_SIZE)
        
        return must_zero_bit
    
    
    #Return metric as 32 bits
    def formatMetric(self, myMetric):
        metric_bit = bin(myMetric)[2:]
        metric_bit = self.bitSizeCorrection(metric_bit, METRIC_SIZE)
        
        return metric_bit
    
    
    
    
    #def correctSize(self, myBits, size):
        #myBits = myBits[2:]
        
        #if len(myBits) == size:
            #return False
        
        #return True
    
    
    def bitSizeCorrection(self, myBits, size):
        myBits = myBits[2:]
        
        #maybe make a check it 'myBits' is larger than wanted 'size'
        # don't think it is needed
        
        i = 0
        
        while len(myBits) < size:
            myBits = '0' + myBits
        
        
        
        #this returns '0011' not '0b0011'
        return myBits
    
    
    

f = Format()

command = 2
print(f.formatCommand(command))