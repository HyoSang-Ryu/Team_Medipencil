from conftest import Browser
from helpers import data,draft,approve,prepare,publish,publish_body

def candidate(s,scope=None):
    r=draft(s,text='Mikko saa ulkoilutiedon.',scopes=['outdoors'])
    return data(s.post('/staff/residents/aino/consent-candidates',{'recipient_id':'mikko','proposed_scopes':scope or ['outdoors'],'utterance_ref':r['segments'][0]['evidence_refs'][0]}),201)

def test_candidate_scope_expansion_stale_and_revoke(app):
    s=Browser(app);m=Browser(app,'mikko');c=candidate(s)
    assert 'outdoors' not in data(m.get('/family/residents/aino/sharing'))['scopes']
    body={'recipient_id':'mikko','confirmed_scopes':['outdoors','health_context'],'expected_consent_version':1,'speaker_and_scope_checked':True}
    assert s.post('/staff/consent-candidates/'+c['candidate_id']+'/confirm',body,rev=1).status_code==422
    body['confirmed_scopes']=['outdoors'];body['expected_consent_version']=0
    assert s.post('/staff/consent-candidates/'+c['candidate_id']+'/confirm',body,rev=1).status_code==409
    body['expected_consent_version']=1
    grant=data(s.post('/staff/consent-candidates/'+c['candidate_id']+'/confirm',body,rev=1))
    assert 'health_context' not in grant['scopes']
    approve(s,draft(s,text='Ulkoilu havaittu.'))
    approve(s,draft(s,text='Salainen terveystieto.',scopes=['outdoors','health_context']))
    p=prepare(s,'mikko');publish(s,p)
    assert 'Salainen' not in m.get('/family/residents/aino/board').text
    id=p['items'][0]['item_id']
    assert m.get('/family/items/'+id+'/evidence').status_code==200
    data(s.post('/staff/residents/aino/consents/mikko/revoke',{'scopes':grant['scopes'],'expected_consent_version':2,'reason_code':'demo'}))
    assert data(m.get('/family/residents/aino/sharing'))['scopes']==[]
    assert m.get('/family/items/'+id+'/evidence').status_code==404
    assert 'Ulkoilu havaittu.' not in m.get('/family/residents/aino/board').text

def test_simple_settings_atomic_evidence_stale_and_replay(app):
    from uuid import uuid4
    s=Browser(app);m=Browser(app,'mikko')
    path='/staff/residents/aino/consents/mikko/settings'
    body={'scopes':['meals','outdoors'],'expected_consent_version':1,'confirmation_method':'written','confirmation_date':'2026-01-01','confirmation_note':'Synthetic authorized consent.','consent_checked':True}
    assert m.post(path,body).status_code==403
    assert s.post(path,{**body,'consent_checked':False}).status_code==422
    assert s.post(path,{**body,'confirmation_note':' '}).status_code==422
    assert s.post(path,{**body,'scopes':['unknown']}).status_code==422
    assert s.post(path,{**body,'confirmation_date':'2099-01-01'}).status_code==422
    key=str(uuid4());result=data(s.post(path,body,key=key))
    assert result['scopes']==['meals','outdoors'] and result['version']==2
    assert data(s.post(path,body,key=key))['version']==2
    assert s.post(path,body).status_code==409
    history=data(s.get('/staff/residents/aino/consents'))['history']
    evidence=[h for h in history if h['recipient_id']=='mikko' and h['version']==2][0]['evidence_ref']
    assert evidence['kind']=='staff_attestation' and evidence['note']==body['confirmation_note']
    approve(s,draft(s,text='Synthetic outdoor observation.',scopes=['outdoors']))
    p=prepare(s,'mikko');publish(s,p)
    item=p['items'][0]['item_id'];assert m.get('/family/items/'+item+'/evidence').status_code==200
    data(s.post(path,{**body,'scopes':[],'expected_consent_version':2}))
    assert data(m.get('/family/residents/aino/sharing'))['scopes']==[]
    assert m.get('/family/items/'+item+'/evidence').status_code==404
    assert s.post(path.replace('mikko','staff'),body).status_code==422
