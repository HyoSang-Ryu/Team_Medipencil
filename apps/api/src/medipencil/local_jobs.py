"""Durable jobs; model calls run outside SQLite write transactions."""
from threading import Lock

# Canceled durable jobs can still have an in-flight model call. Keep the execution slot
# occupied until that call exits, rather than trusting the public job status alone.
_execution_slot=Lock()

from datetime import datetime,timedelta,timezone
from fastapi import BackgroundTasks,Request
from .common import Fault,now,uid,envelope
from .db import need,one,insert,dump
from .domain import source_ref,timestamp
from .security import session,access,revision,execute
from .local_providers import WhisperSpeech,OllamaExtraction

def enqueue(request,background,cap_id,kind,payload):
    from .records import job_dto
    store=request.app.state.store;config=request.app.state.settings.models
    with store.transaction() as db:
        actor=session(request,db,'staff');cap=need(db,'SELECT * FROM captures WHERE capture_id=?',(cap_id,));access(db,actor,cap['subject_id'],'can_review')
        def operation():
            revision(request,cap)
            expected='audio_uploaded' if kind=='transcribe' else 'transcribed'
            if cap['status']!=expected:raise Fault('INVALID_STATE',409)
            resident=need(db,'SELECT * FROM residents WHERE subject_id=?',(cap['subject_id'],))
            if resident['data_origin']!='TEAM_SYNTHETIC':raise Fault('EGRESS_DENIED',403)
            if one(db,'SELECT job_id FROM processing_jobs WHERE status IN ("queued","running")'):raise Fault('PROVIDER_BUSY',503)
            if kind=='extract':
                refs=cap['source_refs']
                for ref in refs:
                    source_ref(db,ref,cap['subject_id'])
                    src=need(db,'SELECT * FROM source_events WHERE source_id=? AND version=?',(ref['source_id'],ref['source_version']))
                    if src['data_origin']!='TEAM_SYNTHETIC' or src['source_refs']:raise Fault('EGRESS_DENIED',403)
                for qid in payload['question_ids']:
                    q=need(db,'SELECT * FROM family_questions WHERE question_id=?',(qid,))
                    if q['subject_id']!=cap['subject_id']:raise Fault('SUBJECT_MISMATCH',409)
                    if q['status']=='answered':raise Fault('INVALID_STATE',409)
            else:refs=[]
            id=uid();t=now();backend=config.stt_backend if kind=='transcribe' else config.llm_backend
            meta={'requested_by':actor['actor_id'],'provider_id':backend,'execution_mode':'NOT_RUN','ai_executed':False,'input_mode':cap['input_mode'],'stt':'pending' if kind=='transcribe' else ('skipped' if cap['input_mode']=='text' else 'completed'),'origin':'TEAM_SYNTHETIC'}
            insert(db,'processing_jobs',job_id=id,subject_id=cap['subject_id'],job_type=kind,status='queued',target_id=cap_id,expected_revision=cap['revision']+1,input_refs_json=refs,provider_id=backend,execution_meta_json=meta,deadline_at=(datetime.now(timezone.utc)+timedelta(seconds=config.timeout+5)).isoformat(),created_at=t,updated_at=t)
            db.execute('UPDATE captures SET status=?,revision=revision+1,updated_at=? WHERE capture_id=?',('transcribing' if kind=='transcribe' else 'drafting',t,cap_id))
            background.add_task(run,request.app.state.settings,store,id,payload)
            return {'id':id}
        return envelope(execute(request,db,actor,payload,operation,lambda ref:job_dto(db,ref['id'])))

def current(db,id):
    j=need(db,'SELECT * FROM processing_jobs WHERE job_id=?',(id,))
    c=need(db,'SELECT * FROM captures WHERE capture_id=?',(j['target_id'],))
    membership=one(db,'SELECT m.can_review FROM access_memberships m JOIN actors a ON a.actor_id=m.actor_id WHERE m.actor_id=? AND m.subject_id=? AND m.active=1 AND a.active=1',(j['execution_meta'].get('requested_by',c['actor_id']),c['subject_id']))
    valid=bool(membership and membership['can_review']) and j['status']=='running' and j['deadline_at']>now() and c['revision']==j['expected_revision'] and c['status'] in ('transcribing','drafting')
    return j,c,valid

