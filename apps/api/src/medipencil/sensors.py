from typing import Literal
from fastapi import APIRouter,Request
from pydantic import Field
from .common import Input,Fault,envelope,uid,now
from .db import insert,need
from .records import staff,record_dto
from .security import execute
from .aggregation import intervals
router=APIRouter(prefix='/api/v1')
class Event(Input):
    kind:Literal['enter','leave']
    at:str
class Sensor(Input):
    sensor:Literal['door','bed']
    window_start:str
    window_end:str
    coverage:Literal['complete','incomplete']
    subject_attribution_checked:bool
    events:list[Event]=Field(max_length=1000)

@router.post('/staff/residents/{s}/sensor-observations',status_code=201)
def sensor(s:str,body:Sensor,request:Request):
    with request.app.state.store.transaction() as db:
        actor=staff(request,db,s)
        def operation():
            if not body.subject_attribution_checked:raise Fault('REVIEW_REQUIRED')
            result=intervals([e.model_dump() for e in body.events],body.window_start,body.window_end,body.coverage)
            topic='outdoors' if body.sensor=='door' else 'sleep'
            text=('Ovihavainto' if body.sensor=='door' else 'Vuoteessa havaittu aika')+f": {int(result['seconds'])} sekuntia."
            if result['coverage_state']!='complete':text+=' Aineisto on puutteellinen; koko jakson tilaa ei voida päätellä.'
            id=uid();r=uid();segment=uid();t=now()
            payload={'text':text,'speaker':'unknown','type':'observation','required_scopes':[topic],'aggregation':result,'events':[e.model_dump() for e in body.events],'subject_attribution':'staff_checked_synthetic'}
            insert(db,'source_events',source_id=id,version=1,subject_id=s,source_type='sensor_aggregate',occurred_at=result['window_end'],recorded_at=t,data_origin='TEAM_SYNTHETIC',integration_mode='MOCK_INTEGRATION',payload_json=payload)
            insert(db,'record_versions',record_id=r,version=1,subject_id=s,status='draft',segments_json=[{'segment_id':segment,'text':text,'speaker':'unknown','type':'observation','required_scopes':[topic],'evidence_refs':[{'kind':'source','source_id':id,'source_version':1}]}],created_at=t,updated_at=t)
            return {'id':r,'version':1}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:record_dto(db,ref['id'],ref['version'])))
