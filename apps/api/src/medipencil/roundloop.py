"""Opt-in external live STT; credentials never enter browser responses."""
import asyncio
import json
import secrets
import time
from pathlib import Path
from urllib.parse import urlsplit,urlencode
from fastapi import APIRouter,Request,WebSocket
from websockets.asyncio.client import connect
from .common import Input,Fault,envelope
from .security import session,access
router=APIRouter(prefix='/api/v1/staff/roundloop')

def config(settings):
    if settings.shared_review or settings.poc_mode:return None
    p=Path.home()/'.config/medipencil/roundloop.json'
    if not p.is_file():return None
    try:
        c=json.loads(p.read_text());u=urlsplit(c.get('base_url',''))
    except (OSError,ValueError,AttributeError,TypeError):return None
    if u.scheme!='https' or not u.hostname or u.username or u.password or u.query or u.fragment or u.path not in ('','/') or not c.get('api_key'):return None
    return c

def authorized(request,subject):
    if not config(request.app.state.settings):raise Fault('PROVIDER_NOT_CONFIGURED',503)
    if subject in ('A','B'):
        from .provided_workflow import auth
        a,_=auth(request,subject,True)
    else:
        with request.app.state.store.transaction() as db:
            a=session(request,db,'staff');access(db,a,subject,'can_review')
    return a

@router.get('/status')
def status(request:Request):
    with request.app.state.store.transaction() as db:session(request,db,'staff')
    return envelope({'configured':bool(config(request.app.state.settings)),'provider':'KaiLab Round Loop','external':True,'languages':['ko','en','fi'],'language_support':'provider_reported'})
class Start(Input):
    subject:str
    external_synthetic_ack:bool
@router.post('/sessions')
def issue(body:Start,request:Request):
    a=authorized(request,body.subject)
    if not body.external_synthetic_ack:raise Fault('REVIEW_REQUIRED')
    tickets=request.app.state.roundloop_tickets
    for key in list(tickets):
        if tickets[key]['expires']<time.monotonic() or tickets[key]['actor']==a['actor_id']:tickets.pop(key)
    if len(tickets)>=10:raise Fault('PROVIDER_BUSY',503)
    token=secrets.token_urlsafe(32)
    tickets[token]={'actor':a['actor_id'],'session':a['session_hash'],'expires':time.monotonic()+30,'subject':body.subject}
    return envelope({'path':'/api/v1/staff/roundloop/stream/'+token,'expires_in':30})

def clean_message(raw):
    if not isinstance(raw,str) or len(raw)>200000:raise ValueError('invalid frame')
    m=json.loads(raw);kind=m.get('type')
    if kind in ('ready','done'):return {'type':kind}
    if kind=='error':return {'type':'error','message':'ROUNDLOOP_PROVIDER_ERROR'}
    if kind!='transcript':raise ValueError('unknown frame')
    segments=m.get('segments',[]);partial=m.get('partial','')
    if not isinstance(segments,list) or len(segments)>1000 or not isinstance(partial,str) or len(partial)>20000:raise ValueError('invalid transcript')
    out=[]
    for s in segments:
        if not isinstance(s,dict) or not isinstance(s.get('text'),str) or len(s['text'])>20000:raise ValueError('invalid segment')
        out.append({k:s.get(k,'') for k in ('text','start','end')})
    return {'type':'transcript','segments':out,'partial':partial,'speech':m.get('speech') is True}

@router.websocket('/stream/{token}')
async def stream(ws:WebSocket,token:str):
    ticket=ws.app.state.roundloop_tickets.pop(token,None)
    request=Request({**ws.scope,'type':'http','method':'GET'})
    try:
        if ws.headers.get('origin')!=ws.app.state.settings.origin or not ticket or ticket['expires']<time.monotonic():raise ValueError('invalid session')
        def check():
            a=authorized(request,ticket['subject'])
            if a['actor_id']!=ticket['actor'] or a['session_hash']!=ticket['session']:raise ValueError('changed session')
        check()
        if ws.app.state.roundloop_active>=2:raise ValueError('busy')
    except Exception:
        await ws.close(code=1008);return
    await ws.accept();ws.app.state.roundloop_active+=1
    cfg=config(ws.app.state.settings)
    uri=cfg['base_url'].rstrip('/').replace('https://','wss://',1)+'/v1/stream?'+urlencode({'key':cfg['api_key']})
    try:
        async with asyncio.timeout(210):
            async with connect(uri,proxy=None,open_timeout=15,close_timeout=2,max_size=250000) as upstream:
                stopped=False
                async def send_audio():
                    nonlocal stopped
                    total=0
                    while True:
                        m=await ws.receive();check()
                        if m['type']=='websocket.disconnect':return
                        if m.get('bytes') is not None:
                            b=m['bytes'];total+=len(b)
                            if not b or len(b)>40000 or len(b)%2 or total>16000*2*180:raise ValueError('audio limit')
                            await upstream.send(b)
                        elif m.get('text') and json.loads(m['text'])=={'type':'stop'}:
                            stopped=True;await upstream.send('{"type":"stop"}')
                            # Keep waiting for disconnect so cancellation still releases upstream.
                            async with asyncio.timeout(25):
                                while (await ws.receive())['type']!='websocket.disconnect':pass
                            return
                        else:raise ValueError('invalid control')
                async def receive_text():
                    async for raw in upstream:
                        check();m=clean_message(raw)
                        if m['type']=='done' and not stopped:raise ValueError('unexpected done')
                        await ws.send_json(m)
                        if m['type'] in ('done','error'):return
                    raise ValueError('incomplete stream')
                tasks=[asyncio.create_task(send_audio()),asyncio.create_task(receive_text())]
                try:
                    done,_=await asyncio.wait(tasks,return_when=asyncio.FIRST_COMPLETED)
                    for task in done:task.result()
                finally:
                    for task in tasks:task.cancel()
                    await asyncio.gather(*tasks,return_exceptions=True)
    except Exception:
        # Never echo upstream URLs, response bodies or exception messages containing credentials.
        try:await ws.send_json({'type':'error','message':'ROUNDLOOP_STREAM_FAILED'})
        except Exception:pass
    finally:
        ws.app.state.roundloop_active-=1
        try:await ws.close()
        except Exception:pass
