# import Python default modules
import sys
# import explainer's modules
from parser.parser import parseEvents
from explainer.explainer import explain
from post_processor.post_processor import post_process

def main(args):
    # check command line arguments
    if len(args) == 1 and args[0] in ["-h","--help"]:
        cli_help()
        exit(-1)
    if len(args) != 2 or args[0][0]=='-' or args[1][0]=='-':
        print("ERROR: wrong input arguments.")
        print()
        cli_help()
        return
    # parse "event" to be explained and all "applicationLogs"
    event = "event_to_explain.pl"
    parseEvents(args[0],event)
    applicationLogs = "logged_events.pl"
    parseEvents(args[1],applicationLogs)
    
    # explain event
    # TODO
    explain(event,applicationLogs)

    # post processing & output
    # TODO
    post_process()

def cli_help():
    print("Usage of explain.py is as follows:")
    print("  python3 explain.py event.json event_logs.json")
    print("where")
    print("  - event.json contains event to be explained and")
    print("  - event_logs.json contains all events logged by an application.")
    print()

if __name__ == "__main__":
    main(sys.argv[1:])