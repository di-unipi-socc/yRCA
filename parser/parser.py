from parser.model.message import MessageType

# The method "parse" imported from the "templates" package must parse a log line and
# return an "Event" object (see "model/event.py")

def parseEvents(applicationLogs,targetFile,templater):
    # open source/target files 
    loggedEvents = open(applicationLogs,"r")
    knowledgeBase = open(targetFile,"w")

    # parse logged events (reversed, to go from last logged event to first logged event)
    for le in reversed(list(loggedEvents)): 
        # parsing log event with chosen template
        event = templater.parse(le)
        # write prolog corresponding fact
        knowledgeBase.write(generateLogFact(event))

    # close source/target files
    loggedEvents.close()
    knowledgeBase.close()

# function for generating the Prolog representation of a log event
# (it takes as input an "Event" -> see module "event.py")
def generateLogFact(event):
    fact = "log("
    fact += event.serviceName + ","
    fact += event.instanceId + ","
    fact += str(event.timestamp) + "," 
    fact += generateMessage(event.message) + ","
    fact += "'" + str(event.message.content) + "',"
    fact += event.severity
    fact += ").\n"
    return fact

# support function for generating a Prolog representation of log messages
# (it takes as input a "Message" -> see module "message.py")
def generateMessage(msg):
    if msg.type == MessageType.CLIENT_SEND:
        return "sendTo(" + msg.parameters.service + ",'" + msg.parameters.requestId + "')"
    if msg.type == MessageType.CLIENT_RECEIVE:
        return "okFrom(" + msg.parameters.service + ",'" + msg.parameters.requestId + "')"
    if msg.type == MessageType.CLIENT_ERROR:
        return "errorFrom(" + msg.parameters.service + ",'" + msg.parameters.requestId + "')"
    if msg.type == MessageType.CLIENT_TIMEOUT:
        return "timeout(" + msg.parameters.service + ",'" + msg.parameters.requestId + "')"
    if msg.type == MessageType.SERVER_RECEIVE:
        return "received('" + msg.parameters.requestId + "')"
    if msg.type == MessageType.SERVER_SEND:
        return "answeredTo('" + msg.parameters.requestId + "')"
    return "internal"
