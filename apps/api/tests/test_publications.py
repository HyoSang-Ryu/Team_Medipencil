from conftest import Browser
from helpers import data,draft,approve,prepare,publish

def test_full_text_loop_and_evidence(app):
    f=Browser(app,'liisa');s=Browser(app)
    q=data(f.post('/family/residents/aino/questions',{'text':'Ulkoilu?'}),201)
    r=draft(s,q['question_id'],text='Ulkoilua suunnitellaan.',kind='plan')
    assert 'Ulkoilua' not in f.get('/family/residents/aino/board').text
    approve(s,r);p=prepare(s)
    assert 'Ulkoilua' not in f.get('/family/residents/aino/board').text
    publish(s,p)
    board=data(f.get('/family/residents/aino/board'))
    assert board['answers'][0]['question_id']==q['question_id']
    assert data(f.get('/family/residents/aino/questions'))['items'][0]['answer_available']
    id=p['items'][0]['item_id']
    assert data(f.get('/family/items/'+id+'/evidence'))['excerpt']=='Ulkoilua suunnitellaan.'
    assert Browser(app,'mikko').get('/family/items/'+id+'/evidence').status_code==404
    assert board['tiles'][3]['items'][0]['action_status']=='planned'

def test_plan_cannot_confirm(app):
    s=Browser(app);r=approve(s,draft(s,kind='plan'))
    action=data(s.get('/staff/residents/aino/actions'))['items'][0]
    assert s.post('/staff/actions/'+action['action_id']+'/confirm',{'confirmation_ref':action['planned_in'],'meaning_checked':True},rev=1).status_code==422
