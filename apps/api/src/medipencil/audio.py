import hashlib
import io
import os
import wave
from pathlib import Path
from uuid import UUID
from fastapi import APIRouter,Request,UploadFile,File
from .common import Input,Fault,now,uid,envelope
from .db import need,one,many,insert,dump
from .security import session,access,revision,execute
from .domain import source_ref
from .records import staff,job_dto
router=APIRouter(prefix='/api/v1')
MAX_BYTES=20*1024*1024
class Permission(Input):
    utterance_ref:dict
    recording_allowed:bool
class Empty(Input):pass

def artifact(root,ref):
    try:UUID(ref)
    except (ValueError,TypeError):raise Fault('INVALID_ARTIFACT',422)
    directory=Path(root)/'audio'
    if directory.is_symlink() or Path(root).is_symlink():raise Fault('INVALID_ARTIFACT',422)
    directory.mkdir(mode=0o700,exist_ok=True)
    file=directory/(ref+'.wav')
    if file.is_symlink() or file.resolve().parent!=directory.resolve():raise Fault('INVALID_ARTIFACT',422)
    return file

def cleanup(store,root,capture,trigger):
    with store.transaction() as db:
        cap=need(db,'SELECT * FROM captures WHERE capture_id=?',(capture,))
        if not cap['audio_ref']:return {'audio_applicable':cap['input_mode']=='audio','deletion_status':'unverified','deleted_at':None}
        job=one(db,'SELECT * FROM audio_cleanup_jobs WHERE capture_id=? ORDER BY rowid DESC LIMIT 1',(capture,))
        if not job:
            id=uid();insert(db,'audio_cleanup_jobs',cleanup_id=id,capture_id=capture,artifact_refs_json=[cap['audio_ref']],deletion_status='unverified',trigger=trigger,receipts_json=[])
        else:id=job['cleanup_id']
    receipts=[];status='deleted'
    try:
        path=artifact(root,cap['audio_ref']);path.unlink(missing_ok=True)
        if path.exists():raise OSError('removal not confirmed')
        receipts=[{'artifact':cap['audio_ref'],'area':'local_only_no_engine_called','removed':True}]
    except (OSError,Fault):status='failed'
    with store.transaction() as db:
        db.execute('UPDATE audio_cleanup_jobs SET deletion_status=?,deleted_at=?,attempts=attempts+1,receipts_json=?,trigger=? WHERE cleanup_id=?',(status,now() if status=='deleted' else None,dump(receipts),trigger,id))
        return need(db,'SELECT * FROM audio_cleanup_jobs WHERE cleanup_id=?',(id,))

def recover(store,root):
    with store.transaction() as db:
        rows=many(db,'SELECT capture_id FROM captures WHERE audio_ref IS NOT NULL')
        db.execute('UPDATE processing_jobs SET status="failed",error_code="PROCESS_INTERRUPTED",updated_at=? WHERE status IN ("queued","running")',(now(),))
        db.execute('UPDATE captures SET status="failed",error_code="PROCESS_INTERRUPTED",revision=revision+1,updated_at=? WHERE input_mode="audio" AND status NOT IN ("approved","canceled","failed")',(now(),))
    for r in rows:cleanup(store,root,r['capture_id'],'startup_recovery')

def accept_late_result(db,job_id,result):
    j=need(db,'SELECT * FROM processing_jobs WHERE job_id=?',(job_id,))
    if j['status']!='running' or j['deadline_at']<now():return False
    cap=need(db,'SELECT * FROM captures WHERE capture_id=?',(j['target_id'],))
    if cap['status'] in ('failed','canceled') or cap['revision']!=j['expected_revision']:return False
    # No real provider schema has been verified. Never persist an arbitrary success payload.
    raise Fault('PROVIDER_NOT_CONFIGURED',503)

@router.post('/staff/residents/{s}/recording-permissions',status_code=201)
def permission(s:str,body:Permission,request:Request):
    with request.app.state.store.transaction() as db:
        actor=staff(request,db,s)
        def operation():
            if not body.recording_allowed:raise Fault('REVIEW_REQUIRED')
            source_ref(db,body.utterance_ref,s);id=uid()
            insert(db,'source_events',source_id=id,version=1,subject_id=s,source_type='recording_permission',occurred_at=now(),recorded_at=now(),data_origin='TEAM_SYNTHETIC',integration_mode='MANUAL_INPUT',payload_json={'recording_allowed':True,'checked_by':actor['actor_id'],'required_scopes':['health_context']},source_refs_json=[body.utterance_ref])
            return {'id':id}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:{'permission_ref':ref['id']}))

