const {chromium}=require('playwright'),assert=require('node:assert/strict'),http=require('node:http'),fs=require('node:fs'),path=require('node:path'),os=require('node:os'),{spawn}=require('node:child_process');
(async()=>{
 const temp=fs.mkdtempSync(path.join(os.tmpdir(),'ae-cohort-'));
 const python=process.env.AE_PYTHON||path.join(process.cwd(),'.venv/bin/python');
 const api=spawn(python,['-m','uvicorn','backend.api:app','--host','127.0.0.1','--port','8001'],{env:{...process.env,AE_DB:path.join(temp,'test.sqlite')},stdio:'ignore'});
 let browser,server;
 try{
  for(let i=0;i<60;i++){try{const r=await fetch('http://127.0.0.1:8001/health');if(r.ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
  server=http.createServer((req,res)=>{const file=path.join(process.cwd(),'app/src/main/assets',req.url==='/'?'index.html':req.url);try{res.setHeader('Content-Type',file.endsWith('.js')?'application/javascript':file.endsWith('.css')?'text/css':file.endsWith('.json')?'application/json':'text/html');res.end(fs.readFileSync(file));}catch{res.writeHead(404);res.end();}});await new Promise(r=>server.listen(8081,'127.0.0.1',r));
  browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});
  const page=await browser.newPage({viewport:{width:393,height:851}});const errors=[];page.on('pageerror',e=>errors.push(e.message));
  // HTTPS origin is simulated, while all grading/SQLite operations use the actual local API.
  await page.route('https://cohort.test/**',async route=>{const response=await route.fetch({url:route.request().url().replace('https://cohort.test','http://127.0.0.1:8001')});await route.fulfill({response,headers:{...response.headers(),'access-control-allow-origin':'http://127.0.0.1:8081'}});});
  await page.goto('http://127.0.0.1:8081');await page.getByText('A little closer').waitFor();await page.locator('[data-tab="ranks"]').click();await page.locator('#cohort-url').fill('https://cohort.test/');await page.locator('#cohort-name').fill('Integration Cadet');await page.getByRole('button',{name:'Join cohort'}).click();await page.getByRole('button',{name:'Start 20-question challenge'}).waitFor();await page.getByRole('button',{name:'Start 20-question challenge'}).click();
  let expected=0;for(let i=0;i<20;i++){const choice=page.locator('[data-choice]').first();if(await choice.getAttribute('data-choice')==='0')expected++;await choice.click();await page.locator('[data-action="next"]').click();}
  await page.getByText('Another step forward.').waitFor();await page.getByText('Cohort score recorded:',{exact:false}).waitFor();const local=await page.evaluate(()=>JSON.parse(localStorage.getItem('ae-prepware-v1')));assert.equal(local.history[0].correct,expected);
  const leaderboard=await (await fetch('http://127.0.0.1:8001/leaderboard')).json();assert.equal(leaderboard.entries[0].points,expected);assert.equal(leaderboard.entries[0].attempts,20);
  await page.locator('[data-tab="ranks"]').click();await page.getByRole('button',{name:'Refresh ↻'}).click();await page.getByText('Integration Cadet',{exact:true}).waitFor();await page.screenshot({path:'artifacts/06-cohort.png',fullPage:true});
  assert.deepEqual(errors,[]);console.log('PASS cohort UI → real local API → SQLite → leaderboard; HTTPS origin simulated; score='+expected+'/20');
 }finally{if(browser)await browser.close();if(server)server.close();api.kill();fs.rmSync(temp,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exit(1)});
