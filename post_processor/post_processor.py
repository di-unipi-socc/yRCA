from datetime import datetime


def post_process(event,rootCauses,applicationLogs):
    # TODO: ongoing, just for testing purposes

    # get event fact
    eventProlog = open(event,"r")
    eventFact = eventProlog.readline()
    eventProlog.close()
    eventFact = eventFact[:len(eventFact)-2]

    # print root causes 
    for rc in rootCauses:
        # rc["Explanations"] contains all possible explanations
        for c in rc["Explanations"]:
            print(eventFact)
            # each explanations is a list of prolog facts
            for e in c: 
                print(" ->",e) 
        print("Found",len(rc["Explanations"]),"explanations.")

