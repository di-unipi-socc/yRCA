:-set_prolog_flag(last_call_optimisation, true).
:-set_prolog_flag(stack_limit, 16 000 000 000).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Predicate xfail/3 can explain logged events of the form:
% log(serviceName,serviceInstance,timestamp,eventType,message,severity)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

xfail(Event,Explanations,RootCause) :-                              %determine all possible explanations for "Event"
    findall(E,distinct(causedBy(Event,E,RootCause)),Explanations).
xfail(NumSols,Event,Explanations,RootCause) :-                      %determine "NumSols" possible explanations for "Event"
    findnsols(NumSols,E,distinct(causedBy(Event,E,RootCause)),Explanations).

/* 1. Internal error of invoked service                                                     SI          SJ
** This case explains that a failure/timeout event E at service instance SI                  |---------->|
** happening at the end of a failed or timed-out interaction with service SJ,                |           ϟ 
** may have been caused by an internal failure (i.e., a logged event ϟ  whose                |<----------|                             
** severity is at least warning) at service SJ. Last, yRCA recurs on the internal            E           |
** error of SJ to explain it.                                                                |           |     
*/
causedBy(log(SI,I,T,E,M,Sev),[X|Xs],Root) :-                        
    (E=errorFrom(SJ,Id);E=timeout(SJ,Id)),
    failedInteraction(Id,(SI,I),(SJ,J),Ts,Te),
    log(SJ,J,U,internal,MJ,SevJ), lte(SevJ,warning), Ts =< U, U =< Te, 
    X=log(SI,I,T,E,M,Sev),
    causedBy(log(SJ,J,U,internal,MJ,SevJ),Xs,Root).

/* 2. Internal error of invoked service                                                     SI          SJ          SK             
** This case explains that a failure/timeout event E at service instance SI                  |---------->|           |
** has been caused by a failure event F at service SJ, which -- in turn --                   |           |---------->|
** has been caused by a failed interaction ϟ of SJ with SK. After identifying the            |           |           ϟ                          
** failure cascade SK -> SJ -> SI, yRCA recurs on the timeout at SJ to explain it.           |           |<----------|
**                                                                                           |           F           |
**                                                                                           |<----------|           |
**                                                                                           E           |           |
*/                                                  
causedBy(log(SI,I,T,E,M,Sev),[X|Xs],Root) :-                        
    (E=errorFrom(SJ,Id);E=timeout(SJ,Id)),
    failedInteraction(Id,(SI,I),(SJ,J),TsIJ,TeIJ), 
    failedInteraction(_,(SJ,J),(_,_),TsJK,TeJK), TsIJ =< TsJK, TeJK =< TeIJ,
    log(SJ,J,TeJK,F,MJ,SevJ), lte(SevJ,warning), 
    X=log(SI,I,T,E,M,Sev),
    causedBy(log(SJ,J,TeJK,F,MJ,SevJ),Xs,Root).

/* 3. Timed-out interaction of invoked service instance                                     SI          SJ          SK             
** This case explains that a timeout event E at service instance SI                          |---------->|           |
** has been caused by a timeout event O at service SJ, which -- in turn --                   |           |---------->|
** has been caused by a timeout event O'related to an interaction of SJ with SK.             |           |           |                          
** After identifying the failure cascade SK -> SJ -> SI, yRCA recurs on the                  |           O           |
** timeout at SJ to explain it.                                                              |           |           |
**                                                                                           O           |           |
*/    
causedBy(log(SI,I,T,timeout(SJ,Id),M,Sev),[X|Xs],Root) :-           %timed-out interaction of invoked service
    timedOutInteraction(Id,(SI,I),(SJ,J),_,TeIJ), 
    timedOutInteraction(_,(SJ,J),(SK,_),TsJK,TeJK), TsJK =< TeIJ, TeIJ < TeJK, 
    log(SJ,J,TeJK,timeout(SK,IdJK),MJ,SevJ),
    X=log(SI,I,T,timeout(SJ,Id),M,Sev),
    causedBy(log(SJ,J,TeJK,timeout(SK,IdJK),MJ,SevJ),Xs,Root).

