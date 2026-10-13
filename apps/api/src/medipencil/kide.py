"""Local synthetic voice -> Finnish draft -> human reviewed family cards."""
import json
import re
import sqlite3
import threading
from datetime import datetime,timezone
from contextlib import contextmanager, closing
import httpx
from fastapi import APIRouter, Request
from pydantic import Field
from .common import Input, Fault, envelope, now
from .security import session, access, grant
from .domain import SCOPES
from .roundloop import config

router=APIRouter(prefix='/api/v1/kide')
GENERATION_SLOT=threading.BoundedSemaphore(1)
NOTES='yleistila oireet_ja_kipu elintoiminnot ravitsemus_ja_nesteytys liikkuminen_ja_toimintakyky mieliala_ja_jaksaminen hoitotoimet_ja_laakitys suunnitelma_ja_jatkohoito laheisen_asiat'.split()
CARDS='vointi_tanaan kipu_ja_olo syominen_ja_juominen liikkuminen taman_paivan_hoito seuraavat_askeleet vastaus_laheiselle miten_voit_auttaa'.split()
COMMAND=re.compile(r'(?:kide|키데|키드)[,，:!\s]*(?:정리해\s*줘|정리해\s*주세요|summari[sz]e(?:\s+please)?|tee\s+yhteenveto)[.!?\s]*$',re.I)

def clean_transcript(text):
    return COMMAND.sub('',text.strip()).strip()

def auth(request,subject,staff=True):
    if subject in ('A','B'):
        from .provided_workflow import auth as supplied,subject_profile
        a,_=supplied(request,subject,staff);subject_profile(request.app.state.settings,subject)
        return a
    with request.app.state.store.transaction() as db:
        a=session(request,db,'staff' if staff else None);access(db,a,subject,'can_review' if staff else None)
        return a

@contextmanager
def store(request):
    with closing(sqlite3.connect(request.app.state.settings.root/'kide.sqlite',timeout=10)) as db:
        db.row_factory=sqlite3.Row
        db.execute('CREATE TABLE IF NOT EXISTS drafts(id TEXT PRIMARY KEY,subject TEXT,actor TEXT,transcript TEXT,state TEXT,result TEXT,reviewed TEXT,recipients TEXT,created TEXT,updated TEXT)')
        columns={r[1] for r in db.execute('PRAGMA table_info(drafts)')}
        if 'reviewer' not in columns:db.execute('ALTER TABLE drafts ADD COLUMN reviewer TEXT')
        if 'client_result' not in columns:db.execute('ALTER TABLE drafts ADD COLUMN client_result INTEGER NOT NULL DEFAULT 0')
        with db:yield db

def scopes_for(subject):return ['daily','social','health'] if subject in ('A','B') else sorted(SCOPES)

def recipients(request,subject):
    if subject in ('A','B'):
        from .provided_workflow import people,workflow,policy
        with workflow(request.app.state.settings) as db:
            return [{**{k:p[k] for k in ('actor_id','display_name')},'scopes':policy(db,p)['groups'],'version':policy(db,p)['revision']} for p in people(request.app.state.settings) if p['subject']==subject]
    with request.app.state.store.transaction() as db:
        return [{'actor_id':r['actor_id'],'display_name':r['display_name'],'scopes':grant(db,subject,r['actor_id'])['scopes'] if grant(db,subject,r['actor_id'])['status']=='confirmed' else [],'version':grant(db,subject,r['actor_id'])['version']} for r in db.execute("SELECT a.* FROM actors a JOIN access_memberships m ON m.actor_id=a.actor_id WHERE a.role='family' AND a.active=1 AND m.active=1 AND m.subject_id=?",(subject,))]

def row(db,id,subject):
    r=db.execute('SELECT * FROM drafts WHERE id=? AND subject=?',(id,subject)).fetchone()
    if not r:raise Fault('RESOURCE_NOT_FOUND',404)
    return r

def dto(r):
    return {'id':r['id'],'state':r['state'],'transcript':r['transcript'],'result':json.loads(r['reviewed'] or r['result']) if (r['reviewed'] or r['result']) else None,'created':r['created'],'language':'fi','ai_executed':None if r['client_result'] else bool(r['result']),'execution_mode':'CLIENT_REPORTED' if r['client_result'] else 'LIVE','origin':'TEAM_SYNTHETIC_VOICE','reviewed_by':r['reviewer']}

