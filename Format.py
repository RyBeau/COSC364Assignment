COMMAND_SIZE = 8
VERSION_SIZE = 8
MUST_BE_ZERO_16_SIZE = 16
MUST_BE_ZERO_32_SIZE = 32
ADDR_FAMILY_ID_SIZE = 16
ID_SIZE = 32
METRIC_SIZE = 32

'''
Format integer values to bits in string. Use "Format" class before concatenating a 32 bit line for "bytes()" representation.
'''


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

# f = Format()

# command = 2
# print(f.formatAddrFamilyID(2))
