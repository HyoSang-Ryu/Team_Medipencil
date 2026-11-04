"""Local supplied-data workflow, isolated from independent demo and real consent."""
import re
import hashlib
import io
import json
import sqlite3
import wave
from contextlib import closing, contextmanager
from datetime import date, datetime
from zoneinfo import ZoneInfo
from typing import Literal
from fastapi import APIRouter, Request, UploadFile, File
from pydantic import Field
from .common import Input, Fault, envelope, now, uid
from .security import session
from .provided_data import available, FILENAME, representative

router=APIRouter(prefix='/api/v1')
DAILY=['breakfast','lunch','dinner','fluids_dl','sleep_hours','sleep_quality','outdoor','outdoor_minutes','outdoor_type','assistance_level']
SOCIAL=['activities','social_interaction']
HEALTH=['mood_label','pain_score','health_event']
GROUPS={'daily':DAILY,'social':SOCIAL,'health':HEALTH}

def family_identity(label, relation):
    match=re.fullmatch(r'(.*?) \((\d+) v, (nainen|mies)\)',label)
    name,age,sex=(match[1],int(match[2]),match[3]) if match else (label,None,None)
    relation=relation.strip().lower()
    # Source relation describes the guardian; invert to the resident's relation.
    child=relation in ('tytär','poika','lapsi')
    parent=relation in ('äiti','isä','vanhempi')
    key=('mother' if sex=='nainen' else 'father' if sex=='mies' else 'parent') if child else ('daughter' if sex=='nainen' else 'son' if sex=='mies' else 'child') if parent else 'spouse' if relation in ('puoliso','aviomies','vaimo') else 'family'
    return {'name':name,'age':age,'relationship':key}

def people(settings):
    if not available(settings):return []
    result=[]
    with closing(sqlite3.connect((settings.root/FILENAME).as_uri()+'?mode=ro',uri=True)) as db:
        for subject,payload,family in db.execute('SELECT * FROM subjects ORDER BY id'):
            profile=json.loads(payload)
            for p in representative(json.loads(family)):
                actor='provided-'+hashlib.sha256((subject+':'+p['family_id']).encode()).hexdigest()[:20]
                result.append({'actor_id':actor,'display_name':p['name'],'subject':subject,'resident':profile['label'],'scope_text':p.get('consent_scope',''),'relation':p.get('relation_ko',p.get('relation_fi','')),'family_identity':family_identity(profile['label'],p.get('relation_fi',''))})
    return result

def sync_accounts(app):
    from .db import one,insert
    profiles=people(app.state.settings)
    with app.state.store.transaction() as db:
        db.execute("UPDATE actors SET active=0 WHERE actor_id LIKE 'provided-%'")
        if profiles:
            # Retire the initial Helmi/Liisa demo while preserving linked audit history.
            db.execute("UPDATE actors SET active=0 WHERE actor_id IN ('liisa','mikko')")
            db.execute("DELETE FROM demo_sessions WHERE actor_id IN ('liisa','mikko')")
            db.execute("UPDATE access_memberships SET active=0 WHERE actor_id IN ('liisa','mikko')")
            db.execute("UPDATE delivery_schedules SET enabled=0,next_run_at=NULL WHERE subject_id='aino'")
        for p in profiles:
            if one(db,'SELECT actor_id FROM actors WHERE actor_id=?',(p['actor_id'],)):
                db.execute('UPDATE actors SET display_name=?,active=1 WHERE actor_id=?',(p['display_name'],p['actor_id']))
            else:insert(db,'actors',actor_id=p['actor_id'],display_name=p['display_name'],role='family',active=1)

