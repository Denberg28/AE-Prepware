(function(root,factory){const api=factory();if(typeof module==='object')module.exports=api;else root.AE=api;})(typeof globalThis!=='undefined'?globalThis:this,function(){
'use strict';
const DAY=86400000;
const day=(now=Date.now())=>{const d=new Date(now);return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;};
function fresh(){return {schema:1,name:'Cadet',stats:{},daily:{},bookmarks:[],flags:[],history:[],session:null,endpoint:'',cohort:null,accountNumber:null,pending:[],selection:'random',sourceMode:'AI'};}
function origin(q){return q.origin||'AI';}
function canonical(value){return Array.isArray(value)?value.map(canonical):value&&typeof value==='object'?Object.fromEntries(Object.keys(value).sort().map(k=>[k,canonical(value[k])])):value;}
function questionContent(bank,q){return JSON.stringify(canonical([q.subject,q.topic,q.prompt,q.choices,q.answer,q.explanation,q.source,q.review,q.reviewer,q.reviewedAt,origin(q),q.upload||null,q.supersedes||null,bank.sources[q.source]]));}
function unchangedQuestion(old,bank,q){const before=old?.questions.find(x=>x.id===q.id);return !!before&&questionContent(old,before)===questionContent(bank,q);}
function validateRefresh(old,next){
 if(next.extends!==old.version||next.version===old.version)throw Error('Refresh must extend the current bank with a new version.');
 validateBank(next,true,old);
 const index=new Map(next.questions.map(q=>[q.id,q]));
 for(const q of old.questions)if(!index.has(q.id)||questionContent(old,q)!==questionContent(next,index.get(q.id)))throw Error('Refresh changes an existing question or citation: '+q.id);
 return next;
}
function sourceCounts(state,bank,subject){const counts={AI:0,IN:0};for(const q of bank.questions)if(q.subject===subject&&q.active!==false&&!state.flags.includes(q.id))counts[origin(q)]++;return counts;}
function pickSources(state,bank,mode,subject,sourceMode='AI',rng=Math.random){
 if(!['AI','IN','hybrid'].includes(sourceMode))throw Error('Select AI, IN or both before starting.');
 const counts=sourceCounts(state,bank,subject),needs=sourceMode==='hybrid'?{AI:25,IN:25}:{[sourceMode]:50};
 let selected=[];
 for(const [source,count]of Object.entries(needs)){
  if(counts[source]<count)throw Error(`${source} has ${counts[source]} active questions for this subject; this selection needs ${count}.`);
  const filtered={...bank,questions:bank.questions.filter(q=>origin(q)===source)};
  selected.push(...pick(state,filtered,mode,subject,count,Date.now(),rng));
 }
 return shuffle(selected,rng);
}
function validateBank(b,imported=false,trusted=null){
 if(!b||b.schema!==1||typeof b.version!=='string'||!b.version.trim()||b.version.length>100||typeof b.blueprintSource!=='string'||!b.blueprintSource.startsWith('https://')||!Array.isArray(b.subjects)||!Array.isArray(b.questions)||b.questions.length<6||b.questions.length>3000)throw Error('Unsupported question bank.');
 const weights={math:10,aero:25,structures:20,construction:15,powerplant:20,ethics:10};const subjects=new Set(Object.keys(weights));
 if(b.subjects.length!==6||new Set(b.subjects.map(s=>s.id)).size!==6||b.subjects.some(s=>!subjects.has(s.id)||typeof s.name!=='string'||s.weight!==weights[s.id])||b.subjects.reduce((a,s)=>a+s.weight,0)!==100)throw Error('Invalid six-subject blueprint.');
 const ids=new Set(),activeContent=new Set();
 for(const q of b.questions){
  if(!q||typeof q.id!=='string'||!q.id.match(/^[A-Za-z0-9_-]{1,64}$/)||ids.has(q.id)||!subjects.has(q.subject)||typeof q.topic!=='string'||!q.topic.trim()||typeof q.prompt!=='string'||q.prompt.length<10||q.prompt.length>4000||!Array.isArray(q.choices)||q.choices.length!==4||q.choices.some(c=>typeof c!=='string'||!c.trim()||c.length>1000)||new Set(q.choices).size!==4||!Number.isInteger(q.answer)||q.answer<0||q.answer>3||typeof q.explanation!=='string'||q.explanation.length<10||!q.reviewer||!q.reviewedAt||!(imported&&!unchangedQuestion(trusted,b,q)?['approved']:['approved','source-checked']).includes(q.review))throw Error('Invalid or unapproved question: '+(q?.id||'?'));
  if(!['AI','IN'].includes(origin(q))||(q.active!==undefined&&typeof q.active!=='boolean'))throw Error('Invalid AI/IN origin or activation.');
  if(q.explanation.length>4000||q.topic.length>200||typeof q.reviewer!=='string'||!q.reviewer.trim()||q.reviewer.length>200||typeof q.reviewedAt!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(q.reviewedAt))throw Error('Invalid topic, explanation or review metadata.');
  const fingerprint=JSON.stringify([q.prompt.trim().toLowerCase(),q.choices.map(c=>c.trim().toLowerCase()).sort()]);if(q.active!==false){if(activeContent.has(fingerprint))throw Error('Duplicate active question content.');activeContent.add(fingerprint);}
  if(origin(q)==='IN'&&(!q.upload||!['file','locator','rights'].every(k=>typeof q.upload[k]==='string'&&q.upload[k].trim()&&q.upload[k].length<=500)||!['instructor-original','permission-granted','public-domain','open-license'].includes(q.upload.rights)||q.review!=='approved'))throw Error('IN question needs instructor approval and upload provenance.');
  const source=b.sources?.[q.source];if(!source||typeof source.title!=='string'||typeof source.locator!=='string'||typeof source.url!=='string'||!source.url.startsWith('https://'))throw Error('Missing source for '+q.id);
  ids.add(q.id);
 }
 if([...subjects].some(id=>!b.questions.some(q=>q.subject===id)))throw Error('Each subject needs questions.');
 return b;
}
function validateState(s,bank){
 if(!s||s.schema!==1||typeof s.name!=='string'||s.name.length>40||!s.stats||typeof s.stats!=='object'||Array.isArray(s.stats)||!s.daily||typeof s.daily!=='object'||Array.isArray(s.daily)||!Array.isArray(s.bookmarks)||!Array.isArray(s.flags)||!Array.isArray(s.history)||s.history.length>200)throw Error('Backup format is invalid.');
 const ids=new Set(bank.questions.map(q=>q.id));
 if(s.accountNumber!=null&&!/^AE-[0-9]{16}$/.test(s.accountNumber))throw Error('Invalid account number.');
 if(s.pending!==undefined&&(!Array.isArray(s.pending)||s.pending.length>200))throw Error('Invalid pending results.');
 for(const h of [...s.history,...(s.pending||[])]){if(!h||!Number.isInteger(h.total)||h.total<1||h.total>100||!Number.isInteger(h.correct)||h.correct<0||h.correct>h.total||!Number.isFinite(h.date))throw Error('Invalid result record.');if(h.ids&&(!Array.isArray(h.ids)||h.ids.length!==h.total||new Set(h.ids).size!==h.total||h.ids.some(id=>!ids.has(id))||!Array.isArray(h.answers)||h.answers.length!==h.total||h.answers.some(a=>!Number.isInteger(a)||a<0||a>3)||typeof h.id!=='string'||!/^[-a-zA-Z0-9_]{1,64}$/.test(h.id)||h.accountNumber!==s.accountNumber))throw Error('Invalid account result.');}
 for(const h of s.history){if(h.orders&&(!Array.isArray(h.orders)||h.orders.length!==h.total||h.orders.some(o=>!Array.isArray(o)||o.some(x=>!Number.isInteger(x))||[...o].sort().join('')!=='0123')))throw Error('Invalid recorded answer order.');if(h.ids&&h.correct!==h.ids.filter((id,i)=>bank.questions.find(q=>q.id===id).answer===h.answers[i]).length)throw Error('Recorded score does not match answers.');}
 for(const h of s.pending||[]){if(!h.ids||!h.id||h.total!==50||typeof h.bankVersion!=='string'||!h.bankVersion)throw Error('Invalid pending session.');}
 for(const [id,x]of Object.entries(s.stats)){if(!ids.has(id)||!x||!Number.isInteger(x.seen)||x.seen<1||!Number.isInteger(x.correct)||x.correct<0||x.correct>x.seen||!Number.isInteger(x.streak)||x.streak<0||!Number.isFinite(x.due)||!Number.isFinite(x.last))throw Error('Invalid progress record.');}
 for(const [d,v]of Object.entries(s.daily)){if(!/^\d{4}-\d{2}-\d{2}$/.test(d)||!v||!Array.isArray(v.answered)||!Array.isArray(v.correct)||new Set(v.answered).size!==v.answered.length||new Set(v.correct).size!==v.correct.length||v.answered.some(x=>!ids.has(x))||v.correct.some(x=>!v.answered.includes(x)))throw Error('Invalid daily progress.');}
 if(s.bookmarks.some(id=>!ids.has(id))||s.flags.some(id=>!ids.has(id)))throw Error('Unknown bookmarked or reported question.');
 if(s.endpoint&& !validEndpoint(s.endpoint))throw Error('Invalid cohort service URL.');
 if(s.cohort&& (typeof s.cohort.token!=='string'||s.cohort.token.length>100||typeof s.cohort.id!=='string'))throw Error('Invalid cohort account.');
 if(s.session){const t=s.session;if(!Array.isArray(t.ids)||!t.ids.length||t.ids.length>100||new Set(t.ids).size!==t.ids.length||t.ids.some(id=>!ids.has(id))||!Array.isArray(t.orders)||t.orders.length!==t.ids.length||t.orders.some(o=>!Array.isArray(o)||o.some(x=>!Number.isInteger(x))||[...o].sort().join('')!=='0123')||!Number.isInteger(t.index)||t.index<0||t.index>=t.ids.length||!Array.isArray(t.answers)||t.answers.length!==t.ids.length||t.answers.some(a=>a!==null&&(!Number.isInteger(a)||a<0||a>3))||t.answers.some((a,i)=>i<t.index&&a===null||i>t.index&&a!==null)||typeof t.mode!=='string')throw Error('Invalid saved session.');}
 return s;
}
function shuffle(arr,rng=Math.random){arr=[...arr];for(let i=arr.length-1;i>0;i--){const j=Math.floor(rng()*(i+1));[arr[i],arr[j]]=[arr[j],arr[i]];}return arr;}
function summary(state,bank){return bank.subjects.map(s=>{const items=bank.questions.filter(q=>q.subject===s.id&&q.active!==false&&!state.flags.includes(q.id));let seen=0,correct=0,covered=0,mastered=0;for(const q of items){const st=state.stats[q.id];if(st){seen+=st.seen;correct+=st.correct;covered++;if(st.streak>=3)mastered++;}}return {...s,total:items.length,seen,correct,covered,mastered,accuracy:seen?Math.round(100*correct/seen):null,estimate:(correct+1)/(seen+2)};});}
function weakest(state,bank){return summary(state,bank).filter(s=>s.total).sort((a,b)=>a.estimate-b.estimate||b.weight-a.weight)[0];}
function pick(state,bank,mode='adaptive',subject=null,count=10,now=Date.now(),rng=Math.random){
 const available=bank.questions.filter(q=>q.active!==false&&!state.flags.includes(q.id)&&(!subject||q.subject===subject));
 let candidates=available;
 if(mode==='bookmarks')candidates=candidates.filter(q=>state.bookmarks.includes(q.id));
 if(mode==='mistakes')candidates=candidates.filter(q=>state.stats[q.id]&&state.stats[q.id].streak===0);
 if(mode==='mock'){
  const result=[];for(const s of bank.subjects){const quota=s.weight/5;const pool=shuffle(candidates.filter(q=>q.subject===s.id),rng);if(pool.length<quota)throw Error('Not enough active questions for a weighted 20-question check. Restore reported questions or use practice.');result.push(...pool.slice(0,quota));}return shuffle(result,rng);
 }
 if((mode==='subject'||mode==='adaptive-subject')&&candidates.length<count)throw Error(`This subject has ${candidates.length} active questions. A session needs ${count} distinct questions. Restore set-aside questions or import a larger approved bank.`);
 if(mode==='adaptive'||mode==='adaptive-subject'){
  const focus=subject||weakest(state,bank)?.id;
  const scored=candidates.map(q=>{const st=state.stats[q.id];return {q,score:(q.subject===focus?5:0)+(!st?3:st.streak===0?6:st.due<=now?4:0)+rng()*3};});
  return scored.sort((a,b)=>b.score-a.score).slice(0,count).map(x=>x.q);
 }
 return shuffle(candidates,rng).slice(0,count);
}
function start(state,questions,mode,rng=Math.random){if((state.pending||[]).length>=200)throw Error('Sync or export your 200 pending account results before starting another session.');if(!questions.length)throw Error('No questions here yet.');state.session={ids:questions.map(q=>q.id),orders:questions.map(()=>shuffle([0,1,2,3],rng)),answers:questions.map(()=>null),index:0,mode,started:Date.now()};return state.session;}
function answer(state,bank,choice,now=Date.now()){
 const t=state.session;if(!t||!Number.isInteger(choice)||choice<0||choice>3)throw Error('Invalid answer.');
 const i=t.index;if(t.answers[i]!==null)return false;
 const q=bank.questions.find(q=>q.id===t.ids[i]);if(!q)throw Error('Question no longer exists.');
 const ok=choice===q.answer;t.answers[i]=choice;
 const old=state.stats[q.id]||{seen:0,correct:0,streak:0};const streak=ok?old.streak+1:0;
 state.stats[q.id]={seen:old.seen+1,correct:old.correct+(ok?1:0),streak,last:now,due:now+(ok?[1,3,7,14,30][Math.min(streak-1,4)]*DAY:10*60000)};
 const d=state.daily[day(now)]||(state.daily[day(now)]={answered:[],correct:[]});
 if(!d.answered.includes(q.id))d.answered.push(q.id);if(ok&&!d.correct.includes(q.id))d.correct.push(q.id);
 return true;
}
function finish(state,bank,now=Date.now()){
 const t=state.session;if(!t||t.answers.some(a=>a===null))throw Error('Finish every question before submitting.');
 const map=new Map(bank.questions.map(q=>[q.id,q]));const correct=t.ids.filter((id,i)=>t.answers[i]===map.get(id).answer).length;
 const result={id:uid(),mode:t.mode,total:t.ids.length,correct,date:now,started:t.started,subject:new Set(t.ids.map(id=>map.get(id).subject)).size===1?map.get(t.ids[0]).subject:'mixed',accountNumber:state.accountNumber||null,bankVersion:bank.version,ids:[...t.ids],answers:[...t.answers],orders:t.orders.map(o=>[...o])};
 if(state.accountNumber&&t.ids.length===50){state.pending=state.pending||[];if(state.pending.length>=200)throw Error('Pending results queue is full. Sync or export before completing.');state.pending.push(result);}
 state.history.unshift(result);state.history=state.history.slice(0,200);state.session=null;return result;
}
function uid(){return globalThis.crypto.randomUUID();}
function xp(state){return Object.values(state.daily).reduce((n,d)=>n+d.correct.length*10+d.answered.filter(id=>!d.correct.includes(id)).length*2,0);}
function streak(state,now=Date.now()){let n=0,t=now;if(!state.daily[day(t)]?.answered.length)t-=DAY;while(state.daily[day(t)]?.answered.length){n++;t-=DAY;}return n;}
function validEndpoint(value){try{const u=new URL(value);return u.protocol==='https:'&&!u.username&&!u.password&&!u.search&&!u.hash&&u.pathname==='/';}catch{return false;}}
return {origin,questionContent,validateRefresh,sourceCounts,pickSources,uid,DAY,day,fresh,validateBank,validateState,shuffle,summary,weakest,pick,start,answer,finish,xp,streak,validEndpoint};
});
