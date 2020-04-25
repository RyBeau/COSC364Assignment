import RoutingTable

import datetime
import random

import time
import threading

#routing update - 30 sec
#triggered update - when topology changes 1 - 5 sec
#timeout - 180 sec
#garbage collection - 120 sec  



""" EITHER MAKE A THREAD FOR ROUTING & TRIGGERED UPDATE OR MAKE FOR LOOP """



"""Maintains router and RTE timers"""
class Timer:
    
    #next_routing_update_time = 0            # last time a routing update was sent(30 sec update)
    #next_triggerd_update = 0                # time when a triggerd update can be performed
    
    #timeout_bin = []                        # list of RTE's timeout time
    #garbage_bin = []                        # list of RTE's pending garbage collection
    
    
    
    
    
    """All it needs to do is tell caller that it can now send a unsolicited message"""
    def unsolisotedMessageTimer(self):
        next_routing_update_time = self.setNextRoutingUpdateTime()                      # Initialize var
        
        while (1):
            now = datetime.datetime.now()                                               # Current time
            
            if (now >= self.next_routing_update_time):                                  # If current time >= the next unsolicited message time
                return True
            
            

    """All it needs to do is tell caller that it can now send a unsolicited message"""
    def triggeredMessageTimer(self):
        next_triggerd_update = self.setNextTriggeredUpdateTime()                        # Initialize var
        
        while (1):
            now = datetime.datetime.now()                                               # Current time
            
            if (now >= self.next_triggerd_update):                                      # If current time >= the next available time for a triggerd update
                return True
    
    
    
    
    
    
    
    """
    
    Helper methods
    
    """
    
    
    
    
    
    """Set 'next_routing_update_time' to when the next router update can be generated"""
    def setNextRoutingUpdateTime(self):
        min_margin = 0
        max_margin = 5
        
        offset_time = self.getOffsetTime(min_margin, max_margin)        
        
        #self.next_routing_update_time = getDeltaDateTime(30 + offset_time)
        return getDeltaDateTime(30 + offset_time)
    
    
    """Set 'next_triggerd_update' to when the next triggered update can be generated"""
    def setNextTriggeredUpdateTime(self):
        min_margin = 1
        max_margin = 5
        
        offset_time = self.getOffsetTime(min_margin, max_margin)
        
        #self.next_routing_update_time = getDeltaDateTime(offset_time)
        return getDeltaDateTime(offset_time)
    
    
    
    
    
    
    
    
    """Return a random time inteval from min_margin to max_margin in seconds"""
    def getOffsetTime(self, min_margin, max_margin):
        return random.randint(min_margin, max_margin)
    
    
    
    """Return 'timeDelta' in 'datetime' syntax"""
    def getDeltaDateTime(self, timeDelta):
        return datetime.timedelta(seconds = timeDelta)





    
    
    
    
    
    
    
    #"""Check if a RTE in 'timeout_bin' list has reached it's 180 sec"""
    #def checkTimeoutTimers(self):
        ##not sure if I should pop the timeout if its time expired
        
        #timeout_bin = self.timeout_bin      # local 'timeout_bin' list
        
        #while True:
            #i = 0
            #while i < len(timeout_bin):
                
                #RTE_id = timeout_bin[i][0]
                #RTE_timeout_time = timeout_bin[i][1]
                
                
                #if (RTE_timeout_time <= self.getDateTime()):        # if RTE's timeout time has expired
                    #self.addToGarbageBin(RTE_id)
                    #self.popTimeoutBin(RTE_id)
                    
                    
                #i += 1
                
            #garbage_bin = self.garbage_bin      # set local 'garbage_bin' equal to global 'garbage_bin'
            
        
    
    
    
    
    #"""Check if a RTE in 'garbage_bin' list has reached it's 120 sec"""
    #def checkGarbageTimers(self):
        ## using local 'garbage_bin' to check each RTE since the global 'garbage_bin' can change during loop
        
        #garbage_bin = self.garbage_bin      # local 'garbage_bin' list
        
        #while True:
            #i = 0
            #while i < len(garbage_bin):
                
                #RTE_id = garbage_bin[i][0]
                #RTE_garbage_time = garbage_bin[i][1]
                
                
                #if (RTE_garbage_time <= self.getDateTime()):        # if RTE's garbage time has expired
                    #self.collectGarbage(RTE_id)
                    #self.popGarbageBin(RTE_id)
                    
                    
                #i += 1
                
            #garbage_bin = self.garbage_bin      # set local 'garbage_bin' equal to global 'garbage_bin'
            
            
    
    
    #"""Get current date & time"""
    #def getDateTime(self):
        #return datetime.datetime.now()
    
    
    

    
    
    
    
    #"""Append new RTE to 'timeout_bin' list"""
    #def addToTimeoutBin(self, RTE_id):
        #RTE_timeout_time = self.getDateTime() + self.getDeltaDateTime(180)
        #timeout_RTE = tuple([RTE_id, RTE_timeout_time])
        
        #self.timeout_bin.append(timeout_RTE)
    
    
    
    #"""Pop a RTE off the global 'timeout_bin' list"""
    #def popTimeoutBin(self, RTE_id):
        
        ##enumerate() makes every tuple '(0, RTE tuple)'
        #RTE_index = [x for x, y in enumerate(self.timeout_bin) if y[0] == RTE_id]
        
        #try:
            #self.timeout_bin.pop(RTE_index)
            
        #except:
            #print("Problem finding RTE in 'timeout_bin'")
    
    
    
    
    #"""Append timed out RTE to global 'garbage_bin' list"""
    #def addToGarbageBin(self, RTE_id):
        
        #RTE_garbage_timeout_time = self.getDateTime() + self.getDeltaDateTime(120)
        #garbage_RTE = tuple([RTE_id, RTE_garbage_timeout_time])
        
        #self.garbage_bin.append(garbage_RTE)
    
    
    
    #"""Pop a RTE off the global 'garbage_bin' list"""
    #def popGarbageBin(self, RTE_id):
        
        ##enumerate() makes every tuple '(0, RTE tuple)'
        #RTE_index = [x for x, y in enumerate(self.garbage_bin) if y[0] == RTE_id]
        
        #try:
            #self.garbage_bin.pop(RTE_index)
            
        #except:
            #print("Problem finding RTE in 'garbage_bin'")
    
    
    
    #"""Remove RTE from 'RoutingTable'"""
    #def collectGarbage(self, RTE_id):
        #pass
    
    
    
    

    
    



#t = Timer()

##make a check if thread is running
#x = threading.Thread(target=t.checkGarbageTimers)
#x.start()


#t.addToGarbageBin("0000")

#time.sleep(10)
#t.addToGarbageBin("1111")