@router.post('/staff/captures/{c}/audio',status_code=201)
def upload(c:str,request:Request,file:UploadFile=File(...)):
    store=request.app.state.store;root=request.app.state.settings.root
    # Authenticate before reading the file. Multipart parser limits are supplemented by body middleware.
    with store.transaction() as db:
        actor=session(request,db,'staff');cap=need(db,'SELECT * FROM captures WHERE capture_id=?',(c,));access(db,actor,cap['subject_id'],'can_review')
    data=file.file.read(MAX_BYTES+1)
    if len(data)>MAX_BYTES:raise Fault('AUDIO_TOO_LARGE',413)
    if file.content_type not in ('audio/wav','audio/x-wav'):raise Fault('AUDIO_FORMAT_UNSUPPORTED',415)
    try:
        with wave.open(io.BytesIO(data)) as wav:
            if wav.getnchannels() not in (1,2) or wav.getframerate()<=0 or wav.getnframes()/wav.getframerate()>180:raise Fault('AUDIO_TOO_LARGE',413)
            if len(wav.readframes(wav.getnframes()))!=wav.getnframes()*wav.getnchannels()*wav.getsampwidth():raise Fault('AUDIO_FORMAT_UNSUPPORTED',415)
    except (wave.Error,EOFError):raise Fault('AUDIO_FORMAT_UNSUPPORTED',415)
    ref=uid()
    with store.transaction() as db:
        actor=session(request,db,'staff');cap=need(db,'SELECT * FROM captures WHERE capture_id=?',(c,));access(db,actor,cap['subject_id'],'can_review')
        def operation():
            revision(request,cap)
            if cap['input_mode']!='audio' or cap['status']!='created' or cap['audio_ref']:raise Fault('INVALID_STATE',409)
            db.execute('UPDATE captures SET audio_ref=?,revision=revision+1,updated_at=? WHERE capture_id=?',(ref,now(),c))
            insert(db,'audio_cleanup_jobs',cleanup_id=uid(),capture_id=c,artifact_refs_json=[ref],deletion_status='unverified',trigger='upload',receipts_json=[])
            return {'id':c,'artifact':ref}
        stored=execute(request,db,actor,{'sha256':hashlib.sha256(data).hexdigest()},operation,lambda r:r)
    if stored['artifact']!=ref:
        with store.transaction() as db:return envelope(need(db,'SELECT * FROM captures WHERE capture_id=?',(c,)))
    try:
        path=artifact(root,ref)
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
        with os.fdopen(fd,'wb') as out:out.write(data)
        with store.transaction() as db:
            current=need(db,'SELECT * FROM captures WHERE capture_id=?',(c,))
            if current['status']!='created':raise Fault('INVALID_STATE',409)
            db.execute('UPDATE captures SET status="audio_uploaded",revision=revision+1,updated_at=? WHERE capture_id=?',(now(),c))
            return envelope(need(db,'SELECT * FROM captures WHERE capture_id=?',(c,)))
    except BaseException:
        cleanup(store,root,c,'failure');raise

@router.post('/staff/captures/{c}/transcribe',status_code=202)
def transcribe(c:str,body:Empty,request:Request):
    store=request.app.state.store
    with store.transaction() as db:
        actor=session(request,db,'staff');cap=need(db,'SELECT * FROM captures WHERE capture_id=?',(c,));access(db,actor,cap['subject_id'],'can_review')
        def operation():
            revision(request,cap)
            if cap['status']!='audio_uploaded':raise Fault('INVALID_STATE',409)
            id=uid();t=now()
            insert(db,'processing_jobs',job_id=id,subject_id=cap['subject_id'],job_type='transcribe',status='failed',target_id=c,expected_revision=cap['revision'],input_refs_json=[],provider_id='not_configured',execution_meta_json={'input_mode':'audio','provider_id':'not_configured','execution_mode':'NOT_RUN','ai_executed':False,'origin':'TEAM_SYNTHETIC'},deadline_at=t,error_code='PROVIDER_NOT_CONFIGURED',created_at=t,updated_at=t)
            db.execute('UPDATE captures SET status="failed",error_code="PROVIDER_NOT_CONFIGURED",revision=revision+1,updated_at=? WHERE capture_id=?',(t,c))
            return {'id':id}
        result=execute(request,db,actor,{},operation,lambda ref:job_dto(db,ref['id']))
    cleanup(store,request.app.state.settings.root,c,'failure')
    return envelope(result)

@router.post('/staff/captures/{c}/cancel')
def cancel(c:str,body:Empty,request:Request):
    store=request.app.state.store
    with store.transaction() as db:
        actor=session(request,db,'staff');cap=need(db,'SELECT * FROM captures WHERE capture_id=?',(c,));access(db,actor,cap['subject_id'],'can_review')
        def operation():
            revision(request,cap)
            if cap['status']=='approved':raise Fault('INVALID_STATE',409)
            db.execute('UPDATE captures SET status="canceled",revision=revision+1,updated_at=? WHERE capture_id=?',(now(),c))
            db.execute('UPDATE processing_jobs SET status="canceled",canceled_at=?,updated_at=? WHERE target_id=? AND status IN ("queued","running")',(now(),now(),c))
            return {'id':c}
        result=execute(request,db,actor,{},operation,lambda ref:need(db,'SELECT * FROM captures WHERE capture_id=?',(ref['id'],)))
    cleanup(store,request.app.state.settings.root,c,'cancel')
    return envelope(result)

@router.get('/staff/captures/{c}/audio-status')
def status(c:str,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');cap=need(db,'SELECT * FROM captures WHERE capture_id=?',(c,));access(db,actor,cap['subject_id'],'can_review')
        job=one(db,'SELECT deletion_status,deleted_at FROM audio_cleanup_jobs WHERE capture_id=? ORDER BY rowid DESC LIMIT 1',(c,))
        return envelope({'audio_applicable':cap['input_mode']=='audio','policy':{'cleanup_on':['saved','cancel','failure','timeout','startup_recovery']},'runtime':job or {'deletion_status':'unverified','deleted_at':None}})

@router.post('/staff/captures/{c}/retry-cleanup',status_code=202)
def retry(c:str,body:Empty,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');cap=need(db,'SELECT * FROM captures WHERE capture_id=?',(c,));access(db,actor,cap['subject_id'],'can_review');revision(request,cap)
        if cap['status'] not in ('canceled','failed','approved'):raise Fault('INVALID_STATE',409)
        if not request.headers.get('idempotency-key'):raise Fault('VALIDATION_FAILED')
    return envelope(cleanup(request.app.state.store,request.app.state.settings.root,c,'failure'))