@contextmanager
def workflow(settings):
    with closing(sqlite3.connect(settings.root/'provided-workflow.sqlite',timeout=10)) as db:
        db.row_factory=sqlite3.Row
        db.executescript('''CREATE TABLE IF NOT EXISTS policies(actor TEXT PRIMARY KEY,groups_json TEXT,revision INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS notes(id TEXT PRIMARY KEY,subject TEXT,text TEXT,topic TEXT,created TEXT,checked INTEGER,recipient_json TEXT);
        CREATE TABLE IF NOT EXISTS questions(id TEXT PRIMARY KEY,subject TEXT,actor TEXT,text TEXT,created TEXT,reply TEXT,replied TEXT);
        CREATE TABLE IF NOT EXISTS visits(id TEXT PRIMARY KEY,subject TEXT,actor TEXT,kind TEXT,visit_day TEXT,visit_time TEXT,guests INTEGER,created TEXT,status TEXT,reviewed TEXT);
        CREATE TABLE IF NOT EXISTS family_messages(id TEXT PRIMARY KEY,subject TEXT,actor TEXT,text TEXT,created TEXT,status TEXT,processed TEXT);
        CREATE TABLE IF NOT EXISTS note_reads(note_id TEXT,actor TEXT,read_at TEXT,PRIMARY KEY(note_id,actor));
        CREATE TABLE IF NOT EXISTS note_reactions(note_id TEXT,actor TEXT,kind TEXT,created TEXT,PRIMARY KEY(note_id,actor));
        CREATE TABLE IF NOT EXISTS family_preferences(actor TEXT PRIMARY KEY,daily INTEGER,social INTEGER,health INTEGER);
        CREATE TABLE IF NOT EXISTS chart_drafts(subject TEXT PRIMARY KEY,payload TEXT,revision INTEGER,updated TEXT);''')
        with db:
            db.execute('BEGIN IMMEDIATE')
            yield db

def auth(request,subject=None,staff=False):
    if not available(request.app.state.settings):raise Fault('RESOURCE_NOT_FOUND',404)
    with request.app.state.store.transaction() as db:a=session(request,db,'staff' if staff else None)
    if a['role']=='staff':return a,None
    p=next((p for p in people(request.app.state.settings) if p['actor_id']==a['actor_id']),None)
    if not p or (subject and subject!=p['subject']):raise Fault('ROLE_FORBIDDEN',403)
    return a,p

def policy(db,p):
    row=db.execute('SELECT * FROM policies WHERE actor=?',(p['actor_id'],)).fetchone()
    if row:return {'groups':json.loads(row['groups_json']),'revision':row['revision']}
    scope=p['scope_text']
    return {'groups':(['daily'] if 'arki' in scope else [])+(['social'] if 'osallisuus' in scope else [])+(['health'] if scope=='terveys, hoito, arki ja osallisuus' else []),'revision':0}

def subject_profile(settings,s):
    with closing(sqlite3.connect((settings.root/FILENAME).as_uri()+'?mode=ro',uri=True)) as db:
        row=db.execute('SELECT payload FROM subjects WHERE id=?',(s,)).fetchone()
        if not row:raise Fault('RESOURCE_NOT_FOUND',404)
        return json.loads(row[0])

@router.get('/provided/workspace')
def workspace(request:Request):
    a,p=auth(request)
    profiles=people(request.app.state.settings)
    ids=sorted({x['subject'] for x in profiles}) if a['role']=='staff' else [p['subject']]
    return envelope({'subjects':[{'id':s,**subject_profile(request.app.state.settings,s)} for s in ids], 'family':profiles if a['role']=='staff' else [p], 'policy_mode':'LOCAL_SYNTHETIC_PRESET','today':datetime.now(ZoneInfo('Europe/Helsinki')).date().isoformat()})

