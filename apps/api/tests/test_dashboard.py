from datetime import date
from conftest import Browser
from helpers import data,draft,approve,prepare,publish
from medipencil.dashboard import summarize,TOPICS


def test_seven_days_helsinki_boundary_and_missing():
    result=summarize([{'topic':'sleep','observed_at':'2026-10-06T21:30:00Z'},
                      {'topic':'sleep','observed_at':'2026-09-30T20:59:59Z'},
                      {'topic':'meals','observed_at':'2026-10-07T00:00:00Z'}],{'sleep'},date(2026,10,7))
    assert result['dates']==['2026-10-01','2026-10-02','2026-10-03','2026-10-04','2026-10-05','2026-10-06','2026-10-07']
    sleep=next(t for t in result['topics'] if t['topic']=='sleep')
    assert sleep['daily']==[0,0,0,0,0,0,1]
    assert result['topics'][0]['daily']==[None]*7


def test_counts_require_approval_publication_and_current_permission(app):
    staff=Browser(app);liisa=Browser(app,'liisa');mikko=Browser(app,'mikko')
    path='/family/residents/aino/dashboard';sp='/staff/residents/aino/dashboard'
    r=draft(staff,kind='plan',scopes=['outdoors','health_context'])
    assert sum(t['total'] or 0 for t in data(staff.get(sp))['topics'])==0
    approve(staff,r)
    assert sum(t['total'] or 0 for t in data(staff.get(sp))['topics'])==1
    assert sum(t['total'] or 0 for t in data(liisa.get(path))['topics'])==0
    p=publish(staff,prepare(staff))
    result=data(liisa.get(path));assert sum(t['total'] or 0 for t in result['topics'])==1
    assert result['ai_executed'] is False
    assert 'statement' not in str(result)
    assert next(t for t in data(mikko.get(path))['topics'] if t['topic']=='outdoors')['total'] is None
    assert liisa.get(sp).status_code==403
    assert liisa.get('/family/residents/other/dashboard').status_code==404
    scopes=data(liisa.get('/family/residents/aino/sharing'))
    data(staff.post('/staff/residents/aino/consents/liisa/revoke',{'scopes':scopes['scopes'],'expected_consent_version':scopes['version'],'reason_code':'synthetic-test'}))
    assert all(t['total'] is None for t in data(liisa.get(path))['topics'])


def test_stale_publication_and_invalid_source_are_not_counted(app):
    b=Browser(app);f=Browser(app,'liisa');r=approve(b,draft(b));publish(b,prepare(b))
    with app.state.store.transaction() as db:
        db.execute('UPDATE source_events SET valid=0')
    assert sum(t['total'] or 0 for t in data(b.get('/staff/residents/aino/dashboard'))['topics'])==0
    assert sum(t['total'] or 0 for t in data(f.get('/family/residents/aino/dashboard'))['topics'])==0


def test_custom_period_limits_and_current_permissions(app):
    staff=Browser(app);family=Browser(app,'liisa');restricted=Browser(app,'mikko')
    approve(staff,draft(staff,scopes=['medication'],occurred_at='2026-01-02T22:30:00Z'))
    publish(staff,prepare(staff))
    path='/family/residents/aino/dashboard'
    result=data(family.get(path+'?start_date=2026-01-03&end_date=2026-01-03'))
    assert result['dates']==['2026-01-03']
    assert next(t for t in result['topics'] if t['topic']=='medication')['daily']==[1]
    result=data(restricted.get(path+'?start_date=2026-01-01&end_date=2026-01-30'))
    assert len(result['dates'])==30
    assert next(t for t in result['topics'] if t['topic']=='medication')['daily']==[None]*30
    for query in ['start_date=2026-01-01','start_date=bad&end_date=2026-01-03','start_date=2026-02-30&end_date=2026-03-01','start_date=2026-02-01&end_date=2026-01-01','start_date=2026-01-01&end_date=2026-05-01','start_date=2999-01-01&end_date=2999-01-02','start_date=2026-01-01&end_date=2026-01-02&recipient_id=liisa']:
        assert family.get(path+'?'+query).status_code==422
