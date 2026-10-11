from alembic import op
revision='005'
down_revision='004'

def upgrade():
    op.execute('''CREATE TABLE delivery_schedules(subject_id TEXT NOT NULL REFERENCES residents,
        recipient_id TEXT NOT NULL REFERENCES actors, enabled INTEGER NOT NULL DEFAULT 0,
        revision INTEGER NOT NULL DEFAULT 1, configured_by TEXT NOT NULL REFERENCES actors,
        next_run_at TEXT, last_run_at TEXT, last_result TEXT, last_publication_id TEXT,
        exceptions_json TEXT NOT NULL DEFAULT '[]', updated_at TEXT NOT NULL,
        PRIMARY KEY(subject_id,recipient_id))''')
    op.execute('''CREATE TABLE routine_delivery_sources(source_id TEXT NOT NULL, source_version INTEGER NOT NULL,
        PRIMARY KEY(source_id,source_version), FOREIGN KEY(source_id,source_version) REFERENCES source_events(source_id,version))''')
    op.execute('''CREATE TABLE routine_delivery_runs(subject_id TEXT NOT NULL,recipient_id TEXT NOT NULL,
        local_day TEXT NOT NULL,result TEXT NOT NULL,publication_id TEXT,created_at TEXT NOT NULL,
        PRIMARY KEY(subject_id,recipient_id,local_day))''')

def downgrade():
    raise RuntimeError('Destructive downgrade is not supported')
