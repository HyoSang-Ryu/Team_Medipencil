from conftest import Browser
from helpers import data

def setup(s,required=None):
    c=data(s.post('/staff/residents/aino/captures',{'input_mode':'text'}),201)
    c=data(s.post('/staff/captures/'+c['capture_id']+'/text',{'occurred_at':'2026-01-01T08:00:00Z','utterances':[{'text':'약은 복용하지 않았습니다. 산책은 계획입니다.','speaker':'carer','type':'statement','required_scopes':['medication','health_context']}]},c['revision']),201)
    chart=data(s.post('/staff/residents/aino/voice-charts',{'capture_id':c['capture_id'],'required':required or ['medication','mobility']}),201)
    return c,chart

def test_chart_checklist_draft_and_replay(app):
    s=Browser(app);cap,c=setup(s)
    assert c['pending']==['medication','mobility']
    assert not c['execution']['ai_executed']
    assert c['suggestions']['medication']==['약은 복용하지 않았습니다. 산책은 계획입니다.']
    path='/staff/voice-charts/'+c['chart_id']
    assert s.post(path+'/finish',{'checked':True},c['revision']).status_code==422
    answers={'medication':{'status':'confirmed','text':'약은 복용하지 않았습니다.','speaker':'carer','type':'observation','observed_at':'2026-01-01T08:00:00Z'},'mobility':{'status':'follow_up','reason':'실행 확인 필요'}}
    c=data(s.patch(path,{'answers':answers},c['revision']))
    assert not c['pending']
    assert data(s.get(path))['answers']['mobility']['status']=='follow_up'
    assert s.patch(path,{'answers':answers},1).status_code==412
    result=s.post(path+'/finish',{'checked':True},c['revision'],key='finish-chart')
    r=data(result);assert r['status']=='draft'
    assert r['segments'][0]['text']=='약은 복용하지 않았습니다.'
    assert set(r['segments'][0]['required_scopes'])=={'medication','health_context'}
    assert len(r['segments'][0]['evidence_refs'])==2
    assert data(s.post(path+'/finish',{'checked':True},c['revision'],key='finish-chart'))['record_id']==r['record_id']
    assert Browser(app,'liisa').get(path).status_code==403
    assert data(s.get(path))['status']=='completed'

def test_chart_requires_explicit_evidence(app):
    s=Browser(app);cap,c=setup(s,['pain']);path='/staff/voice-charts/'+c['chart_id']
    for answer in [{'status':'unknown'},{'status':'confirmed','text':'pain'}]:
        assert s.patch(path,{'answers':{'pain':answer}},1).status_code==422
    c=data(s.patch(path,{'answers':{'pain':{'status':'unknown','reason':'측정하지 않음'}}},1))
    assert s.post(path+'/finish',{'checked':True},c['revision']).status_code==422
    assert data(s.get(path))['status']=='draft'
    with app.state.store.transaction() as db:
        db.execute("UPDATE captures SET status='canceled' WHERE capture_id=?",(cap['capture_id'],))
    assert s.get(path).status_code==409

def test_chart_rejects_invalid_fields_and_subject(app):
    s=Browser(app);cap,c=setup(s)
    assert s.post('/staff/residents/aino/voice-charts',{'capture_id':cap['capture_id'],'required':['fake']}).status_code==422
    assert s.post('/staff/residents/other/voice-charts',{'capture_id':cap['capture_id'],'required':['pain']}).status_code ==404

def test_chart_preserves_plan_and_invalidates_source(app):
    from helpers import approve
    s=Browser(app);cap,c=setup(s,['mobility']);path='/staff/voice-charts/'+c['chart_id']
    answers={'mobility':{'status':'confirmed','text':'산책은 계획입니다.','speaker':'carer','type':'plan','observed_at':'2026-01-01T08:00:00Z'}}
    c=data(s.patch(path,{'answers':answers},1))
    r=data(s.post(path+'/finish',{'checked':True},c['revision']))
    assert r['segments'][0]['type']=='plan'
    approve(s,r)
    with app.state.store.transaction() as db:
        db.execute('UPDATE source_events SET valid=0 WHERE source_id=?',(cap['source_refs'][0]['source_id'],))
    assert s.get(path).status_code==409

def test_chart_cannot_reuse_consumed_capture(app):
    s=Browser(app);cap,c=setup(s,['pain'])
    path='/staff/voice-charts/'+c['chart_id']
    c=data(s.patch(path,{'answers':{'pain':{'status':'confirmed','text':'통증 확인 필요라는 진술','observed_at':'2026-01-01T08:00:00Z'}}},1))
    with app.state.store.transaction() as db:
        db.execute("UPDATE captures SET status='draft_ready' WHERE capture_id=?",(cap['capture_id'],))
    assert s.post(path+'/finish',{'checked':True},c['revision']).status_code==409
