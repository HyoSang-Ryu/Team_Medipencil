from conftest import Browser

def test_identity_and_scope(app):
    liisa=Browser(app,'liisa');mikko=Browser(app,'mikko')
    assert liisa.get('/staff/residents').status_code==403
    assert 'health_context' not in mikko.get('/family/residents/aino/sharing').json()['data']['scopes']
    assert mikko.get('/family/residents/other/sharing').status_code==404
    assert mikko.get('/family/residents/aino/sharing?recipient_id=liisa').status_code==422

def test_origin_csrf_and_rotation(app):
    b=Browser(app);old=b.client.cookies.get('mp_session')
    b.client.headers['origin']='https://invalid.example'
    assert b.client.post('/api/v1/demo/session',json={'demo_actor_id':'liisa'}).status_code==403
    b.client.headers['origin']=app.state.settings.origin
    assert b.client.post('/api/v1/demo/session',json={'demo_actor_id':'liisa'}).status_code==201
    b.client.cookies.clear(); b.client.cookies.set('mp_session',old)
    assert b.get('/session').status_code==401
