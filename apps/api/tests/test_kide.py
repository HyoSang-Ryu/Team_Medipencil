from uuid import uuid4
from unittest.mock import Mock
from conftest import Browser
from medipencil.kide import NOTES,CARDS,clean_transcript
from test_provided_workflow import setup

TEXT='Hän söi puolet aamiaisesta. Ulkoilua suunnitellaan.'
def output():
 return {'nursing_note':{k:TEXT if i==0 else None for i,k in enumerate(NOTES)},'laheiskortti':{k:{'teksti':'Aamiaisella hän söi puolet.','lahde':'Hän söi puolet aamiaisesta.','kasitelty':i==0} for i,k in enumerate(CARDS)},'huomiot_hoitajalle':['Tarkista tiedot.']}
def make(staff,subject='aino',id=None):return staff.post(f'/kide/{subject}/drafts',{'request_id':id or str(uuid4()),'transcript':TEXT+' KIDE, 정리해줘','external_synthetic_ack':True})

def test_auto_draft_review_publish_scope_and_withdraw(app,monkeypatch):
 mock=Mock(return_value=output());monkeypatch.setattr('medipencil.kide.generate',mock)
 s=Browser(app);f=Browser(app,'liisa');other=Browser(app,'mikko')
 id=str(uuid4());d=make(s,id=id).json()['data'];assert d['state']=='draft' and d['transcript']==TEXT
 assert make(s,id=id).status_code==200 and mock.call_count==1
 assert f.get('/kide/aino/drafts').status_code==403
 assert f.get('/kide/aino/family').json()['data']['items']==[]
 assert f.post('/kide/aino/drafts',{'request_id':str(uuid4()),'transcript':TEXT,'external_synthetic_ack':True}).status_code==403
 p={'result':d['result'],'recipients':['liisa'],'checked':False}
 path=f'/kide/aino/drafts/{id}/publish'
 assert s.post(path,p).status_code==422
 p['checked']=True;p['result']['laheiskortti'][CARDS[0]]['lahde']='Invented evidence'
 assert s.post(path,p).status_code==422
 p['result']['laheiskortti'][CARDS[0]]['lahde']='Hän söi puolet aamiaisesta.'
 assert s.post(path,{**p,'recipients':['mikko']}).status_code==403
 assert s.post(path,p).status_code==200
 assert s.post(path,p).status_code==200
 visible=f.get('/kide/aino/family').json()['data']['items'];assert len(visible)==1 and len(visible[0]['cards'])==1
 assert 'transcript' not in str(visible) and 'nursing_note' not in str(visible)
 assert other.get('/kide/aino/family').json()['data']['items']==[]
 assert s.post(f'/kide/aino/drafts/{id}/withdraw',{}).status_code==200
 assert f.get('/kide/aino/family').json()['data']['items']==[]

def test_failed_provider_retry_and_no_ack(app,monkeypatch):
 from medipencil.common import Fault
 mock=Mock(side_effect=Fault('KIDE_GENERATION_FAILED',502));monkeypatch.setattr('medipencil.kide.generate',mock)
 s=Browser(app);id=str(uuid4())
 assert s.post('/kide/aino/drafts',{'request_id':id,'transcript':TEXT,'external_synthetic_ack':False}).status_code==422
 assert mock.call_count==0
 assert make(s,id=id).status_code==502
 d=s.get('/kide/aino/drafts').json()['data']['items'][0];assert d['state']=='failed' and d['transcript']==TEXT
 mock.side_effect=None;mock.return_value=output()
 assert make(s,id=id).json()['data']['state']=='draft'
 assert clean_transcript('KIDE, 정리해줘')==''
 assert clean_transcript('He said summarize yesterday.')=='He said summarize yesterday.'

def test_supplied_card_scopes_and_policy_revision(app,tmp_path,monkeypatch):
 a,b=setup(app,tmp_path);s=Browser(app);fa=Browser(app,a['actor_id']);fb=Browser(app,b['actor_id'])
 mock=Mock(return_value=output());monkeypatch.setattr('medipencil.kide.generate',mock)
 d=make(s,'A').json()['data'];p={'result':d['result'],'recipients':[a['actor_id']],'checked':True};path=f"/kide/A/drafts/{d['id']}/publish"
 assert s.post(path,p).status_code==403
 p['result']['laheiskortti'][CARDS[0]]['scopes']=['daily']
 assert s.post(path,p).status_code==200
 assert len(fa.get('/kide/A/family').json()['data']['items'])==1
 assert fb.get('/kide/A/family').status_code==403
 assert s.client.put('/api/v1/provided/A/sharing',json={'actor_id':a['actor_id'],'groups':[],'revision':0}).status_code==200
 assert fa.get('/kide/A/family').json()['data']['items']==[]
 assert s.client.put('/api/v1/provided/A/sharing',json={'actor_id':a['actor_id'],'groups':['daily'],'revision':1}).status_code==200
 assert fa.get('/kide/A/family').json()['data']['items']==[]
 mock.assert_called_once_with(TEXT,app.state.settings)
