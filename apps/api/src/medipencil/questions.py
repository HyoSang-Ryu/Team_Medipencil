from fastapi import APIRouter,Request
from pydantic import Field
from .common import Input,Fault,uid,now,envelope
from .db import one,many,need,insert,audit
from .security import session,access,execute,revision
from .domain import timestamp
from .pagination import page
from .dto import Response,QuestionDTO,Page
router=APIRouter(prefix='/api/v1')
class QuestionCreate(Input):
    text:str=Field(min_length=1,max_length=2000)
    topic_hint:str|None=None
class Schedule(Input):
    assigned_to:str
    review_due:str
class Reason(Input):
    reason_code:str=Field(min_length=1,max_length=100)

def question_dto(db,q,actor):
    result={k:q[k] for k in ('question_id','subject_id','text','status','review_due','created_at','updated_at','revision')}
    if q['status']=='scheduled' and q['review_due'] and q['review_due']<now(): result['status']='unanswered'
    assigned=one(db,'SELECT display_name FROM actors WHERE actor_id=?',(q['assigned_to'],)) if q['assigned_to'] else None
    result.update(answer_available=False,display_state=result['status'],assigned_to_display=assigned['display_name'] if assigned else None)
    author=need(db,'SELECT display_name FROM actors WHERE actor_id=?',(q['recipient_id'],))
    result.update(author_display=author['display_name'],reply=None)
    if q['status']=='answered':
        from .publications import latest
        publication=latest(db,q['subject_id'],q['recipient_id'],'fi')
        available=bool(publication and any(b['question_id']==q['question_id'] for b in publication['answer_bindings']))
        result.update(answer_available=available,display_state='answered' if available else 'access_changed')
        if available:
            ids={id for binding in publication['answer_bindings'] if binding['question_id']==q['question_id'] for id in binding['item_ids']}
            author=need(db,'SELECT display_name FROM actors WHERE actor_id=?',(publication['reviewed_by'],))
            result['reply']={'author_display':author['display_name'],'published_at':publication['published_at'],
                             'items':[{k:item[k] for k in ('statement','claim_type')} for item in publication['items'] if item['item_id'] in ids]}
    return result

@router.post('/family/residents/{s}/questions',status_code=201,response_model=Response[QuestionDTO])
def create(s:str,body:QuestionCreate,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'family');access(db,actor,s,'can_ask')
        def operation():
            recent=db.execute('SELECT count(*) FROM family_questions WHERE recipient_id=? AND created_at>?',(actor['actor_id'],now()[:16])).fetchone()[0]
            if recent>=20: raise Fault('RATE_LIMITED',429)
            id=uid();t=now()
            insert(db,'family_questions',question_id=id,subject_id=s,recipient_id=actor['actor_id'],text=body.text,status='received',created_at=t,updated_at=t)
            audit(db,actor['actor_id'],'question.create',s,id)
            return {'id':id}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:question_dto(db,need(db,'SELECT * FROM family_questions WHERE question_id=? AND recipient_id=?',(ref['id'],actor['actor_id'])),actor)))

@router.get('/family/residents/{s}/questions',response_model=Response[Page[QuestionDTO]])
def questions(s:str,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'family');access(db,actor,s)
        rows=many(db,'SELECT * FROM family_questions WHERE subject_id=? AND recipient_id=? ORDER BY created_at DESC,question_id DESC',(s,actor['actor_id']))
        return envelope(page(request,[question_dto(db,q,actor) for q in rows],actor['actor_id']+':'+s+':questions'))

@router.get('/staff/question-queue')
def queue(request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff')
        rows=many(db,'SELECT q.* FROM family_questions q JOIN residents r ON q.subject_id=r.subject_id JOIN access_memberships m ON m.subject_id=q.subject_id WHERE m.actor_id=? AND m.can_review=1 AND m.active=1 ORDER BY r.care_order,q.created_at',(actor['actor_id'],))
        return envelope({'items':[question_dto(db,q,actor)|{'recipient_id':q['recipient_id']} for q in rows],'next_cursor':None})

@router.post('/staff/questions/{q}/schedule')
def schedule(q:str,body:Schedule,request:Request):
    return change(q,body,request,True)

@router.post('/staff/questions/{q}/mark-unanswered')
def unanswered(q:str,body:Reason,request:Request):
    return change(q,body,request,False)

def change(id,body,request,scheduling):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');q=need(db,'SELECT * FROM family_questions WHERE question_id=?',(id,));access(db,actor,q['subject_id'],'can_review')
        def operation():
            revision(request,q)
            if q['status']=='answered':raise Fault('INVALID_STATE',409)
            if scheduling:
                access(db,{'actor_id':body.assigned_to},q['subject_id'],'can_review')
                due=timestamp(body.review_due,future=True)
                db.execute('UPDATE family_questions SET assigned_to=?,review_due=?,status="scheduled",revision=revision+1,updated_at=? WHERE question_id=?',(body.assigned_to,due,now(),id))
            else: db.execute('UPDATE family_questions SET status="unanswered",status_reason=?,revision=revision+1,updated_at=? WHERE question_id=?',(body.reason_code,now(),id))
            audit(db,actor['actor_id'],'question.schedule' if scheduling else 'question.unanswered',q['subject_id'],id)
            return {'id':id}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:question_dto(db,need(db,'SELECT * FROM family_questions WHERE question_id=?',(ref['id'],)),actor)))
