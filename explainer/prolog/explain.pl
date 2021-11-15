:-set_prolog_flag(last_call_optimisation, true).
:-set_prolog_flag(stack_limit, 16 000 000 000).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% xFail can explain logged events of the form:
% log(serviceName,serviceInstance,timestamp,eventType,message,severity)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

xfail(Event,Explanations,RootCause) :-                  %determine all possible explanations for "Event"
    findall(E,causedBy(Event,E,RootCause),Explanations).
xfail(NumSols,Event,Explanations,RootCause) :-          %determine "NumSols" possible explanations for "Event"
    findnsols(NumSols,E,distinct(causedBy(Event,E,RootCause)),Explanations).
    
% TODO: fix bug in timeout never considered recursively (see event.log, all.log)

causedBy(log(_,I,T,E,_,_),[X],Root) :-                  %invoked service never started
    dif(E,internal),
    log(_,I,Ts,sendTo(Root,_),_,_), Ts < T, horizon(H), Ts >= T - H,
    \+ log(Root,_,_,_,_,_),
    X = neverStarted(Root).
causedBy(log(_,I,_,timeout(Root,Id),_,_),[X],Root) :-                  %unreachable service
    nonReceivedRequest(Id,I,Root), 
    log(Root,_,_,_,_,_),
    X = unreachable(Root).
causedBy(log(SI,I,_,E,_,_),[X|Xs],Root) :-              %internal error of invoked service
    (E=errorFrom(SJ,Id);E=timeout(SJ,Id)),
    write(E),
    failedInteraction(Id,(SI,I),(SJ,J),Ts,Te), 
    log(SJ,J,U,internal,M,Sev), lte(Sev,warning), Ts =< U, U =< Te, 
    X=log(SJ,J,U,internal,M,Sev),
    causedBy(X,Xs,Root).
causedBy(log(SI,I,_,E,_,_),[X|Xs],Root) :-              %failed interaction of invoked service
    (E=errorFrom(SJ,Id);E=timeout(SJ,Id)),
    failedInteraction(Id,(SI,I),(SJ,J),TsIJ,TeIJ), 
    failedInteraction(_,(SJ,J),(_,_),TsJK,TeJK), TsIJ < TsJK, TeJK < TeIJ,
    log(SJ,J,TeJK,F,M,Sev), lte(Sev,warning), 
    X=log(SJ,J,TeJK,F,M,Sev),
    causedBy(X,Xs,Root).
causedBy(log(SI,I,_,E,_,_),[X|Xs],Root) :-              %timed-out interaction of invoked service
    (E=errorFrom(SJ,Id);E=timeout(SJ,Id)),
    failedInteraction(Id,(SI,I),(SJ,J),_,TeIJ), 
    timedOutInteraction(_,(SJ,J),(SK,_),TsJK,TeJK), TsJK < TeIJ, TeIJ < TeJK,
    log(SJ,J,TeJK,timeout(SK,IdJK),M,Sev),X=log(SJ,J,TeJK,timeout(SK,IdJK),M,Sev),
    causedBy(X,Xs,Root).
causedBy(log(Root,_,_,_,_,_),[],Root).           %base case

nonReceivedRequest(Id,I,SJ) :-
    log(SI,I,Ts,sendTo(SJ,Id),_,_),
    log(SI,I,Te,timeout(SJ,Id),_,_),
    \+ (log(SJ,_,Tr,received(X),_,_), Ts < Tr, Tr < Te, (X=Id;X=noId)).

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
    (X=Id; X=noId), Ts < Tr, Tr < Te. % noId accounts for non-instrumented components

lte(S1,S2) :- severity(S1,A), severity(S2,B), A=<B.


% MEMO: If (passive) components are not instrumented to propagate IDs, just put "noId" as ID when templating logs corresponding to receive/answer to service interactions (in the log template parser)