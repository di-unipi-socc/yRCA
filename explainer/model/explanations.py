from datetime import datetime
from enum import Enum
from multiprocessing import Event

# class for distinguishing the "type" of events
class EventType(Enum):
    LOG = "log"
    UNREACHABLE = "unreachable"
    FAILED = "failed"
    NEVER_STARTED = "neverStarted"

# class to represent list of possible root causes/explanations
# (takes as input "explanationsList" returned by pyswip)
class Explanations:
    def __init__(self,explanationsList): # TODO: add applicationLogs to retrieve messages
        self.explanations = []
        # create a post-processed explanation 
        # for each found explanation
        for explanation in explanationsList:
            ppExp = [] # post-processed explanation
            # given an explanation, create a post-processed 
            # event modelling each original event 
            for event in explanation:
                ppEvent = {} # post-processed event
                ppEvent["serviceName"] = str(event.args[0])
                eventType = str(event.name)
                # case: event = "log(serviceName,instanceId,timestamp,_,_)"
                if eventType == EventType.LOG.value:
                    ppEvent["type"] = EventType.LOG
                    ppEvent["instance"] = str(event.args[1])
                    ppEvent["timestamp"] = datetime.fromtimestamp(event.args[2]) # timestamp saved as ISO
                    ppEvent["message"] = str(event.args[4])
                # case: event = "failed(serviceName,instanceId,startTimestamp,endTimestamp)"
                elif eventType == EventType.FAILED.value:
                    ppEvent["type"] = EventType.FAILED # save event type
                    ppEvent["instance"] = str(event.args[1]) # 
                # case: event = "neverStarted(serviceName)"
                elif eventType == EventType.NEVER_STARTED.value:
                    ppEvent["type"] = EventType.NEVER_STARTED
                # case: event = "unreachable(serviceName,startTimestamp,endTimestamp)"
                elif eventType == EventType.UNREACHABLE.value:
                    ppEvent["type"] = EventType.UNREACHABLE
                # case: unknown event type 
                else:
                    raise TypeError("unknown event type " + eventType) # to avoid missing events (if not corresponding to a known type)
                ppExp.append(ppEvent)
            self.explanations.append(ppExp)

    # returns True if exp1 and exp2 have the same explanation structure
    def akin(self,exp1,exp2):
        if len(exp1) != len(exp2):
                return False
        i = 0       
        while i < len(exp1):
            if not(self.akinEvent(exp1[i],exp2[i])):
                return False
            i = i + 1
        return True
       
    # function to compare if two events are of the same type (even if associated with different timestamps/messages)
    def akinEvent(self,e1,e2):
        if e1["type"] == e2["type"] and e1["serviceName"] == e2["serviceName"]:
            return True
        else:
            return False

    # function for printing the possible failure cascades (only considering service names)
    def compactPrint(self):
        printedCascades = []
        i=1
        for explanation in self.explanations:
            if len(explanation) > 0:
                # check if explanation has already been printed
                toPrint = True
                for printed in printedCascades:
                    if self.akin(explanation,printed):
                        toPrint = False
                        break
                # if not yet printed, print skeleton
                if toPrint:
                    printedCascades.append(explanation)
                    print(str(i) + ": " + self.compactEventString(explanation[0]), end="\n  ")
                    for event in explanation[1:]:
                        print(" -> " + self.compactEventString(event), end="\n  ")
                    print()
                    i=i+1
    
    # function for printing a single event in an explanation (without message)
    def compactEventString(self,e):
        if e["type"] == EventType.LOG:
            return e["serviceName"] + " logged some warning/error"
        elif e["type"] == EventType.FAILED:
            return e["serviceName"] + " failed"
        elif e["type"] == EventType.NEVER_STARTED:
            return e["serviceName"] + " never started"
        elif e["type"] == EventType.UNREACHABLE:
            return e["serviceName"] + " was unreachable"

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
        if e["type"] == EventType.LOG:
            timestamp = str(e["timestamp"])
            #print("event logged by " + e["instance"] + " (" + e["serviceName"] + ") at time " + timestamp)
            return "[" + timestamp + "] " + e["instance"] + " (" + e["serviceName"] + "): " + e["message"]
        elif e["type"] == EventType.FAILED:
            return e["instance"] + " (" + e["serviceName"] + ") failed"
        elif e["type"] == EventType.NEVER_STARTED:
            return e["serviceName"] + " never started"
        elif e["type"] == EventType.UNREACHABLE:
            return e["serviceName"] + " was unreachable"

    # getter for the total number of explanations
    def size(self):
        l = len(self.explanations)
        if [] in self.explanations:
            l = l-1  # the "empty" explanation should not be counted
        return l
