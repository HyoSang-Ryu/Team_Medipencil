"""Durable synthetic EMR -> local AI -> reviewable publication, never auto approval."""
from datetime import datetime,timedelta,timezone
from zoneinfo import ZoneInfo
from fastapi import APIRouter,Request,BackgroundTasks
from pydantic import Field
from .common import Input,Fault,now,uid,envelope
from .db import one,need,insert,dump
from .security import access,grant,permitted,execute
from .records import staff,job_dto
from .domain import source_ref
from .synthetic_emr import records
from .ai_wording import OllamaFamilyWording,Summary,validate_summary
from .local_jobs import _execution_slot
router=APIRouter(prefix='/api/v1')

class Generate(Input):
    recipient_id:str
    days:int=Field(default=3,ge=1,le=30)

@router.post('/staff/residents/{s}/ai-summary',status_code=202)
def generate(s:str,body:Generate,request:Request,background:BackgroundTasks):
    store=request.app.state.store;settings=request.app.state.settings
    with store.transaction() as db:
        actor=staff(request,db,s);access(db,{'actor_id':body.recipient_id},s)
        target=need(db,'SELECT * FROM actors WHERE actor_id=?',(body.recipient_id,))
        if target['role']!='family' or not target['active']:raise Fault('ROLE_FORBIDDEN',403)
        def operation():
            if settings.models.llm_backend!='ollama':raise Fault('PROVIDER_NOT_CONFIGURED',503)
            if one(db,'SELECT job_id FROM processing_jobs WHERE status IN ("queued","running")'):raise Fault('PROVIDER_BUSY',503)
            resident=need(db,'SELECT * FROM residents WHERE subject_id=?',(s,))
            if resident['data_origin']!='TEAM_SYNTHETIC':raise Fault('EGRESS_DENIED',403)
            end=datetime.now(ZoneInfo('Europe/Helsinki')).date();raw=records(s,end,body.days)
            g=grant(db,s,body.recipient_id);evidence=[];refs=[]
            for e in raw:
                if not permitted(db,s,body.recipient_id,e['required_scopes']):continue
                sid='family-synthetic-v1-'+e['key'];ref={'kind':'source','source_id':sid,'source_version':1,'utterance_id':e['key']}
                if not one(db,'SELECT * FROM source_events WHERE source_id=? AND version=1',(sid,)):
                    insert(db,'source_events',source_id=sid,version=1,subject_id=s,source_type='transcript',occurred_at=e['occurred_at'],recorded_at=now(),data_origin='TEAM_SYNTHETIC',integration_mode='SIMULATED',payload_json={'adapter':'family-synthetic-v1','utterances':[e|{'utterance_id':e['key']}]})
                u=source_ref(db,ref,s)
                if u['text']!=e['text']:raise Fault('STALE_EVIDENCE',409)
                evidence.append(e);refs.append(ref)
            if not evidence:raise Fault('EVIDENCE_REQUIRED')
            id=uid();meta={'provider_id':'ollama','execution_mode':'NOT_RUN','ai_executed':False,'origin':'TEAM_SYNTHETIC','input_mode':'synthetic_emr','requested_by':actor['actor_id'],'recipient_id':body.recipient_id,'consent_version':g['version'],'content_epoch':resident['content_epoch'],'period':{'start':(end-timedelta(days=body.days-1)).isoformat(),'end':end.isoformat()},'evidence':evidence}
            insert(db,'processing_jobs',job_id=id,subject_id=s,job_type='family_summary',status='queued',target_id=id,expected_revision=1,input_refs_json=refs,provider_id='ollama',execution_meta_json=meta,deadline_at=(datetime.now(timezone.utc)+timedelta(seconds=settings.models.timeout+10)).isoformat(),created_at=now(),updated_at=now())
            background.add_task(run,store,settings.models,id)
            return {'id':id}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:job_dto(db,ref['id'])))

