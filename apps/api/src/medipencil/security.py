import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from .common import Fault, now
from .db import one, need, insert, dump

def digest(secret, value): return hmac.new(secret.encode(), value.encode(), hashlib.sha256).hexdigest()

def reviewer(request):
    settings=request.app.state.settings
    if not settings.shared_review or settings.public_review: return None
    supplied=request.headers.get('x-medipencil-proxy-key','')
    identity=request.headers.get('x-medipencil-reviewer','')
    if not hmac.compare_digest(supplied.encode(), settings.proxy_secret.encode()) or identity not in settings.reviewers:
        raise Fault('SESSION_REQUIRED',401)
    return identity

def allowed_actor(request, actor_id):
    if request.app.state.settings.public_review and actor_id not in ('staff','liisa','mikko'):
        raise Fault('ROLE_FORBIDDEN',403)
    identity=reviewer(request)
    if identity is not None and actor_id not in request.app.state.settings.reviewers[identity]:
        raise Fault('ROLE_FORBIDDEN',403)

def session_digest(request, token):
    identity=reviewer(request)
    value=token if identity is None else dump([identity, token])
    return digest(request.app.state.settings.secret, value)

def pages_request(request):
    allowed=request.app.state.settings.pages_origin
    return bool(allowed and request.headers.get('origin') == allowed)

def session_token(request):
    authorization=request.headers.get('authorization', '')
    if authorization:
        if not pages_request(request) or not authorization.startswith('Bearer '):
            raise Fault('SESSION_REQUIRED',401)
        return authorization[7:]
    # The cross-site frontend must use an in-memory bearer, not third-party cookies.
    if pages_request(request):return ''
    return request.cookies.get('mp_session','')

def origin(request):
    if request.headers.get('origin') != request.app.state.settings.origin and not pages_request(request):
        raise Fault('CSRF_INVALID',403)

def session(request, db, role=None):
    token=session_token(request)
    secret=request.app.state.settings.secret
    row=one(db,'SELECT s.*,a.role,a.display_name FROM demo_sessions s JOIN actors a ON a.actor_id=s.actor_id WHERE session_hash=? AND a.active=1',(session_digest(request,token),))
    if not row or row['expires_at']<=now(): raise Fault('SESSION_REQUIRED',401)
    allowed_actor(request,row['actor_id'])
    if role and row['role']!=role: raise Fault('ROLE_FORBIDDEN',403)
    if request.method not in ('GET','HEAD'):
        origin(request)
        if not hmac.compare_digest(digest(secret,request.headers.get('x-csrf-token','')),row['csrf_hash']): raise Fault('CSRF_INVALID',403)
    return row

def access(db, actor, subject, permission=None):
    row=need(db,'SELECT * FROM access_memberships WHERE actor_id=? AND subject_id=? AND active=1',(actor['actor_id'],subject))
    if permission and not row[permission]: raise Fault('ROLE_FORBIDDEN',403)
    return row

def grant(db, subject, recipient):
    row=one(db,'SELECT * FROM consent_versions WHERE subject_id=? AND recipient_id=? ORDER BY version DESC LIMIT 1',(subject,recipient))
    return row or {'version':0,'scopes':[],'status':'revoked'}

def permitted(db,subject,recipient,required):
    g=grant(db,subject,recipient)
    return g['status']=='confirmed' and set(required)<=set(g['scopes'])

def revision(request, obj):
    value=request.headers.get('if-match')
    if value is None: raise Fault('PRECONDITION_REQUIRED',428)
    if value != '"'+str(obj['revision'])+'"': raise Fault('REVISION_CONFLICT',412)

def execute(request, db, actor, payload, operation, render):
    # Called only after current role and subject access checks.
    key=request.headers.get('idempotency-key','')
    if not key or len(key)>128: raise Fault('VALIDATION_FAILED')
    route=request.method+' '+request.url.path
    hashed=digest(request.app.state.settings.secret,dump(payload))
    old=one(db,'SELECT * FROM idempotency_keys WHERE actor_id=? AND route_key=? AND request_key=?',(actor['actor_id'],route,key))
    if old:
        if old['request_digest']!=hashed: raise Fault('IDEMPOTENCY_CONFLICT',409)
        result=render(old['object_ref'])
        if isinstance(result,dict) and 'execution' in result:
            result['execution']={'execution_mode':'REPLAY','original':result['execution'],'ai_executed':False}
        return result
    ref=operation()
    insert(db,'idempotency_keys',actor_id=actor['actor_id'],route_key=route,request_key=key,request_digest=hashed,object_ref_json=ref,result_status=200,state='complete',expires_at=(datetime.now(timezone.utc)+timedelta(days=1)).isoformat())
    return render(ref)
