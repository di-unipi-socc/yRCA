:-set_prolog_flag(last_call_optimisation, true).

%determine K possible explanations for "Event"
xfail(K,Event,Exps,Root) :-
    findnsols(K,E,distinct(causedBy(Event,E,Root)),Exps).
    
%invoked service never started
causedBy(log(_,S,T,_,_),[X],N) :-
    log(_,S,Ts,sendTo(N,_),_), Ts < T, lookbackRadius(Z), Ts >= T - Z,
    \+ log(N,_,_,_,_),
    X = neverStarted(N).
%unreachable service
causedBy(log(_,S,T,_,_),[X],N) :-
    unhandledRequest(S,N,Ts,_), Ts < T, lookbackRadius(Z), Ts >= T - Z,
    log(N,_,_,_,_),
    X = unreachable(N).
%error of invoked service
causedBy(log(_,S,T,_,_),[X|Xs],R) :-
    interaction(S,S2,Ts,Te), Ts < T, lookbackRadius(Z), Ts >= T - Z,
    log(N,S2,U,M,Sev), lte(Sev,warning), Ts =< U, U =< Te, 
    X=log(N,S2,U,M,Sev),
    causedBy(X,Xs,R).
%crash of invoked service
causedBy(log(_,S,T,_,_),[X],N) :-
    interaction(S,S2,Ts,Te), Ts < T, lookbackRadius(Z), Ts >= T - Z,
    heartbeat(P), T0 is Ts - P, T1 is Te + P,
    findall(N, (log(N,S2,U,_,_), T0=<U, U=<T1, \+ (log(_,S2,V,_,_), U<V, V-U=<P)), [N|_]),
    X = failed(N,S2). 
%internal crash
causedBy(log(N,S,T,_,_),[X],N) :-
    heartbeat(P), T0 is T-P, T0>0,
    \+ (log(_,S,U,_,_), T0 =< U, U < T),
    X = failed(N,S). 
%base case
causedBy(log(N,_,_,_,_),[],N).

lte(S1,S2) :- severity(S1,A), severity(S2,B), A=<B.

interaction(S1,S2,Ts,Te) :-
    log(N1,S1,Ts,sendTo(N2,Id),_), 
    log(N2,S2,_,received(Id),_),
    log(N1,S1,Te,answerFrom(N2,Id),_). %, Ts < Te.

unhandledRequest(S1,N2,Ts,Te) :-
    log(N1,S1,Ts,sendTo(N2,Id),_),
    \+ log(N2,_,_,received(Id),_),
    log(N1,S1,Te,answerFrom(N2,Id),_). %, Ts < Te.