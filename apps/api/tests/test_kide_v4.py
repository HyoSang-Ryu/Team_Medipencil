from uuid import uuid4
from copy import deepcopy
from conftest import Browser
from medipencil.kide_v4 import AREAS

# Independent fixture, not copied from the provided clinical examples.
TEXT='Synthetic demo resident drank 120 ml. Medication intake is not confirmed.'
def candidate(sleep=6):
 return {'charting':[{'area':AREAS[0],'topic':'fluids','value_fi':'120 ml','value_ko':'수분 120 ml','claim_type':'observation','source_ko':TEXT.split('. ')[0]+'.'}],
 'missing_questions':[{'area':AREAS[2],'topic':'demo','question_ko':'복용을 확인했나요?','question_fi':'Onko ottaminen vahvistettu?','if_unanswered_fi':'ei vahvistettu'}],
 'nursing_note':[{'area':a,'text_fi':'Synteettinen testikirjaus.','text_ko':'합성 시험 기록.'} for a in AREAS],
 'metrics':{'sleep_hours':sleep,'outdoor_minutes':0,'meds':{'taken':[],'unconfirmed':['demo-sensitive']}},
 'family_notices':[{'guardian':'Demo guardian','relation':'lapsi','send':True,'text_fi':'Nesteitä 120 ml.','text_ko':'수분 120 ml.','reason_ko':None},{'guardian':'Other demo','relation':'lapsi','send':False,'text_fi':None,'text_ko':None,'reason_ko':'알림 없음'}],
 'family_filter_excluded':['demo-sensitive']}

def save(staff,day='2026-10-01',sleep=6):
 body={'request_id':str(uuid4()),'transcript':TEXT,'external_synthetic_ack':True,'context':{'date':day,'medications':[{'name':'demo-sensitive','purpose':'demo','sensitive':True}]},'result':candidate(sleep)}
 response=staff.post('/kide/aino/drafts/direct',body)
 assert response.status_code==200,response.text
 return response.json()['data']

def reviewed(d):
 result=deepcopy(d['result']);result['missing_reviewed']=True
 c=result['laheiskortti']['notice_0'];c.update(lahde=TEXT.split('. ')[0]+'.',recipient_id='liisa',scopes=['meals'])
 return {'result':result,'recipients':['liisa'],'checked':True}

def test_v4_confirmation_scope_identity_and_metrics(app):
 s=Browser(app);f=Browser(app,'liisa');other=Browser(app,'mikko');d=save(s);path=f"/kide/aino/drafts/{d['id']}/publish";body=reviewed(d)
 assert d['state']=='draft' and len(d['result']['nursing_note'])==5
 assert f.get('/kide/aino/family').json()['data']['items']==[]
 trend='/kide/aino/trends?start=2026-10-01&end=2026-10-03'
 assert f.get(trend).status_code==403
 assert s.get(trend).json()['data']['days']==[]
 bad=deepcopy(body);bad['result']['missing_reviewed']=False
 assert s.post(path,bad).status_code==422
 bad=deepcopy(body);bad['result']['v4']['metrics']['sleep_hours']=8
 assert s.post(path,bad).status_code==422
 bad=deepcopy(body);bad['result']['laheiskortti']['notice_0']['teksti']='demo-sensitive'
 assert s.post(path,bad).status_code==403
 bad=deepcopy(body);bad['result']['laheiskortti']['notice_0']['recipient_id']='mikko'
 assert s.post(path,bad).status_code==403
 bad=deepcopy(body);bad['result']['laheiskortti']['notice_1']['kasitelty']=True
 assert s.post(path,bad).status_code==422
 assert s.post(path,body).status_code==200
 visible=f.get('/kide/aino/family').json()['data']['items']
 assert len(visible)==1 and visible[0]['cards']['notice_0']['lahde']==''
 assert 'demo-sensitive' not in str(visible) and 'metrics' not in str(visible)
 assert other.get('/kide/aino/family').json()['data']['items']==[]
 for day,h in [('2026-10-02',5.5),('2026-10-03',5)]:
  d2=save(s,day,h);assert s.post(f"/kide/aino/drafts/{d2['id']}/publish",reviewed(d2)).status_code==200
 data=s.get(trend).json()['data'];assert data['sleep_decreasing']
 assert [d['sleep_hours'] for d in data['days']]==[6,5.5,5]
 assert data['days'][0]['fluids_ml'] is None
 assert data['days'][0]['outdoor_minutes']==0
 assert data['days'][0]['meds']=={'taken':0,'delayed':None,'not_taken':None,'unconfirmed':1}
 assert s.post(f"/kide/aino/drafts/{d['id']}/withdraw",{}).status_code==200
 assert len(s.get(trend).json()['data']['days'])==2
 assert not s.get(trend).json()['data']['sleep_decreasing']

def test_v4_context_and_invalid_shape(app):
 s=Browser(app)
 body={'request_id':str(uuid4()),'transcript':TEXT,'external_synthetic_ack':True,'context':{'date':'2024-11-17'},'result':candidate()}
 assert s.post('/kide/aino/drafts/direct',body).status_code==422
 body['context']={'date':'2026-10-01'};body['result']['metrics']['sleep_hours']=-1
 assert s.post('/kide/aino/drafts/direct',body).status_code==422
 body['result']=candidate();body['result']['nursing_note'].pop()
 assert s.post('/kide/aino/drafts/direct',body).status_code==422

def test_v4_missing_source_stays_null():
 from medipencil.kide_v4 import normalize
 raw=candidate();raw['charting'][0]['source_ko']=None
 assert normalize(raw,['daily'])['v4']['charting'][0]['source_ko'] is None