@router.get('/provided/{s}/board')
def board(s:str,request:Request,start:date,end:date):
    a,p=auth(request,s)
    subject=subject_profile(request.app.state.settings,s)
    if p:subject['family_identity']=p['family_identity']
    today=datetime.now(ZoneInfo('Europe/Helsinki')).date()
    if start.year!=2026 or end.year!=2026 or start>end:raise Fault('INVALID_DATE_RANGE')
    limit=min(end,today) if p else end
    with workflow(request.app.state.settings) as db:
        permitted=policy(db,p)['groups'] if p else list(GROUPS)
        keys=[k for g in permitted for k in GROUPS[g]]
        with closing(sqlite3.connect((request.app.state.settings.root/FILENAME).as_uri()+'?mode=ro',uri=True)) as src:
            rows=[json.loads(r[0]) for r in src.execute("SELECT payload FROM entries WHERE subject=? AND kind='daily_log' AND day>=? AND day<=? ORDER BY day",(s,start.isoformat(),limit.isoformat()))]
        daily=[{'date':r['date'],**{k:r[k] for k in keys if k in r},'future_scenario':r['date']>today.isoformat()} for r in rows] if permitted else []
        notes=[]
        for r in db.execute('SELECT * FROM notes WHERE subject=? ORDER BY created DESC',(s,)):
            if p and (p['actor_id'] not in json.loads(r['recipient_json']) or r['topic'] not in permitted):continue
            notes.append({k:r[k] for k in ('id','text','topic','created','checked')})
        questions=[dict(r) for r in db.execute('SELECT * FROM questions WHERE subject=?'+(' AND actor=?' if p else '')+' ORDER BY created DESC',(s,p['actor_id']) if p else (s,))]
        notes_read={r['note_id'] for r in db.execute('SELECT note_id FROM note_reads WHERE actor=?',(p['actor_id'],))} if p else set()
        for n in notes:
            if p:
                n['read']=n['id'] in notes_read
                own=db.execute('SELECT kind FROM note_reactions WHERE note_id=? AND actor=?',(n['id'],p['actor_id'])).fetchone()
                n['my_reaction']=own['kind'] if own else None
            else:n['read_count']=db.execute('SELECT count(*) FROM note_reads WHERE note_id=?',(n['id'],)).fetchone()[0]
            n['reactions']={k:db.execute('SELECT count(*) FROM note_reactions WHERE note_id=? AND kind=?',(n['id'],k)).fetchone()[0] for k in ('heart','thanks','smile')}
        visits=[dict(r) for r in db.execute('SELECT * FROM visits WHERE subject=?'+(' AND actor=?' if p else '')+' ORDER BY created DESC',(s,p['actor_id']) if p else (s,))]
        messages=[dict(r) for r in db.execute('SELECT * FROM family_messages WHERE subject=?'+(' AND actor=?' if p else '')+' ORDER BY created DESC',(s,p['actor_id']) if p else (s,))]
        pref=db.execute('SELECT * FROM family_preferences WHERE actor=?',(p['actor_id'],)).fetchone() if p else None
    if p and 'daily' not in permitted:
        for q in questions:q['reply']=None;q['replied']=None
    return envelope({'subject':subject,'daily':daily,'notes':notes,'questions':questions,'visits':visits,'family_messages':messages,'preferences':{k:bool(pref[k]) if pref else True for k in ('daily','social','health')} if p else None,'groups':permitted,'today':today.isoformat(),'policy_mode':'LOCAL_SYNTHETIC_PRESET'})

@router.get('/provided/{s}/sharing')
def sharing(s:str,request:Request):
    a,p=auth(request,s);subject_profile(request.app.state.settings,s)
    with workflow(request.app.state.settings) as db:
        return envelope({'items':[{**r,**policy(db,r)} for r in people(request.app.state.settings) if r['subject']==s and (not p or r['actor_id']==p['actor_id'])],'policy_mode':'LOCAL_SYNTHETIC_PRESET'})

class Policy(Input):
    actor_id:str
    groups:list[Literal['daily','social','health']]
    revision:int=Field(ge=0)
@router.put('/provided/{s}/sharing')
def update_policy(s:str,body:Policy,request:Request):
    auth(request,s,True)
    p=next((p for p in people(request.app.state.settings) if p['actor_id']==body.actor_id and p['subject']==s),None)
    if not p:raise Fault('ROLE_FORBIDDEN',403)
    with workflow(request.app.state.settings) as db:
        if policy(db,p)['revision']!=body.revision:raise Fault('REVISION_CONFLICT',409)
        db.execute('INSERT OR REPLACE INTO policies VALUES (?,?,?)',(p['actor_id'],json.dumps(sorted(set(body.groups))),body.revision+1))
    return envelope({'revision':body.revision+1})

class Note(Input):
    text:str=Field(min_length=1,max_length=5000)
    topic:Literal['daily','social','health']
    finnish_checked:bool
    recipients:list[str]=Field(max_length=20)
    request_id:str=Field(min_length=16,max_length=80)
@router.post('/provided/{s}/notes')
def note(s:str,body:Note,request:Request):
    auth(request,s,True);subject_profile(request.app.state.settings,s)
    if not body.finnish_checked or not body.text.strip():raise Fault('REVIEW_REQUIRED')
    with workflow(request.app.state.settings) as db:
        profiles={p['actor_id']:p for p in people(request.app.state.settings) if p['subject']==s}
        if any(r not in profiles or body.topic not in policy(db,profiles[r])['groups'] for r in body.recipients):raise Fault('SCOPE_FORBIDDEN',403)
        old=db.execute('SELECT * FROM notes WHERE id=?',(body.request_id,)).fetchone()
        if old and (old['subject']!=s or old['text']!=body.text or old['topic']!=body.topic or json.loads(old['recipient_json'])!=body.recipients):raise Fault('IDEMPOTENCY_CONFLICT',409)
        if not old:db.execute('INSERT INTO notes VALUES (?,?,?,?,?,?,?)',(body.request_id,s,body.text,body.topic,now(),1,json.dumps(body.recipients)))
    return envelope({'id':body.request_id,'language':'fi','ai_executed':False,'policy_mode':'LOCAL_SYNTHETIC_PRESET'})

