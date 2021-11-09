import datetime
import json 
import yaml
import re

# import message structure
from parser.model.message import Message, MessageType, Parameters
from parser.model.event import Event

class Templater:
    def __init__(self,templateFile):
        # parse YAML template file
        with open(templateFile, "r") as stream:
            try:
                self.templates = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def parse(self,jsonLog):
        log = json.loads(jsonLog)
        serviceName = self.parseServiceName(log["container_name"])
        instanceId = self.parseInstanceId(log["container_name"])
        try:
            message = log["event"]
            severity = log["severity"]
            timestamp = log["timestamp"]
        except:
            # handle Logstash's grok parse failures
            message = log["message"].replace("\\","").replace("/","")
            severity = "INFO"
            timestamp = log["@timestamp"].replace("T"," ").replace("Z","")

        # formatting fields "timestamp", "message", and "severity" as required
        timestamp = self.parseTimestamp(timestamp)
        message = self.parseMessage(message)
        severity = self.parseSeverity(severity)
        return Event(serviceName,instanceId,timestamp,message,severity)

    # function for extracting service name from container_name
    def parseServiceName(self,containerName):
        echoName = containerName.split(".")[0]
        return echoName.split("_")[1]
        
    # function for extracting service instance identifier from container_name
    def parseInstanceId(self,containerName):
        if containerName.find(".") < 0: # case: docker compose deployment (name already set)
            return containerName
        # case: docker stack deployment (name to be extracted)
        info = containerName.split(".")
        serviceName = info[0]
        serviceInstance = info[1]
        return serviceName + "_" + serviceInstance

    # function for transforming ISO timestamps to epoch timestamps
    def parseTimestamp(self,timestamp):
        return datetime.datetime.fromisoformat(timestamp).timestamp()

    # function for parsing messages based on log templates
    def parseMessage(self,message):
        for template in self.templates:
            msg = None

            # get message type
            if template == "client_send":
                msgType = MessageType.CLIENT_SEND
            elif template == "client_receive":
                msgType = MessageType.CLIENT_RECEIVE
            elif template == "client_error":
                msgType = MessageType.CLIENT_ERROR
            elif template == "client_timeout":
                msgType = MessageType.CLIENT_TIMEOUT
            elif template == "server_receive":
                msgType = MessageType.SERVER_RECEIVE
            elif template == "server_send":
                msgType = MessageType.SERVER_SEND

            # parse regex to check whether message is of type "template"
            for regex in self.templates[template]:
                msgInfo = re.match(r'' + regex, message)
                if msgInfo is not None:
                    try:
                        service = msgInfo.group('service')
                    except:
                        service = None
                    try:
                        requestId = msgInfo.group('requestId')
                    except:
                        requestId = "noId"
                    parameters = Parameters(service,requestId)
                    msg = Message(msgType,message,parameters)
                    break
            
            # stop if "message" has been templated
            if msg is not None: 
                break
        
        # default: classic logging message
        if msg is None:
            msg = Message(MessageType.OTHER,message,None)

        return msg

    # function for transforming logged severity to Syslog protocol: https://datatracker.ietf.org/doc/html/rfc5424
    # (from Apache Log4j: https://logging.apache.org/log4j/)
    def parseSeverity(self,severity):
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