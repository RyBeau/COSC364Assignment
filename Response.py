#import RoutingTable
#import Format

#For unsolicited response and triggered updates caused by route change

#Receiving responses, so reading, validating, and returning data to caller class
class ResponseSend:
    RTE_count = 0
    
    command = 2
    version = 1
    
    #This will be encapsulated inside 'bytes()' function
    RIP_packet = []
    
    
    
    def createRTE(r_table_RTE):
        #r_table_RTE is tuple then split
        #then check if there are right number of splits
        
        #next assign each split to correct var
        
        #next format each split        
        pass


    
    """Initial function to call"""
    def makeResonse():
        #add command, version and zero field
        
        #get entire routing table
        #then loop through routing table
        # and call createRTE to create a single RTE to 'RIP_packet'
        
        pass
        


class ResponseReceive:
    
    def __init__(self):
        pass