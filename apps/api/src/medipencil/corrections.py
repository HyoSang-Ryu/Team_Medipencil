from typing import Literal
from fastapi import APIRouter,Request
from pydantic import Field
from .common import Input,Fault,uid,now,envelope
from .db import need,insert,audit,dump,many
from .security import session,access,execute,revision
from .domain import scopes,timestamp,source_ref
from .records import staff,invalidate,record_dto
router=APIRouter(prefix='/api/v1')
class Correction(Input):
    version:int
    reason_code:str=Field(min_length=1,max_length=100)
class Source(Input):
    occurred_at:str
    source_type:Literal['staff_note']='staff_note'
    text:str=Field(min_length=1,max_length=20000)
    speaker:Literal['resident','carer','unknown']
    required_scopes:list[str]
    related_source_refs:list[dict]=Field(default_factory=list)
    type:Literal['statement','observation','plan']='statement'

@router.post('/staff/residents/{s}/sources',status_code=201)
def source(s:str,body:Source,request:Request):
    with request.app.state.store.transaction() as db:
        actor=staff(request,db,s)
        def operation():
            for ref in body.related_source_refs:source_ref(db,ref,s)
            id=uid()
            insert(db,'source_events',source_id=id,version=1,subject_id=s,source_type='staff_note',occurred_at=timestamp(body.occurred_at),recorded_at=now(),data_origin='TEAM_SYNTHETIC',integration_mode='MANUAL_INPUT',payload_json={'text':body.text,'speaker':body.speaker,'type':body.type,'required_scopes':scopes(body.required_scopes)},source_refs_json=body.related_source_refs)
            return {'id':id}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:need(db,'SELECT * FROM source_events WHERE source_id=? AND version=1',(ref['id'],))))

@router.post('/staff/records/{r}/corrections',status_code=201)
def correct(r:str,body:Correction,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');old=need(db,'SELECT * FROM record_versions WHERE record_id=? AND version=?',(r,body.version));access(db,actor,old['subject_id'],'can_review')
        def operation():
            revision(request,old)
            if old['status']!='approved':raise Fault('INVALID_STATE',409)
            for segment in old['segments']:
                for ref in segment['evidence_refs']:
                    db.execute('UPDATE source_events SET valid=0,invalidated_at=? WHERE source_id=? AND version=?',(now(),ref['source_id'],ref['source_version']))
            db.execute('UPDATE record_versions SET status="superseded",revision=revision+1,updated_at=? WHERE record_id=? AND version=?',(now(),r,body.version))
            insert(db,'record_versions',record_id=r,version=body.version+1,subject_id=old['subject_id'],status='draft',segments_json=old['segments'],supersedes_version=body.version,correction_reason=body.reason_code,created_at=now(),updated_at=now())
            for c in many(db,'SELECT * FROM answer_candidates WHERE record_id=? AND record_version=?',(r,body.version)):
                insert(db,'answer_candidates',candidate_id=uid(),question_id=c['question_id'],record_id=r,record_version=body.version+1,answer_segment_ids_json=c['answer_segment_ids'],review_status='pending')
            invalidate(db,old['subject_id'],'source_correction',questions=True)
            db.execute('UPDATE care_actions SET status="planned",confirmed_in_json=NULL,review_required=1,revision=revision+1,updated_at=? WHERE subject_id=?',(now(),old['subject_id']))
            audit(db,actor['actor_id'],'record.correct',old['subject_id'],r)
            return {'id':r,'version':body.version+1}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:record_dto(db,ref['id'],ref['version'])))
