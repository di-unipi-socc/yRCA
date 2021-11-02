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
        
    # run Prolog reasoner to find (and return) root causes
    # query example: xfail(3,log(frontend,echo_frontend_1,1627883313.98,answerFrom(backend,'1629b530-1192-4579-8620-65098bf2f71d'),err),C,R).
    query = "xfail(" 
    query += (str(nSols) + ",") if nSols is not None else "" # find "nSols" only if specified 
    query += eventToExplain + ",Explanations,"
    query += (rootCause) if rootCause is not None else "Root" # use "Root" if rootCause is not specified
    query += ")"
    rootCauses = list(reasoner.query(query))
    return Explanations(rootCauses[0]["Explanations"])