import pytest
from conftest import Browser
from medipencil.local_providers import LocalModels
from medipencil.db import one,many
from medipencil.common import Fault
from medipencil.ai_wording import Summary,validate_summary

@pytest.fixture
def provider(app,monkeypatch):
    app.state.settings.models=LocalModels(llm_backend='ollama')
    calls=[]
    def render(self,snapshot):
        calls.append(snapshot)
        groups={}
        for e in snapshot['evidence']:groups.setdefault(e['topic'],[]).append(e)
        return {'items':[{'statement':' '.join(dict.fromkeys(e['text'] for e in rows)),'evidence_keys':[e['key'] for e in rows]} for rows in groups.values()], 'metadata':{'provider_id':'test_fake','execution_mode':'SIMULATED','ai_executed':False}}
    monkeypatch.setattr('medipencil.ai_summary.OllamaFamilyWording.render',render)
    return calls

def generate(app,days=1,recipient='liisa',key=None):
    b=Browser(app);r=b.post('/staff/residents/aino/ai-summary',{'recipient_id':recipient,'days':days},key=key)
    assert r.status_code==202,r.text
    return b,b.get('/staff/jobs/'+r.json()['data']['job_id']).json()['data']

def publish(b,p):
    return b.post('/staff/publications/'+p['publication_id']+'/publish',{'reviewed_items':[{'item_id':i['item_id'],'meaning_checked':True,'language_checked':True,'evidence_checked':True} for i in p['items']],'accepted_answer_candidate_ids':[],'expected_content_epoch':p['content_epoch'],'expected_consent_version':p['consent_version']},p['revision'])

def test_disabled_and_family_cannot_generate(app):
    assert Browser(app).post('/staff/residents/aino/ai-summary',{'recipient_id':'liisa'}).status_code==503
    assert Browser(app,'liisa').post('/staff/residents/aino/ai-summary',{'recipient_id':'liisa'}).status_code==403
    with app.state.store.transaction() as db:assert not many(db,'SELECT * FROM processing_jobs WHERE job_type="family_summary"')

def test_draft_review_publish_and_original_evidence(app,provider):
    b,j=generate(app);assert j['status']=='succeeded',j
    p=b.get('/staff/publications/'+j['result_ref']['id']).json()['data'];family=Browser(app,'liisa')
    assert family.get('/family/residents/aino/board').json()['data']['publication_id']!=p['publication_id']
    assert b.post('/staff/publications/'+p['publication_id']+'/publish',{'reviewed_items':[],'accepted_answer_candidate_ids':[],'expected_content_epoch':p['content_epoch'],'expected_consent_version':p['consent_version']},p['revision']).status_code==422
    assert len(b.get('/staff/residents/aino/ai-summaries').json()['data']['items'])==1
    assert publish(b,p).status_code==200
    board=family.get('/family/residents/aino/board').json()['data'];assert board['publication_id']==p['publication_id']
    for item in p['items']:
        e=family.get('/family/items/'+item['item_id']+'/evidence').json()['data']
        assert e['excerpt']==item['source_excerpt']
    plan=next(i for i in p['items'] if i['topic']=='outdoors');assert plan['claim_type']=='plan'
    with app.state.store.transaction() as db:db.execute('UPDATE source_events SET valid=0 WHERE source_id=?',(p['input_refs'][0]['source_id'],))
    assert family.get('/family/items/'+p['items'][0]['item_id']+'/evidence').status_code==404
    assert b.get('/staff/residents/aino/ai-summaries').json()['data']['items']==[]

def test_consent_filtered_before_ai_and_rechecked_after(app,provider,monkeypatch):
    b,j=generate(app,recipient='mikko');assert j['status']=='succeeded'
    assert all('medication' not in e['required_scopes'] for e in provider[0]['evidence'])
    original=__import__('medipencil.ai_summary',fromlist=['OllamaFamilyWording']).OllamaFamilyWording.render
    def changed(self,snapshot):
        result=original(self,snapshot)
        with app.state.store.transaction() as db:db.execute('UPDATE residents SET content_epoch=content_epoch+1 WHERE subject_id="aino"')
        return result
    monkeypatch.setattr('medipencil.ai_summary.OllamaFamilyWording.render',changed)
    _,j=generate(app);assert j['status']=='failed' and j['error_code']=='STALE_EVIDENCE'

def test_provider_failure_does_not_publish(app,provider,monkeypatch):
    def fail(*args):raise Fault('TIMEOUT',504)
    monkeypatch.setattr('medipencil.ai_summary.OllamaFamilyWording.render',fail)
    _,j=generate(app);assert j['status']=='failed' and j['error_code']=='TIMEOUT'
    with app.state.store.transaction() as db:assert not one(db,'SELECT * FROM publications WHERE generation_meta_json LIKE ?',('%ai-summary-v1%',))

