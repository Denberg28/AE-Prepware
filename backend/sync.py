"""Owner-only offline backups, explicit faculty sharing and authenticated bank pulls."""
import hashlib
import json
import os
import secrets
from fastapi import Depends, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from .readiness_reports import analyze_report, cohort_rows

FIELDS={'schema','name','stats','daily','bookmarks','flags','history','session','selection','sourceMode','studyScope','monitoring','accountNumber'}


class Snapshot(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    operation: str=Field(pattern=r'^[a-f0-9-]{36}$')
    expectedRevision: int=Field(ge=0)
    bankVersion: str=Field(min_length=1,max_length=100)
    state: dict
    share: bool=False
    report: dict|None=None

class Preferences(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    rankOptIn: bool


def validate_snapshot(state,questions,number):
    if set(state)-FIELDS or state.get('schema')!=1 or state.get('accountNumber')!=number or not isinstance(state.get('name'),str) or len(state['name'])>40:raise ValueError('Invalid profile snapshot')
    for field in ('stats','daily'):
        if not isinstance(state.get(field),dict) or len(state[field])>(3000 if field=='stats' else 3660):raise ValueError('Invalid progress records')
    for field in ('bookmarks','flags'):
        values=state.get(field)
        if not isinstance(values,list) or len(values)>3000 or any(not isinstance(i,str) or i not in questions for i in values):raise ValueError('Unknown saved question')
    for qid,p in state['stats'].items():
        if qid not in questions or not isinstance(p,dict) or any(type(p.get(k)) is not int or p[k]<0 for k in ('seen','correct','streak')) or p['seen']<1 or p['correct']>p['seen'] or any(type(p.get(k)) not in (int,float) for k in ('last','due')):raise ValueError('Invalid question progress')
    for d,p in state['daily'].items():
        if not isinstance(d,str) or len(d)!=10 or not isinstance(p,dict):raise ValueError('Invalid daily activity')
        for field in ('answered','correct'):
            if not isinstance(p.get(field),list) or len(p[field])>3000 or any(not isinstance(i,str) or i not in questions for i in p[field]):raise ValueError('Invalid daily questions')
        if not set(p['correct'])<=set(p['answered']):raise ValueError('Invalid daily correctness')
    history=state.get('history')
    if not isinstance(history,list) or len(history)>200:raise ValueError('Invalid history')
    for h in history:
        if not isinstance(h,dict) or type(h.get('total')) is not int or not 1<=h['total']<=100 or type(h.get('correct')) is not int or not 0<=h['correct']<=h['total']:raise ValueError('Invalid result')
        if h.get('ids'):
            ids=h['ids'];answers=h.get('answers')
            if not isinstance(ids,list) or len(ids)!=h['total'] or not isinstance(answers,list) or len(answers)!=len(ids) or any(not isinstance(i,str) or i not in questions for i in ids):raise ValueError('Invalid historical IDs')
            if any(type(a) is not int or not 0<=a<len(questions[i]['choices']) for i,a in zip(ids,answers)) or h['correct']!=sum(questions[i]['answer']==a for i,a in zip(ids,answers)):raise ValueError('Historical grade differs from keys')
    # This is an opaque private backup, not authority for ranking or readiness.
    # Full client validation runs again before restore; bounded size is enforced at HTTP ingress.
    if state.get('session') is not None and not isinstance(state['session'],dict):raise ValueError('Invalid unfinished session')
    if state.get('monitoring') is not None and (not isinstance(state['monitoring'],dict) or state['monitoring'].get('schema')!=1):raise ValueError('Invalid monitoring journal')


def attach_sync(app,db,identity,bank,versions,rate,clock):
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS account_snapshots(account TEXT PRIMARY KEY REFERENCES study_accounts(number) ON DELETE CASCADE,revision INTEGER NOT NULL,bank_version TEXT NOT NULL,state TEXT NOT NULL,report TEXT,shared INTEGER NOT NULL,updated REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS sync_writes(account TEXT NOT NULL REFERENCES study_accounts(number) ON DELETE CASCADE,operation TEXT NOT NULL,digest TEXT NOT NULL,revision INTEGER NOT NULL,created REAL NOT NULL,PRIMARY KEY(account,operation));
        ''')

    @app.post('/accounts/preferences')
    def preferences(body:Preferences,who=Depends(identity)):
        rate('preferences:'+who['number'],60,3600)
        with db() as c:c.execute('UPDATE study_accounts SET ranked=? WHERE number=?',(int(body.rankOptIn),who['number']))
        return {'rankOptIn':body.rankOptIn}

    @app.get('/accounts/snapshot')
    def snapshot(who=Depends(identity)):
        with db() as c:row=c.execute('SELECT * FROM account_snapshots WHERE account=?',(who['number'],)).fetchone()
        if not row:return {'revision':0,'state':None}
        return {'revision':row['revision'],'bankVersion':row['bank_version'],'state':json.loads(row['state']),'share':bool(row['shared']),'updatedAt':row['updated']*1000}

    @app.post('/accounts/snapshot')
    def store(body:Snapshot,who=Depends(identity)):
        rate('snapshot:'+who['number'],60,3600)
        if body.bankVersion not in versions:raise HTTPException(409,'Snapshot bank version is unknown. Keep the offline backup and use the matching service.')
        try:
            validate_snapshot(body.state,versions[body.bankVersion],who['number'])
            if body.share:
                if body.report is None:raise ValueError('A shared readiness report is required')
                analyze_report(json.dumps(body.report).encode(),now=clock()*1000)
        except (ValueError,KeyError,TypeError,OverflowError):raise HTTPException(422,'Invalid offline snapshot or readiness report') from None
        try:canonical=json.dumps(body.model_dump(),sort_keys=True,separators=(',',':'),allow_nan=False)
        except (ValueError,TypeError):raise HTTPException(422,'Snapshot contains invalid values') from None
        digest=hashlib.sha256(canonical.encode()).hexdigest()
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            old=c.execute('SELECT * FROM sync_writes WHERE account=? AND operation=?',(who['number'],body.operation)).fetchone()
            if old:
                if old['digest']!=digest:raise HTTPException(409,'This sync operation already has different data.')
                return {'revision':old['revision'],'operation':body.operation,'saved':True}
            current=c.execute('SELECT revision FROM account_snapshots WHERE account=?',(who['number'],)).fetchone();revision=current['revision'] if current else 0
            if body.expectedRevision!=revision:raise HTTPException(409,'A newer online backup exists. Offline data is preserved. Review Restore online backup before replacing it.')
            revision+=1
            c.execute('INSERT OR REPLACE INTO account_snapshots VALUES(?,?,?,?,?,?,?)',(who['number'],revision,body.bankVersion,json.dumps(body.state),json.dumps(body.report) if body.share else None,int(body.share),clock()))
            c.execute('INSERT INTO sync_writes VALUES(?,?,?,?,?)',(who['number'],body.operation,digest,revision,clock()))
            c.execute('DELETE FROM sync_writes WHERE account=? AND operation NOT IN (SELECT operation FROM sync_writes WHERE account=? ORDER BY created DESC,rowid DESC LIMIT 200)',(who['number'],who['number']))
        return {'revision':revision,'operation':body.operation,'saved':True}

    @app.get('/accounts/bank')
    def download_bank(who=Depends(identity)):
        rate('bank:'+who['number'],30,3600)
        if bank.get('distribution')=='private-study' and not (os.getenv('AE_ALLOW_PRIVATE_BANK_SYNC')=='true' and len(os.getenv('AE_ENROLLMENT_CODE',''))>=16 and who['enrolled']):raise HTTPException(403,'Private guide downloads require an instructor-controlled private service and enrollment. Connect again with the instructor enrollment code.')
        return bank

    @app.get('/faculty/monitoring')
    def faculty(authorization: str=Header(default='')):
        key=os.getenv('AE_FACULTY_SYNC_KEY','')
        if len(key)<32:raise HTTPException(503,'Online faculty monitoring is not configured')
        if not secrets.compare_digest(authorization.encode(),('Bearer '+key).encode()):raise HTTPException(401,'Faculty service authorization required')
        with db() as c:rows=c.execute('SELECT report FROM account_snapshots WHERE shared=1 ORDER BY updated DESC LIMIT 50').fetchall()
        reports=[]
        for row in rows:
            try:reports.append(analyze_report(row['report'].encode(),now=clock()*1000))
            except (ValueError,KeyError,TypeError):continue
        return {'entries':cohort_rows(reports),'evidence':'Voluntarily shared device reports; not proctored'}
