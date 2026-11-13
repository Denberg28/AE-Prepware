const {chromium}=require('playwright'),http=require('node:http'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve('app/src/main/assets');
const server=http.createServer((req,res)=>{try{const file=path.join(root,req.url==='/'?'index.html':req.url);res.setHeader('Content-Type',file.endsWith('.js')?'application/javascript':file.endsWith('.css')?'text/css':file.endsWith('.json')?'application/json':'text/html');res.end(fs.readFileSync(file));}catch{res.writeHead(404);res.end();}});
(async()=>{let browser;try{
 await new Promise(r=>server.listen(8087,'127.0.0.1',r));browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:393,height:800}}),errors=[];page.on('pageerror',e=>errors.push(e.message));const now=Date.UTC(2026,10,14,4),DAY=86400000;
 await page.addInitScript(now=>{Date.now=()=>now;},now);await page.goto('http://127.0.0.1:8087');await page.locator('[data-screen=subjects]').waitFor();await page.locator('nav [data-tab=progress]').click();
 await page.getByRole('heading',{name:'Board readiness',exact:true}).waitFor();await page.getByText('Tracking starts with your next answer.',{exact:false}).waitFor();
 const math=page.locator('.readiness-subject').filter({has:page.getByRole('heading',{name:'Mathematics',exact:true})});
 await math.getByRole('button',{name:'New-item check',exact:true}).click();await page.locator('[data-choice="1"]').click();assert.equal(await page.locator('.feedback,details.explanation').count(),0);assert.equal(await page.evaluate(()=>Object.keys(state.stats).length),0);
 await page.reload();await page.getByRole('button',{name:'Continue · 1 / 20'}).click();assert.equal(await page.locator('[data-choice]:disabled').count(),4);
 for(let i=0;i<20;i++){if(await page.locator('[data-choice]:not(:disabled)').count())await page.locator(`[data-choice="${i<6?1:0}"]`).click();await page.locator('[data-action=next]').click();}
 assert.equal(await page.evaluate(()=>state.history[0].correct),14);await page.locator('nav [data-tab=progress]').click();await math.getByText('Support needed',{exact:true}).waitFor();assert.equal(await math.getByRole('button',{name:'Spaced recheck',exact:true}).isDisabled(),true);
 for(const offset of [8,16]){
  await page.evaluate(t=>{Date.now=()=>t;},now+offset*DAY);await page.locator('nav [data-tab=progress]').click();await math.getByRole('button',{name:'Spaced recheck',exact:true}).click();
  for(let i=0;i<20;i++){await page.locator('[data-choice="0"]').click();await page.locator('[data-action=next]').click();}await page.locator('nav [data-tab=progress]').click();
 }
 await math.getByText('Foundation target met',{exact:true}).waitFor();assert.equal(await page.evaluate(()=>Readiness.report(state,bank).competence.subjects[0].first.correct),14);
 await page.getByText('Facilitator report',{exact:true}).click();await page.locator('#report-alias').fill('Student A');
 await page.getByRole('button',{name:'Export facilitator report',exact:true}).click();await page.locator('#cancel').click();
 const event=page.waitForEvent('download');await page.getByRole('button',{name:'Export facilitator report',exact:true}).click();await page.locator('#confirm').click();const download=await event;await download.saveAs('artifacts/readiness-synthetic.json');
 const report=JSON.parse(fs.readFileSync('artifacts/readiness-synthetic.json'));assert.equal(report.alias,'Student A');assert.equal(report.readiness.boardReadiness,'Not established');assert.equal(report.competence.subjects[0].first.correct,14);
 const snapshot=await page.evaluate(()=>structuredClone(state));await page.evaluate(({state,version})=>{void receiveImport(JSON.stringify({type:'ae-progress',bankVersion:version,state}));},{state:snapshot,version:await page.evaluate(()=>bank.version)});await page.locator('#confirm').click();assert.deepEqual(await page.evaluate(()=>state.monitoring),snapshot.monitoring);
 for(const theme of ['light','dark']){if(await page.locator('html').getAttribute('data-theme')!==theme)await page.locator('#theme-toggle').click();await page.locator('nav [data-tab=progress]').click();await page.locator('#content').evaluate(x=>x.scrollTop=0);await page.screenshot({path:`artifacts/15-readiness-${theme}.png`});for(const width of [320,393,720]){await page.setViewportSize({width,height:640});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth&&scrollY===0));}}
 assert.deepEqual(errors,[]);console.log('PASS BRMS: cold start/unknown history, deferred diagnostic, reload, first-attempt protection, spaced confirmation, voluntary export/cancel, backup and responsive themes.');
 }finally{if(browser)await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