class Question(Input):
    text:str=Field(min_length=1,max_length=2000)
    request_id:str=Field(min_length=16,max_length=80)
@router.post('/provided/{s}/questions')
def ask(s:str,body:Question,request:Request):
    a,p=auth(request,s)
    if not p:raise Fault('ROLE_FORBIDDEN',403)
    if not body.text.strip():raise Fault('VALIDATION_FAILED')
    with workflow(request.app.state.settings) as db:
        old=db.execute('SELECT * FROM questions WHERE id=?',(body.request_id,)).fetchone()
        if old and (old['actor']!=a['actor_id'] or old['subject']!=s or old['text']!=body.text):raise Fault('IDEMPOTENCY_CONFLICT',409)
        if not old:db.execute('INSERT INTO questions VALUES (?,?,?,?,?,?,?)',(body.request_id,s,a['actor_id'],body.text,now(),None,None))
    return envelope({'id':body.request_id})
class Reply(Input):
    text:str=Field(min_length=1,max_length=2000)
    finnish_checked:bool
@router.post('/provided/{s}/questions/{q}/reply')
def reply(s:str,q:str,body:Reply,request:Request):
    auth(request,s,True)
    if not body.finnish_checked or not body.text.strip():raise Fault('REVIEW_REQUIRED')
    with workflow(request.app.state.settings) as db:
        r=db.execute('SELECT * FROM questions WHERE id=? AND subject=?',(q,s)).fetchone()
        if not r:raise Fault('RESOURCE_NOT_FOUND',404)
        p=next((p for p in people(request.app.state.settings) if p['actor_id']==r['actor'] and p['subject']==s),None)
        if not p or 'daily' not in policy(db,p)['groups']:raise Fault('SCOPE_FORBIDDEN',403)
        db.execute('UPDATE questions SET reply=?,replied=? WHERE id=?',(body.text,now(),q))
    return envelope({'id':q})

class Visit(Input):
    kind:Literal['lounge','garden','video']
    visit_day:date
    visit_time:Literal['10:30','14:00','15:00','16:30']
    guests:int=Field(ge=1,le=4)
    request_id:str=Field(min_length=16,max_length=80)

@router.post('/provided/{s}/visits')
def request_visit(s:str,body:Visit,request:Request):
    a,p=auth(request,s)
    if not p:raise Fault('ROLE_FORBIDDEN',403)
    today=datetime.now(ZoneInfo('Europe/Helsinki')).date()
    if body.visit_day<today or (body.visit_day-today).days>60:raise Fault('INVALID_DATE_RANGE')
    with workflow(request.app.state.settings) as db:
        old=db.execute('SELECT * FROM visits WHERE id=?',(body.request_id,)).fetchone()
        if old and any((old[k]!=v for k,v in {'subject':s,'actor':a['actor_id'],'kind':body.kind,'visit_day':body.visit_day.isoformat(),'visit_time':body.visit_time,'guests':body.guests}.items())):raise Fault('IDEMPOTENCY_CONFLICT',409)
        if not old:db.execute('INSERT INTO visits VALUES (?,?,?,?,?,?,?,?,?,?)',(body.request_id,s,a['actor_id'],body.kind,body.visit_day.isoformat(),body.visit_time,body.guests,now(),'requested',None))
    return envelope({'id':body.request_id,'status':'requested','reservation_confirmed':False})

class VisitDecision(Input):
    status:Literal['approved','declined']

