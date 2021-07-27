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
                # case: event = "failed(serviceName,instanceId,startTimestamp,endTimestamp)"
                elif eventType == EventType.FAILED.value:
                    ppEvent["type"] = EventType.FAILED # save event type
                    ppEvent["instance"] = str(event.args[1]) # 
                    ppEvent["interval"] = [ datetime.fromtimestamp(event.args[2]), datetime.fromtimestamp(event.args[3]) ]
                # case: event = "neverStarted(serviceName)"
                elif eventType == EventType.NEVER_STARTED.value:
                    ppEvent["type"] = EventType.NEVER_STARTED
                # case: event = "unreachable(serviceName,startTimestamp,endTimestamp)"
                elif eventType == EventType.UNREACHABLE.value:
                    ppEvent["type"] = EventType.UNREACHABLE
                    ppEvent["interval"] = [ datetime.fromtimestamp(event.args[1]), datetime.fromtimestamp(event.args[2]) ]
                # case: unknown event type 
                else:
                    raise TypeError("unknown event type " + e) # to avoid missing events (if not corresponding to a known type)
                ppExp.append(ppEvent)
            self.explanations.append(ppExp)

    # function for printing all explanations
    def print(self):
        for explanation in self.explanations:
            if len(explanation) > 0:
                self.printEvent(explanation[0])
                for event in explanation[1:]:
                    print(" -> ",end="")
                    self.printEvent(event)
                print()

    # function for printing a single event in an explanation
    def printEvent(self,e):
        if e["type"] == EventType.LOG:
            timestamp = str(e["timestamp"])
            print("event logged by " + e["instance"] + " (" + e["serviceName"] + ") at time " + timestamp)
        elif e["type"] == EventType.FAILED:
            startTime = str(e["interval"][0])
            endTime = str(e["interval"][1])
            print(e["instance"] + " (" + e["serviceName"] + ") failed between " + startTime + " and " + endTime)
        elif e["type"] == EventType.NEVER_STARTED:
            print(e["serviceName"] + " never started")
        elif e["type"] == EventType.UNREACHABLE:
            startTime = str(e["interval"][0])
            endTime = str(e["interval"][1])
            print(e["serviceName"] + "was unreachable between " +startTime + " and " + endTime)

    # getter for the total number of explanations
    def size(self):
        return len(self.explanations)-1 # -1 since we always find an "empty" explanation
