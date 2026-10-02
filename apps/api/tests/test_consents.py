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