@router.post('/provided/{s}/visits/{visit_id}/decision')
def decide_visit(s:str,visit_id:str,body:VisitDecision,request:Request):
    auth(request,s,True)
    with workflow(request.app.state.settings) as db:
        row=db.execute('SELECT * FROM visits WHERE id=? AND subject=?',(visit_id,s)).fetchone()
        if not row:raise Fault('RESOURCE_NOT_FOUND',404)
        if row['status'] not in ('requested',body.status):raise Fault('REVISION_CONFLICT',409)
        db.execute('UPDATE visits SET status=?,reviewed=? WHERE id=?',(body.status,now(),visit_id))
    return envelope({'id':visit_id,'status':body.status,'reservation_confirmed':body.status=='approved'})

@router.post('/provided/{s}/visits/{visit_id}/cancel')
def cancel_visit(s:str,visit_id:str,request:Request):
    a,p=auth(request,s)
    if not p:raise Fault('ROLE_FORBIDDEN',403)
    with workflow(request.app.state.settings) as db:
        row=db.execute('SELECT * FROM visits WHERE id=? AND subject=? AND actor=?',(visit_id,s,a['actor_id'])).fetchone()
        if not row:raise Fault('RESOURCE_NOT_FOUND',404)
        if row['status'] not in ('requested','approved','cancelled'):raise Fault('REVISION_CONFLICT',409)
        db.execute("UPDATE visits SET status='cancelled',reviewed=? WHERE id=?",(now(),visit_id))
    return envelope({'id':visit_id,'status':'cancelled','reservation_confirmed':False})

class FamilyMessage(Input):
    text:str=Field(min_length=1,max_length=1000)
    request_id:str=Field(min_length=16,max_length=80)

@router.post('/provided/{s}/family-messages')
def family_message(s:str,body:FamilyMessage,request:Request):
    a,p=auth(request,s)
    if not p:raise Fault('ROLE_FORBIDDEN',403)
    if not body.text.strip():raise Fault('VALIDATION_FAILED')
    with workflow(request.app.state.settings) as db:
        old=db.execute('SELECT * FROM family_messages WHERE id=?',(body.request_id,)).fetchone()
        if old and (old['subject']!=s or old['actor']!=a['actor_id'] or old['text']!=body.text):raise Fault('IDEMPOTENCY_CONFLICT',409)
        if not old:db.execute('INSERT INTO family_messages VALUES (?,?,?,?,?,?,?)',(body.request_id,s,a['actor_id'],body.text,now(),'pending',None))
    return envelope({'id':body.request_id,'status':'pending','delivered_to_resident':False})

@router.post('/provided/{s}/family-messages/{message_id}/processed')
def process_family_message(s:str,message_id:str,request:Request):
    auth(request,s,True)
    with workflow(request.app.state.settings) as db:
        row=db.execute('SELECT * FROM family_messages WHERE id=? AND subject=?',(message_id,s)).fetchone()
        if not row:raise Fault('RESOURCE_NOT_FOUND',404)
        db.execute("UPDATE family_messages SET status='processed',processed=? WHERE id=?",(now(),message_id))
    return envelope({'id':message_id,'status':'processed'})

@router.post('/provided/{s}/notes/{note_id}/read')
def read_note(s:str,note_id:str,request:Request):
    a,p=auth(request,s)
    if not p:raise Fault('ROLE_FORBIDDEN',403)
    with workflow(request.app.state.settings) as db:
        row=db.execute('SELECT * FROM notes WHERE id=? AND subject=?',(note_id,s)).fetchone()
        if not row:raise Fault('RESOURCE_NOT_FOUND',404)
        if a['actor_id'] not in json.loads(row['recipient_json']) or row['topic'] not in policy(db,p)['groups']:raise Fault('SCOPE_FORBIDDEN',403)
        db.execute('INSERT OR IGNORE INTO note_reads VALUES (?,?,?)',(note_id,a['actor_id'],now()))
    return envelope({'id':note_id,'read':True})

class Reaction(Input):
    kind:Literal['heart','thanks','smile']|None

@router.put('/provided/{s}/notes/{note_id}/reaction')
def react_to_note(s:str,note_id:str,body:Reaction,request:Request):
    a,p=auth(request,s)
    if not p:raise Fault('ROLE_FORBIDDEN',403)
    with workflow(request.app.state.settings) as db:
        row=db.execute('SELECT * FROM notes WHERE id=? AND subject=?',(note_id,s)).fetchone()
        if not row:raise Fault('RESOURCE_NOT_FOUND',404)
        if a['actor_id'] not in json.loads(row['recipient_json']) or row['topic'] not in policy(db,p)['groups']:raise Fault('SCOPE_FORBIDDEN',403)
        if body.kind:db.execute('INSERT OR REPLACE INTO note_reactions VALUES (?,?,?,?)',(note_id,a['actor_id'],body.kind,now()))
        else:db.execute('DELETE FROM note_reactions WHERE note_id=? AND actor=?',(note_id,a['actor_id']))
    return envelope({'id':note_id,'kind':body.kind})

