from datetime import datetime
from enum import Enum
import getopt,json,re,sys

class Severity(Enum):
    FATAL = 0
    ERROR = 1
    WARN = 2
    INFO = 3
    DEBUG = 4

class Templates(Enum):
    ERROR_RESPONSE='Error response \(code: 500\) received from (?P<service>.*) \(request_id: \[(?P<requestId>.*)\]\)'
    TIMEOUT='Failing to contact (?P<service>.*) \(request_id: \[(?P<requestId>.*)\]\). Root cause: (?P<exception>.*)'
    SENT_MESSAGE='Sent message: { "hash": "(?P<hash>.*)", "content": "(?P<message>.*)" } \(request_id: \[(?P<requestId>.*)\]\)'

# function returning the distance of each service from Sock Shop's edgeRouter
def dist(service):
    if service == "edgeRouter":
        return 0
    if service == "frontend":
        return 1
    if service in ["orders","users","catalogue","carts"]:
        return 2
    if service in ["shipping","ordersDb","payment","usersDb","catalogueDb","cartsDb"]:
        return 3
    if service == "rabbitMq":
        return 4
    return 5

def printTrace(eventFilePath,logFilePath,maxSeverity,verbose):
    # read event's "session id"
    eventFile = open(eventFilePath, "r")
    event = eventFile.readline()
    eventFile.close()
    requestId = getRequestId(event)
    
    # get logs involved in the considered cascade
    message = getMessage(requestId,logFilePath)
    ppLogs = getInvolvedEvents(message,event,logFilePath)

    # print logs
    printLogs(ppLogs,maxSeverity,verbose)

# function for parsing a logged event
def parseLogMsg(msg): 
    # parse logged event (case: error response)
    msgInfo = re.match(r'' + Templates.ERROR_RESPONSE.value, msg)
    if msgInfo is not None:
        return msgInfo
    # parse logged event (case: timeout)
    msgInfo = re.match(r'' + Templates.TIMEOUT.value, msg)
    if msgInfo is not None:
        return msgInfo
    # parse logged event (case: message sent)
    msgInfo = re.match(r'' + Templates.SENT_MESSAGE.value, msg)
    if msgInfo is not None:
        return msgInfo
    return None

# function for getting the request id from a logged event
def getRequestId(logString):
    # get logged event
    event = json.loads(logString)
    # parse logged event
    msgInfo = parseLogMsg(event["event"])
    if msgInfo is not None:
        return msgInfo.group("requestId")
    return None

# function for getting the invoked service from a logged event
def getInvokedService(msg):
    # parse logged event
    msgInfo = parseLogMsg(msg)
    if msgInfo is not None:
        return msgInfo.group("service")
    return None

# function for identifying the message sent in an interaction, given the interaction's request id
def getMessage(requestId,logFilePath):
    logFile = open(logFilePath, "r")
    message = None
    for logString in list(logFile):
        if (requestId is not None) and (requestId in logString):
            log = json.loads(logString)
            msg = log["event"]
            msgInfo = re.match(r'' + Templates.SENT_MESSAGE.value,msg)
            if msgInfo is not None:
                message = msgInfo.group("message")
                break
    logFile.close()
    return message

