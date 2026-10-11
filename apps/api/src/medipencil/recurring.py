"""Daily app delivery from a deterministic synthetic EMR adapter, never an AI approval."""
import asyncio
import logging
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
from fastapi import APIRouter,Request
from .common import Input,Fault,envelope,now,uid
from .db import one,many,need,insert,dump,audit
from .security import access,grant,permitted,execute,session
from .records import staff
from .domain import source_ref,record_ref

router=APIRouter(prefix='/api/v1')
ZONE=ZoneInfo('Europe/Helsinki')
ROUTINE={'meals','movement'}

def stamp(dt):return dt.astimezone(timezone.utc).isoformat(timespec='microseconds')
def next_run(dt):
    local=dt.astimezone(ZONE);target=local.replace(hour=18,minute=0,second=0,microsecond=0)
    if target<=local:target+=timedelta(days=1)
    return stamp(target)

class Setting(Input):
    enabled:bool
    expected_revision:int

def schedules(db,s):
    people=many(db,'SELECT a.actor_id,a.display_name FROM actors a JOIN access_memberships m ON m.actor_id=a.actor_id WHERE m.subject_id=? AND m.active=1 AND a.active=1 AND a.role="family"',(s,))
    return [{'recipient_id':p['actor_id'],'display_name':p['display_name'],**(one(db,'SELECT * FROM delivery_schedules WHERE subject_id=? AND recipient_id=?',(s,p['actor_id'])) or {'enabled':False,'revision':0,'next_run_at':None,'last_run_at':None,'last_result':None,'exceptions':[]})} for p in people]

@router.get('/staff/residents/{s}/delivery-schedules')
def get_schedules(s:str,request:Request):
    with request.app.state.store.transaction() as db:
        staff(request,db,s)
        return envelope({'items':schedules(db,s),'timezone':'Europe/Helsinki','local_time':'18:00','integration_mode':'SIMULATED','ai_executed':False})

@router.get('/family/residents/{s}/delivery-schedule')
def family_schedule(s:str,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'family');access(db,actor,s)
        row=one(db,'SELECT * FROM delivery_schedules WHERE subject_id=? AND recipient_id=?',(s,actor['actor_id']))
        return envelope({k:row[k] for k in ['enabled','next_run_at','last_run_at','last_result']} if row else {'enabled':False,'next_run_at':None,'last_run_at':None,'last_result':None})

@router.post('/staff/residents/{s}/delivery-schedules/{recipient}')
def set_schedule(s:str,recipient:str,body:Setting,request:Request):
    with request.app.state.store.transaction() as db:
        actor=staff(request,db,s);access(db,{'actor_id':recipient},s)
        target=need(db,'SELECT * FROM actors WHERE actor_id=?',(recipient,))
        if target['role']!='family' or not target['active']:raise Fault('ROLE_FORBIDDEN',403)
        def operation():
            old=one(db,'SELECT * FROM delivery_schedules WHERE subject_id=? AND recipient_id=?',(s,recipient))
            if (old['revision'] if old else 0)!=body.expected_revision:raise Fault('REVISION_CONFLICT',409)
            if body.enabled and not grant(db,s,recipient)['scopes']:raise Fault('REVIEW_REQUIRED')
            due=next_run(datetime.now(timezone.utc)) if body.enabled else None
            if old:
                db.execute('UPDATE delivery_schedules SET enabled=?,revision=revision+1,configured_by=?,next_run_at=?,updated_at=? WHERE subject_id=? AND recipient_id=?',(int(body.enabled),actor['actor_id'],due,now(),s,recipient))
            else:insert(db,'delivery_schedules',subject_id=s,recipient_id=recipient,enabled=int(body.enabled),configured_by=actor['actor_id'],next_run_at=due,updated_at=now())
            audit(db,actor['actor_id'],'delivery.schedule',s,recipient)
            return {'s':s,'recipient':recipient}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:need(db,'SELECT * FROM delivery_schedules WHERE subject_id=? AND recipient_id=?',(ref['s'],ref['recipient']))))

