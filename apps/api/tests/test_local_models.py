"""Adapter doubles are TEST_FIXTURE; real inference is a separate opt-in script."""
import json
import pytest
from dataclasses import replace
from conftest import Browser
from helpers import data
from test_audio import setup_audio
from medipencil.local_providers import LocalModels,OllamaExtraction
from medipencil.common import now,Fault
from medipencil.db import need

META={'provider_id':'test_double','execution_mode':'REPLAY','ai_executed':False}

def typed(s):
    c=data(s.post('/staff/residents/aino/captures',{'input_mode':'text'}),201)
    return data(s.post('/staff/captures/'+c['capture_id']+'/text',{'occurred_at':now(),'utterances':[{'text':'Ulkoilu ei toteutunut.','speaker':'carer','type':'observation','required_scopes':['outdoors']}]},rev=c['revision']),201)

def test_local_extract_requires_review_and_replay_no_rerun(app,monkeypatch):
    calls=[]
    def extract(self,snapshot):calls.append(snapshot);return {'keys':['0'],'metadata':META}
    monkeypatch.setattr('medipencil.local_jobs.OllamaExtraction.extract',extract)
    s=Browser(app);cap=typed(s);path='/staff/captures/'+cap['capture_id']+'/drafts';body={'processing_mode':'local'}
    queued=data(s.post(path,body,cap['revision'],key='one'),202)
    job=data(s.get('/staff/jobs/'+queued['job_id']));assert job['status']=='succeeded'
    record=data(s.get('/staff/records/'+job['result_ref']['id']+'?version=1'))
    assert record['status']=='draft' and record['segments'][0]['text']=='Ulkoilu ei toteutunut.'
    repeated=data(s.post(path,body,cap['revision'],key='one'),202)
    assert repeated['job_id']==job['job_id'] and len(calls)==1
    assert repeated['execution']['execution_mode']=='REPLAY'

def test_local_result_after_cancel_not_saved(app,monkeypatch):
    s=Browser(app);cap=typed(s)
    def extract(self,snapshot):
        latest=data(s.get('/staff/captures/'+cap['capture_id']))
        data(s.post('/staff/captures/'+cap['capture_id']+'/cancel',{},latest['revision']))
        return {'keys':['0'],'metadata':META}
    monkeypatch.setattr('medipencil.local_jobs.OllamaExtraction.extract',extract)
    queued=data(s.post('/staff/captures/'+cap['capture_id']+'/drafts',{'processing_mode':'local'},cap['revision']),202)
    job=data(s.get('/staff/jobs/'+queued['job_id']));assert job['status']=='canceled' and job['result_ref'] is None

def test_local_llm_failure_keeps_manual_retry(app,monkeypatch):
    def fail(*args):raise Fault('TIMEOUT',504)
    monkeypatch.setattr('medipencil.local_jobs.OllamaExtraction.extract',fail)
    s=Browser(app);cap=typed(s)
    queued=data(s.post('/staff/captures/'+cap['capture_id']+'/drafts',{'processing_mode':'local'},cap['revision']),202)
    job=data(s.get('/staff/jobs/'+queued['job_id']));assert job['error_code']=='TIMEOUT'
    latest=data(s.get('/staff/captures/'+cap['capture_id']));assert latest['status']=='transcribed'
    assert data(s.post('/staff/captures/'+cap['capture_id']+'/drafts',{},latest['revision']),202)['status']=='succeeded'

def test_stt_fixture_persists_unknown_speaker_and_cleans(app,monkeypatch):
    # Use valid existing files only to validate configuration; test double never loads them.
    from pathlib import Path
    app.state.settings.models=LocalModels(stt_backend='whisper',stt_python=__file__,stt_model=__file__)
    monkeypatch.setattr('medipencil.local_jobs.WhisperSpeech.transcribe',lambda *args:{'text':'Synthetic speech.','metadata':META})
    s=Browser(app);cap=setup_audio(s)
    queued=data(s.post('/staff/captures/'+cap['capture_id']+'/transcribe',{},cap['revision'],key='stt'),202)
    job=data(s.get('/staff/jobs/'+queued['job_id']));assert job['status']=='succeeded'
    latest=data(s.get('/staff/captures/'+cap['capture_id']))
    assert latest['utterances'][0]['speaker']=='unknown'
    assert latest['utterances'][0]['required_scopes']==['health_context']
    assert data(s.get('/staff/captures/'+cap['capture_id']+'/audio-status'))['runtime']['deletion_status']=='deleted'
    assert data(s.post('/staff/captures/'+cap['capture_id']+'/transcribe',{},cap['revision'],key='stt'),202)['job_id']==job['job_id']

@pytest.mark.parametrize('url',['https://example.com','http://localhost:11434','http://127.0.0.1:11434/path','http://user@127.0.0.1:11434'])
def test_local_url_fail_closed(url):
    with pytest.raises(ValueError):LocalModels(llm_url=url)

def test_ollama_redirect_unknown_evidence_and_cloud_denied(monkeypatch):
    import httpx
    real=httpx.Client
    def exercise(mode):
        calls=[]
        def handler(request):
            calls.append(request.url.path)
            if request.url.path=='/api/tags':return httpx.Response(200,json={'models':[{'name':'model','digest':'synthetic-digest'}]})
            if request.url.path=='/api/show':return httpx.Response(200,json={'remote_host':'cloud.invalid'} if mode=='cloud' else {})
            if mode=='redirect':return httpx.Response(307,headers={'location':'https://external.invalid'})
            return httpx.Response(200,json={'done':True,'message':{'content':json.dumps({'evidence_keys':['invented']})}})
        monkeypatch.setattr('medipencil.local_providers.httpx.Client',lambda **kw:real(transport=httpx.MockTransport(handler),**kw))
        with pytest.raises(Fault):OllamaExtraction(LocalModels(llm_backend='ollama',llm_model='model')).extract({'lineage':['TEAM_SYNTHETIC'],'evidence':[{'key':'0','text':'Test.'}]})
        assert len(calls)==(2 if mode=='cloud' else 3)
    for mode in ['cloud','redirect','unknown']:exercise(mode)

def test_profile_environment_override(tmp_path,monkeypatch):
    profile=tmp_path/'models.json';profile.write_text(json.dumps({'llm_backend':'ollama','llm_model':'model-a'}))
    monkeypatch.setenv('MEDIPENCIL_MODEL_CONFIG',str(profile));monkeypatch.setenv('MEDIPENCIL_LLM_MODEL','model-b')
    assert LocalModels.env().llm_model=='model-b'

def test_stt_completed_source_survives_recovery(app,monkeypatch):
    from medipencil.audio import recover
    app.state.settings.models=LocalModels(stt_backend='whisper',stt_python=__file__,stt_model=__file__)
    monkeypatch.setattr('medipencil.local_jobs.WhisperSpeech.transcribe',lambda *args:{'text':'Synthetic speech.','metadata':META})
    s=Browser(app);cap=setup_audio(s)
    data(s.post('/staff/captures/'+cap['capture_id']+'/transcribe',{},cap['revision']),202)
    recover(app.state.store,app.state.settings.root)
    saved=data(s.get('/staff/captures/'+cap['capture_id']))
    assert saved['status']=='transcribed' and saved['utterances'][0]['text']=='Synthetic speech.'
