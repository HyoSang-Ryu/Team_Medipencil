from fastapi.testclient import TestClient
from conftest import Browser
from medipencil.db import Store

PAYLOAD = {'reviewer_alias':'reviewer-test','screen':'publication','body':'AUTOMATED TEST: review button spacing'}


def test_comments_persist_filter_and_retry_without_duplicates(app):
    app.state.settings.poc_mode = True
    first, second = Browser(app), Browser(app)
    result = first.post('/poc/comments', PAYLOAD, key='retry-comment')
    assert result.status_code == 201
    comment = result.json()['data']
    assert first.post('/poc/comments', PAYLOAD, key='retry-comment').json()['data'] == comment
    assert first.post('/poc/comments', PAYLOAD | {'body':'changed'}, key='retry-comment').status_code == 409
    assert second.get('/poc/comments?screen=publication').json()['data']['items'] == [comment]
    assert second.get('/poc/comments?screen=consent').json()['data']['items'] == []
    assert 'actor_id' not in comment
    reopened = Store(app.state.settings.root)
    reopened.migrate()
    with reopened.transaction() as db:
        assert db.execute('SELECT count(*) FROM review_comments').fetchone()[0] == 1
    reopened.engine.dispose()


def test_comments_require_poc_staff_session_and_csrf(app):
    staff = Browser(app)
    assert staff.get('/poc/comments').status_code == 404
    assert staff.post('/poc/comments',PAYLOAD).status_code == 404
    app.state.settings.poc_mode = True
    assert TestClient(app).get('/api/v1/poc/comments').status_code == 401
    family = Browser(app,'liisa')
    assert family.get('/poc/comments').status_code == 403
    assert family.post('/poc/comments',PAYLOAD).status_code == 403
    staff.client.headers['x-csrf-token'] = 'invalid'
    assert staff.post('/poc/comments',PAYLOAD).status_code == 403
    assert Browser(app).get('/poc/comments').json()['data']['items'] == []


def test_comments_validate_blank_length_screen_and_extra_fields(app):
    app.state.settings.poc_mode = True
    staff=Browser(app)
    for patch in [{'body':'  '},{'body':'x'*3001},{'reviewer_alias':'  '},{'reviewer_alias':'x'*41},{'screen':'patient-source'},{'actor_id':'liisa'}]:
        assert staff.post('/poc/comments',PAYLOAD|patch).status_code == 422
    assert staff.get('/poc/comments?screen=invalid').status_code == 422
    assert staff.get('/poc/comments').json()['data']['items'] == []


def test_upgrade_preserves_existing_round(tmp_path):
    from pathlib import Path
    from alembic import command
    from alembic.config import Config
    import medipencil
    store=Store(tmp_path)
    config=Config()
    config.set_main_option('script_location',str(Path(medipencil.__file__).parent/'migrations'))
    with store.engine.begin() as connection:
        config.attributes['connection']=connection
        command.upgrade(config,'001')
    with store.transaction() as db:
        db.execute("INSERT INTO units(unit_id,name) VALUES ('existing','synthetic existing round')")
    store.migrate()
    with store.transaction() as db:
        assert db.execute("SELECT name FROM units WHERE unit_id='existing'").fetchone()[0]=='synthetic existing round'
        assert db.execute('SELECT count(*) FROM review_comments').fetchone()[0]==0
    store.engine.dispose()
