import pytest
from fastapi.testclient import TestClient
from medipencil.config import Settings
from medipencil.main import create_app
from medipencil.seed import seed
from uuid import uuid4

@pytest.fixture
def app(tmp_path):
    app=create_app(Settings(tmp_path,secret='s'*32));seed(app.state.store)
    return app

class Browser:
    def __init__(self,app,actor='staff'):
        self.client=TestClient(app);self.actor=actor
        self.client.headers['origin']=app.state.settings.origin
        r=self.client.post('/api/v1/demo/session',json={'demo_actor_id':actor})
        assert r.status_code==201,r.text
        self.client.headers['x-csrf-token']=r.json()['data']['csrf_token']
    def get(self,path,**kw): return self.client.get('/api/v1'+path,**kw)
    def post(self,path,body=None,rev=None,key=None):
        h={'Idempotency-Key':key or str(uuid4())}
        if rev is not None:h['If-Match']='"'+str(rev)+'"'
        return self.client.post('/api/v1'+path,json=body or {},headers=h)
    def patch(self,path,body,rev):
        return self.client.patch('/api/v1'+path,json=body,headers={'Idempotency-Key':str(uuid4()),'If-Match':'"'+str(rev)+'"'})
