import datetime
import json 

def parse(jsonLog):
    log = json.loads(jsonLog)
    event = {}
    event["instance"] = parseInstanceName(log["container_name"])
    try:
        event["message"] = log["event"] # TODO: this should be processed to extract info needed for predicates (or 'other', if not interesting)
        event["severity"] = log["severity"]
        event["timestamp"] = log["timestamp"]
    except:
        # handle Logstash's grok parse failures
        event["message"] = log["message"] # TODO: this could be 'other'
        event["severity"] = "INFO"
        event["timestamp"] = log["@timestamp"].replace("T"," ").replace("Z","")
    
    event["timestamp"] = parseTimestamp(event["timestamp"])
    return event

def parseInstanceName(containerName):
    info = containerName.split(".")
    serviceName = info[0]
    serviceInstance = info[1]
    return serviceName + "_" + serviceInstance

def parseTimestamp(timestamp):
    return datetime.datetime.fromisoformat(timestamp).timestamp()