def validate_result(value,subject):
    if not isinstance(value,dict):raise ValueError()
    notes=value.get('nursing_note');cards=value.get('laheiskortti');warnings=value.get('huomiot_hoitajalle',[])
    if not isinstance(notes,dict) or not isinstance(cards,dict):raise ValueError()
    def string(v,nullable=False):
        if nullable and v is None:return None
        if not isinstance(v,str) or len(v)>5000:raise ValueError()
        return v
    result={'nursing_note':{k:string(notes.get(k),True) for k in NOTES},'laheiskortti':{},'huomiot_hoitajalle':[]}
    for k in CARDS:
        c=cards.get(k)
        if not isinstance(c,dict) or not isinstance(c.get('kasitelty'),bool):raise ValueError()
        result['laheiskortti'][k]={'teksti':string(c.get('teksti') or ''),'lahde':string(c.get('lahde') or ''),'kasitelty':c['kasitelty'],'scopes':scopes_for(subject)}
    if not isinstance(warnings,list) or len(warnings)>50:raise ValueError()
    result['huomiot_hoitajalle']=[string(w) for w in warnings]
    return result

def generate(transcript,settings):
    cfg=config(settings)
    if not cfg:raise Fault('PROVIDER_NOT_CONFIGURED',503)
    if not GENERATION_SLOT.acquire(blocking=False):raise Fault('PROVIDER_BUSY',503)
    try:
        with httpx.Client(timeout=90,follow_redirects=False) as client:
            with client.stream('POST',cfg['base_url'].rstrip('/')+'/v1/record',headers={'X-API-Key':cfg['api_key']},json={'transcript':transcript}) as response:
                if response.status_code!=200:raise ValueError()
                raw=b''
                for chunk in response.iter_bytes():
                    raw+=chunk
                    if len(raw)>200000:raise ValueError()
                return json.loads(raw)
    except Exception:raise Fault('KIDE_GENERATION_FAILED',502) from None
    finally:GENERATION_SLOT.release()

class Create(Input):
    request_id:str=Field(pattern=r'^[a-zA-Z0-9-]{16,80}$')
    transcript:str=Field(min_length=1,max_length=30000)
    external_synthetic_ack:bool

@router.get('/{subject}/drafts')
def drafts(subject:str,request:Request):
    auth(request,subject)
    with store(request) as db:items=[dto(r) for r in db.execute('SELECT * FROM drafts WHERE subject=? ORDER BY created DESC LIMIT 20',(subject,))]
    return envelope({'items':items,'recipients':recipients(request,subject),'scopes':scopes_for(subject)})

@router.post('/{subject}/drafts')
def create(subject:str,body:Create,request:Request):
    a=auth(request,subject);text=clean_transcript(body.transcript)
    if not body.external_synthetic_ack or not text:raise Fault('REVIEW_REQUIRED')
    with store(request) as db:
        db.execute('BEGIN IMMEDIATE')
        old=db.execute('SELECT * FROM drafts WHERE id=?',(body.request_id,)).fetchone()
        if old:
            if old['subject']!=subject or old['transcript']!=text or old['actor']!=a['actor_id']:raise Fault('IDEMPOTENCY_CONFLICT',409)
            if old['state']=='generating' and (datetime.now(timezone.utc)-datetime.fromisoformat(old['updated'])).total_seconds()<120:raise Fault('PROVIDER_BUSY',409)
            if old['state'] not in ('failed','generating'):return envelope(dto(old))
            db.execute("UPDATE drafts SET state='generating',updated=? WHERE id=?",(now(),body.request_id))
        else:db.execute('INSERT INTO drafts(id,subject,actor,transcript,state,result,reviewed,recipients,created,updated) VALUES (?,?,?,?,?,?,?,?,?,?)',(body.request_id,subject,a['actor_id'],text,'generating',None,None,'{}',now(),now()))
    try:
        result=validate_result(generate(text,request.app.state.settings),subject)
        auth(request,subject)
        with store(request) as db:db.execute("UPDATE drafts SET state='draft',result=?,updated=? WHERE id=?",(json.dumps(result,ensure_ascii=False),now(),body.request_id))
    except Exception as e:
        with store(request) as db:db.execute("UPDATE drafts SET state='failed',updated=? WHERE id=?",(now(),body.request_id))
        if isinstance(e,Fault):raise
        raise Fault('KIDE_INVALID_RESULT',502) from None
    with store(request) as db:return envelope(dto(row(db,body.request_id,subject)))

class Review(Input):
    result:dict
    recipients:list[str]=Field(max_length=20)
    checked:bool

