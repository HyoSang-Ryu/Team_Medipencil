from typing import Literal
from fastapi import APIRouter, Request
from pydantic import Field
from .common import Input, Fault, envelope, now, uid
from .db import one, many, need, insert, audit, dump
from .security import session, access, execute, revision
from .domain import timestamp, scopes, source_ref, record_ref
router=APIRouter(prefix='/api/v1')
class Capture(Input):
    input_mode:Literal['text','audio']
    disclosure_ack:bool=False
    recording_permission_ref:str|None=None
class Utterance(Input):
    speaker:Literal['resident','carer','unknown']
    text:str=Field(min_length=1,max_length=20000)
    type:Literal['statement','observation','plan']='statement'
    required_scopes:list[str]=Field(default_factory=lambda:['health_context'])
class Transcript(Input):
    occurred_at:str
    utterances:list[Utterance]=Field(min_length=1,max_length=50)
class Draft(Input): question_ids:list[str]=Field(default_factory=list,max_length=50)
class CandidateReview(Input):
    candidate_id:str
    accepted:bool
    sufficient_answer_checked:bool
class SegmentReview(Input):
    segment_id:str
    meaning_checked:bool
    speaker_checked:bool
    negation_and_tense_checked:bool
    numbers_checked:bool
    scopes_checked:bool
class Approve(Input):
    version:int
    segment_reviews:list[SegmentReview]
    candidate_reviews:list[CandidateReview]
class Segment(Input):
    segment_id:str
    text:str=Field(min_length=1,max_length=20000)
    type:Literal['statement','observation','plan']
    speaker:Literal['resident','carer','unknown']
    evidence_refs:list[dict]=Field(min_length=1)
    required_scopes:list[str]
class Edit(Input):
    version:int
    segments:list[Segment]=Field(min_length=1,max_length=50)
    candidate_reviews:list[CandidateReview]=Field(default_factory=list)


def staff(request,db,s,permission='can_review'):
    actor=session(request,db,'staff');access(db,actor,s,permission);return actor

def invalidate(db,s,reason,questions=False):
    db.execute('UPDATE residents SET content_epoch=content_epoch+1 WHERE subject_id=?',(s,))
    db.execute('UPDATE publications SET status="invalidated",invalidated_at=?,invalidation_reason=?,revision=revision+1 WHERE subject_id=? AND status!="invalidated"',(now(),reason,s))
    if questions:
        db.execute('UPDATE family_questions SET status="unanswered",active_publication_id=NULL,status_reason="evidence_invalidated",revision=revision+1,updated_at=? WHERE subject_id=? AND status="answered"',(now(),s))

def record_dto(db,id,version):
    r=need(db,'SELECT * FROM record_versions WHERE record_id=? AND version=?',(id,version))
    r['answer_candidates']=many(db,'SELECT * FROM answer_candidates WHERE record_id=? AND record_version=?',(id,version))
    r['audio_applicable']=False
    return r

def job_dto(db,id):
    j=need(db,'SELECT * FROM processing_jobs WHERE job_id=?',(id,))
    return {'job_id':id,'job_type':j['job_type'],'status':j['status'],'result_ref':__import__('json').loads(j['result_ref']) if j['result_ref'] else None,'progress_stage':j['status'],'started_at':j['created_at'],'finished_at':j['updated_at'] if j['status'] in ('succeeded','failed','canceled') else None,'error_code':j['error_code'],'retryable':j['status']=='failed','execution':j['execution_meta']}

def manual_job(db,s,target,kind,ref):
    id=uid();t=now()
    insert(db,'processing_jobs',job_id=id,subject_id=s,job_type=kind,status='succeeded',target_id=target,expected_revision=1,input_refs_json=[],result_ref=dump(ref),provider_id='manual',execution_meta_json={'input_mode':'text','provider_id':'manual','execution_mode':'LIVE','ai_executed':False,'stt':'skipped','origin':'TEAM_SYNTHETIC'},deadline_at=t,created_at=t,updated_at=t)
    return id

@router.post('/staff/residents/{s}/captures',status_code=201)
def capture(s:str,body:Capture,request:Request):
    with request.app.state.store.transaction() as db:
        actor=staff(request,db,s)
        def operation():
            if body.input_mode=='audio':raise Fault('PROVIDER_NOT_CONFIGURED',503)
            id=uid();t=now()
            insert(db,'captures',capture_id=id,subject_id=s,actor_id=actor['actor_id'],input_mode=body.input_mode,status='created',created_at=t,updated_at=t)
            return {'id':id}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:need(db,'SELECT * FROM captures WHERE capture_id=?',(ref['id'],))))

