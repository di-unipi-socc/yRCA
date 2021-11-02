:-set_prolog_flag(last_call_optimisation, true).

%determine all possible explanations for "Event"
xfail(Event,Explanations,RootCause) :-
    findall(E,distinct(causedBy(Event,E,RootCause)),Explanations).
%determine "NumSols" possible explanations for "Event"
xfail(NumSols,Event,Explanations,RootCause) :-
    findnsols(NumSols,E,distinct(causedBy(Event,E,RootCause)),Explanations).
    
%invoked service never started
causedBy(log(_,S,T,F,_,_),[X],N) :-
    dif(F,internal),
    log(_,S,Ts,sendTo(N,_),_,_), Ts < T, horizon(H), Ts >= T - H,
    \+ log(N,_,_,_,_,_),
    X = neverStarted(N).
%unreachable service
causedBy(log(_,S,T,F,_,_),[X],N) :-
    dif(F,internal),
    unhandledRequest(S,N,Ts,_), Ts < T, horizon(H), Ts >= T - H,
    log(N,_,_,_,_,_),
    X = unreachable(N).
%error of invoked service
causedBy(log(_,S,T,F,_,_),[X|Xs],R) :-
    dif(F,internal),
    failedInteraction(S,S2,Ts,Te), Ts < T, horizon(H), Ts >= T - H,
    log(N,S2,U,F2,M,Sev), lte(Sev,warning), Ts =< U, U =< Te, 
    X=log(N,S2,U,F2,M,Sev),
    causedBy(X,Xs,R).
%base case
causedBy(log(N,_,_,internal,_,_),[],N).

lte(S1,S2) :- severity(S1,A), severity(S2,B), A=<B.

unhandledRequest(S1,N2,Ts,Te) :-
    log(N1,S1,Ts,sendTo(N2,Id),_,_),
    log(N1,S1,Te,timeout(N2,Id),_,_),
    \+ (log(N2,_,Tr,received(Id),_,_), Ts < Tr, Tr < Te).
unhandledRequest(S1,N2,Ts,Te) :-
    log(N1,S1,Ts,sendTo(N2,Id),_,_),
    log(N1,S1,Te,timeout(N2,Id),_,_),
    \+ (log(N2,_,Tr,received(noId),_,_), Ts < Tr, Tr < Te).

failedInteraction(S1,S2,Ts,Te) :-
    log(N1,S1,Te,errorFrom(N2,Id),_,_),
    interaction(Id,(N1,S1),(N2,S2),Ts,Te).
failedInteraction(S1,S2,Ts,Te) :-
    log(N1,S1,Te,timeout(N2,Id),_,_), 
    interaction(Id,(N1,S1),(N2,S2),Ts,Te).

interaction(Id,(N1,S1),(N2,S2),Ts,Te) :-
    log(N1,S1,Ts,sendTo(N2,Id),_,_), 
    log(N2,S2,Tr,received(Id),_,_), 
    Ts < Tr, Tr < Te.
interaction(Id,(N1,S1),(N2,S2),Ts,Te) :-
    log(N1,S1,Ts,sendTo(N2,Id),_,_),
    log(N2,S2,Tr,received(noId),_,_), 
    Ts < Tr, Tr < Te.

% MEMO: If (passive) components are not instrumented to propagate IDs, just put "noId" as ID when templating logs corresponding to receive/answer to service interactions (in the log template parser)