from conftest import Browser
from helpers import draft,approve,data,approve_body

def test_approval_not_answer_or_consent(app):
    f=Browser(app,'liisa');s=Browser(app)
    q=data(f.post('/family/residents/aino/questions',{'text':'Question?'}),201)
    record=draft(s,q['question_id'],kind='plan')
    assert f.get('/staff/records/'+record['record_id']+'?version=1').status_code==403
    before=Browser(app,'mikko').get('/family/residents/aino/sharing').json()
    approve(s,record)
    assert f.get('/family/residents/aino/questions').json()['data']['items'][0]['status']=='received'
    assert Browser(app,'mikko').get('/family/residents/aino/sharing').json()['data']==before['data']
    assert s.get('/staff/residents/aino/actions').json()['data']['items'][0]['status']=='planned'

def test_fidelity_revision_review(app):
    s=Browser(app);r=draft(s,text='Polvi on kipeä.',scopes=['health_context'])
    body=approve_body(r);body['segment_reviews'][0]['meaning_checked']=False
    assert s.post('/staff/records/'+r['record_id']+'/approve',body,rev=1).status_code==422
    assert s.post('/staff/records/'+r['record_id']+'/approve',approve_body(r),rev=99).status_code==412
    segments=r['segments'];segments[0]['text']='Right knee for several days'
    assert s.patch('/staff/records/'+r['record_id']+'/draft',{'version':1,'segments':segments},1).status_code==422
