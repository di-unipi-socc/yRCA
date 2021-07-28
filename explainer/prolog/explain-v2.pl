:-set_prolog_flag(last_call_optimisation, true).

%invoked service never started
causedBy(log(_,S,T,_,_),[X]) :-
    cond1(S,T,X).
cond1(S,T,X) :-
    log(_,S,Ts,sendTo(N2,_),_), Ts < T, lookbackRadius(Z), Ts >= T - Z,
    \+ started(N2),
    X = neverStarted(N2).
%unreachable service
causedBy(log(_,S,T,_,_),[X]) :-
    cond2(S,T,X).
cond2(S,T,X) :-
    started(N2), lookbackRadius(Z), 
    unhandledRequest(S,N2,Ts,_), Ts < T, Ts >= T - Z,
    X = unreachable(N2). %,Ts,Te).
%error of invoked service
causedBy(log(_,S,T,_,_),[X|Xs]) :-
    cond3(S,T,X,Xs).
cond3(S,T,X,Xs) :-
    interaction(S,S2,Ts,Te), Ts < T, lookbackRadius(Z), Ts >= T - Z,
    log(N,S2,U,M,Sev), lte(Sev,warning), Ts < U, U < Te, % =<?
    X=log(N,S2,U,M,Sev),
    causedBy(X,Xs).
%crash of invoked service
causedBy(log(_,S,T,_,_),[X]) :-
    interaction(S,S2,Ts,Te), Ts < T, lookbackRadius(Z), Ts >= T - Z,
    heartbeat(P), T0 is Ts - P, T1 is Te + P, 
    findall(N, (log(N,S2,U,_,_), T0=<U, U=<T1, \+ (log(_,S2,V,_,_), U<V, V-U=<P)), [N|_]),
    X = failed(N,S2,T0,T1).
%internal crash
causedBy(log(N,S,T,_,_),[X]) :-
    heartbeat(P), T0 is T-P, T0>0,
    \+ (log(_,S,U,_,_), T0 =< U, U < T),
    X = failed(N,S,T0,T). 
%base case
causedBy(_,[]).

lte(S1,S2) :- severity(S1,A), severity(S2,B), A=<B.

interaction(S1,S2,Ts,Te) :-
    log(N1,S1,Ts,sendTo(N2,Id),_), 
    log(N2,S2,_,received(Id),_),
    log(N1,S1,Te,answerFrom(N2,Id),_). %, Ts < Te.

unhandledRequest(S1,N2,Ts,Te) :-
    log(N1,S1,Ts,sendTo(N2,Id),_),
    \+ log(N2,_,_,received(Id),_),
    log(N1,S1,Te,answerFrom(N2,Id),_). %, Ts < Te.

started(N) :-
    findnsols(1,N,log(N,_,_,_,_),[N]).
