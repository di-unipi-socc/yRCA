# import Python default modules
import os, sys, getopt
# import explainer's modules
from parser.parser import parseEvents
from explainer.explainer import explain

def main(argv):
    # parse command line arguments
    try:
        options,args = getopt.getopt(argv,"hl:n:p:r:",["help","lookback=","period=","num=","root="])
    except: 
        cli_error("wrong options used")
        exit(-1)

    # check & process command line arguments
    if len(args) < 2:
        cli_error("missing input arguments")
        exit(-1)
    eventLogLine = args[0]
    applicationLogs = args[1]

    # options to customise the execution of the explainer (with default values)
    heartbeat = 1 # period, in seconds, of heartbeating in logs (default: 1s)
    lookbackRadius = 10 # lookback radius, in seconds (default: 10s)
    nSols = None # number of possible explanations to find (default: all)
    rootCause = None # value for root cause (default: all)

    # getting specified options
    for option, value in options:
        # asking for help
        if option in ["-h","--help"]:
            cli_help()
            exit(0)
        # setting lookback radius
        elif option in ["-l","--lookback"]:
            if value.isnumeric():
                lookbackRadius = value
            else: 
                cli_error("lookback radius must be a number")
                exit(-2)
        # setting number of solutions to identify
        elif option in ["-n","--num"]:
            if value.isnumeric() and int(value)>0:
                nSols = value
            else: 
                cli_error("the amount of solutions to find must be a positive number")
                exit(-2)
        # setting hearbeat period
        elif option in ["-p","--period"]:
            if value.isnumeric():
                heartbeat = float(value)/1000 # converting millis to seconds
            else: 
                cli_error("the value for heartbeat period must be a number")
                exit(-2)
        # setting root causing service
        elif option in ["-r","--rootCause"]:
            rootCause = value

    # ******************
    # * PARSING INPUTS *
    # ******************
    # parse "event" to be explained and all events forming the "knowledgeBase"
    event = "event.pl"
    parseEvents(eventLogLine,event)
    knowledgeBase = "knowledgeBase.pl"
    parseEvents(applicationLogs,knowledgeBase)
    
    # add heartbeat and lookback radius values to "knowledgeBase"
    knowledgeBaseFile = open(knowledgeBase,"a")
    knowledgeBaseFile.write("heartbeat(" + str(heartbeat) + ").\n")
    knowledgeBaseFile.write("lookbackRadius(" + str(lookbackRadius) + ").\n")
    knowledgeBaseFile.close()

    # ***********************
    # * ROOT CAUSE ANALYSIS *
    # ***********************
    rootCauses = explain(event,knowledgeBase,nSols,rootCause)
    
    # *****************
    # * PRINT RESULTS *
    # *****************
    rootCauses.print()
    print("Found",rootCauses.size(), "explanations")

    # Remove generated files
    os.remove(event) # comment this, if needing to keep files for Prolog debugging
    os.remove(knowledgeBase) # comment this, if needing to keep files for Prolog debugging

# function for printing cli erros, followed by cli usage
def cli_error(message):
    print("ERROR: " + message + ".")
    print()
    cli_help()

# function for printing cli usage
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