# function for getting all logged events pertaining to interactions where a given "message" was sent
def getInvolvedEvents(message,event,logFilePath):
    # get timestamp of "event"
    timestamp = json.loads(event)["timestamp"] # needed?

    # get all request ids of interactions sending the "message" (before the "event")
    requestIds = []
    logFile = open(logFilePath, "r")
    for logString in list(logFile):
        loggedEvent = json.loads(logString)
        try: 
            if message in loggedEvent["message"]: # and loggedEvent["timestamp"] <= timestamp:
                requestId = getRequestId(logString)
                if requestId:
                    requestIds.append(requestId)
        except:
            print(loggedEvent)
    logFile.close()

    # get all interaction logs involving the "message" (before the "event")
    logFile = open(logFilePath, "r")
    ppLogs = [] # post-processed logs
    for logString in list(logFile):
        log = json.loads(logString)
        for requestId in requestIds:
            if requestId in log["message"]: # and log["timestamp"] <= timestamp:
                ppLog = {} # post-processed log
                # ppLog's timestamp
                ppLog["timestamp"] = datetime.strptime(log["timestamp"], '%Y-%m-%d %H:%M:%S.%f')
                # ppLog's service instance
                containerName = log["container_name"].split("_")[1]
                ppLog["service"] = containerName.split(".")[0]
                ppLog["instance"] = containerName.split(".")[1]
                # ppLog's logged event
                ppLog["message"] = log["event"]
                # ppLog's severity
                if log["severity"] == "DEBUG":
                    ppLog["severity"] = Severity.DEBUG
                elif log["severity"] == "INFO":
                    ppLog["severity"] = Severity.INFO
                elif log["severity"] == "WARN":
                    ppLog["severity"] = Severity.WARN
                elif log["severity"] == "ERROR":
                    ppLog["severity"] = Severity.ERROR
                elif log["severity"] == "FATAL":
                    ppLog["severity"] = Severity.FATAL
                # add ppLog to post-processed logs
                ppLogs.append(ppLog)
    logFile.close()
    ppLogs.sort(key=lambda x: (dist(x["service"]), -datetime.timestamp(x["timestamp"])))
    return ppLogs

# function for printing post-processed logs
def printLogs(ppLogs,maxSeverity,verbose):
    first = True
    for log in ppLogs:
        if log["severity"].value <= maxSeverity.value:
            toPrint = "   -> "
            if first:
                toPrint = ""
                first = False 
            toPrint += getLogPrintout(log,verbose)
            print(toPrint)

# function for getting the string to print for a log
def getLogPrintout(log,verbose):
    logPrintout = log["service"] + ": "
    if verbose:
        logPrintout += "\n\tInstance: " + log["instance"] 
        logPrintout += "\n\tTimestamp: " + str(log["timestamp"])
        logPrintout += "\n\tMessage: " 
    msgInfo = parseLogMsg(log["message"])
    msg = log["message"].replace(msgInfo.group("requestId"),"<requestId>")
    if "exception" in msgInfo.group():
        msg = msg.replace(msgInfo.group("exception"),"<exception>")
    logPrintout += msg
    return logPrintout

# function for printing cli erros, followed by cli usage
def cli_error(message):
    print("ERROR: " + message + ".")
    print()
    cli_help()

# function for printing cli usage
def cli_help():
    print("Usage of explain.py is as follows:")
    print("  filter_logs.py [OPTIONS] sourceEvent.json applicationLogs.json")
    print("where OPTIONS can be")
    print("  [--help] to print a help on the usage of filter_logs.py")
    print("  [-a|--all] to print all logs (including INFO/DEBUG logs)")
    print("  [-v|--verbose] to print more log info")
    print()

if __name__ == "__main__":
    argv = sys.argv[1:]

    # check if "help" is required
    if "--help" in argv:
        cli_help()
        exit(0)

    # otherwise, parse command line arguments
    try:
        options,args = getopt.getopt(argv,"av",["all:verbose"])
    except: 
        cli_error("wrong options used")
        exit(-1)

    # check & process command line arguments
    if len(args) < 2:
        cli_error("missing input arguments")
        exit(-1)

    # store arguments
    eventFilePath = args[0]
    logFilePath = args[1]

    # set options
    maxSeverity = Severity.WARN # by default, print only error logs
    verbose = False # by default, only printing service name and message
    for option,value in options:
        if option in ["-a","--all"]:
            maxSeverity = Severity.DEBUG # if required, print all logs
        if option in ["-v","--verbose"]:
            verbose = True # if required, print all logs

    # print trace
    printTrace(eventFilePath,logFilePath,maxSeverity,verbose)