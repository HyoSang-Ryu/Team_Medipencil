from alembic import op
revision='007'
down_revision='006'
def upgrade():
    op.execute('''CREATE TABLE voice_charts(
        chart_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL REFERENCES residents,
        capture_id TEXT NOT NULL REFERENCES captures, revision INTEGER NOT NULL DEFAULT 1,
        status TEXT NOT NULL DEFAULT 'draft', required_json TEXT NOT NULL,
        answers_json TEXT NOT NULL DEFAULT '{}', record_id TEXT,
        created_by TEXT NOT NULL REFERENCES actors, created_at TEXT NOT NULL, updated_at TEXT NOT NULL)''')
def downgrade():
    raise RuntimeError('Destructive downgrade is not supported')
