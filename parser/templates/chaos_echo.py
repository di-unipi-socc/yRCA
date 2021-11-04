import datetime
import json 
import re
from matplotlib import container

# import message structure
from parser.model.message import Message, MessageType, Parameters
from parser.model.event import Event

def parse(jsonLog):
    log = json.loads(jsonLog)
    serviceName = parseServiceName(log["container_name"])
    instanceId = parseInstanceId(log["container_name"])
    try:
        message = log["event"]
        severity = log["severity"]
        timestamp = log["timestamp"]
    except:
        # handle Logstash's grok parse failures
        message = "other"
        severity = "INFO"
        timestamp = log["@timestamp"].replace("T"," ").replace("Z","")

    # formatting fields "timestamp", "message", and "severity" as required
    timestamp = parseTimestamp(timestamp)
    message = parseMessage(message)
    severity = parseSeverity(severity)
    return Event(serviceName,instanceId,timestamp,message,severity)

# function for extracting service name from container_name
def parseServiceName(containerName):
    echoName = containerName.split(".")[0]
    return echoName.split("_")[1]
    
# function for extracting service instance identifier from container_name
def parseInstanceId(containerName):
    if containerName.find(".") < 0: # case: docker compose deployment (name already set)
        return containerName
    # case: docker stack deployment (name to be extracted)
    info = containerName.split(".")
    serviceName = info[0]
    serviceInstance = info[1]
    return serviceName + "_" + serviceInstance

# function for transforming ISO timestamps to epoch timestamps
def parseTimestamp(timestamp):
    return datetime.datetime.fromisoformat(timestamp).timestamp()

# function for parsing messages based on log templates
def parseMessage(message):
    # default: classic logging message
    msg = Message(MessageType.OTHER,message,None)
    
    # case 1: client service sending request to server service
    # example: Sending message to backend (request_id: [178cfae5-71a2-4414-bd56-d7c2cef2f172])
    msgInfo = re.match(r'Sending message to (?P<service>.*) \(request_id: \[(?P<requestId>.*)\]\)', message)
    if msgInfo is not None:
        parameters = Parameters(msgInfo.group('service'),msgInfo.group('requestId'))
        msg = Message(MessageType.CLIENT_SEND,message,parameters)

    # case 2: client service receiving answer from server service
    # three possible sub-cases
    # success: Receiving answer from backend (request_id: [178cfae5-71a2-4414-bd56-d7c2cef2f172])
    if msgInfo is None:
        msgInfo = re.match(r'Receiving answer from (?P<service>.*) \(request_id: \[(?P<requestId>.*)\]\)', message)
        if msgInfo is not None:
            parameters = Parameters(msgInfo.group('service'),msgInfo.group('requestId'))
            msg = Message(MessageType.CLIENT_RECEIVE,message,parameters)
    # error answer: Error response (code: 500) received from backend (request_id: [178cfae5-71a2-4414-bd56-d7c2cef2f172])
    if msgInfo is None: 
        msgInfo = re.match(r'Error response (code: 500) received from (?P<service>.*) \(request_id: \[(?P<requestId>.*)\]\)', message)
        if msgInfo is not None:
            parameters = Parameters(msgInfo.group('service'),msgInfo.group('requestId'))
            msg = Message(MessageType.CLIENT_ERROR,message,parameters)
    # failure: Failing to contact backend (request_id: [178cfae5-71a2-4414-bd56-d7c2cef2f172]). Root cause: Root cause: org.springframework.web.client.ResourceAccessException: ...
    if msgInfo is None:
        msgInfo = re.match(r'Failing to contact (?P<service>.*) \(request_id: \[(?P<requestId>.*)\]\). Root cause: (?P<exception>.*)', message) 
        if msgInfo is not None:
            parameters = Parameters(msgInfo.group('service'),msgInfo.group('requestId'))
            msg = Message(MessageType.CLIENT_TIMEOUT,message,parameters)

    # case 3: server service receiving request from client service
    # example: Received POST request from 10.0.0.2 (request_id: 178cfae5-71a2-4414-bd56-d7c2cef2f172)
    if msgInfo is None: 
        msgInfo = re.match(r'Received POST request from (?P<sourceIP>.*) \(request_id: (?P<requestId>.*)\)', message)
        if msgInfo is not None:
            parameters = Parameters(None,msgInfo.group('requestId'))
            # parameters = Parameters(msgInfo.group('service'),"noId") # not instrumented alternative
            msg = Message(MessageType.SERVER_RECEIVE,message,parameters)
    # case 4: server service sending answer to client service
    # example: Answered to POST request from 10.0.0.2 with code: 500 (request_id: 178cfae5-71a2-4414-bd56-d7c2cef2f172)
    if msgInfo is None: 
        msgInfo = re.match(r'Answered to POST request from (?P<sourceIP>.*) with code: (?P<statusCode>.*) \(request_id: (?P<requestId>.*)\)', message)
        if msgInfo is not None:
            parameters = Parameters(None,msgInfo.group('requestId'))
            # parameters = Parameters(msgInfo.group('service'),"noId") # not instrumented alternative
            msg = Message(MessageType.SERVER_SEND,message,parameters)
    return msg

# function for transforming logged severity to Syslog protocol: https://datatracker.ietf.org/doc/html/rfc5424
# (from Apache Log4j: https://logging.apache.org/log4j/)
def parseSeverity(severity):
    syslogSeverity = None
    if severity == "DEBUG":
        syslogSeverity = "debug"
    elif severity == "INFO":
        syslogSeverity = "info"
    elif severity == "WARN":
        syslogSeverity == "warning"
    elif severity == "ERROR":
        syslogSeverity = "err"
    elif severity == "FATAL":
        syslogSeverity == "emerg"
    return syslogSeverity