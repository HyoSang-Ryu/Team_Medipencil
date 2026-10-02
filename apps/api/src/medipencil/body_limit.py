from starlette.responses import JSONResponse
from .common import envelope

class BodyLimit:
    """Bound request bytes before multipart parsing, including chunked requests."""
    def __init__(self,app,max_bytes=21*1024*1024):self.app,self.max_bytes=app,max_bytes
    async def __call__(self,scope,receive,send):
        if scope['type']!='http' or scope['method'] not in ('POST','PATCH','PUT'):
            return await self.app(scope,receive,send)
        parts=[];total=0
        while True:
            message=await receive()
            if message['type']=='http.disconnect':return
            chunk=message.get('body',b'');total+=len(chunk)
            if total>self.max_bytes:
                result=envelope(None);result.pop('data');result['error']={'code':'AUDIO_TOO_LARGE','message_key':'errors.audio_too_large','retryable':False}
                return await JSONResponse(result,status_code=413,headers={'Cache-Control':'no-store'})(scope,receive,send)
            parts.append(chunk)
            if not message.get('more_body',False):break
        consumed=False
        async def replay():
            nonlocal consumed
            if not consumed:
                consumed=True;return {'type':'http.request','body':b''.join(parts),'more_body':False}
            return await receive()
        await self.app(scope,replay,send)
