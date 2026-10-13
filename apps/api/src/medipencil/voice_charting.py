"""Four-domain charting checklist. Rules suggest exact evidence, never clinical facts."""
import re
from typing import Literal
from fastapi import APIRouter,Request
from pydantic import Field
from .common import Input,Fault,now,uid,envelope
from .db import need,many,insert,dump,audit
from .domain import source_ref,timestamp
from .records import staff,record_dto,manual_job
from .security import execute,revision
router=APIRouter(prefix='/api/v1')
# Field-level questions deliberately remain unresolved even when a keyword matches.
FIELDS={
 'food_amount':(1,'meals',r'식사|아침|점심|저녁|ruok|söi|syö|ater|meal|breakfast'),
 'food_help':(1,'meals',r'식사|먹|ruok|syö|söi|eat|meal'),
 'fluids':(1,'meals',r'수분|물\s*\d|마셨|juo|neste|drink|fluid'),
 'hygiene':(1,'health_context',r'위생|샤워|양치|세수|hygien|pesey|suihku|wash|shower'),
 'skin':(1,'health_context',r'피부|상처|욕창|iho|haava|skin|wound'),
 'elimination':(1,'health_context',r'배변|대변|소변|변비|기저귀|ulost|virtsa|ummetus|vaippa|bowel|urine'),
 'mobility':(1,'movement',r'산책|걸|보행|워커|이동|휠체어|낙상|kävel|liikku|rollaatt|pyörätuol|walk|mobil|fall'),
 'sleep':(1,'sleep',r'수면|잠|깼|nukk|herä|uni\b|sleep|awake'),
 'vitals':(2,'health_context',r'혈압|맥박|체온|혈당|verenpaine|syke|lämpö|verensoker|pressure|pulse|temperature|glucose'),
 'pain':(2,'health_context',r'통증|아프|진통|kipu|kivun|pain'),
 'medication':(3,'medication',r'복약|복용|투약|약을|약은|lääk|annos|medicat|dose'),
 'prn':(3,'medication',r'필요시|필요 시|tarvitta|prn\b|as needed'),
 'mood':(4,'health_context',r'기분|불안|초조|mieliala|ahdist|levoto|mood|anxious'),
 'social':(4,'care_contact',r'대화|교류|참여|활동|취미|단체|osallist|keskust|harrast|social|activit|participat'),
}
class Start(Input):
    capture_id:str
    required:list[str]=Field(min_length=1,max_length=len(FIELDS))
class Answer(Input):
    status:Literal['confirmed','unknown','not_applicable','follow_up']
    text:str=Field(default='',max_length=2000)
    reason:str=Field(default='',max_length=500)
    speaker:Literal['resident','carer','unknown']='unknown'
    type:Literal['statement','observation','plan']='statement'
    observed_at:str|None=None
class Save(Input):
    answers:dict[str,Answer]
class Finish(Input):
    checked:bool

def sources(db,row):
    cap=need(db,'SELECT * FROM captures WHERE capture_id=?',(row['capture_id'],))
    if cap['subject_id']!=row['subject_id']:raise Fault('SUBJECT_MISMATCH',409)
    if cap['status'] in ('canceled','failed'):raise Fault('STALE_EVIDENCE',409)
    if not cap['source_refs']:raise Fault('EVIDENCE_REQUIRED')
    for ref in cap['source_refs']:
        src=need(db,'SELECT * FROM source_events WHERE source_id=? AND version=?',(ref['source_id'],ref['source_version']))
        if src['data_origin']!='TEAM_SYNTHETIC':raise Fault('EGRESS_DENIED',403)
    return cap,[source_ref(db,ref,row['subject_id']) for ref in cap['source_refs']]

def render(db,id):
    row=need(db,'SELECT * FROM voice_charts WHERE chart_id=?',(id,));cap,utterances=sources(db,row)
    row['suggestions']={key:[u['text'] for u in utterances if re.search(FIELDS[key][2],u['text'],re.I)] for key in row['required']}
    row['pending']=[key for key in row['required'] if key not in row['answers']]
    row['transcript']=[u['text'] for u in utterances]
    row['execution']={'provider_id':'charting-rules-v1','ai_executed':False,'input_mode':cap['input_mode'],'classification':'keyword_candidates_only'}
    return row

@router.get('/staff/residents/{s}/voice-charts')
def listing(s:str,request:Request):
    with request.app.state.store.transaction() as db:
        staff(request,db,s)
        # List summaries only; opening a draft revalidates evidence.
        return envelope({'items':many(db,'SELECT chart_id,status,revision,created_at FROM voice_charts WHERE subject_id=? ORDER BY created_at DESC LIMIT 50',(s,))})