def import_routine(db,s,dt):
    # Only this internal adapter can designate an eligible source. Text/LLM input cannot.
    if s!='aino':raise Fault('PROVIDER_NOT_CONFIGURED')
    day=dt.astimezone(ZONE).date().isoformat();sid='routine-emr-'+s+'-'+day
    existing=one(db,'SELECT * FROM source_events WHERE source_id=? AND version=1',(sid,))
    if existing:return existing
    utterances=[
        {'utterance_id':sid+'-meals','text':'Aino söi aamupalan ruokasalissa.','type':'observation','speaker':'carer','required_scopes':['meals'],'emr_status':'confirmed'},
        {'utterance_id':sid+'-movement','text':'Aino käveli hoitajan kanssa käytävällä.','type':'observation','speaker':'carer','required_scopes':['movement'],'emr_status':'confirmed'},
        {'utterance_id':sid+'-plan','text':'Iltapäivälle on suunniteltu ulkoilu. Toteutumista ei ole vielä vahvistettu.','type':'plan','speaker':'carer','required_scopes':['outdoors'],'emr_status':'unconfirmed'}]
    occurred=stamp(dt.astimezone(ZONE).replace(hour=8,minute=0,second=0,microsecond=0))
    insert(db,'source_events',source_id=sid,version=1,subject_id=s,source_type='transcript',occurred_at=occurred,recorded_at=stamp(dt),data_origin='TEAM_SYNTHETIC',integration_mode='SIMULATED',payload_json={'adapter':'routine-v1','utterances':utterances})
    insert(db,'routine_delivery_sources',source_id=sid,source_version=1)
    return need(db,'SELECT * FROM source_events WHERE source_id=? AND version=1',(sid,))

def routine_ref(db,ref,s):
    if not one(db,'SELECT * FROM routine_delivery_sources WHERE source_id=? AND source_version=?',(ref.get('source_id'),ref.get('source_version'))):raise Fault('EVIDENCE_REQUIRED')
    u=source_ref(db,ref,s)
    if u.get('emr_status')!='confirmed' or u.get('type')!='observation' or not u.get('required_scopes') or not set(u['required_scopes'])<=ROUTINE:raise Fault('REVIEW_REQUIRED')
    return u

def delivery_day(dt):
    local=dt.astimezone(ZONE)
    return local if local.hour>=18 else local-timedelta(days=1)

