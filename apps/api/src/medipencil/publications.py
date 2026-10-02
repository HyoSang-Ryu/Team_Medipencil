from typing import Literal
from fastapi import APIRouter,Request
from pydantic import Field
from .common import Input,Fault,now,uid,envelope
from .db import one,many,need,insert,audit,dump
from .security import session,access,grant,permitted,execute,revision
from .domain import record_ref,source_ref
from .records import staff,manual_job,job_dto
router=APIRouter(prefix='/api/v1')
TOPICS=['meals','medication','movement','outdoors','sleep','care_contact']
class Prepare(Input):
    subject_id:str
    recipient_id:str
    lang:Literal['fi','sv','en']
    expected_content_epoch:int
    expected_consent_version:int
class ItemReview(Input):
    item_id:str
    meaning_checked:bool
    language_checked:bool
    evidence_checked:bool
class Publish(Input):
    reviewed_items:list[ItemReview]
    accepted_answer_candidate_ids:list[str]
    expected_content_epoch:int
    expected_consent_version:int
class Wording(Input):
    item_id:str
    statement:str=Field(min_length=1,max_length=20000)
class Edit(Input): item_edits:list[Wording]
class Confirm(Input):
    confirmation_ref:dict
    meaning_checked:bool


def check_snapshot(db,p):
    resident=need(db,'SELECT * FROM residents WHERE subject_id=?',(p['subject_id'],))
    if resident['content_epoch']!=p['content_epoch']:raise Fault('STALE_EVIDENCE',409)
    g=grant(db,p['subject_id'],p['recipient_id'])
    if g['version']!=p['consent_version']:raise Fault('STALE_CONSENT',409)
    access(db,{'actor_id':p['recipient_id']},p['subject_id'])
    for item in p['items']:
        if not permitted(db,p['subject_id'],p['recipient_id'],item['required_scopes']):raise Fault('STALE_CONSENT',409)
        for ref in item['evidence_refs']:record_ref(db,ref,p['subject_id'])

def latest(db,s,recipient,lang):
    p=one(db,'SELECT * FROM publications WHERE subject_id=? AND recipient_id=? AND lang=? AND status!="draft" ORDER BY created_at DESC,rowid DESC LIMIT 1',(s,recipient,lang))
    if not p or p['status']!='published':return None
    try:check_snapshot(db,p)
    except Fault:return None
    return p

@router.get('/staff/residents/{s}/publication-context')
def context(s:str,recipient_id:str,request:Request):
    with request.app.state.store.transaction() as db:
        staff(request,db,s);access(db,{'actor_id':recipient_id},s)
        return envelope({'content_epoch':need(db,'SELECT * FROM residents WHERE subject_id=?',(s,))['content_epoch'],'consent_version':grant(db,s,recipient_id)['version']})

