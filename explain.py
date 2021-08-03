# import Python default modules
import sys, getopt
# import explainer's modules
from parser.parser import parseEvents
from explainer.explainer import explain

def main(argv):
    nSols = 10 # default number of possible explanations to find
    heartbeat = 5 # default value considered for heartbeat logs
    lookbackRadius = 10 # default value considered for lookback radius
    rootCause = None # default value for root cause (for finding all possible root causes)

    # parse command line arguments
    try:
        opts,args = getopt.getopt(argv,"hb:l:n:r:",["help","lookbackRadius=","heartbeat=","nSols=","rootCause="])
    except: 
        cli_error("wrong options used")
        exit(-1)
    # check & process command line arguments
    if len(args) < 2:
        cli_error("missing input arguments")
        exit(-1)
    for opt, arg in opts:
        if opt in ["-n","--nSols"]:
            if arg.isnumeric():
                nSols = arg
            else: 
                cli_error("the amount of solutions to find must be a number")
                return
        elif opt in ["-b","--heartbeat"]:
            if arg.isnumeric():
                heartbeat = float(arg)/1000 # converting millis to seconds
            else: 
                cli_error("heartbeat value must be a number")
                return
        elif opt in ["-l","--lookbackRadius"]:
            if arg.isnumeric():
                lookbackRadius = arg
            else: 
                cli_error("lookback radius must be a number")
                return
        elif opt in ["-r","--rootCause"]:
            rootCause = arg
        elif opt in ["-h","--help"]:
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
    
    # add heartbeat and lookback radius values to "knowledgeBase"
    prologFacts = open(knowledgeBase,"a")
    prologFacts.write("heartbeat(" + str(heartbeat) + ").\n")
    prologFacts.write("lookbackRadius(" + str(lookbackRadius) + ").\n")
    prologFacts.close()

    # ***********************
    # * ROOT CAUSE ANALYSIS *
    # ***********************
    rootCauses = explain(event,knowledgeBase,nSols,rootCause)
    
    # *****************
    # * PRINT RESULTS *
    # *****************
    rootCauses.print()
    print("Found",rootCauses.size(), "explanations")

def cli_error(message):
    print("ERROR: " + message + ".")
    print()
    cli_help()

def cli_help():
    print("Usage of explain.py is as follows:")
    print("  explain.py [OPTIONS] eventToBeExplained.json applicationLogs.json")
    print("where OPTIONS can be")
    print("  [-h|--help] to print a help on the usage of explain.py")
    print("  [-b N|--beat=N] to set to N milliseconds the period of the target application's heartbeat logs")
    print("  [-l N|--lookbackRadius=N] to set to N the lookback radius in finding explanations")
    print("  [-n N|--nSols=N] to set to N the amount of possible explanations to identify")
    print("  [-r X|--rootCause X] to require X to be the root cause of identified explanations")
    print()

if __name__ == "__main__":
    main(sys.argv[1:])