/* Bank bytes use IndexedDB so large private guide imports do not exhaust the
   small localStorage quota shared by account progress. Legacy banks still read. */
(function(root){
'use strict';
let connection;
function database(){if(!connection)connection=new Promise((resolve,reject)=>{const request=indexedDB.open('ae-prepware-banks-v1',1);request.onupgradeneeded=()=>request.result.createObjectStore('banks');request.onsuccess=()=>resolve(request.result);request.onerror=()=>{connection=null;reject(Error('Question bank storage could not be opened. Your data is preserved.'));};request.onblocked=()=>{connection=null;reject(Error('Close other Prepware windows before updating bank storage.'));};});return connection;}
async function read(key){const legacy=localStorage.getItem(key);if(legacy!==null)return legacy;const db=await database();return new Promise((resolve,reject)=>{const tx=db.transaction('banks','readonly'),r=tx.objectStore('banks').get(key);r.onsuccess=()=>resolve(r.result??null);r.onerror=()=>reject(Error('Question bank could not be read.'));});}
async function write(key,value){const db=await database();await new Promise((resolve,reject)=>{const tx=db.transaction('banks','readwrite');tx.objectStore('banks').put(value,key);tx.oncomplete=()=>resolve();tx.onabort=tx.onerror=()=>reject(Error('Question bank could not be saved. Free device storage and export a backup.'));});localStorage.removeItem(key);}
async function remove(key){const db=await database();await new Promise((resolve,reject)=>{const tx=db.transaction('banks','readwrite');tx.objectStore('banks').delete(key);tx.oncomplete=resolve;tx.onabort=tx.onerror=()=>reject(Error('Question bank could not be reset.'));});localStorage.removeItem(key);}
root.BankStore={read,write,remove};
})(globalThis);
