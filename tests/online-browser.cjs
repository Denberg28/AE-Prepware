const {spawn}=require('node:child_process'),{chromium}=require('playwright'),fs=require('node:fs'),os=require('node:os'),path=require('node:path'),assert=require('node:assert/strict');
(async()=>{
 const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'ae-combined-'));
 const server=spawn(process.env.AE_PYTHON||path.join(process.cwd(),'.venv/bin/python'),['-m','uvicorn','online:app','--host','127.0.0.1','--port','18083'],{env:{...process.env,AE_DB:path.join(tmp,'test.sqlite'),AE_BANK:'',GEMINI_API_KEY:''},stdio:'ignore'});
 let browser;
 try{
  let ready=false;for(let i=0;i<100;i++){try{if((await fetch('http://127.0.0.1:18083/health')).ok){ready=true;break;}}catch{}await new Promise(r=>setTimeout(r,100));}assert.ok(ready,'Combined ASGI service started');
  browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});
  const page=await browser.newPage();await page.goto('http://127.0.0.1:18083/dashboard/');
  await page.getByRole('tab',{name:'Board readiness',exact:true}).waitFor({timeout:25000});
  assert.deepEqual(await page.getByRole('tab').allTextContents(),['Coursework','Question review','Cohort','Board readiness']);
  await page.getByRole('tab',{name:'Board readiness',exact:true}).click();await page.getByText('Board Readiness Monitoring System',{exact:true}).waitFor();
  const health=await (await fetch('http://127.0.0.1:18083/health')).json();assert.ok(health.capabilities.includes('snapshot-v1'));
  assert.equal((await fetch('http://127.0.0.1:18083/accounts/snapshot')).status,401);
  await page.screenshot({path:'artifacts/17-streamlit-online.png'});
  console.log('PASS combined host: Streamlit tabs and live WebSocket render under /dashboard; root health/sync API responds; owner snapshot requires authentication. Local HTTP only; no production TLS claim.');
 }finally{if(browser)await browser.close();server.kill();fs.rmSync(tmp,{recursive:true,force:true});}
})().catch(e=>{console.error(e);process.exitCode=1;});