@router.post('/staff/residents/{s}/voice-charts',status_code=201)
def start(s:str,body:Start,request:Request):
    with request.app.state.store.transaction() as db:
        actor=staff(request,db,s)
        if len(set(body.required))!=len(body.required) or not set(body.required)<=FIELDS.keys():raise Fault('VALIDATION_FAILED')
        def operation():
            cap,unused=sources(db,{'capture_id':body.capture_id,'subject_id':s})
            if cap['status']!='transcribed':raise Fault('INVALID_STATE',409)
            id=uid();t=now()
            insert(db,'voice_charts',chart_id=id,subject_id=s,capture_id=body.capture_id,required_json=body.required,created_by=actor['actor_id'],created_at=t,updated_at=t)
            audit(db,actor['actor_id'],'voice_chart_created',s,id)
            return {'id':id}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:render(db,ref['id'])))

def authorized(db,id,request):
    row=need(db,'SELECT * FROM voice_charts WHERE chart_id=?',(id,));actor=staff(request,db,row['subject_id']);return row,actor

@router.get('/staff/voice-charts/{id}')
def read(id:str,request:Request):
    with request.app.state.store.transaction() as db:
        authorized(db,id,request)
        return envelope(render(db,id))

@router.patch('/staff/voice-charts/{id}')
def save(id:str,body:Save,request:Request):
    with request.app.state.store.transaction() as db:
        row,actor=authorized(db,id,request)
        def operation():
            revision(request,row);sources(db,row)
            if row['status']!='draft':raise Fault('INVALID_STATE',409)
            if not set(body.answers)<=set(row['required']):raise Fault('VALIDATION_FAILED')
            for answer in body.answers.values():
                if answer.status=='confirmed':
                    if not answer.text.strip() or not answer.observed_at:raise Fault('EVIDENCE_REQUIRED')
                    timestamp(answer.observed_at)
                elif not answer.reason.strip():raise Fault('EVIDENCE_REQUIRED')
            db.execute('UPDATE voice_charts SET answers_json=?,revision=revision+1,updated_at=? WHERE chart_id=?',(dump({k:v.model_dump() for k,v in body.answers.items()}),now(),id))
            audit(db,actor['actor_id'],'voice_chart_saved',row['subject_id'],id)
            return {'id':id}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:render(db,ref['id'])))

@router.post('/staff/voice-charts/{id}/finish')
def finish(id:str,body:Finish,request:Request):
    with request.app.state.store.transaction() as db:
        row,actor=authorized(db,id,request)
        def operation():
            revision(request,row);cap,original=sources(db,row)
            if row['status']!='draft' or cap['status']!='transcribed':raise Fault('INVALID_STATE',409)
            if not body.checked or any(k not in row['answers'] for k in row['required']):raise Fault('REVIEW_REQUIRED')
            # Conservative scopes preserve every original source scope; no automatic declassification.
            inherited={scope for u in original for scope in u['required_scopes']}
            segments=[]
            for key,a in row['answers'].items():
                if a['status']!='confirmed':continue
                scope=sorted(inherited|{FIELDS[key][1],'health_context'})
                sid=uid();observed=timestamp(a['observed_at']);payload={'text':a['text'],'speaker':a['speaker'],'type':a['type'],'required_scopes':scope,'chart_field':key}
                insert(db,'source_events',source_id=sid,version=1,subject_id=row['subject_id'],source_type='staff_note',occurred_at=observed,recorded_at=now(),data_origin='TEAM_SYNTHETIC',integration_mode='MANUAL_INPUT',payload_json=payload,source_refs_json=cap['source_refs'])
                segments.append({k:payload[k] for k in ('text','speaker','type','required_scopes')}|{'segment_id':uid(),'evidence_refs':[{'kind':'source','source_id':sid,'source_version':1},*cap['source_refs']]})
            if not segments:raise Fault('EVIDENCE_REQUIRED')
            record=uid();t=now()
            insert(db,'record_versions',record_id=record,version=1,subject_id=row['subject_id'],capture_id=cap['capture_id'],status='draft',segments_json=segments,created_at=t,updated_at=t)
            manual_job(db,row['subject_id'],cap['capture_id'],'extract',{'kind':'record','id':record,'version':1})
            db.execute('UPDATE voice_charts SET status="completed",record_id=?,revision=revision+1,updated_at=? WHERE chart_id=?',(record,t,id))
            db.execute('UPDATE captures SET status="draft_ready",revision=revision+1,updated_at=? WHERE capture_id=?',(t,cap['capture_id']))
            audit(db,actor['actor_id'],'voice_chart_completed',row['subject_id'],id)
            return {'id':record}
        def output(ref):
            sources(db,row)
            return record_dto(db,ref['id'],1)
        return envelope(execute(request,db,actor,body.model_dump(),operation,output))
