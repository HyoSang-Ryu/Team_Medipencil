from fastapi.testclient import TestClient
from medipencil.main import create_app
from medipencil.config import Settings
from medipencil.seed import seed
from conftest import Browser


def test_new_run_excludes_retired_guardian(tmp_path):
    app=create_app(Settings(tmp_path,secret='s'*32));seed(app.state.store)
    c=TestClient(app,headers={'Origin':app.state.settings.origin})
    assert c.get('/api/v1/health').json()['data']['allowed_actors']==['liisa','staff']
    assert c.post('/api/v1/demo/session',json={'demo_actor_id':'mikko'}).status_code==403
    staff=Browser(app)
    assert [g['recipient_id'] for g in staff.get('/staff/residents/aino/consents').json()['data']['grants']]==['liisa']


def test_upgrade_retires_existing_session_but_preserves_history(app):
    # Standard test fixture deliberately activates a second recipient for isolation tests.
    mikko=Browser(app,'mikko')
    saved=mikko.post('/family/residents/aino/questions',{'text':'Independent synthetic historic question'}).json()['data']
    with app.state.store.transaction() as db:
        db.execute("UPDATE alembic_version SET version_num='003'")
    app.state.store.migrate()
    assert mikko.get('/session').status_code==401
    assert mikko.client.post('/api/v1/demo/session',json={'demo_actor_id':'mikko'}).status_code==403
    assert 'mikko' not in mikko.get('/health').json()['data']['allowed_actors']
    with app.state.store.transaction() as db:
        assert db.execute('SELECT text FROM family_questions WHERE question_id=?',(saved['question_id'],)).fetchone()[0]=='Independent synthetic historic question'
        assert db.execute("SELECT count(*) FROM demo_sessions WHERE actor_id='mikko'").fetchone()[0]==0
        assert db.execute("SELECT active FROM access_memberships WHERE actor_id='mikko' AND subject_id='aino'").fetchone()[0]==0
