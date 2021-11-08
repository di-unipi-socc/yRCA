:-set_prolog_flag(last_call_optimisation, true).

%determine all possible explanations for "Event"
xfail(Event,Explanations,RootCause) :-
    findall(E,distinct(causedBy(Event,E,RootCause)),Explanations).
%determine "NumSols" possible explanations for "Event"
xfail(NumSols,Event,Explanations,RootCause) :-
    findnsols(NumSols,E,distinct(causedBy(Event,E,RootCause)),Explanations).
    
%log(serviceName,serviceInstance,timestamp,eventType,message,severity)

%invoked service never started
causedBy(log(_,I,T,E,_,_),[X],Root) :-
    dif(E,internal),
    log(_,I,Ts,sendTo(Root,_),_,_), Ts < T, horizon(H), Ts >= T - H,
    \+ log(Root,_,_,_,_,_),
    X = neverStarted(Root).

%unreachable service
causedBy(log(_,I,T,E,_,_),[X],Root) :-
    dif(E,internal),
    nonReceivedRequest(I,Root,Ts,_), Ts < T, horizon(H), Ts >= T - H,
    log(Root,_,_,_,_,_),
    X = unreachable(Root).

%error of invoked service
causedBy(log(SI,I,T,E,_,_),[X|Xs],Root) :-
    dif(E,internal),
    failedInteraction((SI,I),(SJ,J),Ts,Te), Ts < T, horizon(H), Ts >= T - H,
    log(SJ,J,U,F,M,Sev), lte(Sev,warning), Ts =< U, U =< Te, 
    X=log(SJ,J,U,F,M,Sev),
    causedBy(X,Xs,Root).

%timeout of invoked service
causedBy(log(SI,I,T,E,_,_),[X|Xs],Root) :-
    dif(E,internal),
    timedOutInteraction((SI,I),(SJ,J),TsIJ,TeIJ), TsIJ < T, horizon(H), TsIJ >= T - H,
    timedOutInteraction((SJ,J),(SK,K),TsJK,TeJK), TsJK < TeIJ, TeIJ < TeJK,
    log(SJ,J,TeJK,timeout(SK,K),M,Sev),X=log(SJ,J,TeJK,timeout(SK,K),M,Sev),
    causedBy(X,Xs,Root).

%base case
causedBy(log(Root,_,_,internal,_,_),[],Root).

% TODO: use file to create associate log templates with events, then use it to parse input and to generate outputs

lte(S1,S2) :- severity(S1,A), severity(S2,B), A=<B.

nonReceivedRequest(I,SJ,Ts,Te) :-
    log(SI,I,Ts,sendTo(SJ,Id),_,_),
    log(SI,I,Te,timeout(SJ,Id),_,_),
    \+ (log(SJ,_,Tr,received(X),_,_), Ts < Tr, Tr < Te, (X=Id;X=noID)).

%failedInteraction((SI,I),(SJ,J),Ts,Te) :-
%    log(SI,I,Te,E,_,_), (E=errorFrom(SJ,Id);E=timeout(SJ,Id)),
%    interaction(Id,(SI,I),(SJ,J),Ts,Te).
failedInteraction((SI,I),(SJ,J),Ts,Te) :-
    errorInteraction((SI,I),(SJ,J),Ts,Te);timedOutInteraction((SI,I),(SJ,J),Ts,Te).
errorInteraction((SI,I),(SJ,J),Ts,Te) :-
    log(SI,I,Te,errorFrom(SJ,Id),_,_),
    interaction(Id,(SI,I),(SJ,J),Ts,Te).
timedOutInteraction((SI,I),(SJ,J),Ts,Te) :-
    log(SI,I,Te,timeout(SJ,Id),_,_),
    interaction(Id,(SI,I),(SJ,J),Ts,Te).

interaction(Id,(SI,I),(SJ,J),Ts,Te) :-
    log(SI,I,Ts,sendTo(SJ,Id),_,_), 
    log(SJ,J,Tr,received(X),_,_), 
    (X=Id;X=noID), Ts < Tr, Tr < Te.

% MEMO: If (passive) components are not instrumented to propagate IDs, just put "noId" as ID when templating logs corresponding to receive/answer to service interactions (in the log template parser)