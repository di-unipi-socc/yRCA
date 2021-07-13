:-set_prolog_flag(last_call_optimisation, true).

%error of invoked service
causedBy(log(S,T,_,_),[X|Xs]) :-
    interaction(S,S2,Ts,Te), Ts < T,
    log(S2,U,M,Sev), lte(Sev,warn), Ts<U, U<Te,
    X=log(S2,U,M,Sev),
    causedBy(X,Xs).
%invoked service never started
causedBy(log(S,T,_,_),[X]) :-
    interaction(S,S2,Ts,_), Ts < T,
    \+ log(S2,_,_,_),
    X=log(S2,0,nostart,warn).
%crash of invoked service
causedBy(log(S,T,_,_),[X]) :-
    interaction(S,S2,Ts,Te), Ts < T, heartbeat(P), 
    \+ (log(S2,U,_,_), log(S2,V,_,_), dif(U,V), Ts-P=<U, V=<Te+P, V-U=<P),
    Tx is Ts-P,
    X=log(S2,Tx,⊥,emerg).
%internal crash
causedBy(log(S,T,M,_),[X]) :-
    dif(M,⊥),
    heartbeat(P), T0 is T-P, T0>0,
    \+ (log(S,U,_,_), T0 =< U, U < T),
    X = log(S,T0,⊥,emerg).
%base case
causedBy(_,[]).

lte(S1,S2) :- severity(S1,A), severity(S2,B), A=<B.
%:-causedBy(log(s1,999,'error',err),X).
%:-causedBy(log(s0,10000,_,_),X).

