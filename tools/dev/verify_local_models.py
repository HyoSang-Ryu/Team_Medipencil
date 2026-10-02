"""Opt-in REAL local inference on generated Finnish speech; never uses patient data."""
import json,subprocess,tempfile,time,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'apps/api/tests'))
from conftest import Browser
from helpers import data,draft,approve,prepare,publish
from medipencil.config import Settings
from medipencil.local_providers import LocalModels
from medipencil.main import create_app
from medipencil.seed import seed
from medipencil.common import now
from medipencil.audio import artifact
from fastapi.testclient import TestClient

with tempfile.TemporaryDirectory(prefix='medipencil-real-local-') as directory:
    root=Path(directory).resolve();models=LocalModels.env()
    speech='Tämä on synteettinen testi. Ulkoilu ei toteutunut.'
    subprocess.run(['say','-v','Eddy (핀란드어(핀란드))','-o',str(root/'speech.aiff'),speech],check=True,capture_output=True)
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-y','-i',str(root/'speech.aiff'),'-ar','16000','-ac','1',str(root/'speech.wav')],check=True,capture_output=True)
    app=create_app(Settings(root/'data',secret='local-synthetic-verification-only-12345',models=models));seed(app.state.store)
    with TestClient(app):
        s=Browser(app)
        typed=data(s.post('/staff/residents/aino/captures',{'input_mode':'text'}),201)
        typed=data(s.post('/staff/captures/'+typed['capture_id']+'/text',{'occurred_at':now(),'utterances':[{'speaker':'carer','text':'Ulkoilu ei toteutunut.','type':'observation','required_scopes':['outdoors']}]},rev=typed['revision']),201)
        queued=data(s.post('/staff/captures/'+typed['capture_id']+'/drafts',{'processing_mode':'local'},rev=typed['revision']),202)
        typed_job=data(s.get('/staff/jobs/'+queued['job_id']));assert typed_job['status']=='succeeded' and typed_job['execution']['stt']=='skipped',typed_job
        r=draft(s,text='Synteettisen tallenteen käsittely sallittu.')
        permission=data(s.post('/staff/residents/aino/recording-permissions',{'utterance_ref':r['segments'][0]['evidence_refs'][0],'recording_allowed':True}),201)
        cap=data(s.post('/staff/residents/aino/captures',{'input_mode':'audio','disclosure_ack':True,'recording_permission_ref':permission['permission_ref']}),201)
        cap=data(s.client.post('/api/v1/staff/captures/'+cap['capture_id']+'/audio',files={'file':('synthetic.wav',(root/'speech.wav').read_bytes(),'audio/wav')},headers={'If-Match':'"1"','Idempotency-Key':'real-upload'}),201)
        start=time.monotonic()
        queued=data(s.post('/staff/captures/'+cap['capture_id']+'/transcribe',{'language':'fi','occurred_at':now()},rev=cap['revision']),202)
        stt=data(s.get('/staff/jobs/'+queued['job_id']));assert stt['status']=='succeeded',stt
        stt_seconds=round(time.monotonic()-start,2)
        assert not artifact(app.state.settings.root,cap['audio_ref']).exists()
        cap=data(s.get('/staff/captures/'+cap['capture_id']))
        transcript=cap['utterances'][0]['text'];assert transcript.strip()
        start=time.monotonic()
        queued=data(s.post('/staff/captures/'+cap['capture_id']+'/drafts',{'question_ids':[],'processing_mode':'local'},rev=cap['revision']),202)
        llm=data(s.get('/staff/jobs/'+queued['job_id']));assert llm['status']=='succeeded',llm
        llm_seconds=round(time.monotonic()-start,2)
        ref=llm['result_ref'];record=data(s.get('/staff/records/'+ref['id']+'?version=1'))
        assert record['status']=='draft' and record['segments'][0]['text']==transcript
        # Automation exercises approval boundaries; this is NOT a human language review.
        approve(s,record);publish(s,prepare(s))
        board=data(Browser(app,'liisa').get('/family/residents/aino/board'))
        assert any(item['claim_type']=='unattributed_statement' for tile in board['tiles'] for item in tile['items'])
        print(json.dumps({'scope':'REAL_LOCAL_MODELS_SYNTHETIC_TTS','input':speech,'transcript':transcript,'stt_seconds':stt_seconds,'llm_seconds':llm_seconds,'stt':stt['execution'],'llm':llm['execution'],'typed_llm':typed_job['execution'],'local_upload_deleted':True,'draft_requires_review':True,'published_via_explicit_test_approval':True,'human_language_review':'NOT_VERIFIED','clinical_quality':'NOT_VERIFIED'},ensure_ascii=False,indent=2))
