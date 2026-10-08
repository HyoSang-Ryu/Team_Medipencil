"""Independent synthetic EMR adapter feeding the existing evidence/review pipeline."""
from datetime import datetime
from zoneinfo import ZoneInfo
from fastapi import APIRouter, Request
from .common import Input, Fault, envelope, now
from .db import one, many, need, insert, dump
from .records import staff, record_dto
from .security import execute
from .domain import source_ref
router=APIRouter(prefix='/api/v1')


def bundle(s):
    day=datetime.now(ZoneInfo('Europe/Helsinki')).date().isoformat()
    return {'bundle_id':f'synthetic-emr-{s}-{day}', 'occurred_at':datetime.fromisoformat(day+'T08:00:00').replace(tzinfo=ZoneInfo('Europe/Helsinki')).isoformat(),
            'integration_mode':'SIMULATED','emr_connected':False,
            'utterances':[
                {'speaker':'carer','text':'Aino söi aamupalan ruokasalissa.','type':'observation','required_scopes':['meals']},
                {'speaker':'carer','text':'Aino käveli hoitajan kanssa käytävällä.','type':'observation','required_scopes':['movement']},
                {'speaker':'carer','text':'Iltapäivälle on suunniteltu ulkoilu. Toteutumista ei ole vielä vahvistettu.','type':'plan','required_scopes':['outdoors']}]}

@router.get('/staff/residents/{s}/emr-review')
def review(s:str,request:Request):
    with request.app.state.store.transaction() as db:
        staff(request,db,s)
        records=[]
        for r in many(db,'SELECT * FROM record_versions r WHERE subject_id=? AND version=(SELECT MAX(version) FROM record_versions v WHERE v.record_id=r.record_id) ORDER BY updated_at DESC LIMIT 100',(s,)):
            job=one(db,'SELECT * FROM processing_jobs WHERE target_id=? AND job_type="extract" AND status="succeeded" ORDER BY created_at DESC LIMIT 1',(r['capture_id'],))
            sources=[]
            for segment in r['segments']:
                for ref in segment['evidence_refs']:
                    # Only return still-valid references; invalidated records remain visible by status.
                    try:u=source_ref(db,ref,s)
                    except Fault:continue
                    if u['text'] not in sources:sources.append(u['text'])
            records.append({'record':record_dto(db,r['record_id'],r['version']), 'source_text':'\n'.join(sources), 'execution':job['execution_meta'] if job else None})
        return envelope({'bundle':bundle(s),'items':records,'limit':100})

@router.post('/staff/residents/{s}/emr-review/import',status_code=201)
def import_bundle(s:str,body:Input,request:Request):
    with request.app.state.store.transaction() as db:
        actor=staff(request,db,s)
        def operation():
            b=bundle(s);id=b['bundle_id'];cap=one(db,'SELECT * FROM captures WHERE capture_id=?',(id,))
            if not cap:
                t=now();utterances=[dict(u,utterance_id=f'{id}-{i}',classification_review='synthetic_emr') for i,u in enumerate(b['utterances'])]
                insert(db,'source_events',source_id=id,version=1,subject_id=s,source_type='transcript',occurred_at=b['occurred_at'],recorded_at=t,data_origin='TEAM_SYNTHETIC',integration_mode='SIMULATED',payload_json={'utterances':utterances,'external_id':id})
                refs=[{'kind':'source','source_id':id,'source_version':1,'utterance_id':u['utterance_id']} for u in utterances]
                insert(db,'captures',capture_id=id,subject_id=s,actor_id=actor['actor_id'],input_mode='text',status='transcribed',source_refs_json=refs,created_at=t,updated_at=t)
            return {'id':id}
        return envelope(execute(request,db,actor,{},operation,lambda ref:need(db,'SELECT * FROM captures WHERE capture_id=?',(ref['id'],))))
