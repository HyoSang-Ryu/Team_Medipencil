"""Opt-in real local STT test with generated speech, never a physical microphone."""
import json,subprocess,tempfile,time,sys,wave
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'apps/api/tests'))
from conftest import Browser
from helpers import data,draft
from medipencil.config import Settings
from medipencil.local_providers import LocalModels
from medipencil.main import create_app
from medipencil.seed import seed
from fastapi.testclient import TestClient
with tempfile.TemporaryDirectory(prefix='care-live-stt-') as tmp:
    root=Path(tmp).resolve();speech='Tämä on synteettinen testi. Ulkoilu ei toteutunut.'
    subprocess.run(['say','-v','Eddy (핀란드어(핀란드))','-o',str(root/'speech.aiff'),speech],check=True,capture_output=True)
    subprocess.run(['/opt/homebrew/bin/ffmpeg','-y','-i',str(root/'speech.aiff'),'-ar','16000','-ac','1',str(root/'speech.wav')],check=True,capture_output=True)
    with wave.open(str(root/'speech.wav')) as wav:seconds=wav.getnframes()/wav.getframerate()
    app=create_app(Settings(root/'data',secret='synthetic-live-stt-verification-only-12345',models=LocalModels.env()));seed(app.state.store)
    with TestClient(app):
        b=Browser(app);record=draft(b,text='Independent synthetic recording permission.')
        permission=data(b.post('/staff/residents/aino/recording-permissions',{'utterance_ref':record['segments'][0]['evidence_refs'][0],'recording_allowed':True}),201)
        cap=data(b.post('/staff/residents/aino/captures',{'input_mode':'audio','disclosure_ack':True,'recording_permission_ref':permission['permission_ref']}),201)
        for i in range(2):
            start=time.monotonic()
            r=data(b.client.post('/api/v1/staff/captures/'+cap['capture_id']+f'/live-transcript?sequence={i}&language=fi',files={'file':('synthetic.wav',(root/'speech.wav').read_bytes(),'audio/wav')}))
            assert r['execution']['ai_executed'] is True and r['provisional'] and not r['saved']
            print(json.dumps({'attempt':i+1,'input_seconds':round(seconds,2),'elapsed_seconds':round(time.monotonic()-start,2),'expected':speech,'result':r,'human_language_review':'NOT_VERIFIED'},ensure_ascii=False),flush=True)
        stored=data(b.get('/staff/captures/'+cap['capture_id']));assert stored['status']=='created' and not stored['source_refs']
