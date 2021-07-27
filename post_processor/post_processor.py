from datetime import datetime

from post_processor.model.explanations import Explanations


def post_process(event,rootCauses,applicationLogs):
    # TODO: ongoing, just for testing purposes

    # get event fact
    eventProlog = open(event,"r")
    eventFact = eventProlog.readline()
    eventProlog.close()
    eventFact = eventFact[:len(eventFact)-2]

    # print root causes 
    explanations = Explanations(rootCauses[0]["Explanations"])
    explanations.print()
    print("\nFound",explanations.size(),"possible root causes")