/* 4. Unreachability of a service called by invoked service instance                        SI          SJ          SK             
** This case explains that a failure/timeout event E at service instance SI                  |---------->|           |
** has been caused by a timeout event O at service SJ, which -- in turn --                   |           |-----!     |
** has been caused by a failed interaction ! of SJ with SK.                                  |           |           |                          
** considers the possibility of the request sent by J to have never been                     |           O           |
** received by the target service K                                                          |<----------|           |
** After identifying the failure cascade SK -> SJ -> SI, yRCA recurs on the                  E           |           |  
** timeout at SJ to explain it.
*/   
causedBy(log(SI,I,T,E,M,Sev),[X|Xs],Root) :-                        
    (E=errorFrom(SJ,Id);E=timeout(SJ,Id)),
    failedInteraction(Id,(SI,I),(SJ,J),TsIJ,TeIJ), 
    nonReceivedRequest(IdK,J,SK,TsJK,TeJK), TsIJ =< TsJK, TsJK =< TeIJ,
    log(SJ,J,TeJK,timeout(SK,IdK),MJ,SevJ),
    X=log(SI,I,T,E,M,Sev),
    causedBy(log(SJ,J,TeJK,timeout(SK,IdK),MJ,SevJ),Xs,Root).

/* 5. Internal error of invoked service                                                     SI          SJ
** This case explains that a timeout event O at service instance SI                          |-----!     |
** has been caused by a non-received request during an interaction of SI with SJ             |           | 
** yRCA abducts that that SJ was unreachable, and recurs to explain it.                      |           |                              
**                                                                                           O           |
**                                                                                           |           |     
*/
causedBy(log(SI,I,T,timeout(SJ,Id),M,Sev),[X|Xs],Root) :-           
    nonReceivedRequest(Id,I,SJ,_,T),
    X = log(SI,I,T,timeout(SJ,Id),M,Sev),
    causedBy(unreachable(SJ),Xs,Root).

/* 6. Internal service error
** This case explains an internal failure event logged by a service, identifying 
** the service itself as the root cause for such an event. Recursion ends.
*/
causedBy(log(Root,R,T,internal,M,Sev),[X],Root) :-                  
    X = log(Root,R,T,internal,M,Sev).               

/* 7. Temporary service unreachability
** This case explains abducted unreachability events for a service, identifying that 
** such a service was temporarily unreachable because it previously logged some information. 
** Recursion ends.
*/
causedBy(unreachable(Root),[X],Root) :-                             
    log(Root,_,_,_,_,_),
    X = unreachable(Root). 

/* 7. Temporary service unreachability
** This case explains abducted unreachability events for a service, identifying that 
** such a service never logged any information. Recursion ends, by abducting the fact 
** that such a service was possibly never started.
*/
causedBy(unreachable(Root),[X],Root) :-                             
    \+ log(Root,_,_,_,_,_),
    X = neverStarted(Root).

nonReceivedRequest(Id,I,SJ,Ts,Te) :-
    log(SI,I,Ts,sendTo(SJ,Id),_,_),
    log(SI,I,Te,timeout(SJ,Id),_,_),
    \+ (log(SJ,_,Tr,received(Id),_,_), Ts =< Tr, Tr =< Te).

failedInteraction(Id,(SI,I),(SJ,J),Ts,Te) :-
    errorInteraction(Id,(SI,I),(SJ,J),Ts,Te); timedOutInteraction(Id,(SI,I),(SJ,J),Ts,Te).

errorInteraction(Id,(SI,I),(SJ,J),Ts,Te) :-
    log(SI,I,Te,errorFrom(SJ,Id),_,_),
    interaction(Id,(SI,I),(SJ,J),Ts,Te).
    
timedOutInteraction(Id,(SI,I),(SJ,J),Ts,Te) :-
    log(SI,I,Te,timeout(SJ,Id),_,_),
    interaction(Id,(SI,I),(SJ,J),Ts,Te).

interaction(Id,(SI,I),(SJ,J),Ts,Te) :-
    log(SI,I,Ts,sendTo(SJ,Id),_,_), 
    log(SJ,J,Tr,received(Id),_,_),
    Ts =< Tr, Tr =< Te.

lte(S1,S2) :- severity(S1,A), severity(S2,B), A=<B.