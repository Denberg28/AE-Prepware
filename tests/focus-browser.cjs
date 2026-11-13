// Public synthetic records exercise scope, migrations and both result lengths.
const {chromium}=require('playwright'),http=require('node:http'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const current=require('../app/src/main/assets/bank.json'),root=path.resolve('app/src/main/assets');
const old=structuredClone(current);delete old.focus;delete old.extends;old.version='test-before-focus';
const next=structuredClone(current);next.version='test-focus-update';next.extends=old.version;
let updated=false;
const server=http.createServer((req,res)=>{if(req.url==='/bank.json'){res.setHeader('Content-Type','application/json');res.end(JSON.stringify(updated?next:old));return;}const file=path.join(root,req.url==='/'?'index.html':req.url);try{res.setHeader('Content-Type',file.endsWith('.js')?'application/javascript':file.endsWith('.css')?'text/css':'text/html');res.end(fs.readFileSync(file));}catch{res.writeHead(404);res.end();}});
(async()=>{let browser;try{
 await new Promise(r=>server.listen(8086,'127.0.0.1',r));browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:393,height:760}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8086');await page.locator('[data-screen=subjects]').waitFor();
 await page.locator('nav [data-tab=account]').click();await page.locator('#account-name').fill('Core Cadet');await page.getByRole('button',{name:'Create account',exact:true}).click();await page.getByRole('button',{name:'I have saved my code'}).click();
 const before=await page.evaluate(async()=>{
  const qs=bank.questions.filter(q=>q.subject==='math'&&q.active!==false).slice(0,50);
  AE.start(state,qs,'subject');for(let i=0;i<50;i++){state.session.index=i;AE.answer(state,bank,0);}AE.finish(state,bank);
  AE.start(state,qs,'subject');AE.answer(state,bank,0);await BankStore.write(bankKey(),JSON.stringify(bank));save();return structuredClone(state);
 });
 updated=true;await page.reload();await page.locator('[data-screen=subjects]').waitFor();assert.equal(await page.evaluate(()=>bank.version),next.version);
 assert.equal(await page.evaluate(async()=>JSON.parse(await BankStore.read(bankKey())).version),next.version);assert.deepEqual(await page.evaluate(()=>state),before);
 await page.getByRole('button',{name:'Continue · 1 / 50'}).click();await page.getByText('Correct',{exact:true}).waitFor();
 await page.locator('nav [data-tab=home]').click();assert.equal(await page.locator('#study-scope').inputValue(),'focus');assert.ok((await page.locator('.session-info').innerText()).includes('20 questions'));
 await page.locator('[data-subject=aero]').click();await page.locator('#confirm').click();assert.equal(await page.evaluate(()=>state.session.ids.length),20);
 assert.equal(await page.evaluate(()=>state.session.ids.every(id=>Object.hasOwn(bank.focus.questions,id))),true);
 for(let i=0;i<20;i++){await page.locator('[data-choice="0"]').click();await page.locator('[data-action=next]').click();}
 assert.deepEqual(await page.evaluate(()=>state.pending.map(h=>h.total)),[50,20]);assert.equal(await page.evaluate(()=>state.history[0].correct),20);
 await page.getByRole('button',{name:'Settings',exact:true}).click();await page.getByText('Coverage gaps',{exact:true}).click();await page.getByText('PRC table of specifications ↗',{exact:true}).waitFor();
 await page.locator('nav [data-tab=home]').click();await page.locator('#study-scope').selectOption('full');await page.locator('[data-subject=math]').click();assert.equal(await page.evaluate(()=>state.session.ids.length),50);
 await page.locator('nav [data-tab=home]').click();await page.locator('#study-scope').selectOption('focus');await page.setViewportSize({width:320,height:640});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.screenshot({path:'artifacts/14-prc-core.png'});assert.deepEqual(errors,[]);
 console.log('PASS core: compatible stored-bank migration, unchanged history/50-item queue/session, 20-item core/queue, full-50 fallback, coverage gaps and 320px layout.');
 }finally{if(browser)await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
