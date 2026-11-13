"""Recoverable practice accounts, server-graded offline results, optional AI selection."""
import hashlib
import json
import os
import re
import secrets
from datetime import datetime
from zoneinfo import ZoneInfo
import httpx
from fastapi import Depends, Header, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, StrictInt, field_validator
from .bank import SUBJECTS

class Credentials(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    number: str = Field(pattern=r'^AE-[0-9]{16}$')
    recovery: str = Field(pattern=r'^[a-f0-9]{64}$')

class Registration(Credentials):
    name: str = Field(min_length=2, max_length=30, pattern=r'^[\w .-]+$')
    enrollment: str = Field(default='',max_length=200)
    rankOptIn: bool = True  # Legacy registration represented joining the ranked cohort.

class StudyAnswer(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    id: str = Field(min_length=1, max_length=64)
    choice: StrictInt = Field(ge=0, le=3)

class StudyResult(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    id: str = Field(pattern=r'^[A-Za-z0-9_-]{1,64}$')
    bankVersion: str = Field(min_length=1, max_length=100)
    subject: str = Field(min_length=1, max_length=30)
    answers: list[StudyAnswer] = Field(min_length=20, max_length=50)

    @field_validator('answers')
    @classmethod
    def supported_length(cls, value):
        if len(value) not in (20,50):
            raise ValueError('A study result must contain 20 or 50 answers')
        return value

class Selection(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    subject: str = Field(min_length=1, max_length=30)
    ai: bool = False
    sourceMode: str = Field(default='AI', pattern=r'^(AI|IN|hybrid)$')
    scope: str = Field(default='full', pattern=r'^(focus|full)$')


def recovery_hash(code, salt):
    return hashlib.scrypt(code.encode(), salt=bytes.fromhex(salt), n=16384, r=8, p=1, maxmem=64*1024*1024, dklen=32).hex()


def attach_accounts(app, db, rate, clock, bank):
    questions = {q['id']: q for q in bank['questions']}
    with db() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS study_accounts(number TEXT PRIMARY KEY,name TEXT NOT NULL,salt TEXT NOT NULL,recovery_hash TEXT NOT NULL,created REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS account_tokens(token_hash TEXT PRIMARY KEY,account TEXT NOT NULL REFERENCES study_accounts(number) ON DELETE CASCADE,created REAL NOT NULL);
        CREATE TABLE IF NOT EXISTS study_results(account TEXT NOT NULL REFERENCES study_accounts(number) ON DELETE CASCADE,id TEXT NOT NULL,payload TEXT NOT NULL,result TEXT NOT NULL,created REAL NOT NULL,PRIMARY KEY(account,id));
        CREATE TABLE IF NOT EXISTS account_progress(account TEXT NOT NULL REFERENCES study_accounts(number) ON DELETE CASCADE,question TEXT NOT NULL,seen INTEGER NOT NULL,correct INTEGER NOT NULL,streak INTEGER NOT NULL,last REAL NOT NULL,PRIMARY KEY(account,question));
        CREATE TABLE IF NOT EXISTS account_credits(account TEXT NOT NULL REFERENCES study_accounts(number) ON DELETE CASCADE,day TEXT NOT NULL,question TEXT NOT NULL,PRIMARY KEY(account,day,question));
        CREATE TABLE IF NOT EXISTS bank_versions(version TEXT PRIMARY KEY,payload TEXT NOT NULL);
        ''')
        if 'ranked' not in {r['name'] for r in c.execute('PRAGMA table_info(study_accounts)')}:
            c.execute('ALTER TABLE study_accounts ADD COLUMN ranked INTEGER NOT NULL DEFAULT 1')
        if 'enrolled' not in {r['name'] for r in c.execute('PRAGMA table_info(study_accounts)')}:
            c.execute('ALTER TABLE study_accounts ADD COLUMN enrolled INTEGER NOT NULL DEFAULT 0')
        saved = c.execute('SELECT payload FROM bank_versions WHERE version=?', (bank['version'],)).fetchone()
        if saved and json.loads(saved['payload']) != bank:
            raise ValueError('Bank version already exists with different content; use a new version')
        # Archived keys support results queued before an append-only correction.
        archived = [json.loads(r['payload']) for r in c.execute('SELECT payload FROM bank_versions')]
        from .authoring import question_content
        for previous in archived:
            for q in previous['questions']:
                if q['id'] not in questions or question_content(previous, q) != question_content(bank, questions[q['id']]):
                    raise ValueError('Bank removes or mutates an archived question: ' + q['id'])
        c.execute('INSERT OR IGNORE INTO bank_versions VALUES(?,?)', (bank['version'], json.dumps(bank)))
    versions = {b['version']: {q['id']: q for q in b['questions']} for b in [*archived, bank]}

    def ip_bucket(request):
        return hashlib.sha256((request.client.host if request.client else 'unknown').encode()).hexdigest()

    def new_token(c, number):
        token = secrets.token_urlsafe(32)
        c.execute('DELETE FROM account_tokens WHERE created<?', (clock()-30*86400,))
        # At most five simultaneous devices per account, including the new one.
        old = c.execute('SELECT token_hash FROM account_tokens WHERE account=? ORDER BY created DESC', (number,)).fetchall()
        for row in old[4:]:
            c.execute('DELETE FROM account_tokens WHERE token_hash=?', (row['token_hash'],))
        c.execute('INSERT INTO account_tokens VALUES(?,?,?)', (hashlib.sha256(token.encode()).hexdigest(), number, clock()))
        return token

    def identity(authorization: str = Header(default='')):
        if not authorization.startswith('Bearer ') or len(authorization)>120:
            raise HTTPException(401, 'Sign in to your study account.')
        token_hash = hashlib.sha256(authorization[7:].encode()).hexdigest()
        with db() as c:
            row = c.execute('SELECT a.*,t.token_hash FROM study_accounts a JOIN account_tokens t ON a.number=t.account WHERE t.token_hash=? AND t.created>?', (token_hash, clock()-30*86400)).fetchone()
        if not row:
            raise HTTPException(401, 'Account session expired. Sign in with your recovery code.')
        return dict(row)

    def profile(c, number):
        who = c.execute('SELECT number,name,ranked FROM study_accounts WHERE number=?', (number,)).fetchone()
        history = [json.loads(x['result']) for x in c.execute('SELECT result FROM study_results WHERE account=? ORDER BY created DESC,id DESC LIMIT 200', (number,))]
        stats = {}
        for row in c.execute('SELECT * FROM account_progress WHERE account=?', (number,)):
            streak=row['streak']; interval=([1,3,7,14,30][min(streak-1,4)]*86400000 if streak else 600000)
            stats[row['question']]={'seen':row['seen'],'correct':row['correct'],'streak':streak,'last':row['last']*1000,'due':row['last']*1000+interval}
        return {'number':who['number'],'name':who['name'],'rankOptIn':bool(who['ranked']),'bankVersion':bank['version'],'history':history,'stats':stats,'supportsSnapshot':True}

    @app.post('/accounts/register', status_code=201)
    def register(body: Registration, request: Request):
        rate('account-register:'+ip_bucket(request), 20, 3600)
        if not body.name.strip():
            raise HTTPException(422, 'Choose a display name.')
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            existing=c.execute('SELECT * FROM study_accounts WHERE number=?', (body.number,)).fetchone()
            if existing:
                if not secrets.compare_digest(recovery_hash(body.recovery, existing['salt']), existing['recovery_hash']):
                    raise HTTPException(409, 'Account number is unavailable.')
            else:
                code=os.getenv('AE_ENROLLMENT_CODE','')
                if bank.get('distribution')=='private-study' and os.getenv('AE_ALLOW_PRIVATE_BANK_SYNC')=='true' and len(code)<16:raise HTTPException(503,'Private cohort enrollment is not configured')
                if code and not secrets.compare_digest(body.enrollment.encode(),code.encode()):raise HTTPException(403,'Instructor enrollment code required')
                salt=secrets.token_hex(16)
                c.execute('INSERT INTO study_accounts(number,name,salt,recovery_hash,created,ranked) VALUES(?,?,?,?,?,?)', (body.number,body.name.strip(),salt,recovery_hash(body.recovery,salt),clock(),int(body.rankOptIn)))
            token=new_token(c,body.number)
            enrollment=os.getenv('AE_ENROLLMENT_CODE','')
            if len(enrollment)>=16 and secrets.compare_digest(body.enrollment.encode(),enrollment.encode()):
                c.execute('UPDATE study_accounts SET enrolled=1 WHERE number=?',(body.number,))
            return {**profile(c,body.number),'token':token}

    @app.post('/accounts/login')
    def login(body: Credentials, request: Request):
        rate('account-login:'+ip_bucket(request), 20, 900)
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute('SELECT * FROM study_accounts WHERE number=?', (body.number,)).fetchone()
            salt=row['salt'] if row else '0'*32
            valid=recovery_hash(body.recovery,salt)
            if not row or not secrets.compare_digest(valid,row['recovery_hash']):
                raise HTTPException(401, 'Account number or recovery code is incorrect.')
            token=new_token(c,body.number)
            return {**profile(c,body.number),'token':token}

    @app.get('/accounts/me')
    def me(who=Depends(identity)):
        with db() as c:
            return profile(c,who['number'])

    @app.post('/accounts/logout')
    def logout(who=Depends(identity)):
        with db() as c:
            c.execute('DELETE FROM account_tokens WHERE token_hash=?', (who['token_hash'],))
        return {'signedOut':True}

    @app.post('/accounts/delete')
    def delete(who=Depends(identity)):
        with db() as c:
            c.execute('DELETE FROM study_accounts WHERE number=?', (who['number'],))
        return {'deleted':True}

    @app.post('/accounts/results')
    def record(body: StudyResult, who=Depends(identity)):
        rate('account-result:'+who['number'], 240, 3600)
        canonical=json.dumps(body.model_dump(),sort_keys=True,separators=(',',':'))
        with db() as c:
            c.execute('BEGIN IMMEDIATE')
            old=c.execute('SELECT payload,result FROM study_results WHERE account=? AND id=?', (who['number'],body.id)).fetchone()
            if old:
                if old['payload']!=canonical:
                    raise HTTPException(409, 'This session ID already has different answers.')
                return json.loads(old['result'])
            grading = versions.get(body.bankVersion)
            if grading is None:
                raise HTTPException(409, 'Question bank versions differ. Preserve the queued result and use the matching API bank.')
            ids=[a.id for a in body.answers]
            if body.subject not in SUBJECTS or len(set(ids))!=len(ids) or any(i not in grading or grading[i]['subject']!=body.subject for i in ids):
                raise HTTPException(422, 'Provide 20 or 50 distinct bank questions from the selected subject.')
            if any(a.choice >= len(grading[a.id]['choices']) for a in body.answers):
                raise HTTPException(422, 'Answer choice does not exist in this source question.')
            now=clock(); day=datetime.fromtimestamp(now,ZoneInfo('Asia/Manila')).strftime('%Y-%m-%d')
            correct=0; credited=0
            for a in body.answers:
                ok=int(a.choice==grading[a.id]['answer']); correct+=ok
                row=c.execute('SELECT * FROM account_progress WHERE account=? AND question=?', (who['number'],a.id)).fetchone()
                seen=(row['seen'] if row else 0)+1
                successes=(row['correct'] if row else 0)+ok
                streak=(row['streak']+1 if row else 1) if ok else 0
                c.execute('INSERT OR REPLACE INTO account_progress VALUES(?,?,?,?,?,?)', (who['number'],a.id,seen,successes,streak,now))
                if ok:
                    credited+=c.execute('INSERT OR IGNORE INTO account_credits VALUES(?,?,?)',(who['number'],day,a.id)).rowcount
            result={'id':body.id,'accountNumber':who['number'],'subject':body.subject,'bankVersion':body.bankVersion,'mode':'subject','total':len(ids),'correct':correct,'date':int(now*1000),'ids':ids,'answers':[a.choice for a in body.answers],'credited':credited,'synced':True}
            c.execute('INSERT INTO study_results VALUES(?,?,?,?,?)', (who['number'],body.id,canonical,json.dumps(result),now))
            return result

    @app.get('/accounts/leaderboard')
    def leaderboard():
        # Public display names plus masked account suffix; full account numbers stay private.
        with db() as c:
            rows=c.execute('''SELECT a.number,a.name,COALESCE(p.points,0) AS points,COALESCE(s.correct,0) AS correct,COALESCE(s.attempts,0) AS attempts FROM study_accounts a
                LEFT JOIN (SELECT account,COUNT(*) points FROM account_credits GROUP BY account) p ON p.account=a.number
                LEFT JOIN (SELECT account,SUM(correct) correct,SUM(seen) attempts FROM account_progress GROUP BY account) s ON s.account=a.number
                WHERE s.attempts>0 AND a.ranked=1 ORDER BY points DESC,correct DESC,a.created ASC LIMIT 100''').fetchall()
        return {'entries':[{'name':r['name'],'accountSuffix':r['number'][-4:],'points':r['points'],'correct':r['correct'],'attempts':r['attempts']} for r in rows], 'dayTimezone':'Asia/Manila'}

    @app.post('/accounts/plan')
    def plan(body: Selection, who=Depends(identity)):
        rate('account-plan:'+who['number'], 20, 3600)
        size=20 if body.scope=='focus' else 50
        if body.scope=='focus' and not bank.get('focus'):
            raise HTTPException(409, 'This bank has no reviewed core selection.')
        needs = {'AI': size//2, 'IN': size//2} if body.sourceMode == 'hybrid' else {body.sourceMode: size}
        pool=[q for q in bank['questions'] if q['subject']==body.subject and q.get('active', True) and q.get('origin', 'AI') in needs and (body.scope=='full' or q['id'] in bank['focus']['questions'])]
        if any(sum(q.get('origin', 'AI') == source for q in pool) < count for source, count in needs.items()):
            raise HTTPException(409, f'Not enough active questions for the selected source. Hybrid needs {size//2} of each; a single source needs {size}.')
        with db() as c:
            progress={r['question']:dict(r) for r in c.execute('SELECT * FROM account_progress WHERE account=?', (who['number'],))}
        topics=sorted({q['topic'] for q in pool}); focus=[]; selection='adaptive'
        if body.ai:
            selection='adaptive-fallback'
            key=os.getenv('GEMINI_API_KEY','').strip(); model=os.getenv('GEMINI_MODEL','gemini-3.5-flash-lite').strip()
            if key and re.fullmatch(r'[A-Za-z0-9._-]{1,100}',model):
                aggregates=[]
                for topic in topics:
                    items=[progress[q['id']] for q in pool if q['topic']==topic and q['id'] in progress]
                    aggregates.append({'topic':topic,'attempts':sum(x['seen'] for x in items),'correct':sum(x['correct'] for x in items)})
                try:
                    prompt='Choose up to three priority study topics from this exact list using practice results. Return ONLY a JSON array of existing topic strings. Do not generate questions or answers. Data: '+json.dumps(aggregates)
                    with httpx.Client(timeout=12,follow_redirects=False) as client:
                        response=client.post(f'https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent',headers={'x-goog-api-key':key},json={'contents':[{'parts':[{'text':prompt}]}],'generationConfig':{'maxOutputTokens':300,'responseMimeType':'application/json'}})
                        response.raise_for_status()
                        text=''.join(p.get('text','') for p in response.json()['candidates'][0]['content']['parts'])
                    result=json.loads(text)
                    if not isinstance(result,list) or not 1<=len(result)<=3 or any(not isinstance(t,str) or t not in topics for t in result):
                        raise ValueError('Invalid topic selection')
                    focus=list(set(result));selection='ai-assisted'
                except (httpx.HTTPError,KeyError,IndexError,TypeError,ValueError,ImportError):
                    focus=[]
        rng=secrets.SystemRandom()
        def priority(q):
            p=progress.get(q['id'])
            return (5 if q['topic'] in focus else 0)+(6 if p and p['streak']==0 else 3 if not p else 1)+rng.random()*4
        chosen=[]
        for source, count in needs.items():
            ranked=sorted((q for q in pool if q.get('origin', 'AI') == source), key=priority, reverse=True)
            if body.scope=='focus':
                buckets={}
                for q in ranked:buckets.setdefault(q['topic'],[]).append(q)
                ranked=[]
                while len(ranked)<count:
                    for items in buckets.values():
                        if items and len(ranked)<count:ranked.append(items.pop(0))
            chosen.extend(ranked[:count])
        rng.shuffle(chosen)
        return {'bankVersion':bank['version'],'ids':[q['id'] for q in chosen],'selection':selection,'topics':focus}

    from .sync import attach_sync
    attach_sync(app,db,identity,bank,versions,rate,clock)
