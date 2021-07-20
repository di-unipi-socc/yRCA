# import Python default modules
import sys
# import explainer's modules
from parser.parser import parse_events
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
    # parse command line arguments
    event = args[0]
    event_logs = args[1]

    # parse events
    logged_facts = "logged_events.pl"
    # TODO
    parse_events(event_logs,logged_facts)
    
    # explain event
    # TODO
    explain(event,logged_facts)

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