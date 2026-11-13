/* Device-wide appearance preference, independent of student profiles/results.
   Loaded before CSS so a saved dark theme does not flash a light page. */
(function(root){
'use strict';
const key='ae-prepware-theme-v1';
const moon='<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M20.7 13.1A8.6 8.6 0 0 1 10.9 3.3 8.8 8.8 0 1 0 20.7 13.1Z"/></svg>';
const sun='<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M4.9 4.9l1.4 1.4m11.4 11.4 1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/></svg>';
let theme='light',revision=0;
try{const saved=localStorage.getItem(key);if(saved==='light'||saved==='dark')theme=saved;}catch{}
function apply(value,persist=false){
 if(value!=='light'&&value!=='dark')return;
 theme=value;const stamp=++revision;document.documentElement.classList.add('theme-switching');document.documentElement.dataset.theme=value;
 requestAnimationFrame(()=>requestAnimationFrame(()=>{if(stamp===revision)document.documentElement.classList.remove('theme-switching');}));
 const meta=document.querySelector('meta[name="theme-color"]');if(meta)meta.content=value==='dark'?'#141d2b':'#ffffff';
 const button=document.getElementById('theme-toggle');
 if(button){button.innerHTML=value==='dark'?sun:moon;const label=value==='dark'?'Switch to light theme':'Switch to dark theme';button.setAttribute('aria-label',label);button.title=label;button.setAttribute('aria-pressed',String(value==='dark'));}
 let saved=true;if(persist){try{localStorage.setItem(key,value);}catch{saved=false;}}
 try{if(root.AndroidFiles&&typeof root.AndroidFiles.setTheme==='function')root.AndroidFiles.setTheme(value);}catch{}
 const status=document.getElementById('theme-status');if(status&&persist)status.textContent=(value==='dark'?'Dark':'Light')+' theme'+(saved?'':' for this session');
}
apply(theme);
document.addEventListener('DOMContentLoaded',()=>{apply(theme);document.getElementById('theme-toggle')?.addEventListener('click',()=>apply(theme==='light'?'dark':'light',true));});
root.Appearance={apply,current:()=>theme};
})(globalThis);
