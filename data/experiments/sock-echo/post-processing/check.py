from distutils.log import error
from enum import Enum
import json
import os
import re
import sys

class Severity(Enum):
    FATAL = 0
    ERROR = 1
    WARN = 2
    INFO = 3
    DEBUG = 4

def getSeverity(sev): 
    if sev == "ERROR":
        return Severity.ERROR
    elif sev == "INFO":
        return Severity.INFO
    else:
        return Severity.DEBUG

class Templates(Enum):
    CLIENT_SEND='Sending message to (?P<service>.*) \(request_id: \[(?P<requestId>.*)\]\)'
    SENT_MESSAGE='Sent message: { "hash": "(?P<hash>.*)", "content": "(?P<message>.*)" } \(request_id: \[(?P<requestId>.*)\]\)'
    ERROR_RESPONSE='Error response \(code: 500\) received from (?P<service>.*) \(request_id: \[(?P<requestId>.*)\]\)'
    TIMEOUT='Failing to contact (?P<service>.*) \(request_id: \[(?P<requestId>.*)\]\). Root cause: (?P<exception>.*)'

# function for parsing a logged message
def parseMessage(msg): 
    # parse logged event (case: client send)
    msgInfo = re.match(r'' + Templates.CLIENT_SEND.value, msg)
    if msgInfo is not None:
        return { "info": msgInfo, "template": Templates.CLIENT_SEND.value }
    # parse logged event (case: message sent)
    msgInfo = re.match(r'' + Templates.SENT_MESSAGE.value, msg)
    if msgInfo is not None:
        return { "info": msgInfo, "template": Templates.SENT_MESSAGE.value }
    # parse logged event (case: error response)
    msgInfo = re.match(r'' + Templates.ERROR_RESPONSE.value, msg)
    if msgInfo is not None:
        return { "info": msgInfo, "template": Templates.ERROR_RESPONSE.value }
    # parse logged event (case: timeout)
    msgInfo = re.match(r'' + Templates.TIMEOUT.value, msg)
    if msgInfo is not None:
        return { "info": msgInfo, "template": Templates.TIMEOUT.value }
    return None

# function for parsing a logged event, given its corresponding JSON string
# returns:
# - (service,requestId,template,traceMsg,timestamp) if the event is interesting (see Templates)
# - None otherwise 
def parseEvent(jsonString):
    # json parsing
    jsonEvent = json.loads(jsonString)

    if '_grokparsefailure' in jsonEvent["tags"]:
        return None # skip useless events

    # event info to be returned
    event = None

    # if it is an event of interest, fill "event"
    msg = parseMessage(jsonEvent["event"])    
    if msg:
        event = {}
        # service name
        event["service"] = jsonEvent["container_name"].split(".")[0].split("_")[1]
        #requestId
        event["requestId"] = msg["info"].group("requestId")
        # log template
        event["template"] = msg["template"]
        if "<service>" in event["template"]:
            event["target"] = msg["info"].group("service")
            event["template"] = event["template"].replace("(?P<service>.*)",msg["info"].group("service"))
        event["template"] = event["template"].replace("\\","").replace("(?P","").replace(".*)","") # log template
        if msg["template"] == Templates.SENT_MESSAGE.value:
            event["traceMsg"] = msg["info"].group("message")
        else:
            event["traceMsg"] = None
        # timestamp
        event["timestamp"] = jsonEvent["timestamp"]
        # severity
        event["severity"] = getSeverity(jsonEvent["severity"])
    return event

# functions to add trace messages (forwarded by chaos echo services) to parsed events
def addTraceMsgs(logs):
    for log in logs:
        if not log["traceMsg"]:
            addTraceMsg(log,logs)
def addTraceMsg(log,logs):
    for l in logs:
        if "Sent message" in l["template"]:
            if log["service"]==l["service"] and log["requestId"]==l["requestId"]:
                log["traceMsg"] = l["traceMsg"]

# function to get all events pertaining to a trace defined by a forwarded message
def getTraceEvents(log,logs):
    events = []
    for l in logs:
        if log["traceMsg"]==l["traceMsg"]:
            events.append(l)
    return events

