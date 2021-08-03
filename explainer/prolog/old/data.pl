%%%%%%%%%%%%%%%%%%%%%%%%%
%%%% Knowledge base %%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%
:- discontiguous log/4.

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
log(se1,s1,200,'alive',info).
log(se1,s1,400,'alive',info).
log(se1,s1,600,'alive',info).
log(se1,s1,800,'alive',info).
log(se1,s1,1000,'alive',info).
log(se1,s1,999,'error',err).

log(se1,s2,200,'alive',info).
log(se1,s2,400,'alive',info).
log(se1,s2,600,'alive',info).
% log(se1,s2,800,'alive',info).
log(se1,s2,1000,'alive',info).
log(se1,s2,967,'error in processing request from s1',err).

log(se1,s3,200,'alive',info).
log(se1,s3,400,'alive',info).
log(se1,s3,600,'alive',info).
log(se1,s3,790,'alive',info).
% s3 crashing and not logging "alive" at time 800
log(se1,s3,1000,'alive',info).

log(se1,s4,200,'alive',info).
log(se1,s4,400,'alive',info).
log(se1,s4,600,'alive',info).
log(se1,s4,800,'alive',info).
log(se1,s4,1000,'alive',info).
log(se1,s4,960,'error in processing request from s5',err).

log(se1,s5,200,'alive',info).
log(se1,s5,400,'alive',info).
log(se1,s5,600,'alive',info).
log(se1,s5,800,'alive',info).
log(se1,s5,1000,'alive',info).
log(se1,s5,975,'error',err).

% interaction(InvokingInstance,InvokedInstance,StartTime,EndTime)
interaction(s1,s2,960,990).
interaction(s1,s6,900,910).
interaction(s2,s3,949,970).
interaction(s3,s4,953,970).
interaction(s5,s4,952,974).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
log(se1,s10,1000,'alive',info).
log(se1,s10,300,'alive',info).
%interaction(s10,s11,795,820).
%log(se1,s11,797,'alive',warn).