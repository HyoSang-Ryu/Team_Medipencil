import sqlite3
from conftest import Browser
from helpers import data,draft,approve,prepare,publish,publish_body
from medipencil.db import one

def test_correction_no_old_fallback(app):
    s=Browser(app);f=Browser(app,'liisa')
    q=data(f.post('/family/residents/aino/questions',{'text':'Ulkoilu?'}),201)
    r=approve(s,draft(s,q['question_id'],text='Old fact.'))
    first=publish(s,prepare(s));second=publish(s,prepare(s))
    corrected=data(s.post('/staff/records/'+r['record_id']+'/corrections',{'version':1,'reason_code':'wrong_fact'},rev=r['revision']),201)
    assert corrected['version']==2
    assert 'Old fact.' not in f.get('/family/residents/aino/board').text
    assert f.get('/family/items/'+first['items'][0]['item_id']+'/evidence').status_code==404
    assert data(f.get('/family/residents/aino/questions'))['items'][0]['status']=='unanswered'
    with app.state.store.transaction() as db:
        assert one(db,'SELECT * FROM record_versions WHERE record_id=? AND version=1',(r['record_id'],))['segments'][0]['text']=='Old fact.'

def test_publish_rollback(app):
    s=Browser(app);f=Browser(app,'liisa')
    q=data(f.post('/family/residents/aino/questions',{'text':'Q?'}),201)
    approve(s,draft(s,q['question_id']));p=prepare(s)
    with app.state.store.transaction() as db:
        db.execute('CREATE TRIGGER fail_publish BEFORE UPDATE OF status ON family_questions WHEN NEW.status="answered" BEGIN SELECT RAISE(ABORT,"injected"); END')
    response=s.post('/staff/publications/'+p['publication_id']+'/publish',publish_body(p),rev=1)
    assert response.status_code==503 and 'injected' not in response.text
    with app.state.store.transaction() as db:
        assert one(db,'SELECT * FROM publications WHERE publication_id=?',(p['publication_id'],))['status']=='draft'
        assert one(db,'SELECT * FROM family_questions WHERE question_id=?',(q['question_id'],))['status']=='received'

def test_idempotent_publish_rechecks_revoked_permission(app):
    s=Browser(app);approve(s,draft(s));p=prepare(s);body=publish_body(p)
    data(s.post('/staff/publications/'+p['publication_id']+'/publish',body,rev=1,key='pub'))
    data(s.post('/staff/residents/aino/consents/liisa/revoke',{'scopes':['outdoors'],'expected_consent_version':1,'reason_code':'test'}))
    assert s.post('/staff/publications/'+p['publication_id']+'/publish',body,rev=1,key='pub').status_code==409
