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

lte(S1,S2) :- severity(S1,A), severity(S2,B), A=<B.

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
log(s2,'alive',info,800).
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
interaction(s2,s3,949,970).
interaction(s2,s4,953,970).
interaction(s5,s4,952,974).


%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Explainer %%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%

all_explanations(Event, Explanations) :-
    findall(E, explain(Event,E), Explanations). 

explain(Event, Explanation) :- 
    heartbeat(P),
    explain(P, [Event], [], Explanation).

explain(P, [E|Evs], Explained, [x(E,log(SId,bot,emerg,FailTime))|Explanation]) :- 
    E = log(SId,Msg,Sev,Time), 
    FailTime is Time - P,
    findall(X, logsBetween(P,SId,X,FailTime,Time), []),
    explain(P, Evs, [log(SId,Msg,Sev,Time)|Explained], Explanation).
explain([], _, []).

logsBetween(SId,log(SId,_,_,XTime),FailTime,Time) :-
    log(SId,_,_,XTime),
    XTime > Time - P, XTime < Time.

%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Run Explainer %%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%
all_explanations(log(s1,'error',err,999),E).