def test_idempotent_retry_does_not_rerun_model(app,provider):
    b=Browser(app);body={'recipient_id':'liisa','days':1}
    a=b.post('/staff/residents/aino/ai-summary',body,key='same');c=b.post('/staff/residents/aino/ai-summary',body,key='same')
    assert a.json()['data']['job_id']==c.json()['data']['job_id'];assert len(provider)==1

@pytest.mark.parametrize('output',[
 {'items':[{'statement':'100 minutes','evidence_keys':['a']}]},
 {'items':[{'statement':'text','evidence_keys':['unknown']}]},
 {'items':[{'statement':'text','evidence_keys':['a','b']}]},
])
def test_output_validation(output):
    evidence=[{'key':'a','text':'5 minutes','occurred_at':'2026-10-11','topic':'movement','type':'observation','speaker':'carer'},{'key':'b','text':'planned','occurred_at':'2026-10-11','topic':'outdoors','type':'plan','speaker':'carer'}]
    with pytest.raises(Fault):validate_summary(Summary.model_validate(output),evidence)

def test_permission_filter_before_model_and_revocation_during_model(app,provider,monkeypatch):
    with app.state.store.transaction() as db:db.execute('INSERT INTO consent_versions SELECT consent_id,version+1,subject_id,recipient_id,status,?,confirmed_by,confirmed_at,revoked_at,evidence_ref_json,derived_from_candidate_id FROM consent_versions WHERE subject_id="aino" AND recipient_id="liisa" ORDER BY version DESC LIMIT 1',('["meals"]',))
    _,j=generate(app);assert j['status']=='succeeded'
    assert {e['topic'] for e in provider[0]['evidence']}=={'meals'}
    original=__import__('medipencil.ai_summary',fromlist=['OllamaFamilyWording']).OllamaFamilyWording.render
    def revoke(self,snapshot):
        result=original(self,snapshot)
        with app.state.store.transaction() as db:db.execute('INSERT INTO consent_versions SELECT consent_id,version+1,subject_id,recipient_id,"revoked","[]",confirmed_by,confirmed_at,revoked_at,evidence_ref_json,derived_from_candidate_id FROM consent_versions WHERE recipient_id="liisa" ORDER BY version DESC LIMIT 1')
        return result
    monkeypatch.setattr('medipencil.ai_summary.OllamaFamilyWording.render',revoke)
    _,j=generate(app);assert j['error_code']=='STALE_CONSENT'


def test_synthetic_30_day_series_distinguishes_dates_plans_and_variation():
    from datetime import date
    from medipencil.synthetic_emr import records
    data=records('aino',date(2026,10,11),30)
    assert len(data)==120 and len({e['key'] for e in data})==120
    assert len({e['text'] for e in data if e['topic']=='meals'})==3
    assert all(e['type']=='plan' for e in data if e['topic']=='outdoors')

def test_rejects_json_copied_as_family_prose():
    evidence=[{'key':'a','text':'5 minutes','occurred_at':'2026-10-11','topic':'movement','type':'observation','speaker':'carer'}]
    with pytest.raises(Fault):validate_summary(Summary(items=[{'statement':'{"records": "5 minutes"}','evidence_keys':['a']}]),evidence)


def test_30_day_grouped_contract_with_fake_model(app,provider):
    b,j=generate(app,days=30);assert j['status']=='succeeded',j
    p=b.get('/staff/publications/'+j['result_ref']['id']).json()['data']
    assert len(p['items'])==4 and len(p['input_refs'])==120
    assert len(b.get('/staff/residents/aino/ai-summaries').json()['data']['items'])==1

def test_plan_without_completion_confirmation_is_not_failure_or_completion():
    evidence=[{'key':'a','text':'Ulkoilu on suunniteltu. Toteutumista ei ole vahvistettu.','occurred_at':'2026-10-11','topic':'outdoors','type':'plan','speaker':'carer'}]
    with pytest.raises(Fault):validate_summary(Summary(items=[{'statement':'Aino ei ole koskaan mennyt ulos.','evidence_keys':['a']}]),evidence)

def test_input_compaction_preserves_every_date_and_original_text():
    from medipencil.ai_wording import compact_group
    rows=[{'topic':'meals','type':'observation','text':'same observation','occurred_at':'2026-10-10T08:00:00+03:00'},{'topic':'meals','type':'observation','text':'same observation','occurred_at':'2026-10-11T08:00:00+03:00'}]
    text=compact_group(rows)
    assert text.count('same observation')==1 and '2026-10-10' in text and '2026-10-11' in text