@router.post('/staff/captures/{c}/text',status_code=201)
def text(c:str,body:Transcript,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');cap=need(db,'SELECT * FROM captures WHERE capture_id=?',(c,));access(db,actor,cap['subject_id'],'can_review')
        def operation():
            revision(request,cap)
            if cap['status']!='created' or cap['input_mode']!='text':raise Fault('INVALID_STATE',409)
            occurred=timestamp(body.occurred_at);id=uid();utterances=[]
            for u in body.utterances:
                utterances.append(u.model_dump()|{'utterance_id':uid(),'required_scopes':scopes(u.required_scopes),'classification_review':'staff_entered'})
            insert(db,'source_events',source_id=id,version=1,subject_id=cap['subject_id'],source_type='transcript',occurred_at=occurred,recorded_at=now(),data_origin='TEAM_SYNTHETIC',integration_mode='MANUAL_INPUT',payload_json={'utterances':utterances})
            refs=[{'kind':'source','source_id':id,'source_version':1,'utterance_id':u['utterance_id']} for u in utterances]
            db.execute('UPDATE captures SET source_refs_json=?,status="transcribed",revision=revision+1,updated_at=? WHERE capture_id=?',(dump(refs),now(),c))
            return {'id':c}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:need(db,'SELECT * FROM captures WHERE capture_id=?',(ref['id'],))))

@router.post('/staff/captures/{c}/drafts',status_code=202)
def draft(c:str,body:Draft,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');cap=need(db,'SELECT * FROM captures WHERE capture_id=?',(c,));access(db,actor,cap['subject_id'],'can_review')
        def operation():
            revision(request,cap)
            if cap['status']!='transcribed':raise Fault('INVALID_STATE',409)
            segments=[]
            for ref in cap['source_refs']:
                u=source_ref(db,ref,cap['subject_id'])
                segments.append({k:u[k] for k in ('text','speaker','type','required_scopes')}|{'segment_id':uid(),'evidence_refs':[ref]})
            id=uid();t=now()
            insert(db,'record_versions',record_id=id,version=1,subject_id=cap['subject_id'],capture_id=c,status='draft',segments_json=segments,created_at=t,updated_at=t)
            for qid in set(body.question_ids):
                q=need(db,'SELECT * FROM family_questions WHERE question_id=?',(qid,))
                if q['subject_id']!=cap['subject_id']:raise Fault('SUBJECT_MISMATCH',409)
                if q['status']=='answered':raise Fault('INVALID_STATE',409)
                insert(db,'answer_candidates',candidate_id=uid(),question_id=qid,record_id=id,record_version=1,answer_segment_ids_json=[s['segment_id'] for s in segments],review_status='pending')
            db.execute('UPDATE captures SET status="draft_ready",revision=revision+1,updated_at=? WHERE capture_id=?',(t,c))
            return {'id':manual_job(db,cap['subject_id'],c,'extract',{'kind':'record','id':id,'version':1})}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:job_dto(db,ref['id'])))

