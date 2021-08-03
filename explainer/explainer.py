from pyswip import Prolog
from explainer.model.explanations import Explanations

def explain(event,applicationLogs,nSols,rootCause):
    # create Prolog reasoner
    reasoner = Prolog()
    
    # load knowledge base
    reasoner.consult("explainer/prolog/severity.pl")
    reasoner.consult("explainer/prolog/explain.pl")
    reasoner.consult(applicationLogs)
    
    # read event to explain
    eventFile = open(event,"r")
    eventToExplain = eventFile.readline() # read line corresponding to event
    eventFile.close()
    eventToExplain = eventToExplain[:len(eventToExplain)-2] # remove "." and "\n" at the end
    
    # configure query options, based on input options
    if nSols is None: 
        nSols = 10000 # to (most probably) find all possible solutions
    if rootCause is None: 
        root = "Root"
    else:
        root = rootCause
    
    # run Prolog reasoner to find (and return) root causes
    # query example: xfail(3,log(frontend,echo_frontend_1,1627883313.98,answerFrom(backend,'1629b530-1192-4579-8620-65098bf2f71d'),err),C,R).
    rootCauses = list(reasoner.query("xfail(" + str(nSols) + "," + eventToExplain + ",Explanations," + root + ")"))
    return Explanations(rootCauses[0]["Explanations"])