import pytest
from conftest import Browser
from helpers import data,approve,prepare,publish,draft

@pytest.mark.parametrize('sensor,topic',[('door','outdoors'),('bed','sleep')])
def test_sensor_observation_not_confirmation(app,sensor,topic):
    s=Browser(app);f=Browser(app,'liisa')
    plan=approve(s,draft(s,kind='plan'))
    body={'sensor':sensor,'window_start':'2026-01-01T00:00:00Z','window_end':'2026-01-01T01:00:00Z','coverage':'incomplete','subject_attribution_checked':True,'events':[{'kind':'enter','at':'2026-01-01T00:01:00Z'},{'kind':'leave','at':'2026-01-01T00:02:00Z'}]}
    record=approve(s,data(s.post('/staff/residents/aino/sensor-observations',body),201))
    p=publish(s,prepare(s));board=data(f.get('/family/residents/aino/board'))
    item=next(i for t in board['tiles'] for i in t['items'] if i['claim_type']=='sensor_observation')
    assert '60 sekuntia' in item['statement'] and 'puutteellinen' in item['statement']
    assert item['topic']==topic and item['status']=='observed'
    action=data(s.get('/staff/residents/aino/actions'))['items'][0]
    ref={'kind':'record','record_id':record['record_id'],'version':1,'segment_id':record['segments'][0]['segment_id']}
    assert s.post('/staff/actions/'+action['action_id']+'/confirm',{'confirmation_ref':ref,'meaning_checked':True},rev=action['revision']).status_code==422
