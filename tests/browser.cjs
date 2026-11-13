const {chromium}=require('playwright'),http=require('node:http'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve('app/src/main/assets');
const server=http.createServer((req,res)=>{const file=path.join(root,req.url==='/'?'index.html':req.url);try{res.setHeader('Content-Type',file.endsWith('.js')?'application/javascript':file.endsWith('.css')?'text/css':file.endsWith('.json')?'application/json':'text/html');res.end(fs.readFileSync(file));}catch{res.writeHead(404);res.end();}});
const stored=()=>{const number=localStorage.getItem('ae-active-account-v1');return JSON.parse(localStorage.getItem(number?'ae-profile-'+number:'ae-prepware-v1'));};
(async()=>{let browser;try{
 fs.mkdirSync('artifacts',{recursive:true});await new Promise(r=>server.listen(8080,'127.0.0.1',r));
 browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:393,height:851}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8080');await page.getByRole('heading',{name:'Choose a subject'}).waitFor();assert.equal(await page.locator('[data-subject]').count(),6);
 await page.screenshot({path:'artifacts/01-subjects.png',fullPage:true});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 await page.locator('[data-subject="math"]').click();let s=await page.evaluate(stored);assert.equal(s.session.ids.length,50);assert.equal(new Set(s.session.ids).size,50);
 await page.locator('[data-choice="1"]').click();await page.getByText('Incorrect',{exact:true}).waitFor();
 s=await page.evaluate(stored);const correctLetter='ABCD'[s.session.orders[0].indexOf(0)];assert.ok((await page.locator('.feedback').innerText()).includes('Correct answer: '+correctLetter));
 assert.equal(await page.locator('[data-choice]:disabled').count(),4);assert.equal(await page.locator('details.explanation[open]').count(),0);
 await page.locator('details.explanation summary').click();assert.equal(await page.locator('details.explanation[open]').count(),1);
 await page.screenshot({path:'artifacts/02-quiz-explanation.png',fullPage:true});
 const before=await page.evaluate(stored);await page.reload();await page.getByRole('button',{name:'Continue · 1 / 50'}).click();assert.deepEqual((await page.evaluate(stored)).session,before.session);
 for(let i=0;i<50;i++){
  if(await page.locator('[data-choice]:not(:disabled)').count())await page.locator('[data-choice="0"]').click();
  await page.locator('[data-action="next"]').click();
  if(await page.getByRole('heading',{name:'Session complete'}).count())break;
 }
 await page.getByRole('heading',{name:'Session complete'}).waitFor();s=await page.evaluate(stored);assert.equal(s.history[0].correct,49);assert.equal(s.history[0].total,50);
 await page.screenshot({path:'artifacts/03-results.png',fullPage:true});
 await page.locator('nav [data-tab="account"]').click();await page.locator('#account-name').fill('Integration Cadet');await page.getByRole('button',{name:'Create account',exact:true}).click();
 await page.getByRole('heading',{name:'Save your account'}).waitFor();const credentials=await page.evaluate(()=>({number:newRecovery.number,recovery:newRecovery.recovery}));
 await page.getByRole('button',{name:'I have saved my code'}).click();s=await page.evaluate(stored);assert.equal(s.accountNumber,credentials.number);assert.equal(s.history[0].correct,49);
 await page.reload();await page.getByRole('heading',{name:'Choose a subject'}).waitFor();assert.equal((await page.evaluate(stored)).accountNumber,credentials.number);
 await page.locator('nav [data-tab="progress"]').click();await page.screenshot({path:'artifacts/04-progress.png',fullPage:true});
 await page.locator('nav [data-tab="account"]').click();await page.getByRole('button',{name:'Sign out on this device'}).click();await page.locator('#confirm').click();await page.getByRole('button',{name:'Create account',exact:true}).waitFor();assert.equal((await page.evaluate(()=>state)).history.length,0);
 await page.locator('details.card summary').click();await page.locator('#login-number').fill(credentials.number);await page.locator('#login-code').fill('b'.repeat(64));await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByText('Account number or recovery code is incorrect.',{exact:true}).waitFor();
 await page.locator('#login-code').fill(credentials.recovery);await page.getByRole('button',{name:'Sign in',exact:true}).click();await page.getByRole('heading',{name:'Choose a subject'}).waitFor();assert.equal((await page.evaluate(stored)).history[0].correct,49);
 // Backup replacement preserves account binding and cancellation behavior.
 const snapshot=await page.evaluate(stored),bankVersion=await page.evaluate(()=>bank.version);
 await page.evaluate(({snapshot,bankVersion})=>{void window.receiveImport(JSON.stringify({type:'ae-progress',bankVersion,state:snapshot}));},{snapshot,bankVersion});await page.locator('#cancel').click();assert.deepEqual(await page.evaluate(stored),snapshot);
 await page.evaluate(({snapshot,bankVersion})=>{void window.receiveImport(JSON.stringify({type:'ae-progress',bankVersion,state:snapshot}));},{snapshot,bankVersion});await page.locator('#confirm').click();await page.getByText('Backup restored.',{exact:true}).waitFor();
 await page.evaluate(()=>window.receiveImport('{bad json'));assert.equal((await page.evaluate(stored)).history[0].correct,49);
 await page.evaluate(()=>{const n=localStorage.getItem('ae-active-account-v1');localStorage.setItem('ae-profile-'+n,'{"schema":99}');});await page.reload();await page.getByText('Saved progress could not be read.',{exact:false}).waitFor();await page.getByRole('button',{name:'Settings',exact:true}).click();await page.getByRole('button',{name:'Recover unreadable storage'}).waitFor();
 await page.setViewportSize({width:320,height:640});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 // A legacy v0.1 guest session remains resumable with the expanded bank.
 await page.evaluate(()=>{localStorage.clear();const s=AE.fresh();delete s.accountNumber;delete s.pending;delete s.selection;AE.start(s,bank.questions.slice(0,10),'random');AE.answer(s,bank,0);localStorage.setItem('ae-prepware-v1',JSON.stringify(s));});await page.reload();await page.getByRole('button',{name:'Continue · 1 / 10'}).click();await page.getByText('Correct',{exact:true}).waitFor();
 assert.deepEqual(errors,[]);console.log('PASS browser: 50-question score, shuffled-letter feedback, collapsed explanation, resume, account binding/recovery/isolation, backup cancellation/restore, corruption and legacy migration.');
 }finally{if(browser)await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
