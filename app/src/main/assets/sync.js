(function(root,factory){const api=factory();if(typeof module==='object')module.exports=api;else root.CloudSync=api;})(globalThis,function(){
'use strict';
const fields=['schema','name','stats','daily','bookmarks','flags','history','session','selection','sourceMode','studyScope','monitoring','accountNumber'];
function projection(state){return structuredClone(Object.fromEntries(fields.filter(k=>state[k]!==undefined).map(k=>[k,state[k]])));}
function canonical(x){return Array.isArray(x)?x.map(canonical):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,canonical(x[k])])):x;}
function sameBank(a,b){return JSON.stringify(canonical(a))===JSON.stringify(canonical(b));}
function acknowledgement(body,response){if(!response?.saved||response.operation!==body.operation||!Number.isInteger(response.revision)||response.revision<1)throw Error('Backup acknowledgement is invalid. The queued upload is preserved.');return response.revision;}
function restore(backup,profile,number){
 if(backup.state?.accountNumber!==number||profile.number!==number)throw Error('Online backup belongs to a different account.');
 const next=structuredClone(backup.state),known=new Set(next.history.map(h=>h.id));
 // A result may have reached the grading service before a failed backup upload.
 // Retain its server record without discarding the journal or unfinished check.
 next.history=[...next.history,...profile.history.filter(h=>!known.has(h.id))].sort((a,b)=>b.date-a.date).slice(0,200);
 for(const [id,p]of Object.entries(profile.stats))if(!next.stats[id]||p.seen>next.stats[id].seen)next.stats[id]=structuredClone(p);
 next.cloudRevision=backup.revision;next.shareReadiness=!!backup.share;next.rankOptIn=!!profile.rankOptIn;next.pending=[];
 return next;
}
return {projection,sameBank,acknowledgement,restore};
});
