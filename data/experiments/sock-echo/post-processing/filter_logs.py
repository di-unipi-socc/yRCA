from datetime import datetime, time
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

def main(argv):
    # check if "help" is required
    if "--help" in argv:
        cli_help()
        return

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

    # check options
    maxSeverity = Severity.WARN # by default, print only error logs
    verbose = False # by default, only printing service name and message
    for option,value in options:
        # setting lookback radius
        if option in ["-a","--all"]:
            maxSeverity = Severity.DEBUG # if required, print all logs
        if option in ["-v","--verbose"]:
            verbose = True # if required, print all logs
    
    # read event's "session id"
    eventFile = open(eventFilePath, "r")
    event = eventFile.readline()
    eventFile.close()
    requestId = getRequestId(event)
    
    # get logs involved in the considered cascade
    message = getMessage(requestId,logFilePath)
    ppLogs = getInvolvedEvents(message,logFilePath)

    # print logs
    printLogs(ppLogs,maxSeverity,verbose)


# function for getting the request id from a logged event
def getRequestId(logString):
    # get logged event
    event = json.loads(logString)
    msg = event["event"]
    # parse logged event (case: error response)
    msgInfo = re.match(r'' + Templates.ERROR_RESPONSE.value, msg)
    if msgInfo is not None:
        return msgInfo.group("requestId")
    # parse logged event (case: timeout)
    msgInfo = re.match(r'' + Templates.TIMEOUT.value, msg)
    if msgInfo is not None:
        return msgInfo.group("requestId")
    # parse logged event (case: message sent)
    msgInfo = re.match(r'' + Templates.SENT_MESSAGE.value, msg)
    if msgInfo is not None:
        return msgInfo.group("requestId")
    return None

# function for identifying the message sent in an interaction, given the interaction's request id
def getMessage(requestId,logFilePath):
    logFile = open(logFilePath, "r")
    message = None
    for logString in list(logFile):
        if (requestId in logString):
            log = json.loads(logString)
            msg = log["event"]
            msgInfo = re.match(r'' + Templates.SENT_MESSAGE.value,msg)
            if msgInfo is not None:
                message = msgInfo.group("message")
                break
    logFile.close()
    return message

# function for getting all logged events pertaining to interactions where a given "message" was sent
def getInvolvedEvents(message,logFilePath):
    # get all request ids of interactions sending the "message"
    requestIds = []
    logFile = open(logFilePath, "r")
    for logString in list(logFile):
        if message in logString:
            requestId = getRequestId(logString)
            if requestId:
                requestIds.append(requestId)
    logFile.close()
    # get all interaction logs involving the "message"
    logFile = open(logFilePath, "r")
    ppLogs = [] # post-processed logs
    for logString in list(logFile):
        for requestId in requestIds:
            if requestId in logString:
                log = json.loads(logString)
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
    ppLogs.sort(key=lambda x: x["timestamp"],reverse=True)
    return ppLogs

# function for printing post-processed logs
def printLogs(ppLogs,maxSeverity,verbose):
    first = True
    for log in ppLogs:
        if log["severity"].value <= maxSeverity.value:
            toPrint = "-> "
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
    logPrintout += log["message"]
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
    main(sys.argv[1:])