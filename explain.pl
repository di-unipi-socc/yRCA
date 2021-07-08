:-set_prolog_flag(last_call_optimisation, true).
%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Explainer %%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%

all_explanations(Event, Explanations) :-
    findall(E, explain(Event,E), Exps), sort(Exps, Explanations),
    write('-- All explanations for "'), write(Event), writeln('":\n'),
    forall(member(X,Explanations), prettyPrint(X)),
    writeln('-- The End --\n').

prettyPrint([F|Explanation]) :- 
    F = x(First,_), write(First), 
    forall(member(x(_,X),[F|Explanation]), (write('\n\t -> '),write(X))), 
    writeln('.\n').

explain(Event, Explanation) :- 
    heartbeat(P),
    explain(P, [Event], [], Explanation).

% internal crash
explain(P, [E|Evs], Explained, [x(E,F)|Explanation]) :- 
    \+ member(E,Explained), E = log(SId,_,_,Time), 
    CrashTime is Time - P, noLogPeriod(SId,CrashTime,Time),
    F = log(SId,'unexpected crash',emerg,CrashTime),
    explain(P, [F|Evs], [E|Explained], Explanation).
% % invoked service never started
explain(P, [E|Evs], Explained, [x(E,F)|Explanation]) :-
    \+ member(E,Explained), E = log(SId,_,_,Time), 
    interaction(SId,SId1,Start,_), Start < Time,
    noLogPeriod(SId1,-1,inf),
    F = log(SId1,noStart,warn,0),
    explain(P, Evs, [E|Explained], Explanation).
% crash of invoked service
explain(P, [E|Evs], Explained, [x(E,F)|Explanation]) :-
    \+ member(E,Explained), E = log(SId,_,_,Time), 
    interaction(SId,SId1,Start,End), Start < Time,
    serviceCrash(SId1,Start,End,Time,P,CrashTime),
    log(SId1,_,_,Before), Before < CrashTime, 
    F = log(SId1,'unexpected crash',emerg,CrashTime),
    explain(P, [F|Evs], [E|Explained], Explanation). 
% error in invoked service 
explain(P, [E|Evs], Explained, [x(E,F)|Explanation]) :-
    \+ member(E,Explained), E = log(SId,_,_,Time), 
    interaction(SId,SId1,Start,End), Start < Time,
    log(SId1,M,Sev,Time1), lte(Sev,warn), Time1 > Start, Time1 < End,
    F = log(SId1,M,Sev,Time1),
    explain(P, [F|Evs], [E|Explained], Explanation).
% SPECIAL CASE: explaining crashes not due to interactions
explain(P, [E|Evs], Explained, [x(E,F)|Explanation]) :-
    \+ member(E,Explained), E = log(SId,_,emerg,Time), 
    F = log(SId,'internal crash',emerg,Time),
    explain(P, Evs, [E|Explained], Explanation).
explain(_, [], _, []).

serviceCrash(SId,Start,End,Time,P,CrashTime) :- 
    MinX is Start - P, MaxX is End + P, 
    findall(X, (between(MinX,MaxX,X), XPlusP is X + P, noLogPeriod(SId,X,XPlusP)), Xs), min_list(Xs,CrashTime), CrashTime < Time.

noLogPeriod(SId,Start,End) :- findall(Y, logsBetween(SId,Y,Start,End), []).

logsBetween(SId,log(SId,_,_,XTime),FailTime,Time) :-
    log(SId,_,_,XTime), XTime >= FailTime, XTime =< Time.

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
log(s3,'alive',info,790).
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