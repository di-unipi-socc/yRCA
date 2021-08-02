:-set_prolog_flag(last_call_optimisation, true).

% xfail(K,Event,Exps,Root) :-
%     id(K,Event,[],Exps,Root); 
%     findall(E,causedBy(Event,E,Root),Exps).

% id(K,Event,OldExps,NewExps,Root) :-
%     findnsols(K,E,(causedBy(Event,E,Root), \+ member(E,OldExps)),Tmp),
%     unique(Tmp,CurrExps), length(CurrExps,Len), Len < K,
%     append(OldExps,CurrExps,Exps), KNew is K - Len, 
%     id(KNew,Event,Exps,NewExps,Root).
% id(K,Event,OldExps,NewExps,Root) :-
%     findnsols(K,E,(causedBy(Event,E,Root), \+ member(E,OldExps)),Tmp),
%     unique(Tmp,NewExps), length(NewExps,Len), Len = K.

% id(K,K,Event,Exps,Root) :-
%     findnsols(K,E,causedBy(Event,E,Root),Tmp),
%     unique(Tmp,Exps), length(Exps,Len), Len >= K.
% id(K,K,Event,Exps,Root) :-
%     findnsols(K,E,causedBy(Event,E,Root),Tmp),
%     unique(Tmp,Exps), length(Exps,Len), Len < K,
%     KNew is K+1, id(KNew,K,Event,Exps,Root).

% xfail(K,Event,Exps,Root) :-
%     xfail(K,Event,[],Exps,Root).

% xfail(K,Event,Exps,NewExps,Root) :-
%     causedBy(Event,E,Root), \+ member(E,Exps),
%     KNew is K-1, xfail(KNew,Event,[E|Exps],NewExps,Root).
% xfail(K,Event,Exps,Exps,Root) :-
%     K > 0, findall(E,(causedBy(Event,E,Root), \+ member(E,Exps)),[]).
% xfail(0,_,Exps,Exps,_).


% xfail(L,Cs,R) :-
%     findall(C,causedBy(L,C,R),Cs), %unique(Cs,X),
%     printExplanations(L, Cs, 1).
% xfail(L,X) :-
%     findall(C, causedBy(L,C), Cs), unique(Cs,X), 
%     printExplanations(L, X, 1).

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
    log(N1,S1,Te,answerFrom(N2,Id),_).

unhandledRequest(S1,N2,Ts,Te) :-
    log(N1,S1,Ts,sendTo(N2,Id),_),
    \+ log(N2,_,_,received(Id),_),
    log(N1,S1,Te,answerFrom(N2,Id),_). 

printExplanations(L,[X|Xs],I) :- 
    write(I), write('. '), write(L), nl, write(' <-- '), writeln(X), nl, INew is I + 1, printExplanations(L,Xs,INew).
printExplanations(_,[],_).

unique([], []).
unique([Head | Tail], Result) :-
    member(Head, Tail), !,
    unique(Tail, Result).
unique([Head | Tail], [Head | Result]) :-
    unique(Tail, Result).