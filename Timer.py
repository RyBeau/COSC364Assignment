import datetime
import random



""" EITHER MAKE A THREAD FOR ROUTING & TRIGGERED UPDATE OR MAKE FOR LOOP """



"""Maintains router and RTE timers"""
class Timer:
    
    """All it needs to do is tell caller that it can now send a unsolicited message"""
    def unsolisotedMessageTimer(self):
        next_routing_update_time = self.setNextRoutingUpdateTime()                      # Initialize var
        
        while (1):
            now = datetime.datetime.now()                                               # Current time
            
            if (now >= next_routing_update_time):                                  # If current time >= the next unsolicited message time
                return True
            
            

    """All it needs to do is tell caller that it can now send a unsolicited message"""
    def triggeredMessageTimer(self):
        next_triggerd_update = self.setNextTriggeredUpdateTime()                        # Initialize var
        
        while (1):
            now = datetime.datetime.now()                                               # Current time
            
            if (now >= next_triggerd_update):                                      # If current time >= the next available time for a triggerd update
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
        return datetime.datetime.now() + self.getDeltaDateTime(30 + offset_time)
    
    
    """Set 'next_triggerd_update' to when the next triggered update can be generated"""
    def setNextTriggeredUpdateTime(self):
        min_margin = 1
        max_margin = 5
        
        offset_time = self.getOffsetTime(min_margin, max_margin)
        
        #self.next_routing_update_time = getDeltaDateTime(offset_time)
        return datetime.datetime.now() + self.getDeltaDateTime(offset_time)
    
    
    
    
    
    
    
    
    """Return a random time inteval from min_margin to max_margin in seconds"""
    def getOffsetTime(self, min_margin, max_margin):
        return random.randint(min_margin, max_margin)
    
    
    
    """Return 'timeDelta' in 'datetime' syntax"""
    def getDeltaDateTime(self, timeDelta):
        return datetime.timedelta(seconds = timeDelta)





#t = Timer()
#print(t.triggeredMessageTimer())
#print(t.unsolisotedMessageTimer())

