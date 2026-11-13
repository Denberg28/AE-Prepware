const {test}=require('node:test'),assert=require('node:assert/strict');
const AE=require('../app/src/main/assets/core'),bank=require('../app/src/main/assets/bank.json');
test('core selection restricts all six subjects and retains the full reference bank',()=>{
 assert.equal(Object.keys(bank.focus.questions).length,120);
 for(const s of bank.subjects){
  const state=AE.fresh(),items=AE.pickSources(state,bank,'adaptive-subject',s.id,'AI',()=>.4,'focus');
  assert.equal(items.length,20);assert.equal(new Set(items.map(q=>q.id)).size,20);
  assert.ok(items.every(q=>Object.hasOwn(bank.focus.questions,q.id)&&q.subject===s.id));
  assert.equal(AE.pickSources(state,bank,'subject',s.id).length,50);
 }
 assert.equal(bank.questions.find(q=>q.id==='ST005').active,false);
 const state=AE.fresh();state.flags=['MA001'];
 assert.throws(()=>AE.pickSources(state,bank,'subject','math','AI',()=>.4,'focus'),/AI has 19/);
 assert.throws(()=>AE.scopeBank(bank,'typo'),/Invalid study scope/);
});
test('core validator rejects dangling IDs, subject mismatches and retired items',()=>{
 for(const change of [b=>b.focus.questions.UNKNOWN={area:'math-1'},b=>b.focus.questions.MA001.area='aero-1',b=>b.questions[0].active=false,b=>b.focus.sessionSize=50,b=>b.focus=null]){
  const b=structuredClone(bank);change(b);assert.throws(()=>AE.validateBank(b),/core|Core/);
 }
});
test('topic diversity prevents early parameter variants crowding out another topic',()=>{
 const qs=[{id:'a',topic:'A'},{id:'b',topic:'A'},{id:'c',topic:'B'},{id:'d',topic:'C'}];
 assert.deepEqual(AE.diversify(qs,3).map(q=>q.id),['a','c','d']);
});
test('20-question results queue and restore alongside legacy 50-question results',()=>{
 const state=AE.fresh();state.accountNumber='AE-1234567890123456';
 for(const scope of ['focus','full']){
  AE.start(state,AE.pickSources(state,bank,'subject','math','AI',()=>.3,scope),'subject');
  for(let i=0;i<state.session.ids.length;i++){state.session.index=i;AE.answer(state,bank,0);}
  AE.finish(state,bank);
 }
 assert.deepEqual(state.pending.map(h=>h.total),[20,50]);
 assert.equal(AE.validateState(structuredClone(state),bank).history.length,2);
});