def check(db,job):
    m=job['execution_meta'];s=job['subject_id']
    for actor in [m['requested_by'],m['recipient_id']]:
        if not need(db,'SELECT * FROM actors WHERE actor_id=?',(actor,))['active']:raise Fault('ROLE_FORBIDDEN',403)
        access(db,{'actor_id':actor},s,'can_review' if actor==m['requested_by'] else None)
    if job['status']!='running' or job['deadline_at']<=now():raise Fault('TIMEOUT',504)
    if grant(db,s,m['recipient_id'])['version']!=m['consent_version']:raise Fault('STALE_CONSENT',409)
    if need(db,'SELECT * FROM residents WHERE subject_id=?',(s,))['content_epoch']!=m['content_epoch']:raise Fault('STALE_EVIDENCE',409)
    for e,ref in zip(m['evidence'],job['input_refs']):
        u=source_ref(db,ref,s);src=need(db,'SELECT * FROM source_events WHERE source_id=? AND version=?',(ref['source_id'],ref['source_version']))
        if src['data_origin']!='TEAM_SYNTHETIC' or src['source_refs']:raise Fault('EGRESS_DENIED',403)
        if u['text']!=e['text'] or not permitted(db,s,m['recipient_id'],e['required_scopes']):raise Fault('STALE_EVIDENCE',409)

def run(store,config,id):
    acquired=False;actual=None
    try:
        acquired=_execution_slot.acquire(blocking=False)
        if not acquired:raise Fault('PROVIDER_BUSY',503)
        with store.transaction() as db:
            j=need(db,'SELECT * FROM processing_jobs WHERE job_id=?',(id,))
            if j['status']!='queued':return
            db.execute('UPDATE processing_jobs SET status="running",updated_at=? WHERE job_id=?',(now(),id))
            j=need(db,'SELECT * FROM processing_jobs WHERE job_id=?',(id,));check(db,j);m=j['execution_meta']
        actual=OllamaFamilyWording(config).render({'lineage':['TEAM_SYNTHETIC'],'period':m['period'],'evidence':m['evidence']})
        validate_summary(Summary.model_validate({'items':actual['items']}),m['evidence'])
        with store.transaction() as db:
            j=need(db,'SELECT * FROM processing_jobs WHERE job_id=?',(id,));check(db,j)
            mapping={e['key']:(e,ref) for e,ref in zip(m['evidence'],j['input_refs'])};items=[]
            for output in actual['items']:
                rows=[mapping[k] for k in output['evidence_keys']];e=rows[0][0];plan=e['type']=='plan'
                items.append({'item_id':uid(),'topic':e['topic'],'statement':output['statement'],'claim_type':'plan' if plan else 'staff_observation','status':'confirmed','action_status':'planned' if plan else None,'observed_at':max(row[0]['occurred_at'] for row in rows),'required_scopes':sorted({scope for row in rows for scope in row[0]['required_scopes']}),'evidence_refs':[row[1] for row in rows],'source_excerpt':'\n'.join(row[0]['occurred_at']+' · '+row[0]['text'] for row in rows),'meaning_checked':False,'language_checked':False})
            pid=uid();t=now();meta=actual['metadata']|{'policy':'ai-summary-v1','input_mode':'synthetic_emr','origin':'TEAM_SYNTHETIC','source_mode':'SIMULATED','period':m['period'],'language_review_status':'pending','human_review_required':True,'stt':'not_applicable'}
            insert(db,'publications',publication_id=pid,subject_id=j['subject_id'],recipient_id=m['recipient_id'],lang='fi',status='draft',consent_version=m['consent_version'],content_epoch=m['content_epoch'],items_json=items,answer_bindings_json=[],input_refs_json=j['input_refs'],generation_meta_json=meta,created_at=t,updated_at=t)
            db.execute('UPDATE processing_jobs SET status="succeeded",result_ref=?,execution_meta_json=?,updated_at=? WHERE job_id=?',(dump({'kind':'publication','id':pid}),dump(m|actual['metadata']),t,id))
    except Exception as exc:
        with store.transaction() as db:
            j=need(db,'SELECT * FROM processing_jobs WHERE job_id=?',(id,));meta=j['execution_meta']|(actual['metadata'] if actual else getattr(exc,'execution',{}))
            db.execute('UPDATE processing_jobs SET status="failed",error_code=?,execution_meta_json=?,updated_at=? WHERE job_id=? AND status IN ("queued","running")',(exc.code if isinstance(exc,Fault) else 'PROVIDER_FAILED',dump(meta),now(),id))
    finally:
        if acquired:_execution_slot.release()

@router.get('/staff/residents/{s}/ai-summaries')
def history(s:str,request:Request):
    from .db import many
    from .publications import check_snapshot
    with request.app.state.store.transaction() as db:
        staff(request,db,s);items=[]
        for p in many(db,'SELECT * FROM publications WHERE subject_id=? ORDER BY created_at DESC,rowid DESC LIMIT 50',(s,)):
            if p['generation_meta'].get('policy')!='ai-summary-v1':continue
            try:check_snapshot(db,p)
            except Fault:continue
            items.append(p)
        return envelope({'items':items})
