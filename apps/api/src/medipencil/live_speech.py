"""Short-chunk STT preview; final durable transcript uses the existing audio job."""
import base64,io,json,os,selectors,subprocess,time,wave
from pathlib import Path
from threading import Lock
from typing import Literal
from fastapi import APIRouter,Request,UploadFile,File,Query
from .common import Fault,envelope
from .db import need
from .security import session,access
from .domain import source_ref
from .local_jobs import _execution_slot
router=APIRouter(prefix='/api/v1')

class LiveSpeech:
    def __init__(self,config):self.config=config;self.process=None;self.lock=Lock()
    def close(self):
        if self.process:
            p=self.process;self.process=None
            if p.poll() is None:p.kill()
            p.communicate()
    def transcribe(self,pcm,language,canceled):
        if self.config.stt_backend!='whisper':raise Fault('PROVIDER_NOT_CONFIGURED',503)
        if not self.lock.acquire(False):raise Fault('PROVIDER_BUSY',503)
        try:
            if not self.process or self.process.poll() is not None:
                self.close()
                env={k:v for k,v in os.environ.items() if k in ('PATH','HOME','TMPDIR','LANG','SYSTEMROOT')}
                env.update({'HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','OMP_NUM_THREADS':'4'})
                self.process=subprocess.Popen([self.config.stt_python,str(Path(__file__).with_name('whisper_live_worker.py')),self.config.stt_model],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,env=env)
            p=self.process;deadline=time.monotonic()+self.config.timeout
            pending=(json.dumps({'pcm':base64.b64encode(pcm).decode(),'language':language})+'\n').encode()
            os.set_blocking(p.stdin.fileno(),False);os.set_blocking(p.stdout.fileno(),False)
            raw=bytearray();sent=0
            with selectors.DefaultSelector() as selector:
                selector.register(p.stdin,selectors.EVENT_WRITE)
                while b'\n' not in raw:
                    if canceled():raise Fault('JOB_CANCELED',409)
                    if time.monotonic()>deadline:raise Fault('TIMEOUT',504)
                    for key,events in selector.select(.2):
                        if key.fileobj is p.stdin:
                            try:sent+=os.write(p.stdin.fileno(),pending[sent:sent+8192])
                            except BlockingIOError:continue
                            if sent==len(pending):
                                selector.unregister(p.stdin);selector.register(p.stdout,selectors.EVENT_READ)
                        else:
                            try:part=os.read(p.stdout.fileno(),8192)
                            except BlockingIOError:continue
                            if not part:raise Fault('PROVIDER_FAILED',502)
                            raw.extend(part)
                            if len(raw)>131072:raise Fault('PROVIDER_SCHEMA_INVALID',502)
            value=json.loads(raw)
            if not isinstance(value.get('text'),str) or len(value['text'])>20000:raise Fault('PROVIDER_SCHEMA_INVALID',502)
            return value
        except Fault:
            self.close();raise
        except (OSError,ValueError,KeyError):
            self.close();raise Fault('PROVIDER_FAILED',502)
        finally:self.lock.release()

def authorized(request,c):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');cap=need(db,'SELECT * FROM captures WHERE capture_id=?',(c,));access(db,actor,cap['subject_id'],'can_review')
        if cap['input_mode']!='audio' or cap['status']!='created':raise Fault('INVALID_STATE',409)
        resident=need(db,'SELECT * FROM residents WHERE subject_id=?',(cap['subject_id'],))
        if resident['data_origin']!='TEAM_SYNTHETIC':raise Fault('EGRESS_DENIED',403)
        permission=need(db,'SELECT * FROM source_events WHERE source_id=? AND version=1',(cap['recording_permission_ref'],))
        if not permission['valid'] or permission['subject_id']!=cap['subject_id'] or permission['source_type']!='recording_permission':raise Fault('REVIEW_REQUIRED')
        for ref in permission['source_refs']:source_ref(db,ref,cap['subject_id'])
        return cap

@router.post('/staff/captures/{c}/live-transcript')
def preview(c:str,request:Request,file:UploadFile=File(...),language:Literal['ko','fi','en','sv']='fi',sequence:int=Query(ge=0,le=100)):
    authorized(request,c)
    data=file.file.read(1024*1024+1)
    if len(data)>1024*1024:raise Fault('AUDIO_TOO_LARGE',413)
    try:
        with wave.open(io.BytesIO(data)) as wav:
            if wav.getnchannels()!=1 or wav.getsampwidth()!=2 or wav.getframerate()!=16000 or not 0<wav.getnframes()<=16000*13:raise Fault('AUDIO_FORMAT_UNSUPPORTED',415)
            pcm=wav.readframes(wav.getnframes())
            if len(pcm)!=wav.getnframes()*2:raise Fault('AUDIO_FORMAT_UNSUPPORTED',415)
    except (wave.Error,EOFError):raise Fault('AUDIO_FORMAT_UNSUPPORTED',415)
    if not _execution_slot.acquire(False):raise Fault('PROVIDER_BUSY',503)
    try:
        def canceled():
            try:authorized(request,c);return False
            except Fault:return True
        result=request.app.state.live_speech.transcribe(pcm,language,canceled)
        authorized(request,c)
        return envelope({'sequence':sequence,'text':result['text'],'execution':result['metadata'],'provisional':True,'saved':False})
    finally:_execution_slot.release()
