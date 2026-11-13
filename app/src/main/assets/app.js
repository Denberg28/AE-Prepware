'use strict';
const $=s=>document.querySelector(s),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const KEY='ae-prepware-v1',BANKKEY='ae-prepware-custom-bank',VERSION='0.8.0-rc.1';
const shortNames={math:'Mathematics',aero:'Aerodynamics',structures:'Structures & design',construction:'Construction & repair',powerplant:'Power plant',ethics:'Economics, laws & ethics'};
let bank,bundled,state,account=null,tab='home',result=null,ranking=null,storageBlocked=false,busy=false,newRecovery=null;
const stateKey=()=>Accounts.key(account),bankKey=()=>account?'ae-bank-'+account:BANKKEY;
const sourcesSelected=()=>{const ai=$('[data-source=AI]')?.checked,ins=$('[data-source=IN]')?.checked;return ai&&ins?'hybrid':ai?'AI':ins?'IN':'';};
const studyScope=()=>bank.focus?(state.studyScope||'focus'):'full';
const sessionSize=()=>studyScope()==='focus'?20:50;
const poolReady=(subject,mode)=>{const c=AE.sourceCounts(state,bank,subject,studyScope()),n=sessionSize();return mode==='hybrid'?c.AI>=n/2&&c.IN>=n/2:!!mode&&c[mode]>=n;};
async function profileBank(){
 const raw=await BankStore.read(bankKey());if(!raw){if(bundled.distribution==='private-study')await BankStore.write(bankKey(),JSON.stringify(bundled));return structuredClone(bundled);}
 const stored=AE.validateBank(JSON.parse(raw),true,bundled);
 if(bundled.extends===stored.version){AE.validateRefresh(stored,bundled);const progress=localStorage.getItem(stateKey());if(progress)AE.validateState(JSON.parse(progress),bundled);await BankStore.write(bankKey(),JSON.stringify(bundled));return structuredClone(bundled);}
 return stored;
}
const subjectName=id=>id==='mixed'?'Mixed subjects':shortNames[id]||id||'Practice';
function notice(message=''){$('#notice').textContent=message;}
function save(){
 if(storageBlocked)throw Error('Storage needs recovery. Export your data in Settings before continuing.');
 try{localStorage.setItem(stateKey(),JSON.stringify(state));}
 catch{storageBlocked=true;throw Error('Progress could not be saved. Free device storage and export recovery data in Settings.');}
}
function sourceLink(q){const s=bank.sources[q.source];return `<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title)} ↗</a><p class="inline-note">${esc(s.locator)}${q.upload?'<br>'+esc(q.upload.locator):''}</p>`;}
function accountLine(){return `<p class="account-line">${account?`${esc(state.name)} · ${esc(account)}`:'Guest'}</p>`;}
function explanation(q){return `<details class="explanation"><summary>Explanation</summary>${q.review==='source-key-verified'?'<p class="inline-note source-review">Printed key checked · Faculty review pending</p>':''}<p>${esc(q.explanation)}</p>${sourceLink(q)}</details>`;}
function setTab(value){tab=value;result=null;render();$('#content').scrollTo(0,0);}
function render(){
 document.body.classList.toggle('quiz',tab==='quiz');
 const activeTab=['quiz','result','study'].includes(tab)?'home':tab;
 document.querySelectorAll('nav [data-tab]').forEach(x=>{const active=x.dataset.tab===activeTab;x.classList.toggle('active',active);if(active)x.setAttribute('aria-current','page');else x.removeAttribute('aria-current');});
 ({home:renderHome,study:renderHome,quiz:renderQuiz,result:renderResult,progress:renderProgress,ranks:renderRanks,account:renderAccount,settings:renderSettings}[tab]||renderHome)();
}
function renderHome(){
 const sourceMode=state.sourceMode??'AI';
 const size=sessionSize(),sessionInfo=sourceMode==='hybrid'?`Hybrid · ${size/2} AI + ${size/2} IN`:sourceMode?`${size} questions · ${sourceMode}`:'Select a bank';
 $('#app').innerHTML=`<section data-screen="subjects" aria-label="Subjects"><h1 class="sr-only">Subjects</h1><button class="principles card" data-tab="progress"><strong>Commitment · Competence · Readiness</strong><span>View your study progress and subject priorities →</span></button><button class="btn secondary full spaced" data-action="feedback-practice">Bearing · Heading · Throat — 20 questions</button>${bank.focus?`<label for="study-scope">Study set</label><select id="study-scope"><option value="focus" ${studyScope()==='focus'?'selected':''}>PRC foundations · 20 questions</option><option value="full" ${studyScope()==='full'?'selected':''}>Full bank · 50 questions</option></select>`:''}<fieldset class="source-picker"><legend>Test bank</legend><div class="source-options"><label class="source-option ${['AI','hybrid'].includes(sourceMode)?'selected':''}"><input type="checkbox" data-source="AI" aria-label="AI-produced questions" ${['AI','hybrid'].includes(sourceMode)?'checked':''}> AI</label><label class="source-option ${['IN','hybrid'].includes(sourceMode)?'selected':''}"><input type="checkbox" data-source="IN" aria-label="IN instructor-uploaded questions" ${['IN','hybrid'].includes(sourceMode)?'checked':''}> IN</label></div><p class="session-info" role="status">${esc(sessionInfo)}</p></fieldset>${state.session?`<button class="btn full" data-action="resume">Continue · ${state.session.index+1} / ${state.session.ids.length}</button>`:''}<div class="subject-tabs" aria-label="Exam subjects">${bank.subjects.map(s=>{const counts=AE.sourceCounts(state,bank,s.id,studyScope());return `<button class="subject-tab" data-subject="${esc(s.id)}" ${poolReady(s.id,sourceMode)?'':'disabled'}><strong>${esc(subjectName(s.id))}</strong><span class="subject-meta"><small>${counts.AI} AI · ${counts.IN} IN</small><span class="subject-weight" aria-label="PRC subject weight ${s.weight}%">${s.weight}%</span></span></button>`;}).join('')}</div><label for="selection">Selection</label><select id="selection"><option value="random" ${state.selection==='random'?'selected':''}>Random</option><option value="adaptive" ${state.selection==='adaptive'?'selected':''}>Adaptive</option><option value="ai" ${state.selection==='ai'?'selected':''}>AI assisted</option></select></section>`;
}
async function begin(subject){
 if(storageBlocked)throw Error('Recover storage in Settings before answering.');
 if(state.session&&!await ask('Start another session?','Answered questions stay in progress. This replaces the unfinished session.','Start '+sessionSize()+' questions'))return;
 const sourceMode=sourcesSelected();if(!poolReady(subject,sourceMode))throw Error('Choose a pool with '+sessionSize()+' questions, or '+sessionSize()/2+' per source for Hybrid. Full bank has additional material.');state.sourceMode=sourceMode;
 const selection=$('#selection')?.value||state.selection||'random';state.selection=selection;
 let questions,mode='subject';
 if(selection==='ai'&&account&&state.cohort&&state.endpoint){
  const plan=await request('/accounts/plan',{subject,ai:true,sourceMode,scope:studyScope()},true);
  if(plan.bankVersion!==bank.version||!Array.isArray(plan.ids)||plan.ids.length!==sessionSize()||new Set(plan.ids).size!==sessionSize())throw Error('The service returned an incompatible question selection.');
  questions=plan.ids.map(id=>bank.questions.find(q=>q.id===id&&q.subject===subject));
  if(questions.some(q=>!q||q.active===false||state.flags.includes(q.id)||(studyScope()==='focus'&&!Object.hasOwn(bank.focus.questions,q.id)))||['AI','IN'].some(src=>questions.filter(q=>q&&AE.origin(q)===src).length!==(sourceMode==='hybrid'?sessionSize()/2:sourceMode===src?sessionSize():0))){questions=AE.pickSources(state,bank,'adaptive-subject',subject,sourceMode,Math.random,studyScope());mode='adaptive-subject';notice('Used local adaptive selection to respect set-aside questions.');}
  else notice(plan.selection==='ai-assisted'?'AI-assisted topic selection. Questions and keys come from the test bank.':'AI unavailable. Used account-based adaptive selection.');
 }else{
  mode=selection==='random'?'subject':'adaptive-subject';questions=AE.pickSources(state,bank,mode,subject,sourceMode,Math.random,studyScope());
  if(selection==='ai')notice('AI needs a connected account. Used local adaptive selection.');else notice('');
 }
 AE.start(state,questions,mode);save();setTab('quiz');
}
function renderQuiz(){
 const t=state.session;if(!t){setTab('home');return;}
 const q=bank.questions.find(q=>q.id===t.ids[t.index]),chosen=t.answers[t.index],checked=chosen!==null,ok=chosen===q.answer,order=t.orders[t.index],letter='ABCD'[order.indexOf(q.answer)];
 const deferred=['mock','cohort','diagnostic','retention'].includes(t.mode); // Preserve unfinished v0.1 sessions.
 $('#app').innerHTML=`<div class="row quiz-toolbar"><button class="link" data-tab="home">← Save & exit</button><span class="eyebrow">${t.index+1} / ${t.ids.length}</span></div><progress class="bar" max="${t.ids.length}" value="${t.index+(checked?1:0)}"></progress><p class="eyebrow">${esc(subjectName(q.subject))} · <span class="source-badge">${AE.origin(q)}</span></p><h1 class="question">${esc(q.prompt)}</h1>${order.map((original,i)=>`<button class="choice ${checked&&!deferred&&original===q.answer?'correct':checked&&!deferred&&original===chosen&&!ok?'wrong':''}" data-choice="${original}" ${checked?'disabled':''}><span class="letter">${'ABCD'[i]}</span><span>${esc(q.choices[original])}</span></button>`).join('')}${checked?deferred?'<p class="inline-note">Answer saved. Results and explanations appear after submission.</p>':`<div class="feedback ${ok?'':'bad'}" role="status"><strong>${ok?'Correct':'Incorrect'}</strong>${ok?'':`<p>Correct answer: <b>${letter}</b> · ${esc(q.choices[q.answer])}</p>`}</div>${explanation(q)}`:''}${checked?`<button class="btn full spaced" data-action="next">${t.index===t.ids.length-1?'Finish & see score':'Next question →'}</button>`:''}<div class="row spaced"><button class="link" data-action="bookmark">${state.bookmarks.includes(q.id)?'★ Saved':'☆ Save question'}</button><button class="link" data-action="report">Set aside</button></div>`;
}
async function next(){
 const t=state.session;if(!t||t.answers[t.index]===null)return;
 if(t.index<t.ids.length-1){t.index++;save();render();$('#content').scrollTo(0,0);return;}
 if(t.mode==='cohort')await request('/challenges/'+encodeURIComponent(t.challenge)+'/submit',{answers:t.ids.map((id,i)=>({id,choice:t.answers[i]}))},true);
 result=AE.finish(state,bank);save();tab='result';render();$('#content').scrollTo(0,0);
 if(account&&state.endpoint&&state.cohort){try{await syncResults();render();}catch(e){notice('Score saved on this device. '+e.message);}}
}
function reviewItems(h){return (h.ids||[]).map((id,i)=>{const q=bank.questions.find(q=>q.id===id);if(!q)return '';const order=h.orders?.[i]||[0,1,2,3];return `<details class="review-item"><summary>${i+1}. ${h.answers[i]===q.answer?'Correct':'Incorrect'} · ${esc(q.prompt)}</summary><p class="inline-note">Your answer: ${'ABCD'[order.indexOf(h.answers[i])]} · ${esc(q.choices[h.answers[i]])}</p><p>Correct answer: ${'ABCD'[order.indexOf(q.answer)]} · ${esc(q.choices[q.answer])}</p>${explanation(q)}</details>`;}).join('');}
function renderResult(){
 if(!result){setTab('home');return;}
 const current=state.history.find(h=>h.id===result.id)||result;
 $('#app').innerHTML=`${accountLine()}<h1>Session complete</h1><p class="muted">${esc(subjectName(result.subject))}</p><div class="score">${result.correct}<small> / ${result.total}</small></div><p class="center muted">${Math.round(100*result.correct/result.total)}% correct</p><p class="center inline-note">${account?`Saved to ${esc(account)}${current.synced?' · Synced':' on this device'}`:'Saved as guest · Create an account to bind your results'}</p><button class="btn full spaced" data-tab="home">Subjects</button><button class="link full" data-tab="progress">View recorded results</button><h2 class="section">Answer review</h2>${reviewItems(result)}`;
}
function readinessPanel(){
 const r=Readiness.report(state,bank),c=r.commitment,g=c.goal,subjects=r.competence.subjects;
 return `<section aria-label="Board readiness monitoring" data-readiness><div class="card"><h2>Commitment</h2><div class="readiness-number">${c.observed7?c.qualified7:'—'}<small> / ${g.days} study days</small></div><p class="inline-note">${c.observed7} / 7 days observed · ${g.questions}+ distinct answers per study day</p><div class="activity-week" aria-label="Last seven days">${c.days.slice(-7).map(d=>`<div class="activity-day ${d.questions>=g.questions?'met':''}" title="${d.date}: ${d.questions} distinct answers"><span>${d.date.slice(5)}</span><strong>${d.questions}</strong></div>`).join('')}</div><p class="fine">${r.trackingSince===null?'Tracking starts with your next answer. ':''}Recorded participation, not motivation. Outside study is not measured. ${c.active28} active days in the last 28.</p><details><summary>Study goal</summary><label for="goal-days">Days per 7-day period</label><input id="goal-days" type="number" min="1" max="7" value="${g.days}"><label for="goal-questions">Distinct answers per day</label><input id="goal-questions" type="number" min="1" max="50" value="${g.questions}"><button class="btn secondary full spaced" data-action="save-goal">Save study goal</button></details></div><div class="card"><h2>Competence</h2><div class="readiness-number">${r.competence.assessed}<small> / 6 subjects checked</small></div><p class="inline-note">Recent checks reveal answers after submission. Practice repetitions do not count as a new-item baseline.</p>${r.competence.weighted===null?'':`<p><strong>${r.competence.weighted}%</strong> PRC-weighted foundation checks</p>`}</div><div class="card"><h2>Readiness</h2><strong>${esc(r.readiness.status)}</strong><p>${r.readiness.subjectsMeetingTarget} / 6 foundation targets met</p><p class="inline-note">Board readiness is not established. PRC content coverage and independent validation remain incomplete.</p><details><summary>How targets work</summary><p class="inline-note">A subject target needs two completed 20-item checks at 80% or higher, at least 7 days apart, within the last 30 days. These are study targets, not a PRC passing standard or pass probability. Checks spanning over 24 hours, or containing retired/set-aside items, are excluded. New-item checks use the full bank and the AI/IN source choice from Subjects.</p></details></div><h2>Subject priorities</h2><p class="fine">${state.sourceMode?`Check sources: ${esc(state.sourceMode)} · change in Subjects`:'Choose AI or IN in Subjects to enable checks.'}</p>${r.readiness.priorities.slice(0,2).map(p=>`<p class="inline-note"><strong>${esc(subjectName(p.subject))}</strong> · ${esc(p.reason)}<br>${esc(p.action)}</p>`).join('')}<div class="readiness-subjects">${subjects.map(s=>{const fresh=Readiness.checkCounts(state,bank,s.id,'diagnostic',state.sourceMode??'AI'),retention=Readiness.checkCounts(state,bank,s.id,'retention',state.sourceMode??'AI');return `<article class="card readiness-subject"><div class="row"><h3>${esc(subjectName(s.id))}</h3><span class="subject-weight">${s.weight}%</span></div><span class="readiness-status ${s.status==='Support needed'?'support':s.status==='Foundation target met'?'met':'pending'}">${esc(s.status)}</span><p>${s.latest?`Latest check: <strong>${s.latest.correct}/${s.latest.total}</strong>`:'No recent diagnostic evidence'}</p>${s.baseline?`<p class="inline-note">Initial recorded diagnostic: ${s.baseline.correct}/20</p>`:''}<p class="inline-note">First attempts recorded: ${s.first.total?`${s.first.correct}/${s.first.total}`:'not yet available'} · Core explored ${s.core.seen}/${s.core.total}</p>${s.topics.length?`<p class="inline-note">First-attempt gaps: ${s.topics.map(t=>`${esc(t.topic)} (${t.correct}/${t.total} first attempts)`).join('; ')}</p>`:''}<div class="readiness-actions"><button class="btn secondary" data-check="diagnostic" data-check-subject="${s.id}" ${fresh.ready?'':'disabled'}>New-item check</button><button class="btn secondary" data-check="retention" data-check-subject="${s.id}" ${retention.ready?'':'disabled'}>Spaced recheck</button></div><p class="fine">${fresh.AI} AI / ${fresh.IN} IN unseen · ${retention.AI} AI / ${retention.IN} IN spaced items available</p></article>`;}).join('')}</div><details class="card"><summary>Facilitator report</summary><p class="inline-note">Export a summary to share manually. It contains your chosen alias and study measures, with no recovery code, account number, question text or answer keys. You can also opt in to facilitator sharing in Account, then press Sync.</p><label for="report-alias">Report alias</label><input id="report-alias" maxlength="40" value="${esc(state.name)}"><button class="btn secondary full spaced" data-action="export-readiness">Export facilitator report</button></details><p class="fine">Monitoring is stored on this profile and included in progress backups. Use Sync to back up this journal and unfinished sessions online. Legacy first attempts remain unknown.</p></section>`;
}
async function beginCheck(subject,kind){
 if(storageBlocked)throw Error('Recover storage before starting a check.');
 if(state.session&&!await ask('Replace unfinished session?','Recorded answers stay in your activity. This starts a new 20-item check.','Start check'))return;
 AE.startCheck(state,bank,subject,kind,state.sourceMode??'AI');save();setTab('quiz');notice(kind==='diagnostic'?'New-item diagnostic · answers revealed after submission.':'Spaced recheck · answers revealed after submission.');
}
function renderProgress(){
 const summary=AE.summary(state,bank),attempts=summary.reduce((n,s)=>n+s.seen,0),correct=summary.reduce((n,s)=>n+s.correct,0);
 $('#app').innerHTML=`${accountLine()}<h1>Board readiness</h1>${readinessPanel()}<h2>Your results</h2><div class="metrics"><div class="metric"><strong>${state.history.length}</strong><span>saved sessions</span></div><div class="metric"><strong>${attempts?Math.round(correct/attempts*100)+'%':'—'}</strong><span>practice accuracy</span></div><div class="metric"><strong>${summary.reduce((n,s)=>n+s.covered,0)}</strong><span>questions explored</span></div></div>${state.pending?.length?`<p class="inline-note">${state.pending.length} session(s) pending sync. Connect your account to back them up online.</p>`:''}<h2>Recent sessions</h2>${state.history.length?state.history.map((h,i)=>`<button class="activity" data-result="${i}"><span>${esc(subjectName(h.subject))}<small>${esc(new Date(h.date).toLocaleString('en-PH',{dateStyle:'medium',timeStyle:'short'}))}${h.synced?' · Synced':''}</small></span><strong>${h.correct}/${h.total}</strong></button>`).join(''):'<p class="muted">Complete a session to record your score.</p>'}<details class="section"><summary>Subject progress</summary>${summary.map(s=>`<div class="subject-row"><strong>${esc(subjectName(s.id))}</strong><p>${s.accuracy===null?'No answers yet':s.accuracy+'% accuracy'} · ${s.covered}/${s.total} explored</p><progress class="bar" max="${s.total||1}" value="${s.covered}"></progress></div>`).join('')}</details><p class="fine">Latest 200 sessions shown. Accuracy includes repeated answers and unfinished sessions. Practice results do not predict board performance.</p>`;
}
function renderRanks(){
 $('#app').innerHTML=`${accountLine()}<h1>Ranking</h1><p class="muted">Keep learning with your cohort.</p>${state.endpoint?`<button class="btn secondary full spaced" data-action="refresh-ranks">Refresh ranking</button>${ranking?ranking.entries.map((x,i)=>`<div class="rank"><span>${i+1}</span><div><strong>${esc(x.name)}</strong><small>Account ••••${esc(x.accountSuffix)} · ${x.correct}/${x.attempts} correct</small></div><strong>${x.points} pt</strong></div>`).join('')||'<p class="inline-note">No synced results yet.</p>':'<p class="inline-note">Refresh to load account standings.</p>'}`:'<div class="card"><p>Connect an instructor-hosted HTTPS service in Account to use shared ranking.</p><button class="btn secondary full" data-tab="account">Open account</button></div>'}<p class="fine">One point per distinct correct bank question per server day. Results are graded by the server. Offline answer keys are visible, so rankings are practice-only and are not proctored exam standings.</p>`;
}
function renderAccount(){
 if(newRecovery){$('#app').innerHTML=`<h1>Save your account</h1><p class="muted">Use this number and recovery code to sign in again.</p><label>Account number</label><p class="credential">${esc(newRecovery.number)}</p><label class="spaced">Recovery code</label><p class="credential">${esc(newRecovery.recovery.match(/.{1,8}/g).join(' '))}</p><p class="inline-note">Keep the code private. Your account number alone cannot sign in. This code cannot be retrieved from the app later.</p><button class="btn full spaced" data-action="export-account">Save account recovery file</button><button class="btn secondary full spaced" data-action="recovery-saved">I have saved my code</button>`;return;}
 $('#app').innerHTML=account?`${accountLine()}<h1>Your account</h1><div class="card"><strong>${esc(state.name)}</strong><p class="credential">${esc(account)}</p><p class="inline-note">${state.history.length} saved session(s) · ${state.pending?.length||0} waiting to sync</p></div><h2 class="section">Connect & sync</h2><p class="inline-note">Use the HTTPS API URL provided by your instructor. The same account number and recovery code restore synced scores on another device.</p><label for="account-url">HTTPS service URL</label><input id="account-url" type="url" placeholder="https://your-cohort.example/" value="${esc(state.endpoint)}">${state.cohort?'<button class="btn full" data-action="sync">Sync saved results</button><button class="btn secondary full spaced" data-action="sync-all">Sync all data</button><button class="link full" data-action="restore-online">Restore online backup</button>':''}<label class="sharing-option"><input id="rank-opt-in" type="checkbox" ${state.rankOptIn?'checked':''}> Join practice ranking with my display name</label><label class="sharing-option"><input id="share-readiness" type="checkbox" ${state.shareReadiness?'checked':''}> Share readiness summary with facilitators on next sync</label><p class="fine">Off by default. Personal backups stay private. Sharing changes take effect after a successful full sync.</p>${state.lastSync?`<p class="fine">Last sync: ${esc(new Date(state.lastSync.at).toLocaleString())}<br>${esc(Object.entries(state.lastSync.steps).map(([k,v])=>k+': '+v).join(' · '))}</p>`:''}<details><summary>Backup upload recovery</summary><button class="link full" data-action="clear-upload">Reset queued backup upload</button></details><label for="enrollment-code">Instructor enrollment code (if required)</label><input id="enrollment-code" type="password" autocomplete="off"><label class="spaced" for="connect-code">Recovery code</label><input id="connect-code" type="password" autocomplete="off" placeholder="Required to connect or renew sign-in"><button class="btn secondary full" data-action="connect">Connect account</button><button class="link full spaced" data-action="signout">Sign out on this device</button>${state.cohort?'<details class="section"><summary>Delete online account</summary><p class="inline-note">Permanently removes online scores, progress and ranking. Local scores remain until you remove app data.</p><button class="btn danger full" data-action="delete-account">Delete online account</button></details>':''}`:`<h1>Your account</h1><p class="muted">Keep results, progress and recommendations together.</p><div class="card"><h2>Create an account</h2><p class="inline-note">Works offline. Current guest results will be linked to the new account on this device.</p><label for="account-name">Display name</label><input id="account-name" maxlength="30" placeholder="Your name or nickname"><button class="btn full" data-action="create-account">Create account</button></div><details class="card"><summary>Sign in to an existing account</summary><label class="spaced" for="login-number">Account number</label><input id="login-number" placeholder="AE-0000000000000000" autocomplete="username"><label for="login-code">Recovery code</label><input id="login-code" type="password" autocomplete="off"><label for="login-url">HTTPS service URL (for another device)</label><input id="login-url" type="url" placeholder="Optional for an account on this device"><button class="btn secondary full" data-action="login">Sign in</button></details><p class="fine">Offline accounts stay on this phone until you export a backup or sync to a hosted service. Keep both the recovery file and a progress backup.</p>`;
}
function renderSettings(){
 $('#app').innerHTML=`<h1>Settings</h1><div class="card"><h2>Exam weights</h2><div class="weight-list">${bank.subjects.map(s=>`<div><span>${esc(subjectName(s.id))}</span><strong>${s.weight}%</strong></div>`).join('')}</div><a class="inline-note" href="${esc(bank.blueprintSource)}" target="_blank" rel="noopener">PRC examination program ↗</a></div><div class="card"><h2>Backup & recovery</h2><p class="inline-note">Export before uninstalling or changing phones. Progress backups exclude sign-in tokens and recovery codes; keep your separate account recovery file.</p><button class="btn secondary full" data-action="export">Export progress backup</button><button class="btn secondary full spaced" data-action="import">Import backup / approved bank</button>${storageBlocked?'<button class="btn danger full spaced" data-action="recover">Recover unreadable storage</button>':''}</div><div class="card"><h2>Question bank</h2>${bank.focus?`<p>${Object.keys(bank.focus.questions).length} core questions</p><details><summary>Coverage gaps</summary><p class="inline-note">Foundation practice does not cover the complete PRC table of specifications.</p>${bank.focus.gaps.map(g=>`<p class="inline-note"><strong>${esc(subjectName(g.subject))}</strong><br>${esc(g.topics)}</p>`).join('')}<a href="${esc(bank.focus.source)}" target="_blank" rel="noopener">PRC table of specifications ↗</a></details>`:''}<p class="inline-note">${esc(bank.notice)}</p><p>${state.flags.length} questions set aside</p><button class="btn secondary full" data-action="restore-flags">Restore set-aside questions</button><button class="link full" data-action="export-reports">Export question report</button><button class="btn secondary full spaced" data-action="export-bank">Export question bank</button><p class="inline-note">Keep this bank export with your progress backup, especially before reinstalling or changing phones.</p></div><p class="fine">AE Prepware ${VERSION} · Android 8+<br>Independent study software. No PRC affiliation or pass guarantee. AI can assist selection; it cannot change scored answers. Subjects follow the <a href="${esc(bank.blueprintSource)}" target="_blank" rel="noopener">PRC blueprint</a>.</p>`;
}
function ask(title,body,confirm='Continue'){return new Promise(resolve=>{const d=$('#modal');d.innerHTML=`<h2>${esc(title)}</h2><p>${esc(body)}</p><div class="row spaced"><button class="btn secondary" id="cancel">Cancel</button><button class="btn" id="confirm">${esc(confirm)}</button></div>`;const done=v=>{d.close();d.oncancel=null;resolve(v);};$('#cancel').onclick=()=>done(false);$('#confirm').onclick=()=>done(true);d.oncancel=e=>{e.preventDefault();done(false);};d.showModal();});}
function download(text,name){if(window.AndroidFiles){AndroidFiles.exportBackup(text,name);return;}const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type:'application/json'}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);}
async function apiAt(url,path,data,token){
 if(!AE.validEndpoint(url))throw Error('Enter a valid HTTPS root service URL.');
 const abort=new AbortController(),timeout=setTimeout(()=>abort.abort(),20000);
 try{const r=await fetch(url.replace(/\/$/,'')+path,{method:data?'POST':'GET',headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},body:data?JSON.stringify(data):undefined,signal:abort.signal,redirect:'error'});if(!r.ok){const d=await r.json().catch(()=>({}));throw Error(typeof d.detail==='string'?d.detail:'Service returned '+r.status);}return await r.json();}
 catch(e){if(e instanceof SyntaxError)throw Error('This URL does not expose the AE sync service. Use the service URL configured with Streamlit.');if(e.name==='AbortError')throw Error('Service timed out. Saved scores remain on this device; retry sync later.');if(e instanceof TypeError)throw Error('Service unavailable. Check the URL, HTTPS and connection.');throw e;}finally{clearTimeout(timeout);}
}
const request=(path,data,auth=false)=>apiAt(state.endpoint,path,data,auth?state.cohort?.token:null);
async function syncResults(){
 if(!account||!state.cohort)throw Error('Connect your account before syncing.');
 for(const h of [...(state.pending||[])]){
  const r=await request('/accounts/results',{id:h.id,subject:h.subject,bankVersion:h.bankVersion,answers:h.ids.map((id,i)=>({id,choice:h.answers[i]}))},true);
  if(r.id!==h.id||r.accountNumber!==account||r.total!==h.total||r.correct!==h.correct)throw Error('Service score mismatch. Pending result preserved for review.');
  state.pending=state.pending.filter(x=>x.id!==h.id);const item=state.history.find(x=>x.id===h.id);if(item)item.synced=true;save();
 }
 notice('All saved results synced.');
}
const uploadKey=()=> 'ae-sync-upload-'+account;
async function uploadQueuedBackup(){
 const raw=await BankStore.read(uploadKey());if(!raw)return;
 const body=JSON.parse(raw);if(body.state.accountNumber!==account)throw Error('Queued backup belongs to another profile.');
 const response=await request('/accounts/snapshot',body,true);state.cloudRevision=CloudSync.acknowledgement(body,response);save();await BankStore.remove(uploadKey());
}
async function syncAll(){
 if(!account||!state.cohort||!state.endpoint){setTab('account');notice('Connect your account to the online service before syncing. Offline data is safe.');return;}
 const button=$('#sync-toggle'),steps={results:'pending',backup:'pending',ranking:'pending',bank:'pending'};button.disabled=true;button.classList.add('syncing');
 try{
  notice('Syncing saved results…');await syncResults();steps.results='done';
  const health=await request('/health');if(!health.capabilities?.includes('snapshot-v1'))throw Error('Results synced. Update the online service to enable full profile and database sync.');
  await request('/accounts/preferences',{rankOptIn:!!state.rankOptIn},true);
  notice('Syncing private offline backup…');await uploadQueuedBackup();Readiness.ensure(state);AE.validateState(state,bank);
  const body={operation:AE.uid(),expectedRevision:state.cloudRevision||0,bankVersion:bank.version,state:CloudSync.projection(state),share:!!state.shareReadiness,report:state.shareReadiness?Readiness.report(state,bank):null};
  if(JSON.stringify(body).length>950000)throw Error('Profile is too large for online backup. Export a progress file; offline data is preserved.');
  await BankStore.write(uploadKey(),JSON.stringify(body));await uploadQueuedBackup();steps.backup='done';
  notice('Refreshing ranking…');ranking=await request('/accounts/leaderboard');if(!Array.isArray(ranking.entries))throw Error('Invalid ranking response');steps.ranking='done';
  notice('Checking question database…');const next=await request('/accounts/bank',null,true);
  if(next.version===bank.version){if(!CloudSync.sameBank(next,bank))throw Error('The server reused a bank version with different data. Update held for review.');}
  else {AE.validateRefresh(bank,next,bundled);AE.validateState(state,next);await BankStore.write(bankKey(),JSON.stringify(next));bank=next;}
  steps.bank='done';state.lastSync={at:Date.now(),steps,complete:true};save();render();notice('Synced results, private backup, ranking and question database.');
 }catch(e){state.lastSync={at:Date.now(),steps,complete:false};try{save();}catch{}notice(e.message+' Offline data and queued uploads are preserved.');}
 finally{button.disabled=false;button.classList.remove('syncing');}
}
async function restoreOnline(){
 if(state.pending?.length)throw Error('Sync saved results before restoring a cloud backup.');
 const remote=await request('/accounts/snapshot',null,true);if(!remote.state)throw Error('No online profile backup exists yet.');
 const profile=await request('/accounts/me',null,true);const next={...CloudSync.restore(remote,profile,account),endpoint:state.endpoint,cohort:state.cohort};AE.validateState(next,bank);
 if(!await ask('Restore online backup?',`${next.history.length} saved sessions; backup dated ${new Date(remote.updatedAt).toLocaleString()}. This replaces this profile’s local progress, goals and unfinished session. Export a local backup first.`, 'Restore backup'))return;
 state=next;save();await BankStore.remove(uploadKey());setTab('progress');notice('Online profile restored, including its monitoring journal.');
}
function validateRemote(r,number){if(r.number!==number||r.bankVersion!==bank.version||typeof r.token!=='string'||!r.stats||!Array.isArray(r.history))throw Error('The service returned an incompatible account or bank.');}
async function loadProfile(number){account=number;bank=await profileBank();state=AE.validateState(JSON.parse(localStorage.getItem(stateKey())),bank);if(state.accountNumber!==number)throw Error('Account profile mismatch.');state.pending=state.pending||[];state.selection=state.selection||'random';ranking=null;storageBlocked=false;}
async function doAction(action){
 if(action==='sync-all'){await syncAll();return;}
 if(action==='feedback-practice'){if(storageBlocked)throw Error('Recover storage before starting.');if(state.session&&!await ask('Start feedback practice?','This replaces the unfinished session. Recorded answers stay saved.','Start practice'))return;const pool=bank.questions.filter(q=>q.id.startsWith('FB-')&&q.active!==false&&!state.flags.includes(q.id));if(pool.length<20)throw Error('This bank needs the 20-item feedback pack. Sync its matching database or use the updated app.');AE.start(state,AE.shuffle(pool).slice(0,20),'subject');save();setTab('quiz');notice('Original AI exercises · source and arithmetic self-checked; independent faculty review pending.');return;}
 if(action==='restore-online'){await restoreOnline();return;}
 if(action==='clear-upload'){if(await ask('Reset queued backup upload?','Offline progress stays on this device. A newer online backup may still require review.','Reset upload')){await BankStore.remove(uploadKey());notice('Queued backup upload reset. Offline progress preserved.');}return;}
 if(action==='resume')return setTab('quiz');
 if(action==='next')return next();
 if(action==='create-account'){
  if(storageBlocked)throw Error('Recover unreadable storage before creating an account.');
  const existingBank=await BankStore.read(bankKey()),created=await Accounts.create(localStorage,state,$('#account-name').value);
  account=created.number;state=created.state;newRecovery=created;setTab('account');if(existingBank)await BankStore.write(bankKey(),existingBank);save();localStorage.removeItem(KEY);newRecovery=created;setTab('account');notice('Account created. Save your recovery code.');return;
 }
 if(action==='export-account'){download(JSON.stringify({type:'ae-account-recovery',number:newRecovery.number,recovery:newRecovery.recovery},null,2),'AE-account-recovery.json');return;}
 if(action==='recovery-saved'){newRecovery=null;notice('');return setTab('home');}
 if(action==='login'){
  const number=$('#login-number').value.trim().toUpperCase(),recovery=Accounts.normalize($('#login-code').value),url=$('#login-url').value.trim();
  if(!/^AE-\d{16}$/.test(number)||!/^[a-f0-9]{64}$/.test(recovery))throw Error('Enter your account number and complete recovery code.');
  if(Accounts.index(localStorage).some(p=>p.number===number)){
   const existing=await Accounts.login(localStorage,number,recovery);
   const chosenBank=await BankStore.read('ae-bank-'+number);AE.validateState(existing,chosenBank?AE.validateBank(JSON.parse(chosenBank),true,bundled):bundled);
   localStorage.setItem(Accounts.ACTIVE,number);await loadProfile(number);
  }else{
   if(!url)throw Error('Enter the HTTPS service URL to recover an account from another device.');
   const r=await apiAt(url,'/accounts/login',{number,recovery});validateRemote(r,number);
   let next=AE.fresh();next.accountNumber=number;next.name=r.name;next.rankOptIn=!!r.rankOptIn;next.stats=r.stats;next.history=r.history;if(r.supportsSnapshot){const backup=await apiAt(url,'/accounts/snapshot',null,r.token);if(backup.state)next=CloudSync.restore(backup,r,number);}next.endpoint=url;next.cohort={id:number,token:r.token};next.pending=[];AE.validateState(next,bank);
   const customBank=await BankStore.read(bankKey());await Accounts.remember(localStorage,number,r.name,recovery,next);if(customBank)await BankStore.write('ae-bank-'+number,customBank);await loadProfile(number);
  }
  newRecovery=null;setTab('home');notice('Signed in.');return;
 }
 if(action==='connect'){
  const url=$('#account-url').value.trim(),recovery=Accounts.normalize($('#connect-code').value);
  await Accounts.login(localStorage,account,recovery);
  const health=await apiAt(url,'/health');if(health.bankVersion!==bank.version)throw Error('Question bank versions differ. Use the matching service.');
  const r=await apiAt(url,'/accounts/register',{number:account,name:state.name,recovery,rankOptIn:!!state.rankOptIn,enrollment:$('#enrollment-code')?.value||''});validateRemote(r,account);
  state.endpoint=url;state.cohort={id:account,token:r.token};save();await syncResults();render();return;
 }
 if(action==='sync'){
  const url=$('#account-url').value.trim();if(url.replace(/\/$/,'')!==state.endpoint.replace(/\/$/,''))throw Error('Use Connect account with your recovery code to change the service URL.');
  await syncResults();render();return;
 }
 if(action==='signout'&&await ask('Sign out?','Save your recovery code and progress backup first. Local account data stays on this device.','Sign out')){
  if(state.cohort&&state.endpoint){try{await request('/accounts/logout',{},true);}catch{ /* Offline signout still clears this device token. */ }}
  state.cohort=null;save();localStorage.removeItem(Accounts.ACTIVE);account=null;bank=await profileBank();const raw=localStorage.getItem(KEY);state=raw?AE.validateState(JSON.parse(raw),bank):AE.fresh();newRecovery=null;ranking=null;setTab('account');notice('Signed out.');return;
 }
 if(action==='delete-account'&&await ask('Permanently delete online account?','All online results, progress and ranking for this account will be deleted. Local results remain.','Delete online')){await request('/accounts/delete',{},true);state.cohort=null;state.history.forEach(h=>h.synced=false);save();render();notice('Online account deleted. Local results remain; they are not automatically re-uploaded.');return;}
 if(action==='refresh-ranks'){ranking=await request('/accounts/leaderboard');if(!Array.isArray(ranking.entries))throw Error('Invalid ranking response.');render();notice('Ranking updated.');return;}
 if(action==='bookmark'){const id=state.session.ids[state.session.index];state.bookmarks=state.bookmarks.includes(id)?state.bookmarks.filter(x=>x!==id):[...state.bookmarks,id];save();render();}
 if(action==='report'){const id=state.session.ids[state.session.index];if(await ask('Set aside this question?','It stays in this session and is excluded from future practice. Export a question report in Settings for your instructor.','Set aside')){if(!state.flags.includes(id))state.flags.push(id);save();notice('Question set aside for future sessions.');}}
 if(action==='restore-flags'&&await ask('Restore set-aside questions?','They become available in future sessions.')){state.flags=[];save();render();}
 if(action==='export'){
  if(storageBlocked){download(JSON.stringify({type:'ae-recovery-raw',account,progress:localStorage.getItem(stateKey()),bank:await BankStore.read(bankKey())},null,2),'AE-recovery-raw.json');return;}
  const copy=structuredClone(state);copy.cohort=null;download(JSON.stringify({type:'ae-progress',schema:1,bankVersion:bank.version,state:copy,exportedAt:new Date().toISOString()},null,2),'AE-Prepware-backup.json');return;
 }
 if(action==='save-goal'){const days=Number($('#goal-days').value),questions=Number($('#goal-questions').value);if(!Number.isInteger(days)||days<1||days>7||!Number.isInteger(questions)||questions<1||questions>50)throw Error('Choose 1–7 days and 1–50 answers per day.');Readiness.ensure(state).goal={days,questions};save();render();notice('Study goal saved.');return;}
 if(action==='export-readiness'){const alias=$('#report-alias').value.trim();if(!alias||alias.length>40)throw Error('Choose a report alias of 1–40 characters.');if(!await ask('Export facilitator summary?','Your chosen alias and study measures will be included. You decide who receives the downloaded report.','Export report'))return;Readiness.ensure(state);save();download(JSON.stringify(Readiness.report(state,bank,Date.now(),alias),null,2),'AE-Board-Readiness.json');notice('Report exported. Share it only with your intended facilitator.');return;}
 if(action==='export-bank'){download(JSON.stringify(bank),bank.distribution==='private-study'?'AE-IN-private-bank.json':'AE-question-bank.json');return;}
 if(action==='export-reports'){download(JSON.stringify({type:'ae-question-report',bankVersion:bank.version,questions:state.flags.map(id=>({id,prompt:bank.questions.find(q=>q.id===id)?.prompt,reason:'Learner requested review'}))},null,2),'AE-question-report.json');return;}
 if(action==='import'){if(window.AndroidFiles)AndroidFiles.importFile();else $('#import').click();}
 if(action==='recover'&&await ask('Recover current profile?','Export recovery data first. This resets only the current profile’s unreadable progress and imported bank.','Start fresh')){await BankStore.remove(bankKey());bank=structuredClone(bundled);if(bundled.distribution==='private-study')await BankStore.write(bankKey(),JSON.stringify(bundled));state=AE.fresh();state.accountNumber=account;state.name=Accounts.index(localStorage).find(p=>p.number===account)?.name||'Cadet';storageBlocked=false;save();render();notice('Current profile reset. Import its valid backup to restore progress.');}
}
window.receiveImport=async function(text){try{
 if(busy)throw Error('Finish the current action before importing.');
 if(text.length>8000000)throw Error('File exceeds 8 MB.');const data=JSON.parse(text);
 if(data.type==='ae-account-recovery'){if(!/^AE-\d{16}$/.test(data.number)||!/^[a-f0-9]{64}$/.test(data.recovery))throw Error('Invalid account recovery file.');setTab('account');if(!account){$('details.card').open=true;$('#login-number').value=data.number;$('#login-code').value=data.recovery;notice('Account recovery loaded. Sign in to continue.');}else if(data.number===account){$('#connect-code').value=data.recovery;notice('Recovery code loaded for this account.');}else throw Error('Sign out before recovering a different account.');return;}
 if(data.type==='ae-progress'){
  const legacy=data.bankVersion==='2026.11-foundations.1'&&bank.version==='2026.11-foundations.2';
  if(data.bankVersion!==bank.version&&data.bankVersion!==bank.extends&&!legacy)throw Error('Backup bank version differs. Import the matching approved bank first.');
  AE.validateState(data.state,bank);if((data.state.accountNumber||null)!==account)throw Error('Sign in to the matching account before importing this backup.');
  if(!await ask('Replace current profile progress?','Export your current backup first. This changes only the signed-in profile.','Replace progress'))return;
  state=data.state;state.pending=state.pending||[];state.selection=state.selection||'random';state.cohort=null;storageBlocked=false;save();setTab('home');notice('Backup restored.');
 }else{
  if(data.version===bank.version)throw Error('Use a new bank version for a question bank change.');
  if(data.extends===bank.version){
   AE.validateRefresh(bank,data);AE.validateState(state,data);
   if(!await ask('Refresh question bank?',(data.distribution==='private-study'?'Private guide keys were checked against the PDFs; faculty review is pending. ':'')+'Updates apply to future sessions. Saved results and the current session keep their original questions.','Refresh bank'))return;
   await BankStore.write(bankKey(),JSON.stringify(data));bank=data;render();notice('Question bank refreshed. Your progress and queued results are preserved.');return;
  }
  AE.validateBank(data,true,bundled);if(state.pending?.length)throw Error('Sync pending results before changing the question bank. Export a backup if the service is unavailable.');
  if(!await ask('Replace current profile bank?',(data.distribution==='private-study'?'Private study guide keys match the source; faculty review is pending. ':'New and revised questions must be faculty approved. ')+'This resets this profile’s progress. Export a backup first.','Use approved bank'))return;
  const next=AE.fresh();next.name=state.name;next.accountNumber=account;await BankStore.write(bankKey(),JSON.stringify(data));bank=data;state=next;storageBlocked=false;save();setTab('home');notice('Approved question bank imported for this profile.');
 }
 }catch(e){notice('Import stopped: '+e.message);}};