def deliver(db,schedule,dt):
    source_dt=delivery_day(dt)
    s,recipient=schedule['subject_id'],schedule['recipient_id'];day=source_dt.date().isoformat()
    if one(db,'SELECT * FROM routine_delivery_runs WHERE subject_id=? AND recipient_id=? AND local_day=?',(s,recipient,day)):return 'already_processed',None,[]
    for who in [recipient,schedule['configured_by']]:
        if not need(db,'SELECT * FROM actors WHERE actor_id=?',(who,))['active']:raise Fault('ROLE_FORBIDDEN',403)
    access(db,{'actor_id':schedule['configured_by']},s,'can_review');access(db,{'actor_id':recipient},s)
    source=import_routine(db,s,source_dt);g=grant(db,s,recipient);items=[];exceptions=[]
    if g['status']!='confirmed' or not g['scopes']:return 'no_permission',None,[]
    for u in source['payload']['utterances']:
        if not permitted(db,s,recipient,u['required_scopes']):continue
        ref={'kind':'source','source_id':source['source_id'],'source_version':source['version'],'utterance_id':u['utterance_id']}
        try:routine_ref(db,ref,s)
        except Fault:exceptions.append({'source_id':source['source_id'],'text':u['text'],'reason':'unconfirmed_or_nonroutine'});continue
        items.append({'item_id':uid(),'topic':u['required_scopes'][0],'statement':u['text'],'claim_type':'staff_observation','status':'confirmed','action_status':None,'observed_at':source['occurred_at'],'required_scopes':u['required_scopes'],'evidence_refs':[ref],'meaning_checked':False,'language_checked':False})
    if not items:return 'no_new_content',None,exceptions
    # Retain previously released, still-valid history; never pick up new AI/manual drafts.
    previous=one(db,'SELECT * FROM publications WHERE subject_id=? AND recipient_id=? AND published_at IS NOT NULL ORDER BY published_at DESC,rowid DESC LIMIT 1',(s,recipient))
    seen={dump(i['evidence_refs']) for i in items}
    if previous:
        for item in previous['items']:
            if dump(item['evidence_refs']) in seen or not permitted(db,s,recipient,item['required_scopes']):continue
            try:
                for ref in item['evidence_refs']:
                    (routine_ref if ref.get('kind')=='source' else record_ref)(db,ref,s)
            except Fault:continue
            items.append(item)
    item_ids={i['item_id'] for i in items}
    bindings=[dict(b,reviewed_by=b.get('reviewed_by') or previous['reviewed_by'],original_published_at=b.get('original_published_at') or previous['published_at']) for b in previous['answer_bindings'] if set(b['item_ids'])<=item_ids] if previous else []
    id=uid();t=stamp(dt);epoch=need(db,'SELECT * FROM residents WHERE subject_id=?',(s,))['content_epoch']
    insert(db,'publications',publication_id=id,subject_id=s,recipient_id=recipient,lang='fi',status='published',consent_version=g['version'],content_epoch=epoch,items_json=items,answer_bindings_json=bindings,input_refs_json=[ref for item in items for ref in item['evidence_refs']],generation_meta_json={'provider_id':'synthetic_emr_routine','input_mode':'confirmed_emr','execution_mode':'SIMULATED','ai_executed':False,'origin':'TEAM_SYNTHETIC','human_review_per_delivery':False,'policy':'routine-v1','stt':'not_applicable'},published_at=t,created_at=t,updated_at=t)
    audit(db,schedule['configured_by'],'delivery.automatic',s,id)
    return 'delivered',id,exceptions

def tick(store,dt=None):
    dt=dt or datetime.now(timezone.utc)
    with store.transaction() as db:
        due=many(db,'SELECT * FROM delivery_schedules WHERE enabled=1 AND next_run_at<=?',(stamp(dt),))
    for schedule in due:
        with store.transaction() as db:
            current=need(db,'SELECT * FROM delivery_schedules WHERE subject_id=? AND recipient_id=?',(schedule['subject_id'],schedule['recipient_id']))
            if not current['enabled'] or current['next_run_at']>stamp(dt):continue
            # Roll back all source/publication mutations on an individual delivery failure.
            db.execute('SAVEPOINT delivery')
            try:result,pid,exceptions=deliver(db,current,dt)
            except Fault as exc:
                db.execute('ROLLBACK TO delivery');result,pid,exceptions='blocked:'+exc.code,None,[]
            db.execute('RELEASE delivery')
            s,recipient=current['subject_id'],current['recipient_id']
            day=delivery_day(dt).date().isoformat()
            db.execute('INSERT OR IGNORE INTO routine_delivery_runs VALUES(?,?,?,?,?,?)',(s,recipient,day,result,pid,stamp(dt)))
            db.execute('UPDATE delivery_schedules SET last_run_at=?,last_result=?,last_publication_id=COALESCE(?,last_publication_id),exceptions_json=?,next_run_at=?,updated_at=? WHERE subject_id=? AND recipient_id=?',(stamp(dt),result,pid,dump(exceptions),next_run(dt),stamp(dt),s,recipient))

async def worker(store):
    while True:
        try:await asyncio.to_thread(tick,store)
        except Exception:logging.getLogger(__name__).exception('Scheduled delivery failed; retrying next minute')
        await asyncio.sleep(60)
