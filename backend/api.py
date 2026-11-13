"""Opt-in, practice-only cohort service. Run behind HTTPS; one SQLite worker."""
import hashlib
import json
import os
import secrets
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, StrictInt, ConfigDict
from .bank import load_bank

class Participant(BaseModel):
    model_config=ConfigDict(extra='forbid')
    name: str=Field(min_length=2,max_length=30,pattern=r'^[\w .-]+$')
class Answer(BaseModel):
    model_config=ConfigDict(extra='forbid')
    id: str=Field(min_length=1,max_length=64)
    choice: StrictInt=Field(ge=0,le=3)
class Submission(BaseModel):
    model_config=ConfigDict(extra='forbid')
    answers:list[Answer]=Field(min_length=20,max_length=20)

def create_app(db_path=None, bank_path=None, clock=time.time, lifespan=None):
    bank=load_bank(bank_path or os.getenv('AE_BANK'))
    question_map={q['id']:q for q in bank['questions']}
    path=str(db_path or os.getenv('AE_DB','ae-prepware.sqlite'))
    @contextmanager
    def db():
        conn=sqlite3.connect(path,timeout=5)
        conn.row_factory=sqlite3.Row
        conn.execute('PRAGMA foreign_keys=ON')
        try:
            with conn:yield conn
        finally:conn.close()
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS participants(id TEXT PRIMARY KEY, name TEXT NOT NULL, token_hash TEXT NOT NULL UNIQUE, created REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS challenges(id TEXT PRIMARY KEY, participant TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE, questions TEXT NOT NULL, created REAL NOT NULL, result TEXT, bank_version TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS credits(participant TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE, day TEXT NOT NULL, question TEXT NOT NULL, PRIMARY KEY(participant,day,question));
        CREATE TABLE IF NOT EXISTS submissions(challenge TEXT PRIMARY KEY REFERENCES challenges(id) ON DELETE CASCADE, participant TEXT NOT NULL REFERENCES participants(id) ON DELETE CASCADE, score INTEGER NOT NULL, total INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS rate_limits(bucket TEXT PRIMARY KEY, start REAL NOT NULL, count INTEGER NOT NULL);
        ''')
    app=FastAPI(title='AE Prepware Cohort',version='0.8.2-rc.1',lifespan=lifespan,docs_url=None,redoc_url=None)
    app.add_middleware(CORSMiddleware,allow_origins=['https://appassets.androidplatform.net']+([os.environ['AE_DEV_ORIGIN']] if os.getenv('AE_DEV_ORIGIN') else []),allow_methods=['GET','POST','OPTIONS'],allow_headers=['Authorization','Content-Type'])
    @app.middleware('http')
    async def limit_body(request:Request,call_next):
        from starlette.responses import JSONResponse
        if bank.get('distribution')=='private-study' and request.url.path.split('/')[1] in ('participants','challenges','leaderboard'):
            return JSONResponse({'detail':'Legacy public cohort routes are disabled on private bank hosts.'},status_code=403)
        try: size=int(request.headers.get('content-length','0') or 0)
        except ValueError: return JSONResponse({'detail':'Invalid content length'},status_code=400)
        maximum=1_000_000 if request.url.path=='/accounts/snapshot' else 16000
        if size>maximum:
            return JSONResponse({'detail':'Request too large'},status_code=413)
        # Enforce actual body size too, including chunked requests.
        if request.method=='POST':
            body=b''
            async for chunk in request.stream():
                body+=chunk
                if len(body)>maximum:return JSONResponse({'detail':'Request too large'},status_code=413)
            request._body=body
        response=await call_next(request)
        response.headers['Cache-Control']='no-store'
        response.headers['X-Content-Type-Options']='nosniff'
        return response
    def rate(key,limit,seconds):
        now=clock()
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            c.execute('DELETE FROM rate_limits WHERE start<?',(now-86400,))
            row=c.execute('SELECT * FROM rate_limits WHERE bucket=?',(key,)).fetchone()
            if row and now-row['start']<seconds:
                if row['count']>=limit:raise HTTPException(429,'Too many requests. Try later.')
                c.execute('UPDATE rate_limits SET count=count+1 WHERE bucket=?',(key,))
            else:c.execute('INSERT OR REPLACE INTO rate_limits VALUES(?,?,1)',(key,now))
    def identity(authorization:str=Header(default='')):
        if not authorization.startswith('Bearer ') or len(authorization)>120:raise HTTPException(401,'Join the cohort first.')
        token_hash=hashlib.sha256(authorization[7:].encode()).hexdigest()
        with db() as c:row=c.execute('SELECT * FROM participants WHERE token_hash=?',(token_hash,)).fetchone()
        if not row:raise HTTPException(401,'Participant credentials are invalid.')
        return dict(row)
    @app.get('/health')
    def health():return {'schema':1,'bankVersion':bank['version'],'version':'0.8.2-rc.1','capabilities':['snapshot-v1','bank-pull','faculty-monitoring']}
    @app.post('/participants',status_code=201)
    def join(body:Participant,request:Request):
        rate('join:'+hashlib.sha256((request.client.host if request.client else 'unknown').encode()).hexdigest(),60,3600)
        if not body.name.strip():raise HTTPException(422,'Choose a display name.')
        token=secrets.token_urlsafe(32);pid=secrets.token_hex(12)
        with db() as c:c.execute('INSERT INTO participants VALUES(?,?,?,?)',(pid,body.name.strip(),hashlib.sha256(token.encode()).hexdigest(),clock()))
        return {'id':pid,'token':token}
    @app.get('/leaderboard')
    def leaderboard():
        with db() as c:
            rows=c.execute('''SELECT p.id,p.name,COALESCE(cr.points,0) AS points,COALESCE(s.correct,0) AS correct,COALESCE(s.attempts,0) AS attempts FROM participants p
            LEFT JOIN (SELECT participant,COUNT(*) AS points FROM credits GROUP BY participant) cr ON cr.participant=p.id
            LEFT JOIN (SELECT participant,SUM(score) AS correct,SUM(total) AS attempts FROM submissions GROUP BY participant) s ON s.participant=p.id
            WHERE s.attempts>0 ORDER BY points DESC, correct DESC, p.created ASC LIMIT 100''').fetchall()
        return {'entries':[dict(x) for x in rows],'dayTimezone':'Asia/Manila'}
    @app.post('/challenges',status_code=201)
    def challenge(who=Depends(identity)):
        rate('challenge:'+who['id'],12,3600)
        # One resumable challenge per participant; abandoned items expire in 24 hours.
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            c.execute('DELETE FROM challenges WHERE result IS NULL AND created<?',(clock()-86400,))
            old=c.execute('SELECT * FROM challenges WHERE participant=? AND result IS NULL AND bank_version=?',(who['id'],bank['version'])).fetchone()
            if old:ids=json.loads(old['questions']);cid=old['id']
            else:
                ids=[]
                for s in bank['subjects']:
                    pool=[q['id'] for q in bank['questions'] if q['subject']==s['id'] and q.get('active', True)]
                    quota=s['weight']//5
                    if len(pool)<quota:raise HTTPException(409,'Bank has insufficient questions for a weighted challenge.')
                    ids+=secrets.SystemRandom().sample(pool,quota)
                secrets.SystemRandom().shuffle(ids);cid=secrets.token_hex(16)
                c.execute('INSERT INTO challenges VALUES(?,?,?,?,NULL,?)',(cid,who['id'],json.dumps(ids),clock(),bank['version']))
        return {'id':cid,'bankVersion':bank['version'],'questions':[{k:q[k] for k in ('id','subject','topic','prompt','choices')} for q in (question_map[i] for i in ids)]}
    @app.post('/challenges/{cid}/submit')
    def submit(cid:str,body:Submission,who=Depends(identity)):
        rate('submit:'+who['id'],60,3600)
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute('SELECT * FROM challenges WHERE id=? AND participant=?',(cid,who['id'])).fetchone()
            if not row:raise HTTPException(404,'Challenge not found.')
            if row['result']:return json.loads(row['result'])
            if row['bank_version']!=bank['version']:raise HTTPException(409,'Bank changed. Start a new challenge.')
            if clock()-row['created']>86400:raise HTTPException(410,'Challenge expired. Start a new challenge.')
            ids=json.loads(row['questions']);answers={a.id:a.choice for a in body.answers}
            if len(answers)!=20 or set(answers)!=set(ids):raise HTTPException(422,'Answer each challenge question exactly once.')
            if any(answers[i]>=len(question_map[i]['choices']) for i in ids):raise HTTPException(422,'Answer choice does not exist.')
            day=datetime.fromtimestamp(clock(),ZoneInfo('Asia/Manila')).strftime('%Y-%m-%d')
            correct=[i for i in ids if answers[i]==question_map[i]['answer']]
            credited=0
            for i in correct:
                cursor=c.execute('INSERT OR IGNORE INTO credits VALUES(?,?,?)',(who['id'],day,i));credited+=cursor.rowcount
            result={'score':len(correct),'total':20,'credited':credited,'day':day,'review':[{k:question_map[i][k] for k in ('id','answer','explanation','source')} for i in ids]}
            c.execute('INSERT INTO submissions VALUES(?,?,?,20)',(cid,who['id'],len(correct)))
            c.execute('UPDATE challenges SET result=? WHERE id=?',(json.dumps(result),cid))
        return result
    @app.post('/participants/delete')
    def delete(who=Depends(identity)):
        with db() as c:c.execute('DELETE FROM participants WHERE id=?',(who['id'],))
        return {'deleted':True}
    from .accounts import attach_accounts
    attach_accounts(app,db,rate,clock,bank)
    return app

app=create_app()
