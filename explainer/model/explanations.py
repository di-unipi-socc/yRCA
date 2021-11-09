from datetime import datetime
from enum import Enum
from os import putenv

# import message structure
from parser.model.message import MessageType

# class for distinguishing the "type" of events
class EventType(Enum):
    LOG = "log"
    UNREACHABLE = "unreachable"
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
    def akin(exp1,exp2,templater):
        if len(exp1) != len(exp2):
                return False
        i = 0       
        while i < len(exp1):
            if not(Explanations.akinEvent(exp1[i],exp2[i],templater)):
                return False
            i = i + 1
        return True
       
    # function to compare if two events are of the same type (even if associated with different timestamps/messages)
    @staticmethod
    def akinEvent(e1,e2,templater):
        if e1.type == e2.type and e1.serviceName == e2.serviceName:
            if e1.type != EventType.LOG:
                return True
            else:
                msg1 = templater.parseMessage(e1.message)
                msg2 = templater.parseMessage(e2.message)
                if msg1.type == msg2.type and msg1.template == msg2.template:
                    return True
                else:
                    return False
        else:
            return False

    def groupExplanations(self,templater):
        # create an array "groupedExplanations" of explanation groups
        # (explanations with the same skeleton go in the same group)
        groupedExplanations = []
        for explanation in self.explanations:
            if len(explanation) > 0:
                expList = None
                if groupedExplanations != []:
                    for cascade in groupedExplanations:
                        if Explanations.akin(explanation,cascade[0],templater):
                            expList = cascade
                            break
                if expList:
                    expList.append(explanation)
                else:
                    expList = []
                    expList.append(explanation)
                    groupedExplanations.append(expList)
        # sort the array "groupedExplanations" by group size (descending)
        groupedExplanations = sorted(groupedExplanations, key=lambda expList: len(expList), reverse=True)
        return groupedExplanations

    # function for printing the possible failure cascades (only considering service names)
    def compactPrint(self,templater):
        expLists = self.groupExplanations(templater)
        size = float(self.size())
        # print the explanation skeletons in "cascades"
        for expList in expLists:
            explanation = expList[0]
            percentage = round(len(expList)/size,3)
            print("[" + str(percentage) + "]: " + self.compactEventString(explanation[0],templater), end="\n  ")
            for event in explanation[1:]:
                print(" -> " + self.compactEventString(event,templater), end="\n  ")
            print()
    
    # function for printing a single event in an explanation (without message)
    def compactEventString(self,e,templater):
        eventString = e.serviceName + ": " 
        # return log template structure in case of logged events
        if e.type == EventType.LOG:
            msg = templater.parseMessage(e.message)
            if msg.type == MessageType.OTHER:
                eventString += e.message
            else:
                eventString += msg.template.replace("(?P","").replace(".*)","").replace("\\","").replace("<service>",e.serviceName)
        elif e.type == EventType.NEVER_STARTED:
            eventString += "never started"
        elif e.type == EventType.UNREACHABLE:
            eventString += "unreachable"
        return eventString

    # function for printing all explanations (verbose, with message)
    def print(self,templater):
        expLists = self.groupExplanations(templater)
        i=1
        for expList in expLists:
            for explanation in expList:
                print(str(i) + ": " + self.eventString(explanation[0]))
                for event in explanation[1:]:
                    print(" -> " + self.eventString(event))
                i=i+1
            print()

    # function for marshalling all explanations (verbose, with message)
    def marshal(self,templater,outputFile):
        expLists = self.groupExplanations(templater)
        output = open(outputFile,"w")
        output.write("* "*40 + "\n")
        for expList in expLists:
            for explanation in expList:
                output.write("\n" + self.eventString(explanation[0]) + "\n")
                for event in explanation[1:]:
                    output.write(" -> " + self.eventString(event) + "\n")
            output.write("\n" + "* "*40 + "\n")
        output.close()

    # function for printing a single event in an explanation (verbose, with message)
    def eventString(self,e):
        if e.type == EventType.LOG:
            timestamp = str(e.timestamp)
            return "[" + timestamp + "] " + e.instance + " (" + e.serviceName + "): " + e.message
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