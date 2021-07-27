# import Python default modules
import sys, getopt
# import explainer's modules
from parser.parser import parseEvents
from explainer.explainer import explain
from post_processor.post_processor import post_process

def main(argv):
    heartbeat = 10 # default value considered for heartbeat logs

    # parse command line arguments
    try:
        opts,args = getopt.getopt(argv,"hb:",["help","heartbeat=",])
    except: 
        cli_error("wrong options used")
        exit(-1)
    # check & process command line arguments
    if len(args) < 2:
        cli_error("missing input arguments")
        exit(-1)
    for opt, arg in opts:
        if opt in ["-b","--heartbeat"]:
            if arg.isnumeric():
                heartbeat = arg
            else: 
                cli_error("heartbeat value must be a number")
                return
        if opt in ["-h","--help"]:
            cli_help()
    eventLogLine = args[0]
    applicationLogs = args[1]

    # ******************
    # * PARSING INPUTS *
    # ******************
    # parse "event" to be explained and all events forming the "knowledgeBase"
    event = "event.pl"
    parseEvents(eventLogLine,event)
    knowledgeBase = "knowledgeBase.pl"
    parseEvents(applicationLogs,knowledgeBase)
    
    # add heartbeat value to "knowledgeBase"
    prologFacts = open(knowledgeBase,"a")
    prologFacts.write("heartbeat(" + str(heartbeat) + ").")
    prologFacts.close()

    # ***********************
    # * ROOT CAUSE ANALYSIS *
    # ***********************
    rootCauses = explain(event,knowledgeBase)
    
    # *******************
    # * POST-PROCESSING *
    # *******************
    post_process(event,rootCauses,applicationLogs)

def cli_error(message):
    print("ERROR: " + message + ".")
    print()
    cli_help()

def cli_help():
    print("Usage of explain.py is as follows:")
    print("  explain.py [OPTIONS] eventToBeExplained.json applicationLogs.json")
    print("where OPTIONS can be")
    print("  [-h|--help] to print a help on the usage of explain.py")
    print("  [-b N|--beat=N] to set to N the period of the target application's heartbeat logs")
    print()

if __name__ == "__main__":
    main(sys.argv[1:])