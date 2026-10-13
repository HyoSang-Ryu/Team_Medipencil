from uuid import uuid4
from unittest.mock import Mock
import io,wave
from conftest import Browser
from test_provided_data import fixture_bundle
from medipencil.provided_data import import_bundle
from medipencil.provided_workflow import sync_accounts,people

def setup(app,tmp_path):
    a,p=fixture_bundle(tmp_path);import_bundle(a,p,app.state.settings.root);sync_accounts(app)
    return people(app.state.settings)

def test_family_scope_subject_and_notes(app,tmp_path):
    profiles=setup(app,tmp_path);a,b=profiles
    staff=Browser(app);fa=Browser(app,a['actor_id']);fb=Browser(app,b['actor_id'])
    path='/provided/A/board?start=2026-01-01&end=2026-12-31'
    assert fa.get('/provided/workspace').json()['data']['subjects'][0]['id']=='A'
    assert fb.get(path).status_code==403
    d=fa.get(path).json()['data'];assert d['groups']==['daily'];assert all(not r['future_scenario'] for r in d['daily'])
    assert all(set(r)<=set(['date','future_scenario','sleep_hours','fluids_dl']) for r in d['daily'])
    body={'text':'Testikirjaus.','topic':'daily','finnish_checked':True,'recipients':[a['actor_id']],'request_id':str(uuid4())}
    assert staff.post('/provided/A/notes',body).status_code==200
    assert staff.post('/provided/A/notes',body).status_code==200
    assert len(fa.get(path).json()['data']['notes'])==1
    assert fa.post('/provided/A/notes',body).status_code==403
    assert staff.post('/provided/A/notes',{**body,'request_id':str(uuid4()),'recipients':[b['actor_id']]}).status_code==403
    assert staff.post('/provided/A/notes',{**body,'topic':'health','request_id':str(uuid4())}).status_code==403
    assert staff.post('/provided/A/notes',{**body,'text':'changed'}).status_code==409
    policy={'actor_id':a['actor_id'],'groups':[],'revision':0}
    assert staff.client.put('/api/v1/provided/A/sharing',json=policy).status_code==200
    assert staff.client.put('/api/v1/provided/A/sharing',json=policy).status_code==409
    d=fa.get(path).json()['data'];assert d['notes']==[] and d['daily']==[]
    app.state.settings.pages_origin='https://example.invalid'
    assert fa.get(path).status_code==404
    assert fa.post('/demo/session',{'demo_actor_id':a['actor_id']}).status_code==403

def test_questions_replies_and_revocation(app,tmp_path):
    a,b=setup(app,tmp_path);staff=Browser(app);fa=Browser(app,a['actor_id']);fb=Browser(app,b['actor_id'])
    q={'text':'Testikysymys?','request_id':str(uuid4())}
    assert fa.post('/provided/A/questions',q).status_code==200
    assert fa.post('/provided/A/questions',q).status_code==200
    assert fb.post('/provided/A/questions',q).status_code==403
    assert staff.post('/provided/B/questions/'+q['request_id']+'/reply',{'text':'Vastaus','finnish_checked':True}).status_code==404
    assert staff.post('/provided/A/questions/'+q['request_id']+'/reply',{'text':'Vastaus','finnish_checked':True}).status_code==200
    path='/provided/A/board?start=2026-01-01&end=2026-12-31'
    assert len(fa.get(path).json()['data']['questions'])==1
    staff.client.put('/api/v1/provided/A/sharing',json={'actor_id':a['actor_id'],'groups':[],'revision':0})
    assert fa.get(path).json()['data']['questions'][0]['reply'] is None

def test_local_transcript_guards(app,tmp_path):
    a,b=setup(app,tmp_path);staff=Browser(app);family=Browser(app,a['actor_id'])
    app.state.live_speech.transcribe=Mock(return_value={'text':'Testi','metadata':{'provider_id':'test'}})
    out=io.BytesIO()
    with wave.open(out,'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000);w.writeframes(bytes(32000))
    endpoint='/api/v1/provided/A/live-transcript?language=fi&synthetic_ack=true'
    assert family.client.post(endpoint,files={'file':('test.wav',out.getvalue(),'audio/wav')}).status_code==403
    assert staff.client.post(endpoint,files={'file':('test.wav',b'bad','audio/wav')}).status_code==415
    r=staff.client.post(endpoint,files={'file':('test.wav',out.getvalue(),'audio/wav')})
    assert r.status_code==200;assert r.json()['data']['saved'] is False
    assert app.state.live_speech.transcribe.call_count==1

def test_one_primary_and_retired_session_denied(app,tmp_path):
    import sqlite3,json
    a,b=setup(app,tmp_path)
    old=Browser(app,a['actor_id'])
    with sqlite3.connect(app.state.settings.root/'provided-scenarios.sqlite') as db:
        p=json.loads(db.execute("SELECT family FROM subjects WHERE id='A'").fetchone()[0])
        p.append({**p[0],'family_id':'second','name':'Second fixture','primary_contact':True,'consent_scope':'terveys, hoito, arki ja osallisuus'})
        db.execute("UPDATE subjects SET family=? WHERE id='A'",(json.dumps(p),))
    # Re-evaluate the representative on every access, including existing sessions.
    assert old.get('/provided/A/board?start=2026-01-01&end=2026-12-31').status_code==403
    sync_accounts(app)
    profiles=people(app.state.settings)
    assert len(profiles)==2
    primary=next(p for p in profiles if p['subject']=='A')
    assert primary['display_name']=='Second fixture'
    current=Browser(app,primary['actor_id'])
    assert current.get('/provided/A/board?start=2026-01-01&end=2026-12-31').status_code==200
    assert old.post('/demo/session',{'demo_actor_id':a['actor_id']}).status_code==403
    staff=Browser(app)
    assert len(staff.get('/provided/A/sharing').json()['data']['items'])==1
    body={'text':'Testi','topic':'daily','finnish_checked':True,'recipients':[a['actor_id']],'request_id':str(uuid4())}
    assert staff.post('/provided/A/notes',body).status_code==403
    with sqlite3.connect(app.state.settings.root/'provided-scenarios.sqlite') as db:
        assert len(json.loads(db.execute("SELECT family FROM subjects WHERE id='A'").fetchone()[0]))==2
