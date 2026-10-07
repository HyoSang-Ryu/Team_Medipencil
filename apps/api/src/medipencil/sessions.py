import secrets
from datetime import datetime,timedelta,timezone
from fastapi import APIRouter,Request,Response
from .common import Input,Fault,envelope
from .db import one,insert,many
from .security import origin,digest,session,grant,access,allowed_actor,session_digest,pages_request,session_token
router=APIRouter(prefix='/api/v1')
class Login(Input): demo_actor_id: str

@router.post('/demo/session',status_code=201)
def login(body:Login,request:Request,response:Response):
    origin(request)
    allowed_actor(request,body.demo_actor_id)
    secret=request.app.state.settings.secret
    with request.app.state.store.transaction() as db:
        actor=one(db,'SELECT * FROM actors WHERE actor_id=? AND active=1',(body.demo_actor_id,))
        if not actor: raise Fault('ROLE_FORBIDDEN',403)
        db.execute('DELETE FROM demo_sessions WHERE session_hash=?',(session_digest(request,session_token(request)),))
        token=secrets.token_urlsafe(32); csrf=digest(secret,'csrf:'+token)
        insert(db,'demo_sessions',session_hash=session_digest(request,token),actor_id=actor['actor_id'],csrf_hash=digest(secret,csrf),expires_at=(datetime.now(timezone.utc)+timedelta(hours=2)).isoformat())
        if not pages_request(request):response.set_cookie('mp_session',token,httponly=True,samesite='strict',max_age=7200,secure=request.app.state.settings.shared_review,path=request.app.state.settings.cookie_path)
        return envelope({**actor,**({'access_token':token} if pages_request(request) else {}),'csrf_token':csrf,'locale':'fi','authentication':'PUBLIC_SYNTHETIC_POC' if request.app.state.settings.public_review else 'AUTHENTICATED_SYNTHETIC_REVIEW' if request.app.state.settings.shared_review else 'LOCAL_DEMO_ONLY'})

@router.get('/session')
def who(request:Request):
    with request.app.state.store.transaction() as db:
        actor=session(request,db)
        return envelope({k:actor[k] for k in ['actor_id','role','display_name']} | {'locale':'fi','csrf_token':digest(request.app.state.settings.secret,'csrf:'+session_token(request))})

@router.delete('/demo/session',status_code=204)
def logout(request:Request,response:Response):
    with request.app.state.store.transaction() as db:
        actor=session(request,db)
        db.execute('DELETE FROM demo_sessions WHERE session_hash=?',(actor['session_hash'],))
        response.delete_cookie('mp_session',path=request.app.state.settings.cookie_path,secure=request.app.state.settings.shared_review,httponly=True,samesite='strict')

@router.get('/family/residents')
@router.get('/staff/residents')
def residents(request:Request):
    role='family' if '/family/' in request.url.path else 'staff'
    with request.app.state.store.transaction() as db:
        actor=session(request,db,role)
        permission='can_ask' if role=='family' else 'can_review'
        return envelope({'items':many(db,f'SELECT r.subject_id,r.display_name,r.care_order FROM residents r JOIN access_memberships m ON r.subject_id=m.subject_id WHERE m.actor_id=? AND m.active=1 AND m.{permission}=1 ORDER BY r.care_order',(actor['actor_id'],)),'next_cursor':None})

@router.get('/family/residents/{s}/sharing')
def sharing(s:str,request:Request):
    if request.query_params: raise Fault('VALIDATION_FAILED')
    with request.app.state.store.transaction() as db:
        actor=session(request,db,'family'); access(db,actor,s)
        g=grant(db,s,actor['actor_id'])
        return envelope({'version':g['version'],'scopes':g['scopes'] if g['status']=='confirmed' else []})
