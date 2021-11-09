:-set_prolog_flag(last_call_optimisation, true).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% xFail can explain logged events of the form:
% log(serviceName,serviceInstance,timestamp,eventType,message,severity)
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

xfail(Event,Explanations,RootCause) :-                  %determine all possible explanations for "Event"
    findall(E,distinct(causedBy(Event,E,RootCause)),Explanations).
xfail(NumSols,Event,Explanations,RootCause) :-          %determine "NumSols" possible explanations for "Event"
    findnsols(NumSols,E,distinct(causedBy(Event,E,RootCause)),Explanations).
    
causedBy(log(_,I,T,E,_,_),[X],Root) :-                  %invoked service never started
    dif(E,internal),
    log(_,I,Ts,sendTo(Root,_),_,_), Ts < T, horizon(H), Ts >= T - H,
    \+ log(Root,_,_,_,_,_),
    X = neverStarted(Root).
causedBy(log(_,I,T,E,_,_),[X],Root) :-                  %unreachable service
    dif(E,internal),
    nonReceivedRequest(I,Root,Ts,_), Ts < T, horizon(H), Ts >= T - H,
    log(Root,_,_,_,_,_),
    X = unreachable(Root).
causedBy(log(SI,I,T,E,_,_),[X|Xs],Root) :-              %internal error of invoked service
    dif(E,internal),
    failedInteraction((SI,I),(SJ,J),Ts,Te), Ts < T, horizon(H), Ts >= T - H,
    log(SJ,J,U,internal,M,Sev), lte(Sev,warning), Ts =< U, U =< Te, 
    X=log(SJ,J,U,internal,M,Sev),
    causedBy(X,Xs,Root).
causedBy(log(SI,I,T,E,_,_),[X|Xs],Root) :-              %failed interaction of invoked service
    dif(E,internal),
    failedInteraction((SI,I),(SJ,J),TsIJ,TeIJ), TsIJ < T, horizon(H), TsIJ >= T - H,
    failedInteraction((SJ,J),(_,_),TsJK,TeJK), TsIJ < TsJK, TeJK < TeIJ,
    log(SJ,J,TeJK,F,M,Sev), lte(Sev,warning), 
    X=log(SJ,J,TeJK,F,M,Sev),
    causedBy(X,Xs,Root).
causedBy(log(SI,I,T,E,_,_),[X|Xs],Root) :-              %timed-out interaction of invoked service
    dif(E,internal),
    timedOutInteraction((SI,I),(SJ,J),TsIJ,TeIJ), TsIJ < T, horizon(H), TsIJ >= T - H,
    timedOutInteraction((SJ,J),(SK,K),TsJK,TeJK), TsJK < TeIJ, TeIJ < TeJK,
    log(SJ,J,TeJK,timeout(SK,K),M,Sev),X=log(SJ,J,TeJK,timeout(SK,K),M,Sev),
    causedBy(X,Xs,Root).
causedBy(log(Root,_,_,internal,_,_),[],Root).           %base case

nonReceivedRequest(I,SJ,Ts,Te) :-
    log(SI,I,Ts,sendTo(SJ,Id),_,_),
    log(SI,I,Te,timeout(SJ,Id),_,_),
    \+ (log(SJ,_,Tr,received(X),_,_), Ts < Tr, Tr < Te, (X=Id;X=noID)).

failedInteraction((SI,I),(SJ,J),Ts,Te) :-
    errorInteraction((SI,I),(SJ,J),Ts,Te); timedOutInteraction((SI,I),(SJ,J),Ts,Te).

errorInteraction((SI,I),(SJ,J),Ts,Te) :-
    log(SI,I,Te,errorFrom(SJ,Id),_,_),
    interaction(Id,(SI,I),(SJ,J),Ts,Te).
    
timedOutInteraction((SI,I),(SJ,J),Ts,Te) :-
    log(SI,I,Te,timeout(SJ,Id),_,_),
    interaction(Id,(SI,I),(SJ,J),Ts,Te).

interaction(Id,(SI,I),(SJ,J),Ts,Te) :-
    log(SI,I,Ts,sendTo(SJ,Id),_,_), 
    log(SJ,J,Tr,received(X),_,_), 
    (X=Id; X=noID), Ts < Tr, Tr < Te. % noID accounts for non-instrumented components

lte(S1,S2) :- severity(S1,A), severity(S2,B), A=<B.


% MEMO: If (passive) components are not instrumented to propagate IDs, just put "noId" as ID when templating logs corresponding to receive/answer to service interactions (in the log template parser)