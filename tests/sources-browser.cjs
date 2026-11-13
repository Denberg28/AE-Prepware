// Synthetic teaching records exercise the import workflow; none are shipped.
const {chromium}=require('playwright'),http=require('node:http'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const original=require('../app/src/main/assets/bank.json'),root=path.resolve('app/src/main/assets');
const server=http.createServer((req,res)=>{const file=path.join(root,req.url==='/'?'index.html':req.url);try{res.setHeader('Content-Type',file.endsWith('.js')?'application/javascript':file.endsWith('.css')?'text/css':file.endsWith('.json')?'application/json':'text/html');res.end(fs.readFileSync(file));}catch{res.writeHead(404);res.end();}});
(async()=>{let browser;try{
 await new Promise(r=>server.listen(8082,'127.0.0.1',r));
 browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:393,height:851}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8082');await page.getByRole('heading',{name:'Choose a subject'}).waitFor();
 await page.locator('[data-source=AI]').uncheck();assert.equal(await page.locator('[data-subject]:disabled').count(),6);
 await page.locator('[data-source=IN]').check();assert.equal(await page.locator('[data-subject]:disabled').count(),6);
 await page.locator('[data-source=IN]').uncheck();await page.locator('[data-source=AI]').check();
 await page.locator('[data-subject=math]').click();await page.locator('[data-choice="0"]').click();
 const before=await page.evaluate(()=>structuredClone(state)),currentId=before.session.ids[0];
 const bank=structuredClone(original);bank.version='synthetic-refresh';bank.extends=original.version;
 const old=bank.questions.find(q=>q.id===currentId);old.active=false;
 bank.questions.push({...structuredClone(old),id:'TEST-REVISION',active:true,answer:1,review:'approved',reviewer:'Automated TEST FIXTURE',supersedes:old.id});
 for(const [i,q]of original.questions.filter(q=>q.subject==='aero').slice(0,50).entries())bank.questions.push({...structuredClone(q),id:'TEST-IN-'+i,prompt:'Synthetic fixture: '+q.prompt,origin:'IN',review:'approved',reviewer:'Automated TEST FIXTURE',upload:{file:'synthetic.json',locator:'Test '+i,rights:'instructor-original'}});
 await page.getByRole('button',{name:'Settings',exact:true}).click();
 await page.evaluate(bank=>{void window.receiveImport(JSON.stringify(bank));},bank);await page.locator('#cancel').click();assert.equal(await page.evaluate(()=>bank.version),original.version);
 await page.evaluate(bank=>{void window.receiveImport(JSON.stringify(bank));},bank);await page.locator('#confirm').click();await page.getByText('Question bank refreshed.',{exact:false}).waitFor();assert.deepEqual(await page.evaluate(()=>state),before);
 await page.reload();await page.getByRole('button',{name:'Continue · 1 / 50'}).click();await page.getByText('Correct',{exact:true}).waitFor();assert.equal(await page.evaluate(()=>bank.questions.find(q=>q.id===state.session.ids[0]).answer),0);
 for(let i=0;i<50;i++){if(await page.locator('[data-choice]:not(:disabled)').count())await page.locator('[data-choice="0"]').click();await page.locator('[data-action=next]').click();if(await page.getByRole('heading',{name:'Session complete'}).count())break;}
 assert.equal(await page.evaluate(()=>state.history[0].correct),50);
 await page.locator('nav [data-tab=home]').click();await page.locator('[data-source=IN]').check();assert.equal(await page.locator('[data-subject=math]').isDisabled(),true);assert.equal(await page.locator('[data-subject=aero]').isEnabled(),true);
 await page.screenshot({path:'artifacts/06-source-selection.png',fullPage:true});
 await page.locator('[data-subject=aero]').click();assert.equal(await page.evaluate(()=>state.session.ids.filter(id=>AE.origin(bank.questions.find(q=>q.id===id))==='IN').length),25);
 await page.getByRole('button',{name:'Settings',exact:true}).click();const tampered=structuredClone(bank);tampered.version='tampered';tampered.extends=bank.version;tampered.questions[0].answer=2;tampered.questions[0].review='approved';
 await page.evaluate(bank=>window.receiveImport(JSON.stringify(bank)),tampered);await page.getByText('Refresh changes an existing question',{exact:false}).waitFor();assert.equal(await page.evaluate(()=>bank.version),bank.version);
 await page.setViewportSize({width:320,height:640});await page.locator('nav [data-tab=home]').click();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
 assert.deepEqual(errors,[]);console.log('PASS mobile source/refresh: no-source/empty-IN blocks, cancel/confirm, ongoing old-key resume, 50/50 historical score, exact Hybrid quota, tamper rejection and 320px layout.');
 }finally{if(browser)await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
