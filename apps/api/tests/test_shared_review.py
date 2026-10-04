import pytest
from fastapi.testclient import TestClient
from medipencil.config import Settings
from medipencil.main import create_app
from medipencil.seed import seed

ORIGIN='https://review.example.test'

def settings(tmp_path, **kw):
    values=dict(root=tmp_path,origin=ORIGIN,secret='s'*32,poc_mode=True,shared_review=True,proxy_secret='p'*32,reviewers={'nurse':['staff'],'family':['liisa'],'other':['staff']})
    return Settings(**(values|kw))

@pytest.mark.parametrize('overrides',[{'origin':'http://review.example.test'},{'poc_mode':False},{'proxy_secret':''},{'proxy_secret':'s'*32},{'reviewers':{}},{'reviewers':{'x':['admin']}},{'cookie_path':'/bad;path/'},{'origin':'https://review.example.test/path'}])
def test_reject_unsafe_configuration(tmp_path,overrides):
    with pytest.raises(ValueError): settings(tmp_path,**overrides)

def test_access_roles_identity_binding_and_revocation(tmp_path):
    app=create_app(settings(tmp_path));seed(app.state.store)
    with TestClient(app,base_url=ORIGIN) as client:
        for path in ['/', '/api/v1/health','/api/v1/staff/residents']:
            assert client.get(path).status_code==401
        client.headers.update({'X-Medipencil-Reviewer':'nurse','X-Medipencil-Proxy-Key':'wrong'})
        assert client.get('/api/v1/health').status_code==401
        client.headers.update({'X-Medipencil-Proxy-Key':'p'*32,'Origin':ORIGIN})
        assert client.get('/api/v1/health').json()['data']['allowed_actors']==['staff']
        assert client.post('/api/v1/demo/session',json={'demo_actor_id':'mikko'}).status_code==403
        r=client.post('/api/v1/demo/session',json={'demo_actor_id':'staff'})
        assert r.status_code==201
        assert 'Secure' in r.headers['set-cookie'] and 'HttpOnly' in r.headers['set-cookie']
        assert r.json()['data']['authentication']=='AUTHENTICATED_SYNTHETIC_REVIEW'
        assert client.get('/api/v1/staff/residents').status_code==200
        client.headers['X-Medipencil-Reviewer']='other'
        assert client.get('/api/v1/staff/residents').status_code==401
        client.headers['X-Medipencil-Reviewer']='nurse'
        app.state.settings.reviewers['nurse']=['liisa']
        assert client.get('/api/v1/staff/residents').status_code==403
        del app.state.settings.reviewers['nurse']
        assert client.get('/api/v1/health').status_code==401

def test_family_cannot_select_staff_or_read_comments(tmp_path):
    app=create_app(settings(tmp_path));seed(app.state.store)
    with TestClient(app,base_url=ORIGIN,headers={'Origin':ORIGIN,'X-Medipencil-Reviewer':'family','X-Medipencil-Proxy-Key':'p'*32}) as client:
        assert client.post('/api/v1/demo/session',json={'demo_actor_id':'staff'}).status_code==403
        r=client.post('/api/v1/demo/session',json={'demo_actor_id':'liisa'})
        assert r.status_code==201
        assert client.get('/api/v1/poc/comments').status_code==403
        client.headers['X-CSRF-Token']=r.json()['data']['csrf_token']
        client.headers['Origin']='https://evil.example.test'
        assert client.delete('/api/v1/demo/session').status_code==403
        assert client.get('/api/v1/health',headers={'host':'evil.example.test'}).status_code==400

def test_scoped_cookie_and_env(tmp_path,monkeypatch):
    import json
    reviewers=tmp_path/'reviewers.json';reviewers.write_text(json.dumps({'nurse':['staff']}))
    for key,value in {'MEDIPENCIL_DATA_ROOT':str(tmp_path/'data'),'MEDIPENCIL_ORIGIN':ORIGIN,'MEDIPENCIL_SESSION_SECRET':'s'*32,'MEDIPENCIL_PROXY_SECRET':'p'*32,'MEDIPENCIL_POC':'1','MEDIPENCIL_SHARED_REVIEW':'1','MEDIPENCIL_REVIEWERS_FILE':str(reviewers),'MEDIPENCIL_COOKIE_PATH':'/medipencil/'}.items():monkeypatch.setenv(key,value)
    app=create_app(Settings.env());seed(app.state.store)
    with TestClient(app,base_url=ORIGIN,headers={'Origin':ORIGIN,'X-Medipencil-Reviewer':'nurse','X-Medipencil-Proxy-Key':'p'*32}) as client:
        r=client.post('/api/v1/demo/session',json={'demo_actor_id':'staff'})
        assert 'Path=/medipencil/' in r.headers['set-cookie']
        assert app.state.settings.models.stt_backend=='disabled'