class Preferences(Input):
    daily:bool
    social:bool
    health:bool

@router.put('/provided/{s}/preferences')
def save_preferences(s:str,body:Preferences,request:Request):
    a,p=auth(request,s)
    if not p:raise Fault('ROLE_FORBIDDEN',403)
    with workflow(request.app.state.settings) as db:
        db.execute('INSERT OR REPLACE INTO family_preferences VALUES (?,?,?,?)',(a['actor_id'],int(body.daily),int(body.social),int(body.health)))
    return envelope(body.model_dump())

class ChartDraft(Input):
    meal_percent:int|None=Field(default=None,ge=0,le=100)
    swallowing:Literal['normal','cough','assisted']|None=None
    temperature_c:float|None=Field(default=None,ge=30,le=43)
    systolic:int|None=Field(default=None,ge=60,le=250)
    diastolic:int|None=Field(default=None,ge=30,le=150)
    glucose_mmol:float|None=Field(default=None,ge=1,le=40)
    medication_note:str=Field(default='',max_length=1000)
    activity_note:str=Field(default='',max_length=1000)
    staff_note:str=Field(default='',max_length=2000)
    revision:int=Field(ge=0)

@router.get('/provided/{s}/chart-draft')
def get_chart_draft(s:str,request:Request):
    auth(request,s,True);subject_profile(request.app.state.settings,s)
    with workflow(request.app.state.settings) as db:
        row=db.execute('SELECT * FROM chart_drafts WHERE subject=?',(s,)).fetchone()
    return envelope({'draft':json.loads(row['payload']) if row else None,'revision':row['revision'] if row else 0,'updated':row['updated'] if row else None})

@router.put('/provided/{s}/chart-draft')
def save_chart_draft(s:str,body:ChartDraft,request:Request):
    auth(request,s,True);subject_profile(request.app.state.settings,s)
    with workflow(request.app.state.settings) as db:
        row=db.execute('SELECT revision FROM chart_drafts WHERE subject=?',(s,)).fetchone()
        current=row['revision'] if row else 0
        if current!=body.revision:raise Fault('REVISION_CONFLICT',409)
        payload=body.model_dump(exclude={'revision'})
        db.execute('INSERT OR REPLACE INTO chart_drafts VALUES (?,?,?,?)',(s,json.dumps(payload,ensure_ascii=False),current+1,now()))
    return envelope({'revision':current+1,'saved':True,'published':False})

@router.post('/provided/{s}/live-transcript')
def transcript(s:str,request:Request,file:UploadFile=File(...),language:Literal['fi','ko','en','sv']='fi',synthetic_ack:bool=False):
    auth(request,s,True);subject_profile(request.app.state.settings,s)
    if not synthetic_ack:raise Fault('REVIEW_REQUIRED')
    raw=file.file.read(1024*1024+1)
    if len(raw)>1024*1024:raise Fault('AUDIO_TOO_LARGE',413)
    try:
        with wave.open(io.BytesIO(raw)) as wav:
            if wav.getnchannels()!=1 or wav.getsampwidth()!=2 or wav.getframerate()!=16000 or not 0<wav.getnframes()<=16000*13:raise Fault('AUDIO_FORMAT_UNSUPPORTED',415)
            pcm=wav.readframes(wav.getnframes())
            if len(pcm)!=wav.getnframes()*2:raise Fault('AUDIO_FORMAT_UNSUPPORTED',415)
    except (wave.Error,EOFError):raise Fault('AUDIO_FORMAT_UNSUPPORTED',415)
    # Offline Whisper only. No provided clinical file is included in the model input.
    def canceled():
        try:auth(request,s,True);return False
        except Fault:return True
    result=request.app.state.live_speech.transcribe(pcm,language,canceled)
    auth(request,s,True)
    return envelope({'text':result['text'],'provisional':True,'saved':False,'execution':{**result['metadata'],'origin':'SUPPLIED_SCENARIO_VOICE','ai_executed':True}})
