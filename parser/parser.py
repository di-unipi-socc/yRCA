# import "parse" method from log templater 
from parser.message import Message, MessageType
from parser.templates.chaos_echo import parse

def parseEvents(eventLogs,targetFile):
    # open source/target files 
    logs = open(eventLogs,"r")
    prologLogs = open(targetFile,"w")
    for log in logs:
        # parsing log fields
        event = parse(log)

        # write prolog corresponding fact
        prologLogs.write(logFact(event))

        # TODO: Either introduce predicates as events' messages, or use templating also for parsing interactions

    # close source/target files
    logs.close()
    prologLogs.close()

def logFact(event):
    fact = "log("
    fact += event.serviceName + ","
    fact += event.instanceId + ","
    fact += str(event.timestamp) + "," 
    fact += generateMessage(event.message) + ","
    fact += event.severity
    fact += ").\n"
    return fact

def generateMessage(msg):
    if msg.type == MessageType.CLIENT_SEND:
        return "sendTo(" + msg.parameters.service + "," + msg.parameters.requestId + ")"
    if msg.type == MessageType.CLIENT_RECEIVE:
        return "answerFrom(" + msg.parameters.service + "," + msg.parameters.requestId + ")"
    if msg.type == MessageType.SERVER_RECEIVE:
        return "received(" + msg.parameters.requestId + ")"
    if msg.type == MessageType.SERVER_SEND:
        return "answeredTo(" + msg.parameters.requestId + ")"
    return "other"
