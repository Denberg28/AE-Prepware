(function(root,factory){const api=factory();if(typeof module==='object')module.exports=api;else root.Accounts=api;})(globalThis,function(){
'use strict';
const INDEX='ae-account-index-v1',ACTIVE='ae-active-account-v1',GUEST='ae-prepware-v1';
const key=number=>number?'ae-profile-'+number:GUEST;
const normalize=code=>String(code).replace(/[\s-]/g,'').toLowerCase();
async function digest(code){return Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(normalize(code))))).map(x=>x.toString(16).padStart(2,'0')).join('');}
function index(store){const raw=store.getItem(INDEX);if(!raw)return [];const list=JSON.parse(raw);if(!Array.isArray(list)||list.length>10||list.some(p=>!/^AE-\d{16}$/.test(p.number)||typeof p.name!=='string'||!/^[a-f0-9]{64}$/.test(p.verifier)))throw Error('Account directory is unreadable. Export recovery data before clearing storage.');return list;}
function active(store){const n=store.getItem(ACTIVE);if(!n)return null;if(!index(store).some(p=>p.number===n))throw Error('Saved account was not found.');return n;}
function randomHex(){return Array.from(crypto.getRandomValues(new Uint8Array(32))).map(x=>x.toString(16).padStart(2,'0')).join('');}
async function create(store,state,name){
 const profiles=index(store);if(profiles.length>=10)throw Error('This device already has 10 accounts. Use an existing account.');
 name=name.trim();if(!/^[\p{L}\p{N} ._-]{2,30}$/u.test(name))throw Error('Use a display name of 2–30 letters, numbers, spaces, dots, underscores or hyphens.');
 let number;do{number='AE-'+Array.from(crypto.getRandomValues(new Uint8Array(16))).map(x=>x%10).join('');}while(profiles.some(p=>p.number===number));
 const recovery=randomHex(),profile={number,name,verifier:await digest(recovery)};
 const next=structuredClone(state);next.name=name;next.accountNumber=number;next.cohort=null;next.pending=[];
 // Existing summaries stay local; old guest results cannot become ranked attempts.
 next.history=next.history.map(h=>({...h,accountNumber:number}));
 store.setItem(key(number),JSON.stringify(next));store.setItem(INDEX,JSON.stringify([...profiles,profile]));store.setItem(ACTIVE,number);
 return {state:next,number,recovery};
}
async function login(store,number,recovery){
 const p=index(store).find(x=>x.number===number);
 if(!p||p.verifier!==await digest(recovery))throw Error('Account number or recovery code is incorrect.');
 const raw=store.getItem(key(number));if(!raw)throw Error('Local account data is missing. Restore its backup.');
 return JSON.parse(raw);
}
async function remember(store,number,name,recovery,state){
 const list=index(store);if(!list.some(p=>p.number===number)&&list.length>=10)throw Error('This device already has 10 accounts.');
 const profile={number,name,verifier:await digest(recovery)};
 store.setItem(key(number),JSON.stringify(state));store.setItem(INDEX,JSON.stringify([...list.filter(p=>p.number!==number),profile]));store.setItem(ACTIVE,number);
}
return {INDEX,ACTIVE,GUEST,key,normalize,index,active,digest,create,login,remember};
});
