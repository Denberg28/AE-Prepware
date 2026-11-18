const {chromium}=require('playwright'),http=require('node:http'),fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const root=path.resolve('app/src/main/assets');
const server=http.createServer((req,res)=>{try{const file=path.join(root,req.url==='/'?'index.html':req.url);res.setHeader('Content-Type',file.endsWith('.js')?'application/javascript':file.endsWith('.css')?'text/css':file.endsWith('.json')?'application/json':'text/html');res.end(fs.readFileSync(file));}catch{res.writeHead(404);res.end();}});
(async()=>{let browser;try{
 fs.mkdirSync('artifacts',{recursive:true});await new Promise(r=>server.listen(8091,'127.0.0.1',r));
 browser=await chromium.launch({headless:true,...(process.env.CHROMIUM_PATH?{executablePath:process.env.CHROMIUM_PATH}:{}),args:['--no-sandbox']});
 const page=await browser.newPage({viewport:{width:393,height:760}}),errors=[];page.on('pageerror',e=>errors.push(e.message));
 await page.goto('http://127.0.0.1:8091');await page.locator('[data-screen=subjects]').waitFor();assert.equal(await page.locator('[data-panel=practice]').getAttribute('open'),null);assert.equal(await page.locator('#study-scope').isVisible(),false);await page.locator('[data-panel=practice] > summary').click();
 for(const label of ['Subjects','Results','Ranking','Account'])await page.locator('nav').getByRole('button',{name:label,exact:true}).waitFor();
 await page.locator('#study-scope').selectOption('full');assert.equal(await page.locator('[data-panel=practice]').getAttribute('open'),'');await page.locator('#study-scope').selectOption('focus');await page.locator('[data-source=IN]').check();assert.equal(await page.locator('[data-panel=practice]').getAttribute('open'),'');await page.locator('[data-source=AI]').uncheck();
 await page.locator('.availability-note').waitFor();assert.equal(await page.locator('[data-subject]:not(:disabled)').count(),0);
 await page.locator('[data-source=AI]').check();await page.locator('[data-source=IN]').uncheck();assert.equal(await page.locator('.availability-note').count(),0);await page.locator('[data-panel=practice] > summary').click();
 for(const theme of ['light','dark']){
  if(await page.locator('html').getAttribute('data-theme')!==theme)await page.locator('#theme-toggle').click();
  for(const [width,height]of [[320,480],[393,760],[720,480]]){
   await page.setViewportSize({width,height});await page.locator('nav [data-tab=home]').click();
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth&&scrollY===0));
   const boxes=await page.locator('header button').evaluateAll(nodes=>nodes.map(x=>{const r=x.getBoundingClientRect();return {x:r.x,right:r.right,height:r.height};}));
   assert.ok(boxes.every(b=>b.x>=0&&b.right<=width&&b.height>=44),JSON.stringify(boxes));
   await page.screenshot({path:'artifacts/ui-subjects-'+theme+'-'+width+'.png'});
  }
 }
 await page.setViewportSize({width:393,height:760});
 await page.locator('[data-subject=math]').click();assert.equal(await page.evaluate(()=>document.activeElement.className),'question');
 await page.locator('[data-choice="1"]').click();assert.equal(await page.locator('.choice.selected').count(),1);await page.locator('.choice-selection').getByText('Your answer',{exact:true}).waitFor();
 assert.ok(await page.evaluate(()=>document.activeElement.classList.contains('feedback')));
 // Tab from feedback reaches the collapsed explanation, then next question.
 await page.keyboard.press('Tab');assert.equal(await page.evaluate(()=>document.activeElement.tagName),'SUMMARY');
 await page.locator('[data-action=next]').click();assert.equal(await page.evaluate(()=>document.activeElement.className),'question');
 await page.locator('nav [data-tab=home]').click();await page.locator('[data-subject=aero]').click();await page.locator('#modal').waitFor();
 assert.equal(await page.locator('#modal').getAttribute('aria-labelledby'),'modal-title');await page.locator('#cancel').click();
 await page.locator('nav [data-tab=progress]').click();await page.locator('[data-panel=monitoring] > summary').click();
 const math=page.locator('.readiness-subject').filter({has:page.getByRole('heading',{name:'Mathematics',exact:true})});
 await math.getByRole('button',{name:'New-item check',exact:true}).click();await page.locator('#confirm').click();
 await page.locator('[data-choice="1"]').click();
 assert.equal(await page.locator('.choice.selected').count(),1);assert.equal(await page.locator('.choice.correct,.choice.wrong,.feedback,details.explanation').count(),0);
 assert.ok(await page.evaluate(()=>document.activeElement.classList.contains('answer-saved')));
 const snapshot=await page.evaluate(()=>structuredClone(state.session));await page.reload();await page.locator('[data-action=resume]').click();
 assert.deepEqual(await page.evaluate(()=>state.session),snapshot);assert.equal(await page.locator('.choice-selection').innerText(),'Your answer');
 await page.screenshot({path:'artifacts/ui-saved-check.png'});
 // Enlarged text can wrap the header and remains reachable without horizontal scroll.
 await page.setViewportSize({width:320,height:480});await page.evaluate(()=>document.documentElement.style.fontSize='24px');
 await page.locator('nav [data-tab=home]').click();assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
 await page.getByRole('button',{name:'Settings',exact:true}).click();await page.locator('[data-action=export-bank]').scrollIntoViewIfNeeded();assert.ok(await page.locator('[data-action=export-bank]').isVisible());
 assert.deepEqual(errors,[]);console.log('PASS UI: labeled navigation, unavailable-pool recovery, both themes at 320/393/720px, header reachability, keyboard focus, accessible dialog, selected deferred answer without grade disclosure, resume and enlarged text.');
 }finally{if(browser)await browser.close();server.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
