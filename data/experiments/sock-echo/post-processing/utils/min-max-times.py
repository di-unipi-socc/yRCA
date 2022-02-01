import datetime
import json
import sys

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: please specify the logfile")
        exit(-1)

    # open input log file
    logFile = sys.argv[1]
    jsonLogs = open(logFile)

    # set min/max times to default value
    minTime = None
    maxTime = None

    # parse input log file
    for jsonLog in list(jsonLogs):
        event = json.loads(jsonLog)
        
        # parse event's timestamp
        try:
            timestamp = event["timestamp"]
        except:
            # handle Logstash's grok parse failures
            timestamp = event["@timestamp"].replace("T"," ").replace("Z","")
        timestamp = datetime.datetime.fromisoformat(timestamp).timestamp()

        # check if event's timestamp is biggest timestamp
        if maxTime is None:
            maxTime = timestamp
        elif maxTime < timestamp: 
            maxTime = timestamp
        
        # check if event's timestamp is smaller timestamp
        if minTime is None:
            minTime = timestamp
        elif minTime > timestamp: 
            minTime = timestamp

    jsonLogs.close()

    # outputs
    print("minTime:",minTime)
    print("maxTime:",maxTime)
    print("elapsed seconds: ",(maxTime-minTime))