@router.post('/staff/publications/prepare',status_code=202)
def prepare(body:Prepare,request:Request):
    with request.app.state.store.transaction() as db:
        actor=staff(request,db,body.subject_id);access(db,{'actor_id':body.recipient_id},body.subject_id)
        def operation():
            if body.lang!='fi':raise Fault('LANGUAGE_UNAVAILABLE',409)
            resident=need(db,'SELECT * FROM residents WHERE subject_id=?',(body.subject_id,))
            g=grant(db,body.subject_id,body.recipient_id)
            if body.expected_content_epoch!=resident['content_epoch']:raise Fault('STALE_EVIDENCE',409)
            if body.expected_consent_version!=g['version']:raise Fault('STALE_CONSENT',409)
            items=[];by_segment={}
            for r in many(db,'SELECT * FROM record_versions WHERE subject_id=? AND status="approved" ORDER BY approved_at',(body.subject_id,)):
                for segment in r['segments']:
                    topic=next((t for t in TOPICS if t in segment['required_scopes']),'care_contact')
                    required=sorted(set(segment['required_scopes'])|{topic})
                    if not permitted(db,body.subject_id,body.recipient_id,required):continue
                    ref={'kind':'record','record_id':r['record_id'],'version':r['version'],'segment_id':segment['segment_id']}
                    record_ref(db,ref,body.subject_id)
                    id=uid();by_segment[(r['record_id'],r['version'],segment['segment_id'])]=id
                    claim='plan' if segment['type']=='plan' else 'resident_statement' if segment['speaker']=='resident' else 'staff_observation'
                    source=need(db,'SELECT * FROM source_events WHERE source_id=? AND version=?',(segment['evidence_refs'][0]['source_id'],segment['evidence_refs'][0]['source_version']))
                    items.append({'item_id':id,'topic':topic,'statement':segment['text'],'claim_type':claim,'status':'confirmed','action_status':'planned' if claim=='plan' else None,'observed_at':source['occurred_at'],'required_scopes':required,'evidence_refs':[ref],'meaning_checked':False,'language_checked':False})
            if not items:raise Fault('EVIDENCE_REQUIRED')
            bindings=[]
            for c in many(db,'SELECT c.* FROM answer_candidates c JOIN family_questions q ON q.question_id=c.question_id WHERE q.subject_id=? AND q.recipient_id=? AND c.review_status="accepted"',(body.subject_id,body.recipient_id)):
                ids=[by_segment.get((c['record_id'],c['record_version'],sid)) for sid in c['answer_segment_ids']]
                if ids and all(ids):bindings.append({'question_id':c['question_id'],'candidate_id':c['candidate_id'],'item_ids':ids})
            id=uid();t=now()
            insert(db,'publications',publication_id=id,subject_id=body.subject_id,recipient_id=body.recipient_id,lang=body.lang,status='draft',consent_version=g['version'],content_epoch=resident['content_epoch'],items_json=items,answer_bindings_json=bindings,input_refs_json=[ref for item in items for ref in item['evidence_refs']],generation_meta_json={'provider_id':'manual','input_mode':'text','execution_mode':'LIVE','ai_executed':False,'stt':'skipped','origin':'TEAM_SYNTHETIC','language_review_status':'pending'},created_at=t,updated_at=t)
            return {'id':manual_job(db,body.subject_id,id,'render',{'kind':'publication','id':id})}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:job_dto(db,ref['id'])))

@router.get('/staff/publications/{p}')
def get_pub(p:str,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');pub=need(db,'SELECT * FROM publications WHERE publication_id=?',(p,));access(db,actor,pub['subject_id'],'can_review')
        return envelope(pub)

@router.patch('/staff/publications/{p}/draft')
def edit(p:str,body:Edit,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');pub=need(db,'SELECT * FROM publications WHERE publication_id=?',(p,));access(db,actor,pub['subject_id'],'can_review')
        def operation():
            revision(request,pub);check_snapshot(db,pub)
            if pub['status']!='draft':raise Fault('INVALID_STATE',409)
            edits={e.item_id:e.statement for e in body.item_edits}
            if not set(edits)<={i['item_id'] for i in pub['items']}:raise Fault('VALIDATION_FAILED')
            for item in pub['items']:
                if item['item_id'] in edits:
                    segments=[record_ref(db,r,pub['subject_id']) for r in item['evidence_refs']]
                    if not any(edits[item['item_id']] in s['text'] for s in segments):raise Fault('EVIDENCE_REQUIRED')
                    item['statement']=edits[item['item_id']];item['meaning_checked']=False;item['language_checked']=False
            db.execute('UPDATE publications SET items_json=?,revision=revision+1,updated_at=? WHERE publication_id=?',(dump(pub['items']),now(),p))
            return {'id':p}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:need(db,'SELECT * FROM publications WHERE publication_id=?',(ref['id'],))))

