import pytest
from fastapi.testclient import TestClient
from medipencil.config import Settings
from medipencil.main import create_app
from medipencil.seed import seed

PAGES='https://hyosang-ryu.github.io'
API='https://orch.sungah.kr'

@pytest.fixture
def client(tmp_path):
    app=create_app(Settings(tmp_path, origin=API, secret='s'*32, shared_review=True,
        public_review=True, poc_mode=True, pages_origin=PAGES))
    seed(app.state.store)
    with TestClient(app, base_url=API) as c:yield c


def login(client, actor='staff'):
    response=client.post('/api/v1/demo/session',headers={'Origin':PAGES},json={'demo_actor_id':actor})
    assert response.status_code==201
    assert 'set-cookie' not in response.headers
    assert response.headers['access-control-allow-origin']==PAGES
    data=response.json()['data']
    return {'Origin':PAGES, 'Authorization':'Bearer '+data['access_token'], 'X-CSRF-Token':data['csrf_token']}


def test_pages_preflight_only_exact_origin(client):
    for origin,status in [(PAGES,200),('https://evil.example',400)]:
        r=client.options('/api/v1/poc/comments',headers={'Origin':origin,'Access-Control-Request-Method':'POST',
            'Access-Control-Request-Headers':'authorization,x-csrf-token,idempotency-key,content-type,if-match'})
        assert r.status_code==status
    assert client.post('/api/v1/demo/session',headers={'Origin':'https://evil.example'},json={'demo_actor_id':'staff'}).status_code==403


def test_pages_token_csrf_role_switch_logout(client):
    staff=login(client)
    assert client.get('/api/v1/session',headers=staff).json()['data']['actor_id']=='staff'
    bad=dict(staff,Origin='https://evil.example')
    assert client.get('/api/v1/session',headers=bad).status_code==401
    bad=dict(staff);bad.pop('Origin')
    assert client.get('/api/v1/session',headers=bad).status_code==401
    payload={'reviewer_alias':'AUTO-PAGES-UNIT','screen':'general','body':'Synthetic integration check'}
    bad=dict(staff);bad.pop('X-CSRF-Token')
    assert client.post('/api/v1/poc/comments',headers={**bad,'Idempotency-Key':'bad'},json=payload).status_code==403
    saved=client.post('/api/v1/poc/comments',headers={**staff,'Idempotency-Key':'good'},json=payload)
    assert saved.status_code==201
    other=login(client)
    assert len(client.get('/api/v1/poc/comments',headers=other).json()['data']['items'])==1
    switched=client.post('/api/v1/demo/session',headers=staff,json={'demo_actor_id':'liisa'})
    assert switched.status_code==201
    assert client.get('/api/v1/session',headers=staff).status_code==401
    family=login(client,'liisa')
    assert client.get('/api/v1/poc/comments',headers=family).status_code==403
    assert client.delete('/api/v1/demo/session',headers=other).status_code==204
    assert client.get('/api/v1/session',headers=other).status_code==401


def test_cookie_transport_remains_separate(client):
    r=client.post('/api/v1/demo/session',headers={'Origin':API},json={'demo_actor_id':'liisa'})
    assert r.status_code==201 and 'access_token' not in r.json()['data']
    assert 'set-cookie' in r.headers
    assert client.get('/api/v1/session').status_code==200
    assert client.get('/api/v1/session',headers={'Origin':PAGES}).status_code==401


@pytest.mark.parametrize('origin',['https://hyosang-ryu.github.io/path','http://hyosang-ryu.github.io','*'])
def test_invalid_pages_origin(tmp_path,origin):
    with pytest.raises(ValueError):Settings(tmp_path,origin=API,secret='s'*32,shared_review=True,public_review=True,poc_mode=True,pages_origin=origin)
