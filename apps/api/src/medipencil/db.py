import json
from contextlib import contextmanager
from pathlib import Path
from sqlalchemy import create_engine, event
from alembic.config import Config
from alembic import command
from .common import Fault, now, uid


def dump(value): return json.dumps(value, ensure_ascii=False, sort_keys=True)
def decode(row):
    if row is None: return None
    return {k.removesuffix('_json'): json.loads(v) if k.endswith('_json') and v is not None else v for k,v in dict(row).items()}

class Store:
    def __init__(self, root):
        self.engine = create_engine('sqlite:///' + str(Path(root) / 'demo.sqlite'), connect_args={'check_same_thread':False, 'timeout':10})
        @event.listens_for(self.engine, 'connect')
        def pragmas(conn, _):
            import sqlite3
            conn.row_factory = sqlite3.Row
            conn.execute('PRAGMA foreign_keys=ON')
            conn.execute('PRAGMA journal_mode=WAL')
    def migrate(self):
        config = Config()
        config.set_main_option('script_location', str(Path(__file__).parent / 'migrations'))
        with self.engine.begin() as connection:
            config.attributes['connection'] = connection
            command.upgrade(config, 'head')
    @contextmanager
    def transaction(self):
        conn = self.engine.raw_connection()
        try:
            conn.execute('BEGIN IMMEDIATE')
            yield conn
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        finally: conn.close()


def one(db, sql, args=()): return decode(db.execute(sql,args).fetchone())
def many(db, sql, args=()): return [decode(r) for r in db.execute(sql,args).fetchall()]
def need(db, sql, args=()):
    row=one(db,sql,args)
    if row is None: raise Fault('RESOURCE_NOT_FOUND',404)
    return row

def insert(db, table, **values):
    # Table and field names are internal constants, never request input.
    converted={k:dump(v) if k.endswith('_json') else v for k,v in values.items()}
    db.execute(f"INSERT INTO {table} ({','.join(converted)}) VALUES ({','.join('?' for _ in converted)})",tuple(converted.values()))

def audit(db, actor, action, subject, obj, outcome='success'):
    insert(db,'audit_events',audit_id=uid(),actor_id=actor,action=action,subject_id=subject,object_id=obj,timestamp=now(),outcome=outcome,request_id=uid())
