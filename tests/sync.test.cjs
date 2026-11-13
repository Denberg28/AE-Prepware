const {test}=require('node:test'),assert=require('node:assert/strict');
const S=require('../app/src/main/assets/sync');
test('private snapshot excludes tokens, pending transport and device settings',()=>{
 const s={schema:1,name:'A',stats:{},history:[],pending:['unsent'],endpoint:'https://example.com',cohort:{token:'private'},cloudRevision:3};
 const p=S.projection(s);assert.equal(p.cohort,undefined);assert.equal(p.pending,undefined);assert.equal(p.endpoint,undefined);p.name='B';assert.equal(s.name,'A');
});
test('lost acknowledgements retain operation identity; malformed responses cannot clear queue',()=>{
 assert.equal(S.acknowledgement({operation:'one'},{saved:true,operation:'one',revision:2}),2);
 for(const r of [{saved:true,operation:'two',revision:2},{saved:false,operation:'one',revision:2},{saved:true,operation:'one',revision:0}])assert.throws(()=>S.acknowledgement({operation:'one'},r));
});
test('restore merges grades received after last backup while preserving first-attempt journal and session',()=>{
 const state={accountNumber:'AE-1',stats:{q:{seen:2}},history:[{id:'old',date:1}],session:{id:'unfinished'},monitoring:{first:false}};
 const r=S.restore({state,revision:3,share:true},{number:'AE-1',rankOptIn:false,stats:{q:{seen:3}},history:[{id:'new',date:2},{id:'old',date:1}]},'AE-1');
 assert.deepEqual(r.history.map(h=>h.id),['new','old']);assert.equal(r.stats.q.seen,3);assert.deepEqual(r.monitoring,state.monitoring);assert.deepEqual(r.session,state.session);assert.equal(r.rankOptIn,false);
 assert.throws(()=>S.restore({state},{number:'AE-2'},'AE-2'),/different account/);
});
test('upgrade trusts exact bundled additions while rejecting unknown source-checked imports',()=>{
 const AE=require('../app/src/main/assets/core'),bundled=require('../app/src/main/assets/bank.json');
 const old=structuredClone(bundled);old.version=bundled.extends;delete old.extends;old.questions=old.questions.filter(q=>!q.id.startsWith('FB-'));
 assert.throws(()=>AE.validateRefresh(old,bundled),/unapproved/);
 assert.equal(AE.validateRefresh(old,bundled,bundled),bundled);
 const altered=structuredClone(bundled);altered.questions.find(q=>q.id==='FB-B01').prompt='Unreviewed altered question from another service';
 assert.throws(()=>AE.validateRefresh(old,altered,bundled),/unapproved/);
 const mutated=structuredClone(bundled);mutated.questions[0].answer=1;
 assert.throws(()=>AE.validateRefresh(old,mutated,bundled),/unapproved|changes an existing/);
});
