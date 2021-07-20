import json 

def parse(jsonLog):
    log = json.loads(jsonLog)
    event = {}
    event["instance"] = log["container_name"]
    try:
        event["message"] = log["event"]
        event["severity"] = log["severity"]
        event["timestamp"] = log["timestamp"]
    except:
        # handle Logstash's grok parse failures
        event["message"] = log["message"]
        event["severity"] = "INFO"
        event["timestamp"] = log["@timestamp"]
    return event