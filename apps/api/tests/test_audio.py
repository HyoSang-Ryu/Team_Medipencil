import io,wave
import pytest
from conftest import Browser
from helpers import data,draft
from medipencil.audio import artifact,cleanup,recover,accept_late_result
from medipencil.providers import egress,UnconfiguredProvider
from medipencil.common import Fault

def setup_audio(s):
    r=draft(s,text='Synteettisen tallenteen käsittely sallittu.')
    permission=data(s.post('/staff/residents/aino/recording-permissions',{'utterance_ref':r['segments'][0]['evidence_refs'][0],'recording_allowed':True}),201)
    c=data(s.post('/staff/residents/aino/captures',{'input_mode':'audio','disclosure_ack':True,'recording_permission_ref':permission['permission_ref']}),201)
    buffer=io.BytesIO()
    with wave.open(buffer,'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(8000);wav.writeframes(b'\x00\x00'*800)
    response=s.client.post('/api/v1/staff/captures/'+c['capture_id']+'/audio',files={'file':('synthetic.wav',buffer.getvalue(),'audio/wav')},headers={'If-Match':'"1"','Idempotency-Key':'upload'})
    return data(response,201)

def test_actual_local_cleanup_unconfigured_provider(app):
    s=Browser(app);c=setup_audio(s);path=artifact(app.state.settings.root,c['audio_ref']);assert path.exists()
    status=data(s.get('/staff/captures/'+c['capture_id']+'/audio-status'))
    assert status['runtime']['deleted_at'] is None
    job=data(s.post('/staff/captures/'+c['capture_id']+'/transcribe',{},rev=c['revision']),202)
    assert job['status']=='failed' and job['error_code']=='PROVIDER_NOT_CONFIGURED'
    assert not path.exists()
    assert data(s.get('/staff/captures/'+c['capture_id']+'/audio-status'))['runtime']['deletion_status']=='deleted'
    with app.state.store.transaction() as db:assert accept_late_result(db,job['job_id'],{'fake':'success'}) is False

def test_cleanup_failure_and_recovery(app,monkeypatch):
    s=Browser(app);c=setup_audio(s)
    from pathlib import Path
    original=Path.unlink
    def fail(*a,**k):raise PermissionError()
    monkeypatch.setattr(Path,'unlink',fail)
    result=cleanup(app.state.store,app.state.settings.root,c['capture_id'],'failure')
    assert result['deletion_status']=='failed' and result['deleted_at'] is None
    monkeypatch.setattr(Path,'unlink',original)
    recover(app.state.store,app.state.settings.root)
    assert data(s.get('/staff/captures/'+c['capture_id']+'/audio-status'))['runtime']['deletion_status']=='deleted'

@pytest.mark.parametrize('lineage,url',[(['VEIL'],'http://127.0.0.1'),(['TEAM_SYNTHETIC','VEIL_DERIVED'],'http://127.0.0.1'),(['TEAM_SYNTHETIC'],'https://external.invalid')])
def test_egress_denied(lineage,url):
    with pytest.raises(Fault,match='EGRESS_DENIED'):egress(lineage,url)

def test_audio_requires_separate_permission(app):
    assert Browser(app).post('/staff/residents/aino/captures',{'input_mode':'audio'}).status_code==422
