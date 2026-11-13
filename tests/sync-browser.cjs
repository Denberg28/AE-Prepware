const {chromium}=require('playwright'),assert=require('node:assert/strict'),http=require('node:http'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),{spawn}=require('node:child_process');
(async()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ae-fullsync-')),python=process.env.AE_PYTHON||path.join(process.cwd(),'.venv/bin/python');
 const api=spawn(python,['-m','uvicorn','backend.api:app','--host','127.0.0.1','--port','18081'],{env:{...process.env,AE_DB:path.join(temp,'test.sqlite'),GEMINI_API_KEY:'',AE_ENROLLMENT_CODE:'',AE_FACULTY_SYNC_KEY:'test-faculty-key-'+'a'.repeat(32)},stdio:'ignore'});
 let browser,server;
 try{
  let ready=false;for(let i=0;i<80;i++){try{if((await fetch('http://127.0.0.1:18081/health')).ok){ready=true;break;}}catch{}await new Promise(r=>setTimeout(r,100));}assert.ok(ready,'API started');
  server=http.createServer((req,res)=>{try{const file=path.join(process.cwd(),'app/src/main/assets',req.url==='/'?'index.html':req.url);res.setHeader('Content-Type',file.endsWith('.js')?'application/javascript':file.endsWith('.css')?'text/css':file.endsWith('.json')?'application/json':'text/html');res.end(fs.readFileSync(file));}catch{res.writeHead(404);res.end();}});await new Promise(r=>server.listen(18082,'127.0.0.1',r));
  browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});
  let drop=false,offline=false,tamper=false;
  async function prepare(page){await page.route('https://cohort.test/**',async route=>{
   if(offline)return route.abort('failed');
   const response=await route.fetch({url:route.request().url().replace('https://cohort.test','http://127.0.0.1:18081')});
   if(drop&&route.request().method()==='POST'&&route.request().url().endsWith('/accounts/snapshot')){drop=false;return route.abort('failed');}
   if(tamper&&route.request().url().endsWith('/accounts/bank')){const b=await response.json();b.title='Changed same version';return route.fulfill({json:b});}
   await route.fulfill({response});
  });}
  const page=await browser.newPage({viewport:{width:393,height:851}}),errors=[];page.on('pageerror',e=>errors.push(e.message));await prepare(page);
  await page.goto('http://127.0.0.1:18082');await page.locator('[data-screen=subjects]').waitFor();
  await page.locator('#sync-toggle').click();await page.locator('#account-name').waitFor();assert.equal(await page.evaluate(()=>state.history.length),0);
  await page.locator('#account-name').fill('Sync Cadet');await page.getByRole('button',{name:'Create account',exact:true}).click();await page.getByRole('heading',{name:'Save your account'}).waitFor();const credentials=await page.evaluate(()=>({number:newRecovery.number,recovery:newRecovery.recovery}));await page.getByRole('button',{name:'I have saved my code'}).click();
  await page.locator('[data-action=feedback-practice]').click();assert.equal(await page.evaluate(()=>state.session.ids.every(id=>id.startsWith('FB-'))),true);
  for(let i=0;i<20;i++){await page.locator('[data-choice="0"]').click();await page.locator('[data-action=next]').click();}
  assert.equal(await page.evaluate(()=>state.pending.length),1);
  await page.locator('nav [data-tab=account]').click();await page.locator('#account-url').fill('https://cohort.test/');await page.locator('#connect-code').fill(credentials.recovery);await page.getByRole('button',{name:'Connect account',exact:true}).click();await page.getByRole('button',{name:'Sync all data'}).waitFor();
  assert.equal((await (await fetch('http://127.0.0.1:18081/accounts/leaderboard')).json()).entries.length,0);
  await page.locator('#rank-opt-in').check();await page.locator('#share-readiness').check();
  // Save an unfinished diagnostic: snapshot must retain its answer times/journal.
  await page.locator('nav [data-tab=progress]').click();await page.locator('[data-check=diagnostic][data-check-subject=math]').click();await page.locator('[data-choice="0"]').click();
  const journal=await page.evaluate(()=>structuredClone(state.monitoring)),session=await page.evaluate(()=>structuredClone(state.session));
  drop=true;await page.locator('#sync-toggle').click();await page.waitForFunction(()=>state.lastSync?.complete===false);assert.equal(await page.evaluate(async()=>!!await BankStore.read(uploadKey())),true);
  await page.locator('#sync-toggle').click();await page.waitForFunction(()=>state.lastSync?.complete===true);assert.equal(await page.evaluate(async()=>await BankStore.read(uploadKey())),null);assert.equal(await page.evaluate(()=>state.cloudRevision),2);
  assert.deepEqual(await page.evaluate(()=>state.monitoring),journal);assert.deepEqual(await page.evaluate(()=>state.session),session);
  assert.equal((await (await fetch('http://127.0.0.1:18081/accounts/leaderboard')).json()).entries[0].attempts,20);
  const shared=await (await fetch('http://127.0.0.1:18081/faculty/monitoring',{headers:{Authorization:'Bearer test-faculty-key-'+'a'.repeat(32)}})).json();assert.equal(shared.entries.length,1);
  // Restore the complete profile in a separate storage context.
  const second=await browser.newPage({viewport:{width:393,height:851}});await prepare(second);await second.goto('http://127.0.0.1:18082');await second.locator('nav [data-tab=account]').click();await second.locator('details.card summary').click();await second.locator('#login-number').fill(credentials.number);await second.locator('#login-code').fill(credentials.recovery);await second.locator('#login-url').fill('https://cohort.test/');await second.getByRole('button',{name:'Sign in',exact:true}).click();await second.locator('[data-screen=subjects]').waitFor();
  assert.deepEqual(await second.evaluate(()=>state.monitoring),journal);assert.deepEqual(await second.evaluate(()=>state.session),session);assert.equal(await second.evaluate(()=>state.history[0].correct),20);
  await second.locator('#sync-toggle').click();await second.waitForFunction(()=>state.lastSync?.complete===true);
  await page.locator('#sync-toggle').click();await page.waitForFunction(()=>state.lastSync?.complete===false);await page.getByText('A newer online backup exists.',{exact:false}).waitFor();assert.deepEqual(await page.evaluate(()=>state.session),session);
  // Explicit restore resolves the revision conflict, retaining the current profile.
  await page.locator('nav [data-tab=account]').click();await page.getByRole('button',{name:'Restore online backup',exact:true}).click();await page.locator('#confirm').click();await page.getByText('Online profile restored, including its monitoring journal.',{exact:true}).waitFor();
  offline=true;await page.locator('#sync-toggle').click();await page.waitForFunction(()=>state.lastSync?.complete===false);assert.deepEqual(await page.evaluate(()=>state.session),session);offline=false;
  tamper=true;await second.locator('#sync-toggle').click();await second.waitForFunction(()=>state.lastSync?.complete===false);await second.getByText('The server reused a bank version', {exact:false}).waitFor();assert.equal(await second.evaluate(()=>bank.title),'AE Foundations');tamper=false;
  assert.deepEqual(errors,[]);await page.screenshot({path:'artifacts/16-sync-recovery.png'});
  console.log('PASS full sync: feedback drill, opt-in ranks/sharing, lost-ack retry, profile/journal/unfinished-check recovery, revision conflict, explicit restore, offline failure and tampered bank rejection. HTTPS transport simulated.');
 }finally{if(browser)await browser.close();if(server)server.close();api.kill();fs.rmSync(temp,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
