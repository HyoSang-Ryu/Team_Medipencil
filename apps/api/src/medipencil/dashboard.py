"""Counts of currently valid information, never clinical scores or completion rates."""
from datetime import datetime,timedelta
from zoneinfo import ZoneInfo
from fastapi import APIRouter,Request
from .common import Fault,envelope
from .db import many,need
from .domain import record_ref
from .security import session,access,permitted
from .publications import TOPICS,latest

router=APIRouter(prefix='/api/v1')
ZONE=ZoneInfo('Europe/Helsinki')


def summarize(items,allowed,today):
    dates=[(today-timedelta(days=n)).isoformat() for n in range(6,-1,-1)]
    counts={topic:[0]*7 for topic in TOPICS}
    for item in items:
        topic=item['topic']
        if topic not in counts or topic not in allowed:continue
        day=datetime.fromisoformat(item['observed_at'].replace('Z','+00:00')).astimezone(ZONE).date().isoformat()
        if day in dates:counts[topic][dates.index(day)]+=1
    return {'dates':dates,'timezone':'Europe/Helsinki','metric':'valid_information_count','topics':[
        {'topic':t,'shared':t in allowed,'total':sum(counts[t]) if t in allowed else None,
         'daily':counts[t] if t in allowed else [None]*7} for t in TOPICS]}


@router.get('/family/residents/{s}/dashboard')
@router.get('/staff/residents/{s}/dashboard')
def dashboard(s:str,request:Request):
    if request.query_params:raise Fault('VALIDATION_FAILED')
    role='family' if '/family/' in request.url.path else 'staff'
    with request.app.state.store.transaction() as db:
        actor=session(request,db,role);access(db,actor,s,'can_review' if role=='staff' else None)
        items=[];allowed=set(TOPICS)
        if role=='family':
            allowed={t for t in TOPICS if permitted(db,s,actor['actor_id'],[t])}
            pub=latest(db,s,actor['actor_id'],'fi')
            items=pub['items'] if pub else []
        else:
            for record in many(db,'SELECT * FROM record_versions WHERE subject_id=? AND status="approved"',(s,)):
                for segment in record['segments']:
                    ref={'record_id':record['record_id'],'version':record['version'],'segment_id':segment['segment_id']}
                    try:record_ref(db,ref,s)
                    except Fault:continue
                    source=need(db,'SELECT * FROM source_events WHERE source_id=? AND version=?',(segment['evidence_refs'][0]['source_id'],segment['evidence_refs'][0]['source_version']))
                    items.append({'topic':next((t for t in TOPICS if t in segment['required_scopes']),'care_contact'),'observed_at':source['occurred_at']})
        result=summarize(items,allowed,datetime.now(ZONE).date())
        return envelope({**result,'basis':'current_publication' if role=='family' else 'approved_records','ai_executed':False})
