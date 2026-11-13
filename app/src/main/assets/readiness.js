/* Local, descriptive evidence. These rules do not predict a PRC outcome. */
(function(root,factory){const api=factory();if(typeof module==='object')module.exports=api;else root.Readiness=api;})(globalThis,function(){
'use strict';
const DAY=86400000,POLICY='brms-1',TARGET=80,WINDOW=30*DAY,SPACING=7*DAY;
const day=now=>new Date(now+8*3600000).toISOString().slice(0,10);
const percent=(correct,total)=>total?Math.round(100*correct/total):null;
function ensure(state){if(!state.monitoring)state.monitoring={schema:1,id:crypto.randomUUID(),since:null,goal:{days:4,questions:10},days:{},items:{},baselines:{}};if(!state.monitoring.baselines)state.monitoring.baselines={};return state.monitoring;}
function wasSeen(state,bank,q,index=new Map(bank.questions.map(x=>[x.id,x]))){let at=q,visited=new Set();while(at&&!visited.has(at.id)){if(state.stats[at.id])return true;visited.add(at.id);at=index.get(at.supersedes);}return false;}
function activity(state,id,now){const m=ensure(state);m.since=m.since===null?now:Math.min(m.since,now);const date=day(now),ids=m.days[date]||(m.days[date]=[]);if(!ids.includes(id))ids.push(id);const cutoff=day(now-27*DAY);for(const key of Object.keys(m.days))if(key<cutoff||key>date)delete m.days[key];}
function observe(state,q,correct,now,mode,novel){const m=ensure(state);if(novel&&!m.items[q.id])m.items[q.id]={at:now,correct,kind:['diagnostic','retention'].includes(mode)?mode:'practice'};}
function finishCheck(state,bank,h){
 if(h.mode!=='diagnostic'||h.monitoring.to-h.monitoring.from>DAY)return;
 const index=new Map(bank.questions.map(q=>[q.id,q]));if(h.ids.some(id=>index.get(id)?.active===false||state.flags.includes(id)))return;
 const m=ensure(state);if(!m.baselines[h.subject])m.baselines[h.subject]={id:h.id,kind:'diagnostic',at:h.monitoring.to,total:20,correct:h.correct,bankVersion:h.bankVersion};
}
function validate(state,bank){
 const m=state.monitoring;if(m===undefined)return;
 const ids=new Set(bank.questions.map(q=>q.id)),time=x=>Number.isFinite(x)&&x>=0&&x<=8640000000000000;
 if(!m||m.schema!==1||typeof m.id!=='string'||!/^[a-f0-9-]{36}$/.test(m.id)||(m.since!==null&&!time(m.since))||!m.goal||!Number.isInteger(m.goal.days)||m.goal.days<1||m.goal.days>7||!Number.isInteger(m.goal.questions)||m.goal.questions<1||m.goal.questions>50||!m.days||Array.isArray(m.days)||Object.keys(m.days).length>28||!m.items||Array.isArray(m.items)||Object.keys(m.items).length>3000)throw Error('Invalid readiness journal.');
 if(m.baselines!==undefined){if(!m.baselines||Array.isArray(m.baselines)||Object.keys(m.baselines).length>6)throw Error('Invalid diagnostic baseline.');for(const [subject,x]of Object.entries(m.baselines))if(!bank.subjects.some(s=>s.id===subject)||!x||x.kind!=='diagnostic'||x.total!==20||!Number.isInteger(x.correct)||x.correct<0||x.correct>20||!time(x.at)||typeof x.id!=='string'||!/^[-A-Za-z0-9_]{1,64}$/.test(x.id)||typeof x.bankVersion!=='string'||x.bankVersion.length>100)throw Error('Invalid diagnostic baseline.');}
 for(const [d,items]of Object.entries(m.days))if(!/^\d{4}-\d{2}-\d{2}$/.test(d)||!Array.isArray(items)||items.length>3000||new Set(items).size!==items.length||items.some(id=>!ids.has(id)))throw Error('Invalid readiness activity.');
 for(const [id,x]of Object.entries(m.items))if(!ids.has(id)||!x||!time(x.at)||typeof x.correct!=='boolean'||!['practice','diagnostic','retention'].includes(x.kind))throw Error('Invalid first-attempt observation.');
}
function checkPool(state,bank,subject,kind,sourceMode='AI',now=Date.now()){
 if(!['diagnostic','retention'].includes(kind)||!['AI','IN','hybrid'].includes(sourceMode))throw Error('Select AI, IN or both in Subjects before checking.');
 const index=new Map(bank.questions.map(q=>[q.id,q]));return bank.questions.filter(q=>q.subject===subject&&q.active!==false&&!state.flags.includes(q.id)&&(sourceMode==='hybrid'||(q.origin||'AI')===sourceMode)&&(kind==='diagnostic'?!wasSeen(state,bank,q,index):state.stats[q.id]&&state.stats[q.id].last<=now-SPACING));
}
function checkCounts(state,bank,subject,kind,sourceMode){if(sourceMode==='')return {AI:0,IN:0,ready:false};const pool=checkPool(state,bank,subject,kind,sourceMode),ai=pool.filter(q=>(q.origin||'AI')==='AI').length,ins=pool.length-ai;return {AI:ai,IN:ins,ready:sourceMode==='hybrid'?ai>=10&&ins>=10:pool.length>=20};}
function eligibleChecks(state,bank,now){const index=new Map(bank.questions.map(q=>[q.id,q]));return [...new Map(state.history.map(h=>[h.id,h])).values()].filter(h=>['diagnostic','retention'].includes(h.mode)&&h.monitoring?.schema===1&&h.total===20&&h.ids?.length===20&&h.date<=now&&h.ids.every(id=>index.has(id)&&index.get(id).active!==false&&!state.flags.includes(id))&&Number.isFinite(h.monitoring.from)&&Number.isFinite(h.monitoring.to)&&h.monitoring.to>=h.monitoring.from&&h.monitoring.to-h.monitoring.from<=DAY&&h.monitoring.to<=now&&h.monitoring.kind===h.mode&&h.monitoring.fresh?.length===20&&h.monitoring.fresh.every(x=>x===(h.mode==='diagnostic')));}
function report(state,bank,now=Date.now(),alias=state.name){
 const m=state.monitoring,goal=m?.goal||{days:4,questions:10},index=new Map(bank.questions.map(q=>[q.id,q]));
 const dates=Array.from({length:28},(_,i)=>day(now-(27-i)*DAY)),days=dates.map(date=>({date,questions:(m?.days[date]||[]).length})),week=days.slice(-7);
 const checks=eligibleChecks(state,bank,now),subjects=bank.subjects.map(s=>{
  const observed=Object.entries(m?.items||{}).filter(([id,x])=>index.get(id)?.subject===s.id&&index.get(id).active!==false&&!state.flags.includes(id)&&x.at<=now);
  const topics=new Map();for(const [id,x]of observed){const t=index.get(id).topic,a=topics.get(t)||{topic:t,total:0,correct:0};a.total++;a.correct+=x.correct?1:0;topics.set(t,a);}
  const history=checks.filter(h=>h.subject===s.id).sort((a,b)=>b.monitoring.to-a.monitoring.to).map(h=>({id:h.id,kind:h.mode,at:h.monitoring.to,total:h.total,correct:h.correct}));
  const recent=history.filter(h=>h.at>=now-WINDOW),latest=recent[0]||null;
  const met=!!latest&&percent(latest.correct,20)>=TARGET&&recent.some(h=>latest.at-h.at>=SPACING&&percent(h.correct,20)>=TARGET);
  const status=!latest?(history.length?'Recheck due':'Baseline needed'):percent(latest.correct,20)<TARGET?'Support needed':met?'Foundation target met':'Confirm retention';
  const core=bank.questions.filter(q=>q.subject===s.id&&q.active!==false&&(!bank.focus||Object.hasOwn(bank.focus.questions,q.id)));
  return {id:s.id,name:s.name,weight:s.weight,status,checks:history,latest,baseline:m?.baselines?.[s.id]||null,first:{total:observed.length,correct:observed.filter(([,x])=>x.correct).length},core:{total:core.length,seen:core.filter(q=>!!state.stats[q.id]).length},topics:[...topics.values()].filter(t=>t.total>=3&&percent(t.correct,t.total)<TARGET).sort((a,b)=>a.correct/a.total-b.correct/b.total).slice(0,3)};
 });
 const assessed=subjects.filter(s=>s.latest),met=subjects.filter(s=>s.status==='Foundation target met').length;
 const weighted=assessed.length===6?Math.round(subjects.reduce((n,s)=>n+s.weight*s.latest.correct/s.latest.total,0)):null;
 const priorities=[...subjects].sort((a,b)=>{
  const priority=s=>!s.latest?s.weight:(1-s.latest.correct/s.latest.total)*s.weight;
  return priority(b)-priority(a)||b.weight-a.weight;
 }).filter(s=>s.status!=='Foundation target met').map(s=>({subject:s.id,reason:s.status,action:!s.latest?'Take a new-item diagnostic.':s.status==='Support needed'?'Review errors and prerequisite concepts with a facilitator.':'Check retention after at least seven days.'}));
 return {type:'ae-board-readiness',schema:1,policy:POLICY,profile:m?.id||null,alias:String(alias||'Cadet').trim().slice(0,40),generatedAt:now,bankVersion:bank.version,
  provenance:'device-recorded, self-paced; not proctored or independently verified',trackingSince:m?.since??null,
  commitment:{observed7:m?.since!==null&&Number.isFinite(m?.since)&&m.since<=now?Math.min(7,Math.floor((Date.parse(day(now))-Date.parse(day(m.since)))/DAY)+1):0,timezone:'Asia/Manila',goal,days,active7:week.filter(d=>d.questions>0).length,qualified7:week.filter(d=>d.questions>=goal.questions).length,active28:days.filter(d=>d.questions>0).length},
  competence:{assessed:assessed.length,weighted,subjects},
  readiness:{status:met===6?'Foundation targets met':!assessed.length?'Not yet assessed':subjects.some(s=>s.status==='Support needed')?'Subject support needed':assessed.length===6?'Confirm retention':'Evidence incomplete',subjectsMeetingTarget:met,boardReadiness:'Not established',coverage:'Incomplete or unvalidated PRC coverage',target:TARGET,spacingDays:7,windowDays:30,priorities},
  limits:['Activity measures app participation, not motivation or outside study.','New-item means unanswered in this profile, including known prior revisions; it does not establish unfamiliarity with the concept.','Legacy first-attempt outcomes are unknown. Monitoring is local and included in progress backups; cloud score recovery does not restore this journal.','Current bank coverage and independent faculty validation are incomplete. These rules are study targets, not a pass prediction.']};
}
return {DAY,POLICY,TARGET,day,ensure,wasSeen,activity,observe,finishCheck,validate,checkPool,checkCounts,report};
});
