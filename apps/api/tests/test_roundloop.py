import asyncio,json
from contextlib import asynccontextmanager
import pytest
from starlette.websockets import WebSocketDisconnect
from conftest import Browser
from medipencil.roundloop import clean_message

@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setattr('medipencil.roundloop.config',lambda settings:{'base_url':'https://example.invalid','api_key':'TEST-SECRET'})
    frames=[]
    class Upstream:
        def __init__(self):self.stopped=asyncio.Event()
        async def send(self,data):
            frames.append(data)
            if isinstance(data,str):self.stopped.set()
        async def __aiter__(self):
            yield json.dumps({'type':'ready'})
            await self.stopped.wait()
            yield json.dumps({'type':'transcript','segments':[{'text':'First'}],'partial':'tail'})
            yield json.dumps({'type':'transcript','segments':[{'text':'First'},{'text':'Second'}],'partial':''})
            yield json.dumps({'type':'done'})
    @asynccontextmanager
    async def fake(*args,**kwargs):yield Upstream()
    monkeypatch.setattr('medipencil.roundloop.connect',fake)
    return frames

def test_stream_ticket_origin_replay_and_snapshot(app,provider):
    staff=Browser(app);family=Browser(app,'liisa');body={'subject':'aino','external_synthetic_ack':True}
    assert family.post('/staff/roundloop/sessions',body).status_code==403
    assert staff.post('/staff/roundloop/sessions',{**body,'external_synthetic_ack':False}).status_code==422
    data=staff.post('/staff/roundloop/sessions',body).json()['data']
    assert 'TEST-SECRET' not in str(data)
    with staff.client.websocket_connect(data['path'],headers={'origin':app.state.settings.origin}) as ws:
        assert ws.receive_json()=={'type':'ready'}
        ws.send_bytes(bytes(3200));ws.send_text('{"type":"stop"}')
        assert len(ws.receive_json()['segments'])==1
        assert len(ws.receive_json()['segments'])==2
        assert ws.receive_json()=={'type':'done'}
    with pytest.raises(WebSocketDisconnect):
        with staff.client.websocket_connect(data['path'],headers={'origin':app.state.settings.origin}):pass
    data=staff.post('/staff/roundloop/sessions',body).json()['data']
    with pytest.raises(WebSocketDisconnect):
        with staff.client.websocket_connect(data['path'],headers={'origin':'https://untrusted.invalid'}):pass
    assert provider==[bytes(3200),'{"type":"stop"}']

def test_oversized_stream_and_errors_are_sanitized(app,provider):
    staff=Browser(app);data=staff.post('/staff/roundloop/sessions',{'subject':'aino','external_synthetic_ack':True}).json()['data']
    with staff.client.websocket_connect(data['path'],headers={'origin':app.state.settings.origin}) as ws:
        assert ws.receive_json()['type']=='ready'
        ws.send_bytes(bytes(40002))
        assert ws.receive_json()=={'type':'error','message':'ROUNDLOOP_STREAM_FAILED'}
    assert provider==[]
    assert clean_message('{"type":"error","message":"secret"}')['message']=='ROUNDLOOP_PROVIDER_ERROR'
