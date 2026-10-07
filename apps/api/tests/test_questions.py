from conftest import Browser
from concurrent.futures import ThreadPoolExecutor

def test_persistent_question_isolation_retry(app):
    b=Browser(app,'liisa');s=Browser(app)
    r=b.post('/family/residents/aino/questions',{'text':'Synteettinen kysymys?'},key='same')
    assert r.status_code==201,r.text
    id=r.json()['data']['question_id']
    assert b.post('/family/residents/aino/questions',{'text':'Synteettinen kysymys?'},key='same').json()['data']['question_id']==id
    assert b.post('/family/residents/aino/questions',{'text':'different'},key='same').status_code==409
    assert len(s.get('/staff/question-queue').json()['data']['items'])==1
    assert Browser(app,'mikko').get('/family/residents/aino/questions').json()['data']['items']==[]
    assert s.post(f'/staff/questions/{id}/schedule',{'assigned_to':'staff','review_due':'2020-01-01T00:00:00Z'},rev=1).status_code==200
    assert b.get('/family/residents/aino/questions').json()['data']['items'][0]['status']=='unanswered'

def test_duplicate_concurrent(app):
    b=Browser(app,'liisa')
    with ThreadPoolExecutor(2) as pool:
        results=list(pool.map(lambda _:b.post('/family/residents/aino/questions',{'text':'same'},key='race'),range(2)))
    assert all(r.status_code==201 for r in results)
    assert len({r.json()['data']['question_id'] for r in results})==1

def test_thread_reply_uses_only_current_published_bound_items(app):
    from helpers import data,draft,approve,prepare,publish
    staff=Browser(app);family=Browser(app,'liisa');other=Browser(app,'mikko')
    q=data(family.post('/family/residents/aino/questions',{'text':'Synthetic board question'}),201)
    assert q['author_display']=='Liisa' and q['created_at'] and q['reply'] is None
    r=approve(staff,draft(staff,q['question_id'],text='SYNTHETIC REPLY',kind='plan'))
    approve(staff,draft(staff,text='UNRELATED APPROVED INFORMATION'))
    def thread():return data(family.get('/family/residents/aino/questions'))['items'][0]
    assert thread()['reply'] is None
    publication=prepare(staff)
    assert thread()['reply'] is None
    publish(staff,publication)
    reply=thread()['reply']
    assert reply['author_display']=='Koskinen'
    assert reply['items']==[{'statement':'SYNTHETIC REPLY','claim_type':'plan'}]
    assert data(other.get('/family/residents/aino/questions'))['items']==[]
    assert data(staff.get('/staff/question-queue'))['items'][0]['reply']==reply
    grant=data(family.get('/family/residents/aino/sharing'))
    data(staff.post('/staff/residents/aino/consents/liisa/revoke',{'scopes':grant['scopes'],'expected_consent_version':grant['version'],'reason_code':'test'}))
    assert thread()['reply'] is None and thread()['display_state']=='access_changed'
    assert data(staff.get('/staff/question-queue'))['items'][0]['reply'] is None
