from parser.templates.chaos_echo import parse

def parseEvents(eventLogs,targetFile):
    # open source/target files 
    logs = open(eventLogs,"r")
    prologLogs = open(targetFile,"w")
    for log in logs:
        # parsing log fields
        event = parse(log)
        # write prolog corresponding fact
        prologLogs.write(logFact(event))

    # close source/target files
    logs.close()
    prologLogs.close()

def logFact(event):
    fact = "log("
    fact += event["instance"] + ","
    fact += event["timestamp"] + ","
    fact += "'" + event["message"].replace("'","").replace("/","").replace("\\","") + "',"
    fact += event["severity"]
    fact += ").\n"
    return fact
