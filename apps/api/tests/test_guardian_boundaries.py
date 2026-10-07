from conftest import Browser
from helpers import data, draft, approve, prepare, publish
from medipencil.domain import SCOPES


def test_two_guardians_receive_different_publications_and_private_questions(app):
    nurse=Browser(app); liisa=Browser(app,'liisa'); mikko=Browser(app,'mikko')
    assert data(liisa.get('/family/residents/aino/sharing'))['scopes']==sorted(SCOPES)
    assert set(data(mikko.get('/family/residents/aino/sharing'))['scopes'])=={'meals','movement','care_contact'}
    assert nurse.post('/demo/session',{'demo_actor_id':'aino'}).status_code==403
    # Aino is a resident, with no login actor. The failed login leaves the nurse session intact.
    q=data(liisa.post('/family/residents/aino/questions',{'text':'Synthetic private guardian question'}),201)
    assert data(mikko.get('/family/residents/aino/questions'))['items']==[]
    assert any(item['question_id']==q['question_id'] for item in data(nurse.get('/staff/question-queue'))['items'])
    approve(nurse,draft(nurse,text='Synthetic meal observation',scopes=['meals']))
    approve(nurse,draft(nurse,text='Synthetic restricted medication observation',scopes=['medication']))
    lp=prepare(nurse,'liisa');publish(nurse,lp)
    mp=prepare(nurse,'mikko');publish(nurse,mp)
    lb=liisa.get('/family/residents/aino/board');mb=mikko.get('/family/residents/aino/board')
    assert 'Synthetic restricted medication observation' in lb.text
    assert 'Synthetic meal observation' in mb.text
    assert 'Synthetic restricted medication observation' not in mb.text
    for item in lp['items']:
        assert mikko.get('/family/items/'+item['item_id']+'/evidence').status_code==404
    for guardian in [liisa,mikko]:
        assert guardian.get('/staff/residents/aino/consents').status_code==403
        assert guardian.get('/staff/residents/aino/sources').status_code==403
        assert guardian.get('/family/residents/aino/sharing?recipient_id=liisa').status_code==422
    topics=data(mikko.get('/family/residents/aino/dashboard'))['topics']
    assert next(t for t in topics if t['topic']=='medication')['total'] is None