window.handleBack=()=>{if($('#modal').open){$('#cancel').click();return;}setTab('home');};
document.addEventListener('change',e=>{if(e.target.dataset.source){try{state.sourceMode=sourcesSelected();save();render();}catch(err){notice(err.message);}return;}if(e.target.id==='rank-opt-in'){try{state.rankOptIn=e.target.checked;save();notice('Ranking preference saved. Apply it with Sync.');}catch(err){notice(err.message);}return;}if(e.target.id==='share-readiness'){try{state.shareReadiness=e.target.checked;save();notice('Sharing preference saved. Apply it with a successful full sync.');}catch(err){notice(err.message);}return;}if(e.target.id==='study-scope'){try{state.studyScope=e.target.value;save();render();}catch(err){notice(err.message);}return;}if(e.target.id==='selection'){try{state.selection=e.target.value;save();}catch(err){notice(err.message);}}});
document.addEventListener('click',async e=>{
 const el=e.target.closest('[data-action],[data-tab],[data-choice],[data-subject],[data-result],[data-check]');if(!el||busy||el.disabled)return;
 try{busy=true;el.setAttribute('aria-busy','true');
  if(el.dataset.tab){setTab(el.dataset.tab);return;}
  if(el.dataset.check){await beginCheck(el.dataset.checkSubject,el.dataset.check);return;}
  if(el.dataset.subject){await begin(el.dataset.subject);return;}
  if(el.dataset.result!==undefined){result=state.history[Number(el.dataset.result)];tab='result';render();$('#content').scrollTo(0,0);return;}
  if(el.dataset.choice!==undefined){if(storageBlocked)throw Error('Recover storage before answering.');AE.answer(state,bank,Number(el.dataset.choice));save();render();$('.feedback')?.scrollIntoView({block:'nearest'});return;}
  await doAction(el.dataset.action);
 }catch(err){notice(err.message);}finally{busy=false;el.removeAttribute('aria-busy');}
});
$('#import').addEventListener('change',async e=>{const f=e.target.files[0];if(f){if(f.size>8000000)notice('File exceeds 8 MB.');else await window.receiveImport(await f.text());}e.target.value='';});
(async()=>{try{
 const response=await fetch('bank.json');if(!response.ok)throw Error('Bundled bank is unavailable.');bundled=AE.validateBank(await response.json());bank=structuredClone(bundled);state=AE.fresh();
 try{account=Accounts.active(localStorage);}catch{storageBlocked=true;notice('Account directory could not be read. Existing profile records are preserved.');}
 try{bank=await profileBank();}catch{storageBlocked=true;notice('Imported bank could not be read. Export recovery data in Settings before recovery.');}
 try{const raw=localStorage.getItem(stateKey());if(raw)state=AE.validateState(JSON.parse(raw),bank);if((state.accountNumber||null)!==account)throw Error('Profile mismatch');state.pending=state.pending||[];state.selection=state.selection||'random';}catch{storageBlocked=true;state=AE.fresh();state.accountNumber=account;notice('Saved progress could not be read. It has been preserved. Open Settings to export the raw record or recover from a backup.');}
 render();
 }catch(e){$('#app').innerHTML=`<h1>Could not open Prepware</h1><p>${esc(e.message)}</p><p>Your stored data has not been erased.</p>`;}})();
