'use strict';
const $=s=>document.querySelector(s),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const KEY='ae-prepware-v1',BANKKEY='ae-prepware-custom-bank',VERSION='0.5.0-rc.1';
const shortNames={math:'Mathematics',aero:'Aerodynamics',structures:'Structures & design',construction:'Construction & repair',powerplant:'Power plant',ethics:'Economics, laws & ethics'};
let bank,bundled,state,account=null,tab='home',result=null,ranking=null,storageBlocked=false,busy=false,newRecovery=null;
const stateKey=()=>Accounts.key(account),bankKey=()=>account?'ae-bank-'+account:BANKKEY;
const sourcesSelected=()=>{const ai=$('[data-source=AI]')?.checked,ins=$('[data-source=IN]')?.checked;return ai&&ins?'hybrid':ai?'AI':ins?'IN':'';};
const poolReady=(subject,mode)=>{const c=AE.sourceCounts(state,bank,subject);return mode==='hybrid'?c.AI>=25&&c.IN>=25:!!mode&&c[mode]>=50;};
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
 const sessionInfo=sourceMode==='hybrid'?'Hybrid · 25 AI + 25 IN':sourceMode?`50 questions · ${sourceMode}`:'Select a bank';
 $('#app').innerHTML=`<section data-screen="subjects" aria-label="Subjects"><h1 class="sr-only">Subjects</h1><fieldset class="source-picker"><legend>Test bank</legend><div class="source-options"><label class="source-option ${['AI','hybrid'].includes(sourceMode)?'selected':''}"><input type="checkbox" data-source="AI" aria-label="AI-produced questions" ${['AI','hybrid'].includes(sourceMode)?'checked':''}> AI</label><label class="source-option ${['IN','hybrid'].includes(sourceMode)?'selected':''}"><input type="checkbox" data-source="IN" aria-label="IN instructor-uploaded questions" ${['IN','hybrid'].includes(sourceMode)?'checked':''}> IN</label></div><p class="session-info" role="status">${esc(sessionInfo)}</p></fieldset>${state.session?`<button class="btn full" data-action="resume">Continue · ${state.session.index+1} / ${state.session.ids.length}</button>`:''}<div class="subject-tabs" aria-label="Exam subjects">${bank.subjects.map(s=>{const counts=AE.sourceCounts(state,bank,s.id);return `<button class="subject-tab" data-subject="${esc(s.id)}" ${poolReady(s.id,sourceMode)?'':'disabled'}><strong>${esc(subjectName(s.id))}</strong><span class="subject-meta"><small>${counts.AI} AI · ${counts.IN} IN</small><span class="subject-weight" aria-label="PRC subject weight ${s.weight}%">${s.weight}%</span></span></button>`;}).join('')}</div><label for="selection">Selection</label><select id="selection"><option value="random" ${state.selection==='random'?'selected':''}>Random</option><option value="adaptive" ${state.selection==='adaptive'?'selected':''}>Adaptive</option><option value="ai" ${state.selection==='ai'?'selected':''}>AI assisted</option></select></section>`;
}
async function begin(subject){
 if(storageBlocked)throw Error('Recover storage in Settings before answering.');
 if(state.session&&!await ask('Start another session?','Answered questions stay in progress. This replaces the unfinished session.','Start 50 questions'))return;
 const sourceMode=sourcesSelected();if(!poolReady(subject,sourceMode))throw Error('Choose an available AI/IN pool: 50 from one source or 25 of each.');state.sourceMode=sourceMode;
 const selection=$('#selection')?.value||state.selection||'random';state.selection=selection;
 let questions,mode='subject';
 if(selection==='ai'&&account&&state.cohort&&state.endpoint){
  const plan=await request('/accounts/plan',{subject,ai:true,sourceMode},true);
  if(plan.bankVersion!==bank.version||!Array.isArray(plan.ids)||plan.ids.length!==50||new Set(plan.ids).size!==50)throw Error('The service returned an incompatible question selection.');
  questions=plan.ids.map(id=>bank.questions.find(q=>q.id===id&&q.subject===subject));
  if(questions.some(q=>!q||q.active===false||state.flags.includes(q.id))||['AI','IN'].some(src=>questions.filter(q=>q&&AE.origin(q)===src).length!==(sourceMode==='hybrid'?25:sourceMode===src?50:0))){questions=AE.pickSources(state,bank,'adaptive-subject',subject,sourceMode);mode='adaptive-subject';notice('Used local adaptive selection to respect set-aside questions.');}
  else notice(plan.selection==='ai-assisted'?'AI-assisted topic selection. Questions and keys come from the test bank.':'AI unavailable. Used account-based adaptive selection.');
 }else{
  mode=selection==='random'?'subject':'adaptive-subject';questions=AE.pickSources(state,bank,mode,subject,sourceMode);
  if(selection==='ai')notice('AI needs a connected account. Used local adaptive selection.');else notice('');
 }
 AE.start(state,questions,mode);save();setTab('quiz');
}
function renderQuiz(){
 const t=state.session;if(!t){setTab('home');return;}
 const q=bank.questions.find(q=>q.id===t.ids[t.index]),chosen=t.answers[t.index],checked=chosen!==null,ok=chosen===q.answer,order=t.orders[t.index],letter='ABCD'[order.indexOf(q.answer)];
 const deferred=['mock','cohort'].includes(t.mode); // Preserve unfinished v0.1 sessions.
 $('#app').innerHTML=`<div class="row quiz-toolbar"><button class="link" data-tab="home">← Save & exit</button><span class="eyebrow">${t.index+1} / ${t.ids.length}</span></div><progress class="bar" max="${t.ids.length}" value="${t.index+(checked?1:0)}"></progress><p class="eyebrow">${esc(subjectName(q.subject))} · <span class="source-badge">${AE.origin(q)}</span></p><h1 class="question">${esc(q.prompt)}</h1>${order.map((original,i)=>`<button class="choice ${checked&&!deferred&&original===q.answer?'correct':checked&&!deferred&&original===chosen&&!ok?'wrong':''}" data-choice="${original}" ${checked?'disabled':''}><span class="letter">${'ABCD'[i]}</span><span>${esc(q.choices[original])}</span></button>`).join('')}${checked?deferred?'<p class="inline-note">Answer saved. Review appears after submission for this older session.</p>':`<div class="feedback ${ok?'':'bad'}" role="status"><strong>${ok?'Correct':'Incorrect'}</strong>${ok?'':`<p>Correct answer: <b>${letter}</b> · ${esc(q.choices[q.answer])}</p>`}</div>${explanation(q)}`:''}${checked?`<button class="btn full spaced" data-action="next">${t.index===t.ids.length-1?'Finish & see score':'Next question →'}</button>`:''}<div class="row spaced"><button class="link" data-action="bookmark">${state.bookmarks.includes(q.id)?'★ Saved':'☆ Save question'}</button><button class="link" data-action="report">Set aside</button></div>`;
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
function renderProgress(){
 const summary=AE.summary(state,bank),attempts=summary.reduce((n,s)=>n+s.seen,0),correct=summary.reduce((n,s)=>n+s.correct,0);
 $('#app').innerHTML=`${accountLine()}<h1>Your results</h1><div class="metrics"><div class="metric"><strong>${state.history.length}</strong><span>saved sessions</span></div><div class="metric"><strong>${attempts?Math.round(correct/attempts*100)+'%':'—'}</strong><span>practice accuracy</span></div><div class="metric"><strong>${summary.reduce((n,s)=>n+s.covered,0)}</strong><span>questions explored</span></div></div>${state.pending?.length?`<p class="inline-note">${state.pending.length} session(s) pending sync. Connect your account to back them up online.</p>`:''}<h2>Recent sessions</h2>${state.history.length?state.history.map((h,i)=>`<button class="activity" data-result="${i}"><span>${esc(subjectName(h.subject))}<small>${esc(new Date(h.date).toLocaleString('en-PH',{dateStyle:'medium',timeStyle:'short'}))}${h.synced?' · Synced':''}</small></span><strong>${h.correct}/${h.total}</strong></button>`).join(''):'<p class="muted">Complete a session to record your score.</p>'}<details class="section"><summary>Subject progress</summary>${summary.map(s=>`<div class="subject-row"><strong>${esc(subjectName(s.id))}</strong><p>${s.accuracy===null?'No answers yet':s.accuracy+'% accuracy'} · ${s.covered}/${s.total} explored</p><progress class="bar" max="${s.total||1}" value="${s.covered}"></progress></div>`).join('')}</details><p class="fine">Latest 200 sessions shown. Accuracy includes repeated answers and unfinished sessions. Practice results do not predict board performance.</p>`;
}
function renderRanks(){
 $('#app').innerHTML=`${accountLine()}<h1>Ranking</h1><p class="muted">Keep learning with your cohort.</p>${state.endpoint?`<button class="btn secondary full spaced" data-action="refresh-ranks">Refresh ranking</button>${ranking?ranking.entries.map((x,i)=>`<div class="rank"><span>${i+1}</span><div><strong>${esc(x.name)}</strong><small>Account ••••${esc(x.accountSuffix)} · ${x.correct}/${x.attempts} correct</small></div><strong>${x.points} pt</strong></div>`).join('')||'<p class="inline-note">No synced results yet.</p>':'<p class="inline-note">Refresh to load account standings.</p>'}`:'<div class="card"><p>Connect an instructor-hosted HTTPS service in Account to use shared ranking.</p><button class="btn secondary full" data-tab="account">Open account</button></div>'}<p class="fine">One point per distinct correct bank question per server day. Results are graded by the server. Offline answer keys are visible, so rankings are practice-only and are not proctored exam standings.</p>`;
}
function renderAccount(){
 if(newRecovery){$('#app').innerHTML=`<h1>Save your account</h1><p class="muted">Use this number and recovery code to sign in again.</p><label>Account number</label><p class="credential">${esc(newRecovery.number)}</p><label class="spaced">Recovery code</label><p class="credential">${esc(newRecovery.recovery.match(/.{1,8}/g).join(' '))}</p><p class="inline-note">Keep the code private. Your account number alone cannot sign in. This code cannot be retrieved from the app later.</p><button class="btn full spaced" data-action="export-account">Save account recovery file</button><button class="btn secondary full spaced" data-action="recovery-saved">I have saved my code</button>`;return;}
 $('#app').innerHTML=account?`${accountLine()}<h1>Your account</h1><div class="card"><strong>${esc(state.name)}</strong><p class="credential">${esc(account)}</p><p class="inline-note">${state.history.length} saved session(s) · ${state.pending?.length||0} waiting to sync</p></div><h2 class="section">Connect & sync</h2><p class="inline-note">Use the HTTPS API URL provided by your instructor. The same account number and recovery code restore synced scores on another device.</p><label for="account-url">HTTPS service URL</label><input id="account-url" type="url" placeholder="https://your-cohort.example/" value="${esc(state.endpoint)}">${state.cohort?'<button class="btn full" data-action="sync">Sync saved results</button>':''}<label class="spaced" for="connect-code">Recovery code</label><input id="connect-code" type="password" autocomplete="off" placeholder="Required to connect or renew sign-in"><button class="btn secondary full" data-action="connect">Connect account</button><button class="link full spaced" data-action="signout">Sign out on this device</button>${state.cohort?'<details class="section"><summary>Delete online account</summary><p class="inline-note">Permanently removes online scores, progress and ranking. Local scores remain until you remove app data.</p><button class="btn danger full" data-action="delete-account">Delete online account</button></details>':''}`:`<h1>Your account</h1><p class="muted">Keep results, progress and recommendations together.</p><div class="card"><h2>Create an account</h2><p class="inline-note">Works offline. Current guest results will be linked to the new account on this device.</p><label for="account-name">Display name</label><input id="account-name" maxlength="30" placeholder="Your name or nickname"><button class="btn full" data-action="create-account">Create account</button></div><details class="card"><summary>Sign in to an existing account</summary><label class="spaced" for="login-number">Account number</label><input id="login-number" placeholder="AE-0000000000000000" autocomplete="username"><label for="login-code">Recovery code</label><input id="login-code" type="password" autocomplete="off"><label for="login-url">HTTPS service URL (for another device)</label><input id="login-url" type="url" placeholder="Optional for an account on this device"><button class="btn secondary full" data-action="login">Sign in</button></details><p class="fine">Offline accounts stay on this phone until you export a backup or sync to a hosted service. Keep both the recovery file and a progress backup.</p>`;
}
function renderSettings(){
 $('#app').innerHTML=`<h1>Settings</h1><div class="card"><h2>Exam weights</h2><div class="weight-list">${bank.subjects.map(s=>`<div><span>${esc(subjectName(s.id))}</span><strong>${s.weight}%</strong></div>`).join('')}</div><a class="inline-note" href="${esc(bank.blueprintSource)}" target="_blank" rel="noopener">PRC examination program ↗</a></div><div class="card"><h2>Backup & recovery</h2><p class="inline-note">Export before uninstalling or changing phones. Progress backups exclude sign-in tokens and recovery codes; keep your separate account recovery file.</p><button class="btn secondary full" data-action="export">Export progress backup</button><button class="btn secondary full spaced" data-action="import">Import backup / approved bank</button>${storageBlocked?'<button class="btn danger full spaced" data-action="recover">Recover unreadable storage</button>':''}</div><div class="card"><h2>Question bank</h2><p class="inline-note">${esc(bank.notice)}</p><p>${state.flags.length} questions set aside</p><button class="btn secondary full" data-action="restore-flags">Restore set-aside questions</button><button class="link full" data-action="export-reports">Export question report</button><button class="btn secondary full spaced" data-action="export-bank">Export question bank</button><p class="inline-note">Keep this bank export with your progress backup, especially before reinstalling or changing phones.</p></div><p class="fine">AE Prepware ${VERSION} · Android 8+<br>Independent study software. No PRC affiliation or pass guarantee. AI can assist selection; it cannot change scored answers. Subjects follow the <a href="${esc(bank.blueprintSource)}" target="_blank" rel="noopener">PRC blueprint</a>.</p>`;
}
function ask(title,body,confirm='Continue'){return new Promise(resolve=>{const d=$('#modal');d.innerHTML=`<h2>${esc(title)}</h2><p>${esc(body)}</p><div class="row spaced"><button class="btn secondary" id="cancel">Cancel</button><button class="btn" id="confirm">${esc(confirm)}</button></div>`;const done=v=>{d.close();d.oncancel=null;resolve(v);};$('#cancel').onclick=()=>done(false);$('#confirm').onclick=()=>done(true);d.oncancel=e=>{e.preventDefault();done(false);};d.showModal();});}
function download(text,name){if(window.AndroidFiles){AndroidFiles.exportBackup(text,name);return;}const a=document.createElement('a');a.href=URL.createObjectURL(new Blob([text],{type:'application/json'}));a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);}
async function apiAt(url,path,data,token){
 if(!AE.validEndpoint(url))throw Error('Enter a valid HTTPS root service URL.');
 const abort=new AbortController(),timeout=setTimeout(()=>abort.abort(),20000);
 try{const r=await fetch(url.replace(/\/$/,'')+path,{method:data?'POST':'GET',headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},body:data?JSON.stringify(data):undefined,signal:abort.signal,redirect:'error'});if(!r.ok){const d=await r.json().catch(()=>({}));throw Error(typeof d.detail==='string'?d.detail:'Service returned '+r.status);}return await r.json();}
 catch(e){if(e.name==='AbortError')throw Error('Service timed out. Saved scores remain on this device; retry sync later.');if(e instanceof TypeError)throw Error('Service unavailable. Check the URL, HTTPS and connection.');throw e;}finally{clearTimeout(timeout);}
}
const request=(path,data,auth=false)=>apiAt(state.endpoint,path,data,auth?state.cohort?.token:null);
async function syncResults(){
 if(!account||!state.cohort)throw Error('Connect your account before syncing.');
 for(const h of [...(state.pending||[])]){
  const r=await request('/accounts/results',{id:h.id,subject:h.subject,bankVersion:h.bankVersion,answers:h.ids.map((id,i)=>({id,choice:h.answers[i]}))},true);
  if(r.id!==h.id||r.accountNumber!==account||r.total!==50||r.correct!==h.correct)throw Error('Service score mismatch. Pending result preserved for review.');
  state.pending=state.pending.filter(x=>x.id!==h.id);const item=state.history.find(x=>x.id===h.id);if(item)item.synced=true;save();
 }
 notice('All saved results synced.');
}
function validateRemote(r,number){if(r.number!==number||r.bankVersion!==bank.version||typeof r.token!=='string'||!r.stats||!Array.isArray(r.history))throw Error('The service returned an incompatible account or bank.');}
async function loadProfile(number){account=number;bank=structuredClone(bundled);const raw=await BankStore.read(bankKey());if(raw)bank=AE.validateBank(JSON.parse(raw),true,bundled);else if(bundled.distribution==='private-study')await BankStore.write(bankKey(),JSON.stringify(bundled));state=AE.validateState(JSON.parse(localStorage.getItem(stateKey())),bank);if(state.accountNumber!==number)throw Error('Account profile mismatch.');state.pending=state.pending||[];state.selection=state.selection||'random';ranking=null;storageBlocked=false;}
async function doAction(action){
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
   const next=AE.fresh();next.accountNumber=number;next.name=r.name;next.stats=r.stats;next.history=r.history;next.endpoint=url;next.cohort={id:number,token:r.token};AE.validateState(next,bank);
   const customBank=await BankStore.read(bankKey());await Accounts.remember(localStorage,number,r.name,recovery,next);if(customBank)await BankStore.write('ae-bank-'+number,customBank);await loadProfile(number);
  }
  newRecovery=null;setTab('home');notice('Signed in.');return;
 }
 if(action==='connect'){
  const url=$('#account-url').value.trim(),recovery=Accounts.normalize($('#connect-code').value);
  await Accounts.login(localStorage,account,recovery);
  const health=await apiAt(url,'/health');if(health.bankVersion!==bank.version)throw Error('Question bank versions differ. Use the matching service.');
  const r=await apiAt(url,'/accounts/register',{number:account,name:state.name,recovery});validateRemote(r,account);
  state.endpoint=url;state.cohort={id:account,token:r.token};save();await syncResults();render();return;
 }
 if(action==='sync'){
  const url=$('#account-url').value.trim();if(url.replace(/\/$/,'')!==state.endpoint.replace(/\/$/,''))throw Error('Use Connect account with your recovery code to change the service URL.');
  await syncResults();render();return;
 }
 if(action==='signout'&&await ask('Sign out?','Save your recovery code and progress backup first. Local account data stays on this device.','Sign out')){
  if(state.cohort&&state.endpoint){try{await request('/accounts/logout',{},true);}catch{ /* Offline signout still clears this device token. */ }}
  state.cohort=null;save();localStorage.removeItem(Accounts.ACTIVE);account=null;bank=structuredClone(bundled);const guestBank=await BankStore.read(BANKKEY);if(guestBank)bank=AE.validateBank(JSON.parse(guestBank),true,bundled);else if(bundled.distribution==='private-study')await BankStore.write(BANKKEY,JSON.stringify(bundled));const raw=localStorage.getItem(KEY);state=raw?AE.validateState(JSON.parse(raw),bank):AE.fresh();newRecovery=null;ranking=null;setTab('account');notice('Signed out.');return;
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
document.addEventListener('change',e=>{if(e.target.dataset.source){try{state.sourceMode=sourcesSelected();save();render();}catch(err){notice(err.message);}return;}if(e.target.id==='selection'){try{state.selection=e.target.value;save();}catch(err){notice(err.message);}}});
document.addEventListener('click',async e=>{
 const el=e.target.closest('[data-action],[data-tab],[data-choice],[data-subject],[data-result]');if(!el||busy||el.disabled)return;
 try{busy=true;el.setAttribute('aria-busy','true');
  if(el.dataset.tab){setTab(el.dataset.tab);return;}
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
 try{const custom=await BankStore.read(bankKey());if(custom)bank=AE.validateBank(JSON.parse(custom),true,bundled);else if(bundled.distribution==='private-study')await BankStore.write(bankKey(),JSON.stringify(bundled));}catch{storageBlocked=true;notice('Imported bank could not be read. Export recovery data in Settings before recovery.');}
 try{const raw=localStorage.getItem(stateKey());if(raw)state=AE.validateState(JSON.parse(raw),bank);if((state.accountNumber||null)!==account)throw Error('Profile mismatch');state.pending=state.pending||[];state.selection=state.selection||'random';}catch{storageBlocked=true;state=AE.fresh();state.accountNumber=account;notice('Saved progress could not be read. It has been preserved. Open Settings to export the raw record or recover from a backup.');}
 render();
 }catch(e){$('#app').innerHTML=`<h1>Could not open Prepware</h1><p>${esc(e.message)}</p><p>Your stored data has not been erased.</p>`;}})();
