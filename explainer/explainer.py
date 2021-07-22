from pyswip import Prolog
def explain(event,appLogs):
    # create Prolog reasoner
    reasoner = Prolog()
    
    # load knowledge base
    reasoner.consult("explainer/prolog/severity.pl")
    reasoner.consult("explainer/prolog/explain.pl")
    reasoner.consult(appLogs)
    
    # read event to explain
    eventFile = open(event,"r")
    eventToExplain = eventFile.readline() # read line corresponding to event
    eventFile.close()
    eventToExplain = eventToExplain[:len(eventToExplain)-2] # remove "." and "\n" at the end
    
    # run Prolog reasoner to find (and return) root causes
    rootCauses = list(reasoner.query("causedBy(" + eventToExplain + ",C)"))
    return rootCauses