# function to extract the error events in a trace
# returns a list containing messages structured as in yrca's outputs
def getErrorTrace(traceEvents):
    errorTrace = []
    traceEvents.sort(key=lambda e:e["timestamp"])
    last = None
    for e in traceEvents:
        if e["severity"].value <= Severity.WARN.value:
            eString = e["service"] + ": " + e["template"]
            last = e["target"]
            errorTrace.append(eString)
    errorTrace.append(last)
    return errorTrace

# function to get the error trace for a given failure, given the filePaths
def getErrorTraceFromFiles(eventJson,logsFilePath):
    event = parseEvent(eventJson)

    # get needed logs
    logsFile = open(logsFilePath)
    allLogs = list(logsFile)
    logs = []
    for log in allLogs:
        l = parseEvent(log)
        if l:
            logs.append(l)
    
    # close files
    logsFile.close()

    # add trace messages
    addTraceMsg(event,logs)
    addTraceMsgs(logs)

    # return error trace (as list)
    return getErrorTrace(getTraceEvents(event,logs))

# function to compare two different error traces (given as list of messages structured as in yrca's outputs) 
# returns True if equal, False otherwise
def compareErrorTraces(output,truth):
    # if different lengths, False
    if len(output) != len(truth):
        return False
    # if not rooted in the same service, False
    if not output[len(output)-1].startswith(truth[len(truth)-1]):
        return False
    # otherwise, check if they have the same structure
    for i in range(len(output)-1):
        if output[i] != truth[i]:
            return False
    return True

# function returning an object representing all outputs as follows,    
# o
# - experiment folder
# - - case file
# - - - json event 
# - - - - list of possible explanations    
def getOutputs(outputsFilePath):
    outputsFile = open(outputsFilePath)
    outputs = list(outputsFile)
    outputsFile.close()

    # substrings to match the beginning of different lines in outputs.txt
    matchFolder = "*	"
    matchFile = "> "
    matchEvent = "{"
    matchStartExp = "["
    matchOngoingExp = "   -> "

    # create an object representing all outputs as follows
    o = {}

    for i in range(len(outputs)):
        line = outputs[i]
        # case: new experiment (folder)
        if line.startswith(matchFolder):
            folder = line[len(matchFolder):len(line)-1]
            o[folder] = {} # create object to represent the results of this experiment
        # case: new experiment case (file)
        elif line.startswith(matchFile):
            file = line[len(matchFile):]
            file = file.split(" (")[0]
            o[folder][file] = {} # create object to represent the results of this case
        # case: new case's event (failure) 
        elif line.startswith(matchEvent):
            event = line
            o[folder][file][event] = [] # create list to include the explanations of this event
        # case: new explanation for an event
        elif line.startswith(matchStartExp):
            errorTrace = [line.split("]:")[1]]
            while outputs[i+1].startswith(matchOngoingExp):
                i += 1
                line = outputs[i]
                errorTrace.append(line[len(matchOngoingExp):])
            o[folder][file][event].append(errorTrace)
    return o

if __name__ == "__main__":
    argv = sys.argv[1:]
    
    checkResults = open("check-results.txt","w")

    # input files
    outputsFilePath = argv[0]
    
    # get outputs
    o = getOutputs(outputsFilePath)

    # check outputs (counting mismatches)
    mismatches = 0
    cwd = os.getcwd()
    for folder in o:
        print("*"*30, file=checkResults)
        print(" FOLDER: " + folder, file=checkResults)
        print("*"*30, file=checkResults)
        for file in o[folder]:
            print("FILE: " + file, file=checkResults)
            logsFilePath = os.path.join("../generated-logs",folder,file) 
            c = 0
            for event in o[folder][file]:
                print(str(c) + ": " + event, file=checkResults)
                gtruth = getErrorTraceFromFiles(event,logsFilePath)
                found = False
                for trace in o[folder][file][trace]:
                    if compareErrorTraces(trace,gtruth):
                        found = True
                if not found:
                    mismatches += 1
                    print("MISMATCH ON " + gtruth, file=checkResults)
                    print("", file=checkResults)
                c += 1
            print("", file=checkResults)
        print("", file=checkResults)
            
    print("MISMATCHES: " + str(mismatches), file=checkResults)

    checkResults.close()