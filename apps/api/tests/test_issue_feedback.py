from conftest import Browser
from helpers import data,draft,approve,prepare,publish

def test_display_names_and_authorized_resident_list(app):
    staff=Browser(app);family=Browser(app,'liisa')
    assert data(staff.get('/session'))['display_name']=='Heli Koskinen'
    assert data(family.get('/session'))['display_name']=='Liisa Nieminen'
    residents=data(staff.get('/staff/residents'))['items']
    assert [(r['subject_id'],r['display_name']) for r in residents]==[('aino','Helmi Nieminen')]
    assert residents[0]['unit_name']=='Synteettinen koti'
    assert family.get('/staff/residents').status_code==403
    with app.state.store.transaction() as db:
        db.execute("UPDATE access_memberships SET active=0 WHERE subject_id='aino' AND actor_id='staff'")
    assert data(staff.get('/staff/residents'))['items']==[]

def test_seventh_health_topic_has_distinct_scope_and_never_leaks(app):
    staff=Browser(app);family=Browser(app,'liisa');restricted=Browser(app,'mikko')
    approve(staff,draft(staff,text='Synthetic health observation',scopes=['health_context']))
    publish(staff,prepare(staff))
    board=data(family.get('/family/residents/aino/board'))
    assert [t['topic'] for t in board['tiles']]==['meals','medication','movement','outdoors','sleep','care_contact','health_context']
    assert board['tiles'][-1]['items'][0]['statement']=='Synthetic health observation'
    hidden=data(restricted.get('/family/residents/aino/board'))['tiles'][-1]
    assert hidden['display_state']=='not_shared' and hidden['items']==[]