@router.post('/{subject}/drafts/{id}/publish')
def publish(subject:str,id:str,body:Review,request:Request):
    a=auth(request,subject)
    if not body.checked:raise Fault('REVIEW_REQUIRED')
    try:result=validate_result(body.result,subject)
    except (ValueError,TypeError):raise Fault('VALIDATION_FAILED') from None
    with store(request) as db:
        db.execute('BEGIN IMMEDIATE');r=row(db,id,subject)
        if r['state'] not in ('draft','published'):raise Fault('REVIEW_REQUIRED')
        for key,c in result['laheiskortti'].items():
            scopes=body.result['laheiskortti'][key].get('scopes',[])
            if not isinstance(scopes,list) or not scopes or any(not isinstance(s,str) for s in scopes) or not set(scopes)<=set(scopes_for(subject)):raise Fault('SCOPE_FORBIDDEN',403)
            c['scopes']=sorted(set(scopes))
            if c['kasitelty'] and (not c['teksti'].strip() or not c['lahde'].strip() or c['lahde'] not in r['transcript']):raise Fault('EVIDENCE_REQUIRED')
        profiles={p['actor_id']:p for p in recipients(request,subject)}
        selected={}
        for rid in set(body.recipients):
            p=profiles.get(rid)
            if not p:raise Fault('SCOPE_FORBIDDEN',403)
            if not any(c['kasitelty'] and set(c['scopes'])<=set(p['scopes']) for c in result['laheiskortti'].values()):raise Fault('SCOPE_FORBIDDEN',403)
            selected[rid]=p['version']
        serialized=json.dumps(result,ensure_ascii=False,sort_keys=True)
        if r['state']=='published':
            if r['reviewed']!=serialized or set(json.loads(r['recipients']))!=set(selected):raise Fault('ALREADY_PUBLISHED',409)
        else:
            db.execute("UPDATE drafts SET state='published',reviewed=?,recipients=?,updated=?,reviewer=? WHERE id=?",(serialized,json.dumps(selected),now(),a['actor_id'],id))
    return envelope({'id':id,'state':'published','language':'fi','recipients':len(selected),'reviewed_by':a['actor_id']})

@router.post('/{subject}/drafts/{id}/withdraw')
def withdraw(subject:str,id:str,request:Request):
    auth(request,subject)
    with store(request) as db:
        row(db,id,subject);db.execute("UPDATE drafts SET state='withdrawn',updated=? WHERE id=?",(now(),id))
    return envelope({'state':'withdrawn'})

@router.get('/{subject}/family')
def family(subject:str,request:Request):
    a=auth(request,subject,False)
    if a['role']!='family':raise Fault('ROLE_FORBIDDEN',403)
    p=next((p for p in recipients(request,subject) if p['actor_id']==a['actor_id']),None)
    items=[]
    if p:
        with store(request) as db:
            for r in db.execute("SELECT * FROM drafts WHERE subject=? AND state='published' ORDER BY updated DESC LIMIT 50",(subject,)):
                versions=json.loads(r['recipients'])
                if versions.get(a['actor_id'])!=p['version']:continue
                cards={k:{'teksti':c['teksti'],'lahde':c['lahde']} for k,c in json.loads(r['reviewed'])['laheiskortti'].items() if c['kasitelty'] and set(c['scopes'])<=set(p['scopes'])}
                if cards:items.append({'id':r['id'],'cards':cards,'published_at':r['updated'],'language':'fi'})
    return envelope({'items':items,'language':'fi'})


class ClientDraft(Create):
    result:dict|None=None

@router.post('/{subject}/drafts/direct')
def save_client_draft(subject:str,body:ClientDraft,request:Request):
    """Store a browser-returned provider candidate, never a server-verified AI result."""
    a=auth(request,subject);text=clean_transcript(body.transcript)
    if not body.external_synthetic_ack or not text:raise Fault('REVIEW_REQUIRED')
    result=None
    if body.result is not None:
        try:result=validate_result(body.result,subject)
        except (ValueError,TypeError):raise Fault('KIDE_INVALID_RESULT',422) from None
    with store(request) as db:
        db.execute('BEGIN IMMEDIATE')
        old=db.execute('SELECT * FROM drafts WHERE id=?',(body.request_id,)).fetchone()
        if old:
            if old['subject']!=subject or old['actor']!=a['actor_id'] or old['transcript']!=text or not old['client_result']:raise Fault('IDEMPOTENCY_CONFLICT',409)
            if old['state']!='awaiting_client':return envelope(dto(old))
        else:
            db.execute('INSERT INTO drafts(id,subject,actor,transcript,state,result,reviewed,recipients,created,updated,client_result) VALUES (?,?,?,?,?,?,?,?,?,?,?)',(body.request_id,subject,a['actor_id'],text,'awaiting_client',None,None,'{}',now(),now(),1))
        if result is not None:db.execute("UPDATE drafts SET state='draft',result=?,updated=? WHERE id=?",(json.dumps(result,ensure_ascii=False),now(),body.request_id))
        return envelope(dto(row(db,body.request_id,subject)))
