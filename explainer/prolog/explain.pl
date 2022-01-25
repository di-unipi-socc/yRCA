:-set_prolog_flag(last_call_optimisation, true).
:-set_prolog_flag(stack_limit, 16 000 000 000).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% xFail can explain logged events of the form:
% log(serviceName,serviceInstance,timestamp,eventType,message,severity)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

xfail(Event,Explanations,RootCause) :-                              %determine all possible explanations for "Event"
    findall(E,distinct(causedBy(Event,E,RootCause)),Explanations).
xfail(NumSols,Event,Explanations,RootCause) :-                      %determine "NumSols" possible explanations for "Event"
    findnsols(NumSols,E,distinct(causedBy(Event,E,RootCause)),Explanations).

causedBy(log(SI,I,T,E,M,Sev),[X|Xs],Root) :-                        %internal error of invoked service
    (E=errorFrom(SJ,Id);E=timeout(SJ,Id)),
    failedInteraction(Id,(SI,I),(SJ,J),Ts,Te),
    log(SJ,J,U,internal,MJ,SevJ), lte(SevJ,warning), Ts =< U, U =< Te, 
    X=log(SI,I,T,E,M,Sev),
    causedBy(log(SJ,J,U,internal,MJ,SevJ),Xs,Root).

causedBy(log(SI,I,T,E,M,Sev),[X|Xs],Root) :-                        %failed interaction of invoked service
    (E=errorFrom(SJ,Id);E=timeout(SJ,Id)),
    failedInteraction(Id,(SI,I),(SJ,J),TsIJ,TeIJ), 
    failedInteraction(_,(SJ,J),(_,_),TsJK,TeJK), TsIJ =< TsJK, TeJK =< TeIJ,
    log(SJ,J,TeJK,F,MJ,SevJ), lte(SevJ,warning), 
    X=log(SI,I,T,E,M,Sev),
    causedBy(log(SJ,J,TeJK,F,MJ,SevJ),Xs,Root).

causedBy(log(SI,I,T,timeout(SJ,Id),M,Sev),[X|Xs],Root) :-           %timed-out interaction of invoked service
    timedOutInteraction(Id,(SI,I),(SJ,J),_,TeIJ), 
    timedOutInteraction(_,(SJ,J),(SK,_),TsJK,TeJK), TsJK =< TeIJ, TeIJ < TeJK, 
    log(SJ,J,TeJK,timeout(SK,IdJK),MJ,SevJ),
    X=log(SI,I,T,timeout(SJ,Id),M,Sev),
    causedBy(log(SJ,J,TeJK,timeout(SK,IdJK),MJ,SevJ),Xs,Root).

causedBy(log(SI,I,T,E,M,Sev),[X|Xs],Root) :-                        %unreachable service called by invoked service
    (E=errorFrom(SJ,Id);E=timeout(SJ,Id)),
    failedInteraction(Id,(SI,I),(SJ,J),TsIJ,TeIJ), 
    nonReceivedRequest(IdK,J,SK,TsJK,TeJK), TsIJ =< TsJK, TsJK =< TeIJ,
    log(SJ,J,TeJK,timeout(SK,IdK),MJ,SevJ),
    X=log(SI,I,T,E,M,Sev),
    causedBy(log(SJ,J,TeJK,timeout(SK,IdK),MJ,SevJ),Xs,Root).

causedBy(log(SI,I,T,timeout(SJ,Id),M,Sev),[X|Xs],Root) :-           %unreachable service invoked
    nonReceivedRequest(Id,I,SJ,_,T),
    X = log(SI,I,T,timeout(SJ,Id),M,Sev),
    causedBy(unreachable(SJ),Xs,Root).

causedBy(log(Root,R,T,internal,M,Sev),[X],Root) :-                  %base case: Root experienced internal error
    X = log(Root,R,T,internal,M,Sev).               

causedBy(unreachable(Root),[X],Root) :-                             %base case: Root was unreachable
    log(Root,_,_,_,_,_),
    X = unreachable(Root). 

causedBy(unreachable(Root),[X],Root) :-                             %base case: Root was never started
    \+ log(Root,_,_,_,_,_),
    X = neverStarted(Root).

nonReceivedRequest(Id,I,SJ,Ts,Te) :-
    log(SI,I,Ts,sendTo(SJ,Id),_,_),
    log(SI,I,Te,timeout(SJ,Id),_,_),
    \+ (log(SJ,_,Tr,received(X),_,_), Ts =< Tr, Tr =< Te, (X=Id;X=noId)).

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
    log(SJ,J,Tr,received(X),_,_), 
    (X=Id; X=noId), Ts =< Tr, Tr =< Te. % noId accounts for non-instrumented components

lte(S1,S2) :- severity(S1,A), severity(S2,B), A=<B.


% MEMO: If (passive) components are not instrumented to propagate IDs, just put "noId" as ID when templating logs corresponding to receive/answer to service interactions (in the log template parser)