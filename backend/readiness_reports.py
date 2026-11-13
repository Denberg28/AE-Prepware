"""Validate voluntary device reports; recompute descriptive targets, never pass odds."""
import csv
import io
import json
import math
import re
from datetime import datetime, timedelta, timezone

WEIGHTS={'math':10,'aero':25,'structures':20,'construction':15,'powerplant':20,'ethics':10}
DAY=86400000


def integer(value,low,high):
    if type(value) is not int or not low<=value<=high:raise ValueError('Invalid report count')
    return value


def timestamp(value):
    if type(value) not in (int,float) or not math.isfinite(value) or not 0<=value<=4102444800000:raise ValueError('Invalid report time')
    return value


def analyze_report(raw,now=None):
    if len(raw)>200_000:raise ValueError('Report exceeds 200 KB')
    try:r=json.loads(raw)
    except (ValueError,UnicodeError,RecursionError):raise ValueError('Unreadable report JSON') from None
    if not isinstance(r,dict) or r.get('type')!='ae-board-readiness' or r.get('schema')!=1 or r.get('policy')!='brms-1':raise ValueError('Unsupported readiness report')
    if not isinstance(r.get('alias'),str) or not 1<=len(r['alias'].strip())<=40 or not isinstance(r.get('profile'),str) or not re.fullmatch(r'[a-f0-9-]{36}',r['profile']):raise ValueError('Invalid report alias/profile')
    at=timestamp(r.get('generatedAt'));now=now or datetime.now(timezone.utc).timestamp()*1000
    if at>now+5*60*1000:raise ValueError('Report date is in the future')
    if not isinstance(r.get('bankVersion'),str) or not 1<=len(r['bankVersion'])<=100:raise ValueError('Missing bank version')
    c=r.get('commitment',{});
    if not isinstance(c,dict) or not isinstance(c.get('goal'),dict):raise ValueError('Invalid commitment record')
    goal=c['goal'];target_days=integer(goal.get('days'),1,7);target_q=integer(goal.get('questions'),1,50)
    if c.get('timezone')!='Asia/Manila' or not isinstance(c.get('days'),list) or len(c['days'])!=28:raise ValueError('Invalid activity window')
    end=datetime.fromtimestamp(at/1000,timezone(timedelta(hours=8))).date()
    for i,d in enumerate(c['days']):
        if not isinstance(d,dict) or d.get('date')!=(end-timedelta(days=27-i)).isoformat():raise ValueError('Activity dates must be consecutive')
        integer(d.get('questions'),0,3000)
    competence=r.get('competence');
    if not isinstance(competence,dict):raise ValueError('Invalid competence record')
    subjects=competence.get('subjects')
    if not isinstance(subjects,list) or len(subjects)!=6 or any(not isinstance(s,dict) or not isinstance(s.get('id'),str) for s in subjects) or {s.get('id') for s in subjects}!=set(WEIGHTS):raise ValueError('Six subject records are required')
    rows=[];all_ids=set()
    for s in subjects:
        if s.get('weight')!=WEIGHTS[s['id']]:raise ValueError('Subject weights differ from PRC blueprint')
        first=s.get('first',{});
        if not isinstance(first,dict) or not isinstance(s.get('core'),dict):raise ValueError('Invalid subject counts')
        n=integer(first.get('total'),0,3000);integer(first.get('correct'),0,n)
        core=s.get('core',{});n=integer(core.get('total'),0,3000);integer(core.get('seen'),0,n)
        checks=s.get('checks');topics=s.get('topics')
        if not isinstance(checks,list) or len(checks)>200 or not isinstance(topics,list) or len(topics)>3:raise ValueError('Invalid check/topic records')
        for h in checks:
            if not isinstance(h,dict) or h.get('kind') not in ('diagnostic','retention') or not isinstance(h.get('id'),str) or not re.fullmatch(r'[-A-Za-z0-9_]{1,64}',h['id']) or h['id'] in all_ids or h.get('total')!=20:raise ValueError('Invalid or duplicate check')
            all_ids.add(h['id']);integer(h.get('correct'),0,20)
            if timestamp(h.get('at'))>at:raise ValueError('Check is later than report')
        for t in topics:
            if not isinstance(t,dict) or not isinstance(t.get('topic'),str) or not 1<=len(t['topic'])<=200:raise ValueError('Invalid topic label')
            integer(t.get('correct'),0,integer(t.get('total'),3,3000))
        baseline=s.get('baseline')
        if baseline is not None:
            if not isinstance(baseline,dict) or baseline.get('kind')!='diagnostic' or baseline.get('total')!=20 or not isinstance(baseline.get('bankVersion'),str):raise ValueError('Invalid baseline')
            integer(baseline.get('correct'),0,20)
            if timestamp(baseline.get('at'))>at:raise ValueError('Baseline is later than report')
        recent=sorted((h for h in checks if now-30*DAY<=h['at']<=now),key=lambda h:h['at'],reverse=True);latest=recent[0] if recent else None
        met=bool(latest and latest['correct']>=16 and any(latest['at']-h['at']>=7*DAY and h['correct']>=16 for h in recent))
        status=('Recheck due' if checks else 'Baseline needed') if not latest else 'Support needed' if latest['correct']<16 else 'Foundation target met' if met else 'Confirm retention'
        rows.append({'id':s['id'],'status':status,'latest':latest,'baseline':baseline,'first':first,'core':core,'topics':topics})
    if len(all_ids)>200:raise ValueError('Report exceeds retained check history')
    assessed=sum(s['latest'] is not None for s in rows);weighted=math.floor(sum(WEIGHTS[s['id']]*s['latest']['correct']/20 for s in rows)+0.5) if assessed==6 else None
    since=r.get('trackingSince');observed=0
    if since is not None:
        if timestamp(since)>at:raise ValueError('Tracking starts after report')
        observed=min(7,(end-datetime.fromtimestamp(since/1000,timezone(timedelta(hours=8))).date()).days+1)
    return {'Observed days / 7':observed,'profile':r['profile'],'Alias':r['alias'].strip(),'Bank':r['bankVersion'],'Report date':end.isoformat(),'Report age (days)':max(0,int((now-at)//DAY)),
            'Active days / 7':None if not observed else sum(d['questions']>0 for d in c['days'][-7:]),'Goal days met / 7':None if not observed else sum(d['questions']>=target_q for d in c['days'][-7:]),'Goal days':target_days,
            'Subjects checked':assessed,'Foundation targets met':sum(s['status']=='Foundation target met' for s in rows),'Weighted foundation %':weighted,
            'Assessment needed':', '.join(s['id'] for s in rows if s['status'] in ('Baseline needed','Recheck due')),
            'Subject support':', '.join(s['id'] for s in rows if s['status']=='Support needed'),
            'Board readiness':'Not established','Evidence':'Device-recorded / not proctored','subjects':rows,'generatedAt':at}


def cohort_rows(reports):
    latest={}
    for r in reports:
        if r['profile'] not in latest or r['generatedAt']>latest[r['profile']]['generatedAt']:latest[r['profile']]=r
    return [{k:v for k,v in r.items() if k not in ('profile','subjects','generatedAt')} for r in latest.values()]


def export_csv(rows):
    def safe(value):
        value='' if value is None else str(value)
        return "'"+value if value.lstrip().startswith(('=','+','-','@','\t','\r')) or value.startswith(('\t','\r')) else value
    out=io.StringIO();fields=list(rows[0]) if rows else []
    writer=csv.DictWriter(out,fieldnames=fields);writer.writeheader();writer.writerows({k:safe(v) for k,v in row.items()} for row in rows)
    return out.getvalue()
