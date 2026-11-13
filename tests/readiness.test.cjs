const {test}=require('node:test'),assert=require('node:assert/strict');
const AE=require('../app/src/main/assets/core'),R=require('../app/src/main/assets/readiness'),bank=require('../app/src/main/assets/bank.json');
const NOW=Date.UTC(2026,10,14,4),DAY=R.DAY;
function clock(now,fn){const old=Date.now;Date.now=()=>now;try{return fn();}finally{Date.now=old;}}
function complete(s,subject,kind,now,correct=20){return clock(now,()=>{AE.startCheck(s,bank,subject,kind);for(let i=0;i<20;i++){s.session.index=i;AE.answer(s,bank,i<correct?0:1,now+i);}return AE.finish(s,bank,now+100);});}
test('legacy scores and openings do not fabricate a baseline or activity journal',()=>{
 const s=AE.fresh();s.stats.MA001={seen:8,correct:8,streak:8,last:NOW,due:NOW};
 assert.equal(R.report(s,bank,NOW).competence.assessed,0);assert.equal(R.report(s,bank,NOW).commitment.observed7,0);
 AE.start(s,[bank.questions[0]],'subject');AE.answer(s,bank,0,NOW);AE.finish(s,bank,NOW);
 assert.equal(R.report(s,bank,NOW).competence.subjects[0].first.total,0);
 assert.equal(R.report(s,bank,NOW).commitment.active7,1);
});
test('diagnostic defers grading, resumes, locks answers and grades exactly once',()=>{
 const s=AE.fresh();clock(NOW,()=>AE.startCheck(s,bank,'math','diagnostic'));
 const id=s.session.ids[0];AE.answer(s,bank,1,NOW);assert.equal(s.stats[id],undefined);assert.equal(AE.answer(s,bank,0,NOW+1),false);
 const restored=AE.validateState(structuredClone(s),bank);assert.equal(restored.session.answers[0],1);assert.equal(R.report(s,bank,NOW).competence.assessed,0);
 for(let i=1;i<20;i++){restored.session.index=i;AE.answer(restored,bank,0,NOW+i);}
 const h=AE.finish(restored,bank,NOW+100);assert.equal(h.correct,19);assert.equal(h.mode,'diagnostic');assert.equal(Object.keys(restored.stats).length,20);
 assert.throws(()=>AE.finish(restored,bank,NOW+101));assert.equal(restored.stats[id].seen,1);
 assert.equal(R.report(restored,bank,NOW+200).competence.subjects[0].first.correct,19);
});
test('repeated correct practice never overwrites first attempts or qualifies as a check',()=>{
 const s=AE.fresh(),q=bank.questions[0];for(let i=0;i<5;i++){AE.start(s,[q],'subject');AE.answer(s,bank,i?0:1,NOW+i);AE.finish(s,bank,NOW+i);}
 const r=R.report(s,bank,NOW+10);assert.equal(r.competence.subjects[0].first.correct,0);assert.equal(r.competence.assessed,0);assert.equal(r.commitment.days.at(-1).questions,1);
});
test('spaced confirmation requires two successful checks, seven days apart, within thirty days',()=>{
 const s=AE.fresh();complete(s,'math','diagnostic',NOW,14);
 clock(NOW+DAY,()=>assert.throws(()=>AE.startCheck(s,bank,'math','retention'),/eligible/));
 complete(s,'math','retention',NOW+8*DAY);assert.equal(R.report(s,bank,NOW+8*DAY+200).competence.subjects[0].status,'Confirm retention');
 complete(s,'math','retention',NOW+16*DAY);let r=R.report(s,bank,NOW+16*DAY+200);assert.equal(r.competence.subjects[0].status,'Foundation target met');assert.equal(r.competence.subjects[0].first.correct,14);
 assert.equal(r.competence.weighted,null);assert.equal(r.readiness.boardReadiness,'Not established');
 r=R.report(s,bank,NOW+47*DAY);assert.equal(r.competence.subjects[0].status,'Recheck due');
});
test('all-subject weighted index uses published weights and never becomes pass odds',()=>{
 const s=AE.fresh();for(const sub of bank.subjects)complete(s,sub.id,'diagnostic',NOW,sub.id==='aero'?10:20);
 const r=R.report(s,bank,NOW+1000);assert.equal(r.competence.assessed,6);assert.equal(r.competence.weighted,88);assert.equal(r.readiness.status,'Subject support needed');assert.equal(r.readiness.boardReadiness,'Not established');
 assert.equal(r.readiness.priorities[0].subject,'aero');
});
test('Manila midnight, partial windows, revisions and journal validation are explicit',()=>{
 const s=AE.fresh();R.activity(s,'MA001',Date.UTC(2026,10,13,15,59));R.activity(s,'MA002',Date.UTC(2026,10,13,16,1));
 assert.deepEqual(Object.keys(s.monitoring.days),['2026-11-13','2026-11-14']);
 const revised={...structuredClone(bank.questions[0]),id:'TEST-REV',supersedes:'MA001'};s.stats.MA001={seen:1,correct:0,streak:0,last:NOW,due:NOW};assert.equal(R.wasSeen(s,{...bank,questions:[...bank.questions,revised]},revised),true);
 const bad=structuredClone(s);bad.monitoring.days['2026-11-14'].push('UNKNOWN');assert.throws(()=>AE.validateState(bad,bank),/activity/);
});
test('retired/reported and interrupted-over-24h checks cannot inflate readiness',()=>{
 const s=AE.fresh();const h=complete(s,'math','diagnostic',NOW);s.flags=[h.ids[0]];assert.equal(R.report(s,bank,NOW+1000).competence.assessed,0);s.flags=[];
 h.monitoring.from-=2*DAY;assert.equal(R.report(s,bank,NOW+1000).competence.assessed,0);
});
test('exports contain no account credentials, answer keys or question text',()=>{
 const s=AE.fresh();s.cohort={id:'cohort',token:'SECRET-TOKEN'};s.accountNumber='AE-1234567890123456';complete(s,'math','diagnostic',NOW);
 const raw=JSON.stringify(R.report(s,bank,NOW+1000,'Student A'));for(const text of ['SECRET-TOKEN',s.accountNumber,bank.questions[0].prompt,'"answers"','"choices"'])assert.ok(!raw.includes(text));
});
test('initial diagnostic survives history rotation and failed submission is not graded twice',()=>{
 const s=AE.fresh();complete(s,'math','diagnostic',NOW,14);s.history=[];
 assert.equal(R.report(s,bank,NOW+1000).competence.subjects[0].baseline.correct,14);
 const next=AE.fresh();next.accountNumber='AE-1234567890123456';clock(NOW,()=>AE.startCheck(next,bank,'math','diagnostic'));
 for(let i=0;i<20;i++){next.session.index=i;AE.answer(next,bank,0,NOW+i);}next.pending=Array(200).fill({});
 assert.throws(()=>AE.finish(next,bank,NOW+100),/queue/);assert.equal(Object.keys(next.stats).length,0);
 next.pending=[];AE.finish(next,bank,NOW+100);assert.equal(Object.values(next.stats).reduce((n,x)=>n+x.seen,0),20);
 assert.equal(R.checkCounts(next,bank,'math','diagnostic','').ready,false);
});