@router.post('/staff/publications/{p}/publish')
def publish(p:str,body:Publish,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');pub=need(db,'SELECT * FROM publications WHERE publication_id=?',(p,));access(db,actor,pub['subject_id'],'can_review')
        def operation():
            revision(request,pub)
            if pub['status']!='draft':raise Fault('INVALID_STATE',409)
            if body.expected_content_epoch!=pub['content_epoch']:raise Fault('STALE_EVIDENCE',409)
            if body.expected_consent_version!=pub['consent_version']:raise Fault('STALE_CONSENT',409)
            check_snapshot(db,pub)
            reviews={r.item_id:r for r in body.reviewed_items}
            if len(reviews)!=len(body.reviewed_items) or set(reviews)!={i['item_id'] for i in pub['items']} or not all(r.meaning_checked and r.language_checked and r.evidence_checked for r in reviews.values()):raise Fault('REVIEW_REQUIRED')
            selected=set(body.accepted_answer_candidate_ids)
            if not selected<={b['candidate_id'] for b in pub['answer_bindings']}:raise Fault('EVIDENCE_REQUIRED')
            bindings=[b for b in pub['answer_bindings'] if b['candidate_id'] in selected]
            for item in pub['items']:item.update(meaning_checked=True,language_checked=True)
            db.execute('UPDATE publications SET status="published",reviewed_by=?,published_at=?,updated_at=?,revision=revision+1,items_json=?,answer_bindings_json=? WHERE publication_id=?',(actor['actor_id'],now(),now(),dump(pub['items']),dump(bindings),p))
            for b in bindings:
                q=need(db,'SELECT * FROM family_questions WHERE question_id=?',(b['question_id'],))
                if q['recipient_id']!=pub['recipient_id'] or q['subject_id']!=pub['subject_id']:raise Fault('SUBJECT_MISMATCH',409)
                db.execute('UPDATE family_questions SET status="answered",active_publication_id=?,revision=revision+1,updated_at=? WHERE question_id=?',(p,now(),q['question_id']))
            audit(db,actor['actor_id'],'publication.publish',pub['subject_id'],p)
            return {'id':p}
        def render(ref):
            current=need(db,'SELECT * FROM publications WHERE publication_id=?',(ref['id'],));check_snapshot(db,current)
            if current['status']!='published':raise Fault('STALE_EVIDENCE',409)
            return current
        return envelope(execute(request,db,actor,body.model_dump(),operation,render))

def public_item(item):
    return {k:item[k] for k in ['item_id','topic','statement','status','claim_type','observed_at','action_status']}|{'evidence_handle':item['item_id']}

@router.get('/family/residents/{s}/board')
def board(s:str,request:Request,lang:Literal['fi','sv','en']='fi'):
    if set(request.query_params)-{'lang'}:raise Fault('VALIDATION_FAILED')
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'family');membership=access(db,actor,s)
        resident=need(db,'SELECT * FROM residents WHERE subject_id=?',(s,));p=latest(db,s,actor['actor_id'],lang)
        tiles=[]
        for topic in TOPICS:
            allowed=permitted(db,s,actor['actor_id'],[topic])
            items=[public_item(i) for i in p['items'] if i['topic']==topic] if p and allowed else []
            tiles.append({'topic':topic,'display_state':'not_shared' if not allowed else 'available' if items else 'awaiting_review' if not p else 'no_record','items':items})
        return envelope({'subject':{'subject_id':s,'display_name':resident['display_name']},'viewer':{'actor_id':actor['actor_id'],'display_name':actor['display_name']},'lang':lang,'display_timezone':'Europe/Helsinki','board_state':'ready' if p else 'awaiting_review','language_state':'available' if lang=='fi' else 'unavailable','tiles':tiles,'answers':[{'question_id':b['question_id'],'item_ids':b['item_ids']} for b in p['answer_bindings']] if p else [],'publication_id':p['publication_id'] if p else None,'published_at':p['published_at'] if p else None,'can_ask':bool(membership['can_ask']),'execution':p['generation_meta'] if p else {'ai_executed':False,'origin':'TEAM_SYNTHETIC'}})

@router.get('/family/items/{item}/evidence')
def evidence(item:str,request:Request):
    if request.query_params:raise Fault('VALIDATION_FAILED')
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'family')
        for member in many(db,'SELECT * FROM access_memberships WHERE actor_id=? AND active=1',(actor['actor_id'],)):
            for lang in ['fi','sv','en']:
                pub=latest(db,member['subject_id'],actor['actor_id'],lang)
                if not pub:continue
                for i in pub['items']:
                    if i['item_id']==item:
                        return envelope({'item_id':item,'source_label':'Hyväksytty kirjaus · suora syöttö','occurred_at':i['observed_at'],'excerpt':i['statement'],'evidence_state':'valid'})
        raise Fault('RESOURCE_NOT_FOUND',404)

@router.post('/staff/actions/{a}/confirm')
def confirm(a:str,body:Confirm,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');action=need(db,'SELECT * FROM care_actions WHERE action_id=?',(a,));access(db,actor,action['subject_id'],'can_review')
        def operation():
            revision(request,action)
            s=record_ref(db,body.confirmation_ref,action['subject_id'])
            if not body.meaning_checked or s['type']=='plan' or body.confirmation_ref==action['planned_in']:raise Fault('REVIEW_REQUIRED')
            db.execute('UPDATE care_actions SET status="confirmed",confirmed_in_json=?,review_required=0,revision=revision+1,updated_at=? WHERE action_id=?',(dump(body.confirmation_ref),now(),a))
            audit(db,actor['actor_id'],'action.confirm',action['subject_id'],a)
            return {'id':a}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:need(db,'SELECT * FROM care_actions WHERE action_id=?',(ref['id'],))))
