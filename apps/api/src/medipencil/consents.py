from fastapi import APIRouter,Request
from pydantic import Field
from .common import Input,Fault,envelope,uid,now
from .db import need,many,insert,audit
from .security import session,access,grant,execute,revision
from .domain import scopes,source_ref
from .records import staff
router=APIRouter(prefix='/api/v1')
class Candidate(Input):
    recipient_id:str
    proposed_scopes:list[str]
    utterance_ref:dict
class Confirm(Input):
    recipient_id:str
    confirmed_scopes:list[str]
    expected_consent_version:int
    speaker_and_scope_checked:bool
class Revoke(Input):
    scopes:list[str]
    expected_consent_version:int
    reason_code:str=Field(min_length=1,max_length=100)
class Reject(Input):reason_code:str=Field(min_length=1,max_length=100)

def invalidate_pair(db,s,recipient):
    db.execute('UPDATE publications SET status="invalidated",invalidated_at=?,invalidation_reason="consent_changed",revision=revision+1 WHERE subject_id=? AND recipient_id=? AND status!="invalidated"',(now(),s,recipient))

def consent_dto(db,s,recipient):
    g=grant(db,s,recipient)
    return {'subject_id':s,'recipient_id':recipient,'version':g['version'],'status':g['status'],'scopes':g['scopes']}

def append_grant(db,s,recipient,scope,actor,evidence,candidate=None):
    g=grant(db,s,recipient)
    insert(db,'consent_versions',consent_id=g.get('consent_id','consent-'+uid()),version=g['version']+1,subject_id=s,recipient_id=recipient,status='confirmed' if scope else 'revoked',scopes_json=scope,confirmed_by=actor,confirmed_at=now(),revoked_at=now() if not scope else None,evidence_ref_json=evidence,derived_from_candidate_id=candidate)
    invalidate_pair(db,s,recipient)
    audit(db,actor,'consent.change',s,recipient)

@router.get('/staff/residents/{s}/consents')
def list_consents(s:str,request:Request):
    with request.app.state.store.transaction() as db:
        staff(request,db,s,'can_manage_consent')
        actors=many(db,'SELECT a.actor_id,a.display_name FROM actors a JOIN access_memberships m ON m.actor_id=a.actor_id WHERE m.subject_id=? AND m.active=1 AND a.role="family"',(s,))
        return envelope({'grants':[consent_dto(db,s,a['actor_id'])|{'display_name':a['display_name']} for a in actors],'candidates':many(db,'SELECT * FROM consent_candidates WHERE subject_id=?',(s,)),'history':many(db,'SELECT * FROM consent_versions WHERE subject_id=? ORDER BY recipient_id,version',(s,))})

@router.post('/staff/residents/{s}/consent-candidates',status_code=201)
def candidate(s:str,body:Candidate,request:Request):
    with request.app.state.store.transaction() as db:
        actor=staff(request,db,s,'can_manage_consent');access(db,{'actor_id':body.recipient_id},s)
        if need(db,'SELECT * FROM actors WHERE actor_id=?',(body.recipient_id,))['role']!='family':raise Fault('VALIDATION_FAILED')
        def operation():
            source_ref(db,body.utterance_ref,s);selected=scopes(body.proposed_scopes);id=uid();t=now()
            insert(db,'consent_candidates',candidate_id=id,subject_id=s,recipient_id=body.recipient_id,proposed_scopes_json=selected,utterance_ref_json=body.utterance_ref,disposition='pending',created_at=t,updated_at=t)
            return {'id':id}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:need(db,'SELECT * FROM consent_candidates WHERE candidate_id=?',(ref['id'],))))

@router.post('/staff/consent-candidates/{c}/confirm')
def confirm(c:str,body:Confirm,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');candidate=need(db,'SELECT * FROM consent_candidates WHERE candidate_id=?',(c,));access(db,actor,candidate['subject_id'],'can_manage_consent');access(db,{'actor_id':body.recipient_id},candidate['subject_id'])
        def operation():
            revision(request,candidate)
            if candidate['disposition']!='pending':raise Fault('INVALID_STATE',409)
            selected=scopes(body.confirmed_scopes)
            if not body.speaker_and_scope_checked or body.recipient_id!=candidate['recipient_id'] or not set(selected)<=set(candidate['proposed_scopes']):raise Fault('REVIEW_REQUIRED')
            source_ref(db,candidate['utterance_ref'],candidate['subject_id'])
            g=grant(db,candidate['subject_id'],body.recipient_id)
            if body.expected_consent_version!=g['version']:raise Fault('STALE_CONSENT',409)
            current=g['scopes'] if g['status']=='confirmed' else []
            append_grant(db,candidate['subject_id'],body.recipient_id,sorted(set(current)|set(selected)),actor['actor_id'],candidate['utterance_ref'],c)
            db.execute('UPDATE consent_candidates SET disposition="accepted",reviewed_by=?,reviewed_at=?,revision=revision+1 WHERE candidate_id=?',(actor['actor_id'],now(),c))
            return {'s':candidate['subject_id'],'recipient':body.recipient_id}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:consent_dto(db,ref['s'],ref['recipient'])))

@router.post('/staff/consent-candidates/{c}/reject')
def reject(c:str,body:Reject,request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'staff');candidate=need(db,'SELECT * FROM consent_candidates WHERE candidate_id=?',(c,));access(db,actor,candidate['subject_id'],'can_manage_consent')
        def operation():
            revision(request,candidate)
            if candidate['disposition']!='pending':raise Fault('INVALID_STATE',409)
            db.execute('UPDATE consent_candidates SET disposition="rejected",reviewed_by=?,reviewed_at=?,revision=revision+1 WHERE candidate_id=?',(actor['actor_id'],now(),c))
            return {'id':c}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:need(db,'SELECT * FROM consent_candidates WHERE candidate_id=?',(ref['id'],))))

@router.post('/staff/residents/{s}/consents/{recipient}/revoke')
def revoke(s:str,recipient:str,body:Revoke,request:Request):
    with request.app.state.store.transaction() as db:
        actor=staff(request,db,s,'can_manage_consent');access(db,{'actor_id':recipient},s)
        def operation():
            selected=scopes(body.scopes);g=grant(db,s,recipient)
            if body.expected_consent_version!=g['version']:raise Fault('STALE_CONSENT',409)
            if not set(selected)<=set(g['scopes']):raise Fault('VALIDATION_FAILED')
            append_grant(db,s,recipient,sorted(set(g['scopes'])-set(selected)),actor['actor_id'],{'kind':'revocation','reason_code':body.reason_code})
            return {'s':s,'recipient':recipient}
        return envelope(execute(request,db,actor,body.model_dump(),operation,lambda ref:consent_dto(db,ref['s'],ref['recipient'])))
