const {test}=require('node:test'),assert=require('node:assert/strict');
const AE=require('../app/src/main/assets/core'),original=require('../app/src/main/assets/bank.json');
function merged(){const bank=structuredClone(original);bank.version='test-IN1';bank.extends=original.version;for(const [i,item]of original.questions.filter(q=>q.subject==='aero').slice(0,50).entries())bank.questions.push({...structuredClone(item),id:'TEST-IN-'+i,prompt:'Synthetic instructor fixture: '+item.prompt,origin:'IN',review:'approved',reviewer:'Automated TEST FIXTURE',upload:{file:'synthetic.json',locator:'Test '+i,rights:'instructor-original'}});return bank;}
test('source selection enforces exact 50/25 quotas, excludes reports and retired items',()=>{
 const bank=merged(),s=AE.fresh();AE.validateRefresh(original,bank);
 for(const mode of ['AI','IN','hybrid']){const qs=AE.pickSources(s,bank,'subject','aero',mode);assert.equal(qs.length,50);assert.equal(new Set(qs.map(q=>q.id)).size,50);assert.equal(qs.filter(q=>AE.origin(q)==='IN').length,mode==='hybrid'?25:mode==='IN'?50:0);}
 s.flags=bank.questions.filter(q=>q.origin==='IN').slice(0,26).map(q=>q.id);
 assert.throws(()=>AE.pickSources(s,bank,'subject','aero','hybrid'),/IN has 24/);
 assert.throws(()=>AE.pickSources(s,bank,'subject','math','IN'),/IN has 0/);
 assert.throws(()=>AE.pickSources(s,bank,'subject','math',''),/Select AI/);
});
test('append-only refresh preserves unfinished sessions, old scores and pending queue',()=>{
 const s=AE.fresh();s.accountNumber='AE-1234567890123456';AE.start(s,original.questions.filter(q=>q.subject==='math').slice(0,50),'subject');for(let i=0;i<50;i++){s.session.index=i;AE.answer(s,original,0);}AE.finish(s,original);AE.start(s,original.questions.slice(0,2),'subject');AE.answer(s,original,0);
 const bank=merged();const old=bank.questions[0];old.active=false;bank.questions.push({...structuredClone(old),id:'TEST-REVISION',active:true,answer:1,review:'approved',reviewer:'Automated TEST FIXTURE',supersedes:old.id});AE.validateRefresh(original,bank);
 const restored=AE.validateState(structuredClone(s),bank);assert.equal(restored.history[0].correct,50);assert.equal(restored.pending[0].bankVersion,original.version);assert.equal(restored.session.answers[0],0);assert.ok(!AE.pickSources(s,bank,'subject','math','AI').some(q=>q.id===old.id));
 bank.questions[0].answer=2;bank.questions[0].review='approved';assert.throws(()=>AE.validateRefresh(original,bank),/existing question/);
});
test('IN provenance, approval and duplicate active content are validated',()=>{
 const bank=merged();delete bank.questions.at(-1).upload;assert.throws(()=>AE.validateRefresh(original,bank),/provenance/);
 const duplicate=merged();duplicate.questions.at(-1).prompt=duplicate.questions.at(-2).prompt;duplicate.questions.at(-1).choices=duplicate.questions.at(-2).choices;assert.throws(()=>AE.validateRefresh(original,duplicate),/Duplicate active/);
});
