import io,wave
from conftest import Browser
from helpers import data,draft
from medipencil.local_jobs import _execution_slot

class FakeSpeech:
    def transcribe(self,pcm,language,canceled):
        assert not canceled()
        return {'text':'Synthetic preview only.','metadata':{'ai_executed':False,'execution_mode':'SIMULATED','provider_id':'test'}}
    def close(self):pass

def start(app):
    s=Browser(app);r=draft(s,text='Independent synthetic recording permission.')
    permission=data(s.post('/staff/residents/aino/recording-permissions',{'utterance_ref':r['segments'][0]['evidence_refs'][0],'recording_allowed':True}),201)
    cap=data(s.post('/staff/residents/aino/captures',{'input_mode':'audio','disclosure_ack':True,'recording_permission_ref':permission['permission_ref']}),201)
    return s,cap,permission

def audio(rate=16000,seconds=1):
    out=io.BytesIO()
    with wave.open(out,'wb') as wav:
        wav.setnchannels(1);wav.setsampwidth(2);wav.setframerate(rate);wav.writeframes(b'\0\0'*rate*seconds)
    return out.getvalue()

def send(s,cap,blob=None):
    return s.client.post('/api/v1/staff/captures/'+cap['capture_id']+'/live-transcript?sequence=0&language=en',files={'file':('chunk.wav',blob or audio(),'audio/wav')})

def test_preview_not_durable_and_role_guard(app):
    s,c,p=start(app);app.state.live_speech=FakeSpeech()
    result=data(send(s,c));assert result['provisional'] and not result['saved']
    assert not result['execution']['ai_executed']
    stored=data(s.get('/staff/captures/'+c['capture_id']))
    assert stored['status']=='created' and not stored['source_refs']
    assert send(Browser(app,'liisa'),c).status_code==403
    with app.state.store.transaction() as db:db.execute('UPDATE source_events SET valid=0 WHERE source_id=?',(p['permission_ref'],))
    assert send(s,c).status_code==422

def test_preview_bounds_busy_and_disabled(app):
    s,c,p=start(app)
    assert send(s,c).status_code==503
    assert send(s,c,audio(8000)).status_code==415
    assert send(s,c,audio(seconds=14)).status_code==415
    app.state.live_speech=FakeSpeech()
    _execution_slot.acquire()
    try:assert send(s,c).status_code==503
    finally:_execution_slot.release()
    data(s.post('/staff/captures/'+c['capture_id']+'/cancel',{},rev=1))
    assert send(s,c).status_code==409

def test_preview_checks_permission_after_inference(app):
    s,c,p=start(app)
    class Revoke(FakeSpeech):
        def transcribe(self,*args):
            with app.state.store.transaction() as db:db.execute('UPDATE source_events SET valid=0 WHERE source_id=?',(p['permission_ref'],))
            return {'text':'must not return','metadata':{}}
    app.state.live_speech=Revoke()
    response=send(s,c);assert response.status_code==422
    assert 'must not return' not in response.text