def run(settings,store,id,payload):
    from .audio import artifact,cleanup
    cap_id=None;kind=None;acquired=False
    try:
        with store.transaction() as db:
            job=need(db,'SELECT * FROM processing_jobs WHERE job_id=?',(id,));cap_id=job['target_id'];kind=job['job_type']
            if job['status']!='queued':return
            acquired=_execution_slot.acquire(blocking=False)
            if not acquired:raise Fault('PROVIDER_BUSY',503)
            db.execute('UPDATE processing_jobs SET status="running",updated_at=? WHERE job_id=?',(now(),id))
            job,cap,valid=current(db,id)
            if not valid:raise Fault('JOB_CANCELED',409)
            if kind=='extract':
                evidence=[{'key':str(i),'text':source_ref(db,ref,cap['subject_id'])['text']} for i,ref in enumerate(job['input_refs'])]
                if sum(len(e['text']) for e in evidence)>12000:raise Fault('AI_INPUT_TOO_LARGE')
        if kind=='transcribe':
            def canceled():
                with store.transaction() as db:return not current(db,id)[2]
            result=WhisperSpeech(settings.models).transcribe(artifact(settings.root,cap['audio_ref']),payload['language'],['TEAM_SYNTHETIC'],canceled)
        else:result=OllamaExtraction(settings.models).extract({'lineage':['TEAM_SYNTHETIC'],'evidence':evidence})
        with store.transaction() as db:
            job,cap,valid=current(db,id)
            if not valid:raise Fault('JOB_CANCELED',409)
            # Current source validity is checked again after inference, before storing any result.
            if kind=='transcribe':
                permission=need(db,'SELECT * FROM source_events WHERE source_id=? AND version=1',(cap['recording_permission_ref'],))
                if not permission['valid']:raise Fault('EVIDENCE_REQUIRED')
                for ref in permission['source_refs']:source_ref(db,ref,cap['subject_id'])
                source=uid();utterance=uid()
                insert(db,'source_events',source_id=source,version=1,subject_id=cap['subject_id'],source_type='transcript',occurred_at=timestamp(payload.get('occurred_at') or cap['created_at']),recorded_at=now(),data_origin='TEAM_SYNTHETIC',integration_mode='LOCAL_STT',payload_json={'utterances':[{'utterance_id':utterance,'text':result['text'],'speaker':'unknown','type':'statement','required_scopes':['health_context'],'classification_review':'required'}],'execution':result['metadata']})
                refs=[{'kind':'source','source_id':source,'source_version':1,'utterance_id':utterance}]
                db.execute('UPDATE captures SET source_refs_json=? WHERE capture_id=?',(dump(refs),cap_id))
                ref={'kind':'capture','id':cap_id};status='transcribed'
            else:
                segments=[]
                for key in result['keys']:
                    evidence_ref=job['input_refs'][int(key)];u=source_ref(db,evidence_ref,cap['subject_id'])
                    segments.append({k:u[k] for k in ('text','speaker','type','required_scopes')}|{'segment_id':uid(),'evidence_refs':[evidence_ref]})
                record=uid();t=now()
                insert(db,'record_versions',record_id=record,version=1,subject_id=cap['subject_id'],capture_id=cap_id,status='draft',segments_json=segments,created_at=t,updated_at=t)
                for qid in set(payload['question_ids']):
                    q=need(db,'SELECT * FROM family_questions WHERE question_id=?',(qid,))
                    if q['status']=='answered':raise Fault('INVALID_STATE',409)
                    insert(db,'answer_candidates',candidate_id=uid(),question_id=qid,record_id=record,record_version=1,answer_segment_ids_json=[s['segment_id'] for s in segments],review_status='pending')
                ref={'kind':'record','id':record,'version':1};status='draft_ready'
            meta=job['execution_meta']|result['metadata']
            if kind=='transcribe':meta['stt']='completed'
            db.execute('UPDATE processing_jobs SET status="succeeded",result_ref=?,execution_meta_json=?,updated_at=? WHERE job_id=?',(dump(ref),dump(meta),now(),id))
            db.execute('UPDATE captures SET status=?,error_code=NULL,revision=revision+1,updated_at=? WHERE capture_id=?',(status,now(),cap_id))
    except Exception as exc:
        code=exc.code if isinstance(exc,Fault) else 'PROVIDER_FAILED'
        with store.transaction() as db:
            j,c,valid=current(db,id)
            if j['status'] in ('queued','running'):
                db.execute('UPDATE processing_jobs SET status="failed",error_code=?,updated_at=? WHERE job_id=?',(code,now(),id))
                if c['status'] not in ('canceled','approved'):
                    # LLM failure preserves transcription for explicit manual retry.
                    db.execute('UPDATE captures SET status=?,error_code=?,revision=revision+1,updated_at=? WHERE capture_id=?',('failed' if kind=='transcribe' else 'transcribed',code,now(),c['capture_id']))
    finally:
        try:
            if kind=='transcribe' and cap_id:cleanup(store,settings.root,cap_id,'local_stt_finished')
        finally:
            if acquired:_execution_slot.release()
