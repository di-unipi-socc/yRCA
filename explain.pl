%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Explainer %%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%

all_explanations(Event, Explanations) :-
    findall(E, explain(Event,E), Explanations). 

explain(Event, Explanation) :- 
    heartbeat(P),
    explain(P, [Event], [], Explanation).

% internal crash
explain(P, [E|Evs], Explained, [x(E,F)|Explanation]) :- 
    %write('internalcrash-'),writeln(E),
    \+ member(E,Explained), E = log(SId,_,_,Time), 
    FailTime is Time - P, 
    findall(X, logsBetween(SId,X,FailTime,Time), []),
    F = log(SId,'unexpected crash',emerg,FailTime),
    explain(P, [F|Evs], [E|Explained], Explanation).
% % invoked service never started
explain(P, [E|Evs], Explained, [x(E,F)|Explanation]) :-
    %write('neverstarted-'),writeln(E),
    \+ member(E,Explained), E = log(SId,_,_,Time), 
    interaction(SId,SId1,Start,_), Start < Time,
    findall(X, log(SId1,X,_,_), []),
    F = log(SId1,noStart,warn,0),
    explain(P, Evs, [E|Explained], Explanation).
% crash of invoked service
explain(P, [E|Evs], Explained, [x(E,F)|Explanation]) :-
    %write('crashinvoked'),writeln(E),
    \+ member(E,Explained), E = log(SId,_,_,Time), 
    interaction(SId,SId1,Start,End), Start < Time,
    findall(C,findX(Start,End,P,C),Xs), min_member(X,Xs), X<Time,
    log(SId1,_,_,Before),Before < X, 
    XPlusP is X + P, findall(Y, logsBetween(SId1,Y,X,XPlusP), []),
    F = log(SId1,'unexpected crash',emerg,X),
    explain(P, [F|Evs], [E|Explained], Explanation). 
% error in invoked service 
explain(P, [E|Evs], Explained, [x(E,F)|Explanation]) :-
    %write('errorinvoked-'),writeln(E),
    \+ member(E,Explained), E = log(SId,_,_,Time), 
    interaction(SId,SId1,Start,End), Start < Time,
    log(SId1,M,Sev,Time1), lte(Sev,warn), Time1 > Start, Time1 < End,
    F = log(SId1,M,Sev,Time1),
    explain(P, [F|Evs], [E|Explained], Explanation).
% SPECIAL CASE: explaining crashes not due to interactions
explain(P, [E|Evs], Explained, [x(E,F)|Explanation]) :-
    %write('special-'),writeln(E),
    \+ member(E,Explained), E = log(SId,_,emerg,Time), 
    F = log(SId,'internal crash',emerg,Time),
    explain(P, Evs, [E|Explained], Explanation).
explain(_, [], _, []).

findX(Start,End,P,X) :- 
    MinX is Start - P, MaxX is End + P, between(MinX,MaxX,X),
    \+ (between(MinX,MaxX,X1), X1 < X).

logsBetween(SId,log(SId,_,_,XTime),FailTime,Time) :-
    log(SId,_,_,XTime),
    XTime > FailTime, XTime < Time.

lte(S1,S2) :- severity(S1,A), severity(S2,B), A=<B.

%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Run Explainer %%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%
%all_explanations(log(s1,'error',err,999),E).

%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Knowledge base %%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%

% hearbeat period
heartbeat(200).

% Severity levels as per syslog
severity(emerg, 0). 
severity(alert, 1).
severity(crit, 2).
severity(err, 3).
severity(warn, 4).
severity(notice, 5).
severity(info, 6).
severity(debug, 7).

% log(ServiceInstance,Message,Severity,LogTime).
log(s1,'alive',info,200).
log(s1,'alive',info,400).
log(s1,'alive',info,600).
log(s1,'alive',info,800).
log(s1,'alive',info,1000).
log(s1,'error',err,999).

log(s2,'alive',info,200).
log(s2,'alive',info,400).
log(s2,'alive',info,600).
% log(s2,'alive',info,800).
log(s2,'alive',info,1000).
log(s2,'error in processing request from s1',err,967).

log(s3,'alive',info,200).
log(s3,'alive',info,400).
log(s3,'alive',info,600).
% s3 crashing and not logging "alive" at time 800
log(s3,'alive',info,1000).

log(s4,'alive',info,200).
log(s4,'alive',info,400).
log(s4,'alive',info,600).
log(s4,'alive',info,800).
log(s4,'alive',info,1000).
log(s4,'error in processing request from s5',err,960).

log(s5,'alive',info,200).
log(s5,'alive',info,400).
log(s5,'alive',info,600).
log(s5,'alive',info,800).
log(s5,'alive',info,1000).
log(s5,'error',err,975).

% interaction(InvokingInstance,InvokedInstance,StartTime,EndTime)
interaction(s1,s2,960,990).
interaction(s1,s6,900,910).
interaction(s2,s3,949,970).
interaction(s3,s4,953,970).
interaction(s5,s4,952,974).