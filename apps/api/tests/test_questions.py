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
