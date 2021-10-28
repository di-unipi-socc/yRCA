from datetime import datetime
from enum import Enum
import json

# class for distinguishing the "type" of events
class EventType(Enum):
    LOG = "log"
    UNREACHABLE = "unreachable"
    FAILED = "failed"
    NEVER_STARTED = "neverStarted"

# class to represent an event
class Event:
    def __init__(self,serviceName,type,instance,timestamp,message):
        self.serviceName = serviceName
        self.type = type
        self.instance = instance
        self.timestamp = timestamp
        self.message = message

# class to represent list of possible root causes/explanations
# (takes as input "explanationsList" returned by pyswip)
class Explanations:
    def __init__(self,explanationsList): 
        self.explanations = []
        # create a post-processed explanation 
        # for each found explanation
        for explanation in explanationsList:
            ppExp = [] # post-processed explanation
            # given an explanation, create a post-processed 
            # event modelling each original event 
            for event in explanation:
                # post-processed event info
                serviceName = str(event.args[0])
                type = None
                instance = None
                timestamp = None
                message = None 
                eventType = str(event.name)
                # case: event = "log(serviceName,instanceId,timestamp,_,_)"
                if eventType == EventType.LOG.value:
                    type = EventType.LOG
                    instance = str(event.args[1])
                    timestamp = datetime.fromtimestamp(event.args[2]) # timestamp saved as ISO
                    message = str(event.args[4])
                # case: event = "failed(serviceName,instanceId,startTimestamp,endTimestamp)"
                elif eventType == EventType.FAILED.value:
                    type = EventType.FAILED # save event type
                    instance = str(event.args[1]) # 
                # case: event = "neverStarted(serviceName)"
                elif eventType == EventType.NEVER_STARTED.value:
                    type = EventType.NEVER_STARTED
                # case: event = "unreachable(serviceName,startTimestamp,endTimestamp)"
                elif eventType == EventType.UNREACHABLE.value:
                    type = EventType.UNREACHABLE
                # case: unknown event type 
                else:
                    raise TypeError("unknown event type " + eventType) # to avoid missing events (if not corresponding to a known type)
                ppExp.append(Event(serviceName,type,instance,timestamp,message))
            self.explanations.append(ppExp)

    # returns True if exp1 and exp2 have the same explanation structure
    @staticmethod
    def akin(exp1,exp2):
        if len(exp1) != len(exp2):
                return False
        i = 0       
        while i < len(exp1):
            if not(Explanations.akinEvent(exp1[i],exp2[i])):
                return False
            i = i + 1
        return True
       
    # function to compare if two events are of the same type (even if associated with different timestamps/messages)
    @staticmethod
    def akinEvent(e1,e2):
        if e1.type == e2.type and e1.serviceName == e2.serviceName:
            return True
        else:
            return False

    # function for printing the possible failure cascades (only considering service names)
    def compactPrint(self):
        # create an array "cascade" of explanation skeletons, each with the count of 
        # how many times they appear
        cascades = []
        for explanation in self.explanations:
            if len(explanation) > 0:
                eWithCount = None
                if cascades != []:
                    for cascade in cascades:
                        if Explanations.akin(explanation,cascade["exp"]):
                            eWithCount = cascade
                            break
                if eWithCount:
                    eWithCount["count"] +=1
                else:
                    eWithCount = {}
                    eWithCount["exp"] = explanation
                    eWithCount["count"] = 1
                    cascades.append(eWithCount)
        # sort the array "cascades" by count (descending)
        cascades = sorted(cascades, key=lambda eWithCount: eWithCount['count'], reverse=True)
        # print the explanation skeletons in "cascades"
        i=1
        for eWithCount in cascades:            
            print(str(i) + " [" + str(eWithCount["count"]) + " times]: " + self.compactEventString(eWithCount["exp"][0]), end="\n  ")
            for event in eWithCount["exp"][1:]:
                print(" -> " + self.compactEventString(event), end="\n  ")
            print()
            i=i+1
    
    # function for printing a single event in an explanation (without message)
    def compactEventString(self,e):
        if e.type == EventType.LOG:
            return e.serviceName + " logged some warning/error"
        elif e.type == EventType.FAILED:
            return e.serviceName + " failed"
        elif e.type == EventType.NEVER_STARTED:
            return e.serviceName + " never started"
        elif e.type == EventType.UNREACHABLE:
            return e.serviceName + " was unreachable"

    # function for printing all explanations (verbose, with message)
    def print(self):
        i=1
        for explanation in self.explanations:
            if len(explanation) > 0:
                print(str(i) + ": " + self.eventString(explanation[0]))
                for event in explanation[1:]:
                    print(" -> " + self.eventString(event))
                i=i+1


    # function for printing a single event in an explanation (verbose, with message)
    def eventString(self,e):
        if e.type == EventType.LOG:
            timestamp = str(e.timestamp)
            #print("event logged by " + e.instance + " (" + e.serviceName + ") at time " + timestamp)
            return "[" + timestamp + "] " + e.instance + " (" + e.serviceName + "): " + e.message
        elif e.type == EventType.FAILED:
            return e.instance + " (" + e.serviceName + ") failed"
        elif e.type == EventType.NEVER_STARTED:
            return e.serviceName + " never started"
        elif e.type == EventType.UNREACHABLE:
            return e.serviceName + " was unreachable"

    # getter for the total number of explanations
    def size(self):
        l = len(self.explanations)
        if [] in self.explanations:
            l = l-1  # the "empty" explanation should not be counted
        return l