@router.get('/staff/jobs/{j}')
def job(j:str,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');row=need(db,'SELECT * FROM processing_jobs WHERE job_id=?',(j,));access(db,actor,row['subject_id'],'can_review')
        return envelope(job_dto(db,j))

@router.get('/staff/records/{r}')
def get_record(r:str,version:int,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');row=need(db,'SELECT * FROM record_versions WHERE record_id=? AND version=?',(r,version));access(db,actor,row['subject_id'],'can_review')
        return envelope(record_dto(db,r,version))

def validate_segments(db,segments,subject):
    if len({s['segment_id'] for s in segments})!=len(segments):raise Fault('VALIDATION_FAILED')
    for s in segments:
        needed=set();sources=[]
        for ref in s['evidence_refs']:
            u=source_ref(db,ref,subject);needed.update(u['required_scopes']);sources.append(u)
        # Manual adapter only permits faithful excerpts. Arbitrary wording requires a new source.
        if not any(s['text'] in u['text'] and s['speaker']==u['speaker'] and s['type']==u['type'] for u in sources): raise Fault('EVIDENCE_REQUIRED')
        if not needed<=set(scopes(s['required_scopes'])):raise Fault('REVIEW_REQUIRED')

@router.patch('/staff/records/{r}/draft')
def edit(r:str,body:Edit,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');row=need(db,'SELECT * FROM record_versions WHERE record_id=? AND version=?',(r,body.version));access(db,actor,row['subject_id'],'can_review')
        def operation():
            revision(request,row)
            if row['status']!='draft':raise Fault('INVALID_STATE',409)
            segments=[s.model_dump() for s in body.segments];validate_segments(db,segments,row['subject_id'])
            if {s['segment_id'] for s in segments}!={s['segment_id'] for s in row['segments']}:raise Fault('VALIDATION_FAILED')
            db.execute('UPDATE record_versions SET segments_json=?,revision=revision+1,updated_at=? WHERE record_id=? AND version=?',(dump(segments),now(),r,body.version))
            db.execute('UPDATE answer_candidates SET review_status="pending",reviewed_by=NULL,reviewed_at=NULL WHERE record_id=? AND record_version=?',(r,body.version))
            return {'id':r,'version':body.version}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:record_dto(db,ref['id'],ref['version'])))

@router.post('/staff/records/{r}/approve')
def approve(r:str,body:Approve,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');row=need(db,'SELECT * FROM record_versions WHERE record_id=? AND version=?',(r,body.version));access(db,actor,row['subject_id'],'can_review')
        def operation():
            revision(request,row)
            if row['status']!='draft':raise Fault('INVALID_STATE',409)
            validate_segments(db,row['segments'],row['subject_id'])
            reviews={v.segment_id:v for v in body.segment_reviews}
            if len(reviews)!=len(body.segment_reviews) or set(reviews)!={s['segment_id'] for s in row['segments']}:raise Fault('REVIEW_REQUIRED')
            if not all(all(v for k,v in review.model_dump().items() if k!='segment_id') for review in reviews.values()):raise Fault('REVIEW_REQUIRED')
            candidates=many(db,'SELECT * FROM answer_candidates WHERE record_id=? AND record_version=?',(r,body.version))
            cr={x.candidate_id:x for x in body.candidate_reviews}
            if set(cr)!={x['candidate_id'] for x in candidates}:raise Fault('REVIEW_REQUIRED')
            for candidate in candidates:
                v=cr[candidate['candidate_id']]
                if v.accepted and not v.sufficient_answer_checked:raise Fault('REVIEW_REQUIRED')
                db.execute('UPDATE answer_candidates SET review_status=?,reviewed_by=?,reviewed_at=? WHERE candidate_id=?',('accepted' if v.accepted else 'rejected',actor['actor_id'],now(),v.candidate_id))
            db.execute('UPDATE record_versions SET status="approved",reviewed_by=?,approved_at=?,revision=revision+1,updated_at=? WHERE record_id=? AND version=?',(actor['actor_id'],now(),now(),r,body.version))
            for s in row['segments']:
                if s['type']=='plan':insert(db,'care_actions',action_id=uid(),subject_id=row['subject_id'],description=s['text'],status='planned',planned_in_json={'kind':'record','record_id':r,'version':body.version,'segment_id':s['segment_id']},created_at=now(),updated_at=now())
            if row['capture_id']:db.execute('UPDATE captures SET status="approved",revision=revision+1,updated_at=? WHERE capture_id=?',(now(),row['capture_id']))
            invalidate(db,row['subject_id'],'record_approved')
            audit(db,actor['actor_id'],'record.approve',row['subject_id'],r)
            return {'id':r,'version':body.version}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:record_dto(db,ref['id'],ref['version'])))

@router.get('/staff/residents/{s}/sources')
def sources(s:str,request:Request):
    with request.app.state.store.transaction() as db:
        staff(request,db,s)
        return envelope({'items':many(db,'SELECT * FROM source_events WHERE subject_id=? ORDER BY recorded_at',(s,)),'next_cursor':None})

@router.get('/staff/residents/{s}/actions')
def actions(s:str,request:Request):
    with request.app.state.store.transaction() as db:
        staff(request,db,s)
        return envelope({'items':many(db,'SELECT * FROM care_actions WHERE subject_id=?',(s,)),'next_cursor':None})
