from conftest import Browser
from medipencil.consents import append_grant
from medipencil.db import Store

EVENT = dict(external_id='synthetic-visit',source_version=1,title='Synthetic appointment',starts_at='2030-10-08T10:00:00+03:00',location='Synthetic clinic',details='Synthetic notice only',status='scheduled',required_scopes=['health_context'])


def imported(staff, event=None):
    r=staff.post('/staff/residents/aino/family-events/import',{'data_origin':'TEAM_SYNTHETIC','events':[event or EVENT]})
    assert r.status_code==200,r.text
    return r.json()['data']['items'][0]


def publish(staff,e,recipients=['liisa']):
    return staff.post('/staff/family-events/'+e['event_id']+'/publish',{'recipients':recipients,'reviewed':True},e['revision'])


def listing(browser, role='family'):
    return browser.get('/'+role+'/residents/aino/family-events').json()['data']['items']


def test_review_visibility_acknowledgement_and_persistence(app):
    staff,liisa,mikko=Browser(app),Browser(app,'liisa'),Browser(app,'mikko')
    e=imported(staff);eid=e['event_id']
    assert listing(liisa)==[]
    assert staff.post('/staff/family-events/'+eid+'/publish',{'recipients':['liisa'],'reviewed':False},e['revision']).status_code==422
    assert publish(staff,e,['liisa','mikko']).status_code==422
    assert listing(liisa)==[]  # Entire publication rolls back, not partial delivery.
    assert publish(staff,e).status_code==200
    assert listing(mikko)==[]
    assert mikko.post('/family/family-events/'+eid+'/acknowledge',rev=1).status_code==404
    assert liisa.post('/family/family-events/'+eid+'/acknowledge',rev=0).status_code==412
    first=liisa.post('/family/family-events/'+eid+'/acknowledge',rev=1,key='ack').json()['data']
    assert first['acknowledged_at']
    assert liisa.post('/family/family-events/'+eid+'/acknowledge',rev=1,key='ack').json()['data']==first
    assert listing(staff,'staff')[0]['deliveries'][0]['acknowledged_at']==first['acknowledged_at']
    assert 'deliveries' not in first
    reopened=Store(app.state.settings.root);reopened.migrate()
    with reopened.transaction() as db:
        assert db.execute('SELECT acknowledged_at FROM family_event_deliveries').fetchone()[0]==first['acknowledged_at']
    reopened.engine.dispose()


def test_update_cancel_withdraw_and_revocation_never_replay_old_notice(app):
    staff,liisa=Browser(app),Browser(app,'liisa');e=imported(staff);eid=e['event_id'];publish(staff,e)
    assert liisa.post('/family/family-events/'+eid+'/acknowledge',rev=1,key='ack-old').status_code==200
    updated=imported(staff,EVENT|{'source_version':2,'status':'cancelled'})
    assert listing(liisa)==[]
    assert liisa.post('/family/family-events/'+eid+'/acknowledge',rev=1,key='ack-old').status_code==404
    assert publish(staff,e).status_code==412
    assert publish(staff,updated).status_code==200
    assert listing(liisa)[0]['status']=='cancelled'
    assert listing(liisa)[0]['acknowledged_at'] is None
    with app.state.store.transaction() as db:append_grant(db,'aino','liisa',['care_contact'],'staff',{'kind':'synthetic-test'})
    assert listing(liisa)==[]
    with app.state.store.transaction() as db:append_grant(db,'aino','liisa',['care_contact','health_context'],'staff',{'kind':'synthetic-test'})
    assert listing(liisa)==[]  # Re-grant cannot resurrect old delivery.
    assert staff.post('/staff/family-events/'+eid+'/withdraw',rev=updated['revision']).status_code==200
    draft=listing(staff,'staff')[0];assert publish(staff,draft).status_code==200
    assert len(listing(liisa))==1


def test_import_atomic_deduplicated_and_synthetic_only(app):
    staff=Browser(app);first=imported(staff)
    assert imported(staff)['event_id']==first['event_id']
    assert len(listing(staff,'staff'))==1
    path='/staff/residents/aino/family-events/import'
    for event in [EVENT|{'title':'changed'},EVENT|{'starts_at':'2030-10-08T10:00:00'},EVENT|{'required_scopes':['unknown']}]:
        assert staff.post(path,{'data_origin':'TEAM_SYNTHETIC','events':[event]}).status_code in (409,422)
    assert staff.post(path,{'data_origin':'EMR_LIVE','events':[EVENT]}).status_code==422
    assert staff.post(path,{'data_origin':'TEAM_SYNTHETIC','events':[EVENT,EVENT]}).status_code==422
    assert staff.post(path,{'data_origin':'TEAM_SYNTHETIC','events':[EVENT|{'external_id':'second'},EVENT|{'title':'conflict'}]}).status_code==409
    assert len(listing(staff,'staff'))==1
    assert Browser(app,'liisa').post(path,{'data_origin':'TEAM_SYNTHETIC','events':[EVENT]}).status_code==403
    assert staff.post('/staff/residents/other/family-events/import',{'data_origin':'TEAM_SYNTHETIC','events':[EVENT]}).status_code==404
    staff.client.headers['x-csrf-token']='bad'
    assert staff.post(path,{'data_origin':'TEAM_SYNTHETIC','events':[EVENT]}).status_code==403


def test_two_recipients_have_independent_acknowledgements(app):
    staff,liisa,mikko=Browser(app),Browser(app,'liisa'),Browser(app,'mikko')
    e=imported(staff,EVENT|{'required_scopes':['care_contact']})
    assert publish(staff,e,['liisa','mikko']).status_code==200
    liisa.post('/family/family-events/'+e['event_id']+'/acknowledge',rev=e['revision'])
    assert listing(liisa)[0]['acknowledged_at']
    assert listing(mikko)[0]['acknowledged_at'] is None
