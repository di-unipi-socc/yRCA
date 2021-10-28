# import Python default modules
import os, sys, getopt
# import explainer's modules
from parser.parser import parseEvents
from explainer.explainer import explain

def main(argv):
    # check if "help" is required
    if "--help" in argv:
        cli_help()
        return

    # otherwise, parse command line arguments
    try:
        options,args = getopt.getopt(argv,"h:l:n:r:v",["help","horizon=","num=","root=","verbose"])
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
    horizon = 10 # lookback radius, in seconds (default: 10s)
    nSols = None # number of possible explanations to find (default: all)
    rootCause = None # value for root cause (default: all)
    verbose = False # by default, only "compact" printing (service names, no instances/timestamps/messages)

    # getting specified options
    for option, value in options:
        # setting lookback radius
        if option in ["-h","--horizon"]:
            if value.isnumeric():
                horizon = value
            else: 
                cli_error("lookback radius must be a number")
                exit(-2)
        # setting number of solutions to identify
        elif option in ["-n","--num"]:
            if value.isnumeric() and float(value)>0:
                nSols = value
            else: 
                cli_error("the amount of solutions to find must be a positive number")
                exit(-2)
        # setting root causing service
        elif option in ["-r","--rootCause"]:
            rootCause = value
        # setting verbosity
        elif option in ["-v","--verbose"]:
            verbose = True

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
    knowledgeBaseFile.write("horizon(" + str(horizon) + ").\n")
    knowledgeBaseFile.close()

    # ***********************
    # * ROOT CAUSE ANALYSIS *
    # ***********************
    rootCauses = explain(event,knowledgeBase,nSols,rootCause)
    
    # *****************
    # * PRINT RESULTS *
    # *****************
    if verbose:
        rootCauses.print()
    else:
        rootCauses.compactPrint()

    if rootCauses.size()==0:
        rc = (" from " + rootCause) if rootCause!=None else "" 
        print("Found no failure cascade" + rc + " to the considered event")
    else:
        end = "s" if rootCauses.size() > 1 else "" # plural or singular
        print("Found a total of " + str(rootCauses.size()) + " possible explanation" + end)

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
    print("  [--help] to print a help on the usage of explain.py")
    print("  [-h H|--horizon=H] to set to N the lookback radius in finding explanations")
    print("  [-n N|--num=N] to set to N the amount of possible explanations to identify")
    print("  [-r X|--root=X] to require X to be the root cause of identified explanations")
    print("  [-v X|--verbose] to print verbose analysis results")
    print()

if __name__ == "__main__":
    main(sys.argv[1:])