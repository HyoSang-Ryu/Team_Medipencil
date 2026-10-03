import sqlite3
import pytest
from medipencil.db import Store, insert, one
from medipencil.common import now
from medipencil.domain import timestamp
from medipencil.common import Fault

def test_migrate_foreign_key_and_rollback(tmp_path):
    store=Store(tmp_path); store.migrate(); store.migrate()
    with pytest.raises(sqlite3.IntegrityError), store.transaction() as db:
        insert(db,'residents',subject_id='bad',unit_id='missing',display_name='synthetic',data_origin='TEAM_SYNTHETIC')
    with pytest.raises(RuntimeError), store.transaction() as db:
        insert(db,'units',unit_id='u',name='test'); raise RuntimeError()
    with store.transaction() as db:
        assert one(db,'SELECT * FROM units') is None
        assert db.execute('SELECT count(*) FROM sqlite_master WHERE type="table"').fetchone()[0] == 20

@pytest.mark.parametrize('value',['2026-01-01T00:00:00','2099-01-01T00:00:00Z','bad'])
def test_time_rejection(value):
    with pytest.raises(Fault): timestamp(value)
