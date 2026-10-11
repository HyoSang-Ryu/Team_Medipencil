from datetime import datetime,timezone
from conftest import Browser
from helpers import data,draft
from medipencil.recurring import tick,next_run,delivery_day
from medipencil.db import many,one

def enable(s,recipient='liisa',revision=0):
    return data(s.post('/staff/residents/aino/delivery-schedules/'+recipient,{'enabled':True,'expected_revision':revision}))
def due(app,day='2026-10-10T15:00:00+00:00'):
    with app.state.store.transaction() as db:db.execute('UPDATE delivery_schedules SET next_run_at=?',(day,))
    return datetime.fromisoformat(day)

def test_daily_delivery_without_record_approval_and_current_permission(app):
    s=Browser(app);f=Browser(app,'liisa');m=Browser(app,'mikko')
    assert f.post('/staff/residents/aino/delivery-schedules/liisa',{'enabled':True,'expected_revision':0}).status_code==403
    enable(s);enable(s,'mikko')
    draft(s,text='This AI/manual draft must never be sent.',scopes=['meals'])
    dt=due(app);tick(app.state.store,dt)
    board=data(f.get('/family/residents/aino/board'));texts=[i['statement'] for t in board['tiles'] for i in t['items']]
    assert len(texts)==2 and not any('draft' in t or 'suunniteltu' in t for t in texts)
    assert board['execution']['original']['ai_executed'] is False
    assert board['execution']['original']['execution_mode']=='SIMULATED'
    listing=data(s.get('/staff/residents/aino/delivery-schedules'))['items']
    assert listing[0]['last_result']=='delivered'
    assert listing[0]['exceptions']
    with app.state.store.transaction() as db:
        assert one(db,'SELECT * FROM publications WHERE publication_id=?',(board['publication_id'],))['reviewed_by'] is None
        count=len(many(db,'SELECT * FROM publications'))
    # Even after forced repeated scheduler execution, the local-day unique key prevents duplicate delivery.
    due(app);tick(app.state.store,dt)
    with app.state.store.transaction() as db:assert len(many(db,'SELECT * FROM publications'))==count
    item=board['tiles'][0]['items'][0]['item_id'];assert f.get('/family/items/'+item+'/evidence').status_code==200
    data(s.post('/staff/residents/aino/consents/liisa/revoke',{'scopes':['meals'],'expected_consent_version':1,'reason_code':'test'}))
    assert f.get('/family/items/'+item+'/evidence').status_code==404
    dt=due(app,'2026-10-11T15:00:00+00:00');tick(app.state.store,dt)
    board=data(f.get('/family/residents/aino/board'))
    assert not board['tiles'][0]['items']
    assert all(t['topic'] not in ['outdoors','health_context'] for t in data(m.get('/family/residents/aino/board'))['tiles'] if t['items'])
    # Every retained source must remain valid at family read time.
    with app.state.store.transaction() as db:db.execute('UPDATE source_events SET valid=0 WHERE source_id=?',('routine-emr-aino-2026-10-11',))
    assert data(f.get('/family/residents/aino/board'))['publication_id'] is None

def test_pause_revision_restart_and_dst(app):
    s=Browser(app);enabled=enable(s)
    assert s.post('/staff/residents/aino/delivery-schedules/liisa',{'enabled':False,'expected_revision':0}).status_code==409
    data(s.post('/staff/residents/aino/delivery-schedules/liisa',{'enabled':False,'expected_revision':enabled['revision']}))
    tick(app.state.store,due(app))
    with app.state.store.transaction() as db:assert not many(db,'SELECT * FROM routine_delivery_runs')
    assert next_run(datetime(2026,10,24,16,tzinfo=timezone.utc))=='2026-10-25T16:00:00.000000+00:00'
    assert next_run(datetime(2026,3,28,17,tzinfo=timezone.utc))=='2026-03-29T15:00:00.000000+00:00'
    assert delivery_day(datetime(2026,10,11,4,tzinfo=timezone.utc)).date().isoformat()=='2026-10-10'

def test_background_worker_and_existing_answer_are_preserved(app):
    import time
    from fastapi.testclient import TestClient
    from helpers import approve,prepare,publish
    from datetime import timedelta
    from medipencil.recurring import stamp
    s=Browser(app);f=Browser(app,'liisa')
    q=data(f.post('/family/residents/aino/questions',{'text':'Synthetic question about meals.'}),201)
    approve(s,draft(s,text='Synthetic reviewed meal answer.',scopes=['meals'],question=q['question_id']))
    publish(s,prepare(s,'liisa'))
    original=data(f.get('/family/residents/aino/questions'))['items'][0]['reply']
    enable(s);due(app,stamp(datetime.now(timezone.utc)-timedelta(minutes=1)))
    # Actual ASGI lifespan worker executes without any browser or delivery HTTP request.
    with TestClient(app):
        for _ in range(100):
            with app.state.store.transaction() as db:
                done=one(db,'SELECT last_result FROM delivery_schedules WHERE recipient_id="liisa"')['last_result']
            if done:break
            time.sleep(.02)
        assert done=='delivered'
        reply=data(f.get('/family/residents/aino/questions'))['items'][0]['reply']
        assert reply==original
