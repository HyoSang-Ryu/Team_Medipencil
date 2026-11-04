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

def test_guardian_relationship_is_inverted_and_unknown_not_invented():
    from medipencil.provided_workflow import family_identity
    assert family_identity('Example (75 v, nainen)','tytär')=={'name':'Example','age':75,'relationship':'mother'}
    assert family_identity('Example (25 v, mies)','äiti')['relationship']=='son'
    assert family_identity('Example (80 v, mies)','poika')['relationship']=='father'
    assert family_identity('Example','tuntematon')=={'name':'Example','age':None,'relationship':'family'}

def test_stitch_family_interactions_are_subject_scoped_and_persisted(app,tmp_path):
    from datetime import datetime,timedelta
    from zoneinfo import ZoneInfo
    a,b=setup(app,tmp_path);staff=Browser(app);fa=Browser(app,a['actor_id']);fb=Browser(app,b['actor_id'])
    day=(datetime.now(ZoneInfo('Europe/Helsinki')).date()+timedelta(days=2)).isoformat()
    visit={'kind':'lounge','visit_day':day,'visit_time':'15:00','guests':2,'request_id':str(uuid4())}
    assert fa.post('/provided/A/visits',visit).json()['data']['reservation_confirmed'] is False
    assert fa.post('/provided/A/visits',visit).status_code==200
    assert fb.post('/provided/A/visits',{**visit,'request_id':str(uuid4())}).status_code==403
    assert staff.post('/provided/A/visits',visit).status_code==403
    assert staff.post('/provided/B/visits/'+visit['request_id']+'/decision',{'status':'approved'}).status_code==404
    assert staff.post('/provided/A/visits/'+visit['request_id']+'/decision',{'status':'approved'}).json()['data']['reservation_confirmed'] is True
    msg={'text':'PoC greeting for the care team','request_id':str(uuid4())}
    assert fa.post('/provided/A/family-messages',msg).json()['data']['delivered_to_resident'] is False
    assert staff.post('/provided/A/family-messages',msg).status_code==403
    assert fb.post('/provided/A/family-messages',msg).status_code==403
    note={'text':'Testikirjaus.','topic':'daily','finnish_checked':True,'recipients':[a['actor_id']],'request_id':str(uuid4())}
    assert staff.post('/provided/A/notes',note).status_code==200
    assert fb.post('/provided/A/notes/'+note['request_id']+'/read',{}).status_code==403
    assert fa.post('/provided/A/notes/'+note['request_id']+'/read',{}).status_code==200
    assert fb.client.put('/api/v1/provided/A/notes/'+note['request_id']+'/reaction',json={'kind':'heart'}).status_code==403
    assert fa.client.put('/api/v1/provided/A/notes/'+note['request_id']+'/reaction',json={'kind':'thanks'}).status_code==200
    assert fa.client.put('/api/v1/provided/A/preferences',json={'daily':False,'social':True,'health':False}).status_code==200
    path='/provided/A/board?start=2026-01-01&end=2026-12-31'
    data=fa.get(path).json()['data']
    assert data['visits'][0]['status']=='approved'
    assert data['family_messages'][0]['status']=='pending'
    assert data['notes'][0]['read'] is True
    assert data['notes'][0]['my_reaction']=='thanks' and data['notes'][0]['reactions']['thanks']==1
    assert data['preferences']=={'daily':False,'social':True,'health':False}
    assert fb.post('/provided/A/visits/'+visit['request_id']+'/cancel',{}).status_code==403
    assert fa.post('/provided/A/visits/'+visit['request_id']+'/cancel',{}).status_code==200
    assert fa.get(path).json()['data']['visits'][0]['status']=='cancelled'
    other=fb.get('/provided/B/board?start=2026-01-01&end=2026-12-31').json()['data']
    assert other['visits']==[] and other['family_messages']==[] and other['notes']==[]
    assert staff.post('/provided/A/family-messages/'+msg['request_id']+'/processed',{}).status_code==200
    assert fa.get(path).json()['data']['family_messages'][0]['status']=='processed'
    assert staff.get(path).json()['data']['notes'][0]['read_count']==1
    assert staff.client.put('/api/v1/provided/A/sharing',json={'actor_id':a['actor_id'],'groups':[],'revision':0}).status_code==200
    assert fa.client.put('/api/v1/provided/A/notes/'+note['request_id']+'/reaction',json={'kind':'heart'}).status_code==403
    assert fa.post('/provided/A/notes/'+note['request_id']+'/read',{}).status_code==403
    assert fa.get(path).json()['data']['notes']==[]

def test_chart_draft_is_staff_only_and_never_published(app,tmp_path):
    a,b=setup(app,tmp_path);staff=Browser(app);family=Browser(app,a['actor_id'])
    path='/provided/A/chart-draft'
    draft={'meal_percent':80,'swallowing':'normal','temperature_c':36.5,'systolic':None,'diastolic':None,'glucose_mmol':None,'medication_note':'','activity_note':'Käveli avustettuna.','staff_note':'','revision':0}
    assert family.get(path).status_code==403
    assert family.client.put('/api/v1'+path,json=draft).status_code==403
    saved=staff.client.put('/api/v1'+path,json=draft)
    assert saved.status_code==200 and saved.json()['data']['published'] is False
    assert staff.get(path).json()['data']['draft']['meal_percent']==80
    assert staff.client.put('/api/v1'+path,json=draft).status_code==409
    assert staff.client.put('/api/v1'+path,json={**draft,'revision':1,'meal_percent':101}).status_code==422
    family_board=family.get('/provided/A/board?start=2026-01-01&end=2026-12-31').json()['data']
    assert family_board['notes']==[] and 'chart_draft' not in family_board
