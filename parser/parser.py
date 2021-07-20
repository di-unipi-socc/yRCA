import json
from parser.templates.chaos_echo import parse

def parseEvents(eventLogs,targetFile):
    # open source/target files 
    jsonLogs = open(eventLogs,"r")
    prologLogs = open(targetFile,"w")
    for jsonLog in jsonLogs:
        # parsing log fields
        log = json.loads(jsonLog)

        containerName = log["container_name"]
        containerId = log["container_id"]
        try:
            event = log["event"]
            severity = log["severity"]
            timestamp = log["timestamp"]
        except:
            # handle Logstash's grok parse failures
            event = log["message"]
            severity = "INFO"
            timestamp = log["@timestamp"]

        prologLogs.write(logFact(containerName,containerId,event,timestamp,severity))

    # close source/target files
    jsonLogs.close()
    prologLogs.close()

def logFact(containerName,containerId,event,timestamp,severity):
    fact = "log("
    #fact += containerName + ","
    fact += containerId + ","
    fact += "'" + parse(event) + "',"
    fact += timestamp + ","
    fact += severity
    fact += ").\n"
    return fact
