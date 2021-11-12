heartbeat(5).

log(frontend,f1,5,other,info).
log(frontend,f1,10,other,info).
log(frontend,f1,15,other,info).
log(frontend,f1,20,other,info).
log(frontend,f1,25,other,info).
log(frontend,f1,30,other,info).
log(frontend,f1,35,other,info).
log(frontend,f1,40,other,info).
log(frontend,f1,45,other,info).
log(frontend,f1,50,other,info).
log(frontend,f1,55,other,info).
log(frontend,f1,60,other,info).
%internal crash
%log(frontend,f1,65,other,info).

log(backend,b1,5,other,info).
log(backend,b1,10,other,info).
log(backend,b1,15,other,info).
log(backend,b1,20,other,info).
log(backend,b1,25,other,info).
log(backend,b1,30,other,info).
log(backend,b1,35,other,info).
log(backend,b1,40,other,info).
log(backend,b1,45,other,info).
log(backend,b1,50,other,info).
log(backend,b1,55,other,info).
log(backend,b1,60,other,info).
log(backend,b1,65,other,info).

log(backend,b2,5,other,info).
log(backend,b2,10,other,info).
log(backend,b2,15,other,info).
log(backend,b2,20,other,info).
log(backend,b2,25,other,info).
log(backend,b2,30,other,info).
log(backend,b2,35,other,info).
log(backend,b2,40,other,info).
log(backend,b2,45,other,info).
log(backend,b2,50,other,info).
log(backend,b2,55,other,info).
log(backend,b2,60,other,info).
log(backend,b2,65,other,info).

log(database,d1,5,other,info).
log(database,d1,10,other,info).
log(database,d1,15,other,info).
log(database,d1,20,other,info).
log(database,d1,25,other,info).
log(database,d1,30,other,info).
log(database,d1,35,other,info).
log(database,d1,40,other,info).
log(database,d1,45,other,info).
log(database,d1,50,other,info).
%database crash
%log(database,d1,55,other,info).
%log(database,d1,60,other,info).

%healthy interactions
log(frontend,f1,30,sendTo(backend,'f1b1'),info).
log(backend,b1,31,received('f1b1'),info).
log(backend,b1,39,answeredTo('f1b1'),info).
log(frontend,f1,40,answerFrom(backend,'f1b1'),info).

log(backend,b1,32,sendTo(database,'b1d1'),info).
log(database,d1,33,received('b1d1'),info).
log(database,d1,35,answeredTo('b1d1'),info).
log(backend,b1,36,answerFrom(database,'b1d1'),info).

%failed interactions
log(frontend,f1,50,sendTo(backend,'f1b2'),info).
log(backend,b2,51,received('f1b2'),info).
log(backend,b2,56,answeredTo('f1b2'),info).
log(frontend,f1,57,answerFrom(backend,'f1b2'),err).

log(backend,b2,52,sendTo(database,'b2d1'),info).
log(database,d1,53,received('b2d1'),info). % comment this to test "unreachable"
log(database,d1,54,other,err).
log(backend,b2,5 5,answerFrom(database,'b2d1'),err).

log(backend,b2,53,sendTo(goofy,'b2goofy'),info).

%error to be explained
log(frontend,f1,69,other,err).
